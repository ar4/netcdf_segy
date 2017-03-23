# -*- coding: utf-8 -*-
import click
import segyio
import numpy as np
from netCDF4 import Dataset

@click.command()
@click.argument('netcdf', type=click.Path(exists=True, dir_okay=False))
@click.argument('segy', type=click.Path())
def netcdf2segy(netcdf, segy):
    click.echo('hi n2s %s %s' % (netcdf, segy))

