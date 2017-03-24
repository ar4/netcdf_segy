# -*- coding: utf-8 -*-
# NOT WORKING!!! CODE IS INCOMPLETE!!!
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
    spec = _create_segy_spec(rootgrp)
    with segyio.create(segy_path, spec) as segy:
        _set_attributes(rootgrp, segy)
        _copy_data(rootgrp, segy)
        pass

    rootgrp.close()

def _create_segy_spec(rootgrp):
    spec = segyio.spec()
    spec.iline = None
    spec.ilines = None
    spec.xline = None
    spec.xlines = None
    spec.offsets = [1]
    samples_dim_name = rootgrp.variables['Samples'].dimensions[-1]
    spec.samples = rootgrp.variables[samples_dim_name][:]
    spec.tracecount = np.prod(rootgrp.variables['Samples'].shape[:-1])
    spec.ext_headers = int('ext_headers' in rootgrp.ncattrs())
    spec.format = 5
    spec.sorting = 0
    spec.t0 = 0.0
    return spec

def _set_attributes(rootgrp, segy):
    segy.text[0] = rootgrp.getncattrs('text')
    if 'ext_headers' in rootgrp.ncattrs():
        segy.text[1] = rootgrp.getncattrs('ext_headers')
    segy.bin = rootgrp.getncattrs('bin')

def _copy_data(rootgrp, segy):
    for name, v in rootgrp.variables.index():
        if name == 'Samples':
            segy.trace.raw[:] = rootgrp.variables[name][:]
        elif name in rootgrp.dimensions.keys():
            pass
        else:
            segy.attributes(eval('segyio.TraceField.%s' % name))[:] = \
                    rootgrp.variables[name][:]
