# -*- coding: utf-8 -*-
'''Segy2netcdf: convert SEG-Y files to NetCDF files.
'''
import click
import segyio
import numpy as np
from netCDF4 import Dataset

@click.command()
@click.argument('segy_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('netcdf_path', type=click.Path())
@click.option('--samples_dim_name', '-sdn', type=str,
        help="Name of trace samples dimension (usually Time or Depth)")
@click.option('-d', type=(str, int), multiple=True,
        help='Name and length (separated by a space) '
        'of other dimensions, in slowest to fastest order. If the name '
        'matches the name of a trace header field (using segyio.TraceField '
        'names), then the header values will be used for the dimension '
        'coordinates, otherwise the dimension coordinates will start at '
        '0 and increment by 1. '
        'E.g. -d ShotPoint 10 -d GroupNumber 5, indicates that the data '
        'consists of 10 shot gathers, each with 5 receiver traces. As '
        'ShotPoint is a trace header name, the trace header values will be '
        'used as coordinates for that dimension. GroupNumber is not a '
        'header name, so the coordinates of that dimension will be 0 to 4.')
@click.option('--compress/--no-compress', default=False,
        help='turn on or off NetCDF compression (default off).')
def segy2netcdf(segy_path, netcdf_path, samples_dim_name, d, compress):
    '''Convert a SEG-Y file to a NetCDF file.

       segy_path: path to input SEG-Y file
       netcdf_path: path to output NetCDF file
       samples_dim_name: name of trace samples dimension (usually Time or Depth)
       d: tuple of (name, len) tuples for each dimension, slowest to fastest order
       compress: boolean flag indicating whether NetCDF compression should be used
    '''

    # set default name for trace samples dimension
    if not samples_dim_name:
        samples_dim_name = 'SampleNumber'

    with segyio.open(segy_path) as segy:
        ns = len(segy.samples)
        ntraces = segy.tracecount

        dim_names, dim_lens = _make_dim_name_len(samples_dim_name, ns, d)
        dims_ntraces = _count_traces_in_user_dims(d)

        _check_user_dims(dims_ntraces, ntraces)

        _fill_missing_dims(dims_ntraces, ntraces, dim_names, dim_lens)

        rootgrp = Dataset(netcdf_path, "w", format="NETCDF4")
        _create_dimensions(dim_names, dim_lens, rootgrp)
        variables = _create_variables(rootgrp, dim_names, compress)
        _set_attributes(segy, rootgrp)
        _copy_data(segy, variables, dim_names, dim_lens)

        rootgrp.close()

def _make_dim_name_len(samples_dim_name, ns, d):
    '''Make dim_names and dim_lens lists of dimension names and lens.
       Uses the input 'd' tuple, and the number of samples from the SEG-Y file.
    '''
    dim_names = []
    dim_lens = []
    for dim in d:
        dim_names.append(dim[0])
        dim_lens.append(dim[1])
    dim_names.append(samples_dim_name)
    dim_lens.append(ns)
    return dim_names, dim_lens

def _count_traces_in_user_dims(d):
    '''Determine how many traces are accounted for by the dimensions provided by user.
    '''
    dims_ntraces = 1
    for dim in d:
        dims_ntraces *= dim[1]
    return dims_ntraces

def _check_user_dims(dims_ntraces, ntraces):
    '''Check that the lengths of the user-provided dimensions make sense.
    '''
    if dims_ntraces > ntraces:
        raise ValueError('supplied dimensions imply %d traces, '
        'but only %d in file' % (dims_ntraces, ntraces))
    if ntraces % dims_ntraces != 0:
        raise ValueError('supplied dimensions imply %d traces, '
        'but this does not divide into the %d traces in the file' %
        (dims_ntraces, ntraces))

def _fill_missing_dims(dims_ntraces, ntraces, dim_names, dim_lens):
    '''Make a new dimension (if necessary) for unaccounted traces.
    '''
    if dims_ntraces < ntraces:
        dim_names.insert(0, 'Traces')
        dim_lens.insert(0, int(ntraces / dims_ntraces))

def _create_dimensions(dim_names, dim_lens, rootgrp):
    '''Create the dimensions in the NetCDF file.
    '''
    for dim in zip(dim_names, dim_lens):
        rootgrp.createDimension(dim[0], dim[1])


def _create_variables(rootgrp, dim_names, compress):
    '''Create variables in the NetCDF file.
       The trace data, Time/Depth dimension, and trace headers, are all created as variables.
    '''
    variables = []
    # Trace data
    variables.append(rootgrp.createVariable("Samples", "f4", tuple(dim_names), zlib=compress))
    # Time/Depth dimension
    variables.append(rootgrp.createVariable(dim_names[-1], "f4", dim_names[-1], zlib=compress))
    # Other dimensions
    variables += _create_traceheader_variables(rootgrp, dim_names, compress)
    return variables

def _create_traceheader_variables(rootgrp, dim_names, compress):
    '''Create NetCDF variables for each trace header field.
       Fields that are used as dimensions are only the length of that dimension,
       others have one entry for every trace.
    '''
    fields = [attr for attr in dir(segyio.TraceField)
            if not callable(getattr(segyio.TraceField, attr))
            and not attr.startswith("__")]
    variables = []
    for field in fields:
        # for variables that are dimensions of the dataset, they should be the
        # size of their dimension. All others should be the size of the dataset
        # (excluding the trace samples dimension)
        if field in dim_names:
            variables.append(rootgrp.createVariable(field, "i4", field, zlib=compress))
        else:
            variables.append(rootgrp.createVariable(field, "i4", tuple(dim_names[:-1]), zlib=compress))

    return variables

def _set_attributes(segy, rootgrp):
    '''Copy the file headers (binary and text) to the NetCDF file.
    '''
    rootgrp.bin = str(segy.bin)
    rootgrp.text = segy.text[0]
    if segy.ext_headers:
        rootgrp.ext_headers = segy.text[1]

def _copy_data(segy, variables, dim_names, dim_lens):
    '''Copy the data to the NetCDF file.
       Trace data, Time/Depth dimension indices, and trace header values are copied.
    '''
    traceIDs = np.reshape(np.arange(segy.tracecount), dim_lens[:-1])
    n_trace_dims = len(dim_names[:-1])
    for v in variables:
        if v.name == 'Samples':
            print('starting trace copy')
            v[:] = segy.trace.raw[:]
        elif v.name == dim_names[-1]:
            print('starting time/depth copy')
            v[:] = segyio.sample_indexes(segy)
        else:
            print('starting', v.name)
            v_traceIDs = _get_variable_traceIDs(v, n_trace_dims, dim_names, traceIDs)
            header_field = _get_header_field(v.name)
            v[:] = segy.attributes(header_field)[v_traceIDs.flatten()[:]]

def _get_variable_traceIDs(variable, n_trace_dims, dim_names, traceIDs):
    '''Make a list of trace IDs to copy trace header data from.
       Headers used as dimensions will only copy from traces that should contain
       unique values for them, while other headers will copy from every trace.
    '''
    vdims = ['1,'] * n_trace_dims
    v_trace_dims = variable.dimensions
    for d in v_trace_dims:
        d_idx = dim_names.index(d)
        vdims[d_idx] = ':,'
    v_traceIDs = np.array(eval('traceIDs[%s]' % ''.join(vdims)))
    return v_traceIDs

def _get_header_field(name):
    '''Get the position of the requested header value in the trace headers.
    '''
    try:
        field = eval('segyio.TraceField.%s' % name)
    except AttributeError:
        field = None
    return field
