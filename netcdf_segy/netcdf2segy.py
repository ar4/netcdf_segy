# -*- coding: utf-8 -*-
import click
import segyio
import numpy as np
from netCDF4 import Dataset

@click.command()
@click.argument('netcdf_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('segy_path', type=click.Path())
def cli(netcdf_path, segy_path):
    netcdf2segy(netcdf_path, segy_path)

def netcdf2segy(netcdf_path, segy_path):
    rootgrp = Dataset(netcdf_path, "r", format="NETCDF4")
    spec = _create_segy_spec()
    with segyio.create(segy_path, spec) as segy:
        pass

    rootgrp.close()

def _create_segy_spec(rootgrp, samples_dim_name):
    spec = segyio.spec()
    spec.iline = 0
    spec.ilines = None
    spec.xline = 0
    spec.xlines = None
    spec.offsets = [1]
    spec.samples = rootgrp[samples_dim_name]
    spec.tracecount = rootgrp[] #TODO
    spec.ext_headers = int('ext_headers' in rootgrp)
    spec.format = None
    spec.sorting = None
    spec.t0 = 0.0
    return spec
