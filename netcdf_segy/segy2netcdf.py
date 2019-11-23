# -*- coding: utf-8 -*-
"""Segy2netcdf: convert SEG-Y files to NetCDF files.
"""
import click
import segyio
import numpy as np
from netCDF4 import Dataset


@click.command()
@click.argument("segy_path", type=click.Path(exists=True, dir_okay=False))
@click.argument("netcdf_path", type=click.Path())
@click.option(
    "--samples_dim_name",
    "-sdn",
    type=str,
    help="Name of trace samples dimension (usually Time or Depth)",
)
@click.option(
    "-d",
    type=(str, int),
    multiple=True,
    help="Name and length (separated by a space) "
    "of other dimensions, in slowest to fastest order. If the name "
    "matches the name of a trace header field (using "
    "segyio.TraceField names), then the header values will be used "
    "for the dimension coordinates, otherwise the dimension "
    "coordinates will start at 0 and increment by 1. "
    "E.g. -d FieldRecord 10 -d GroupNumber 5, indicates that the "
    "data consists of 10 shot gathers, each with 5 receiver traces. "
    "As FieldRecord is a trace header name, the trace header values "
    "will be used as coordinates for that dimension. GroupNumber is "
    "not a header name, so the coordinates of that dimension will "
    "be 0 to 4.",
)
@click.option(
    "--compress/--no-compress",
    default=False,
    help="turn on or off NetCDF compression (default off).",
)
@click.option(
    "--verbose/--quiet",
    default=False,
    help="turn on or off verbose output (default off).",
)
def cli(segy_path, netcdf_path, samples_dim_name, d, compress, verbose):
    """Click CLI for segy2netcdf."""
    segy2netcdf(segy_path, netcdf_path, samples_dim_name, d, compress, verbose)


def segy2netcdf(
    segy_path, netcdf_path, samples_dim_name=None, d=(), compress=False, verbose=False
):
    """Convert a SEG-Y file to a NetCDF file.

    Args:
        segy_path: A string specifying the path to input SEG-Y file.
        netcdf_path: A string specifying the path to output NetCDF file
        samples_dim_name: An optional string specifying the name of trace
            samples dimension (usually Time or Depth). Default SampleNumber.
        d: An optional tuple of tuples of the form (string, int), where the
            string specifies a dimension name, and the int specifies the number
            of entries in that dimension. There should be one of these inner
            tuples for each dimension, excluding the trace sample dimension,
            in slowest to fastest order. Any dimensions not accounted for,
            either because d was not specified, or it was specified but did
            not account for all of the traces in the SEG-Y file, a Traces
            dimension will be used for the remainder.
        compress: An optional boolean flag indicating whether NetCDF
            compression should be used. Default False.
        verbose: An optional boolean flag indicating whether to print
            progress. Default False.
    """

    # set default name for trace samples dimension
    if not samples_dim_name:
        samples_dim_name = "SampleNumber"

    with segyio.open(segy_path, ignore_geometry=True) as segy:
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
        _copy_data(segy, variables, dim_names, dim_lens, verbose)

        rootgrp.close()


def _make_dim_name_len(samples_dim_name, ns, d):
    """Make dim_names and dim_lens lists of dimension names and lens.

    Args:
        samples_dim_name: A string specifying the name to use for the trace
            samples dimension. Usually 'Time' or 'Depth'
        ns: An int specifying the number of samples per trace
        d: A tuple of tuples of the form (string, int), where the string
            specifies a dimension name, and the int specifies the number of
            entries in that dimension.

    Returns:
        dim_names: A list with the dimension names
        dim_lens: A list with the lengths of the dimensions
    """
    dim_names = []
    dim_lens = []
    for dim in d:
        dim_names.append(dim[0])
        dim_lens.append(dim[1])
    dim_names.append(samples_dim_name)
    dim_lens.append(ns)
    return dim_names, dim_lens


def _count_traces_in_user_dims(d):
    """Determine how many traces are accounted for by the dimensions provided
       by the user.
    """
    dims_ntraces = 1
    for dim in d:
        dims_ntraces *= dim[1]
    return dims_ntraces


def _check_user_dims(dims_ntraces, ntraces):
    """Check that the lengths of the user-provided dimensions make sense."""
    if dims_ntraces > ntraces:
        raise ValueError(
            "supplied dimensions imply {} traces, "
            "but only {} in file".format(dims_ntraces, ntraces)
        )
    if dims_ntraces < 0:
        raise ValueError("supplied dimensions imply {} traces".format(dims_ntraces))
    if (dims_ntraces == 0) and (ntraces > 0):
        raise ValueError(
            "supplied dimensions imply {} traces, "
            "but {} in file".format(dims_ntraces, ntraces)
        )
    if (dims_ntraces != 0) and (ntraces % dims_ntraces != 0):
        raise ValueError(
            "supplied dimensions imply {} traces, "
            "but this does not divide into the {} traces in the "
            "file".format(dims_ntraces, ntraces)
        )


def _fill_missing_dims(dims_ntraces, ntraces, dim_names, dim_lens):
    """Make a new dimension (if necessary) for unaccounted traces."""
    if dims_ntraces < ntraces:
        dim_names.insert(0, "Traces")
        dim_lens.insert(0, int(ntraces / dims_ntraces))


def _create_dimensions(dim_names, dim_lens, rootgrp):
    """Create the dimensions in the NetCDF file."""
    for dim in zip(dim_names, dim_lens):
        rootgrp.createDimension(dim[0], dim[1])


def _create_variables(rootgrp, dim_names, compress):
    """Create variables in the NetCDF file.

       The trace data, Time/Depth dimension, and trace headers, are all
       created as variables.
    """
    variables = []
    # Trace data
    variables.append(
        rootgrp.createVariable("Samples", "f4", tuple(dim_names), zlib=compress)
    )
    # Time/Depth dimension
    variables.append(
        rootgrp.createVariable(dim_names[-1], "f4", dim_names[-1], zlib=compress)
    )
    # Other dimensions
    variables += _create_traceheader_variables(rootgrp, dim_names, compress)
    return variables


def _create_traceheader_variables(rootgrp, dim_names, compress):
    """Create NetCDF variables for each trace header field.

       Fields that are used as dimensions are only the length of that
       dimension, others have one entry for every trace.
    """
    fields = [
        attr
        for attr in dir(segyio.TraceField)
        if not callable(getattr(segyio.TraceField, attr)) and not attr.startswith("__")
    ]
    variables = []
    for field in fields:
        # for variables that are dimensions of the dataset, they should be the
        # size of their dimension. All others should be the size of the dataset
        # (excluding the trace samples dimension)
        if field in dim_names:
            variables.append(rootgrp.createVariable(field, "i4", field, zlib=compress))
        else:
            variables.append(
                rootgrp.createVariable(
                    field, "i4", tuple(dim_names[:-1]), zlib=compress
                )
            )

    return variables


def _set_attributes(segy, rootgrp):
    """Copy the file headers (binary and text) to the NetCDF file."""
    rootgrp.bin = str(segy.bin)
    rootgrp.text = segy.text[0].decode(errors='replace')
    if segy.ext_headers:
        rootgrp.ext_headers = segy.text[1].decode(errors='replace')


def _copy_data(segy, variables, dim_names, dim_lens, verbose):
    """Copy the data to the NetCDF file.

       Trace data, Time/Depth dimension indices, and trace header values are
       copied.
    """
    traceIDs = np.reshape(np.arange(segy.tracecount), dim_lens[:-1])
    n_trace_dims = len(dim_names[:-1])
    for v in variables:
        if v.name == "Samples":
            if verbose:
                click.echo("copying trace data")
            v[:] = segy.trace.raw[:].reshape(v.shape)
        elif v.name == dim_names[-1]:
            if verbose:
                click.echo("copying time/depth indices")
            v[:] = np.array(segyio.sample_indexes(segy)).reshape(v.shape)
        elif v.name in dim_names[:-1]:
            if verbose:
                click.echo("copying {}".format(v.name))
            v_traceIDs = _get_variable_traceIDs(v, n_trace_dims, dim_names, traceIDs)
            header_field = _get_header_field(v.name)
            v[:] = segy.attributes(header_field)[v_traceIDs.flatten()[:]].reshape(
                v.shape)
        else:
            if verbose:
                click.echo("copying {}".format(v.name))
            header_field = _get_header_field(v.name)
            v[:] = segy.attributes(header_field)[:].reshape(v.shape)


def _get_variable_traceIDs(variable, n_trace_dims, dim_names, traceIDs):
    """Make a list of trace IDs to copy trace header data from.

       Headers used as dimensions will only copy from traces that should
       contain unique values for them, while other headers will copy from
       every trace.
    """
    vdims = [slice(1)] * n_trace_dims
    v_trace_dims = variable.dimensions
    for d in v_trace_dims:
        d_idx = dim_names.index(d)
        vdims[d_idx] = slice(None)
    v_traceIDs = traceIDs[tuple(vdims)]
    return v_traceIDs


def _get_header_field(name):
    """Get the position of the requested header value in the trace headers."""
    return segyio.tracefield.keys[name]
