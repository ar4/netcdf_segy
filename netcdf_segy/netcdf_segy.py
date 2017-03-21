# -*- coding: utf-8 -*-
import click
import segyio
from netCDF4 import Dataset

@click.command()
@click.argument('segy', type=click.Path(exists=True, dir_okay=False))
@click.argument('netcdf', type=click.Path())
@click.option('-d0', type=str, help="name of first (trace samples) dimension")
@click.option('-d', type=(str, int), multiple=True, help="dimension name and length")
def segy2netcdf(segy, netcdf, d0, d):

    # set default name for trace samples dimension to 'samples'
    if not d0:
        d0 = 'SampleNumber'
    print(d)

    with segio.open(segy_path) as segy:
        ns = len(segy.samples)
        ntraces = segy.tracecount

        dim_name_len = _make_dim_name_len(d0, ns, d)
        dims_ntraces = _count_traces_in_user_dims(d)

        _check_user_dims(dims_ntraces, ntraces)

        _fill_missing_dims(dims_ntraces, ntraces, dim_name_len)

        rootgrp = Dataset(netcdf, "w", format="NETCDF4")
        dims = _create_dimensions(dim_name_len)
        netcdf = rootgrp.createVariable("Samples","f4",("time",))

        rootgrp.close()


@click.command()
@click.argument('netcdf', type=click.Path(exists=True, dir_okay=False))
@click.argument('segy', type=click.Path())
def netcdf2segy(netcdf, segy):
    click.echo('hi n2s %s %s' % (netcdf, segy))

def _make_dim_name_len(d0, ns, d):
    dim_name_len = [(d0, ns)]
    for dim in d:
        dim_name_len.append(dim)
    return dim_name_len


def _count_traces_in_user_dims(d):
    dims_ntraces = 1
    for dim in d:
        dims_ntraces *= dim[1]
    return dims_ntraces

def _check_user_dims(dims_ntraces, ntraces):
    if dims_ntraces > ntraces:
        raise ValueError('supplied dimensions imply %d traces, but only %d in file' %
                (dims_ntraces, ntraces))
    if ntraces % dims_ntraces != 0:
        raise ValueError('''supplied dimensions imply %d traces, 
        but this does not divide into the %d traces in the file''' %
        (dims_ntraces, ntraces))

def _fill_missing_dims(dims_ntraces, ntraces, dim_name_len):
    if dims_ntraces > ntraces:
        dim_name_len.append(('traces', ntraces / dims_ntraces))

def _create_dimensions(dim_name_len):
    dims = []
    for dim in dim_name_len:
        dims.append(rootgrp.createDimension(dim[0], dim[1]))
    return dims
