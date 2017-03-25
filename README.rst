===============================
netcdf_segy
===============================


.. image:: https://img.shields.io/pypi/v/netcdf_segy.svg
        :target: https://pypi.python.org/pypi/netcdf_segy

.. image:: https://img.shields.io/travis/ar4/netcdf_segy.svg
        :target: https://travis-ci.org/ar4/netcdf_segy

.. image:: https://pyup.io/repos/github/ar4/netcdf_segy/shield.svg
     :target: https://pyup.io/repos/github/ar4/netcdf_segy/
     :alt: Updates


Convert between SEG-Y and NetCDF

This is currently only a research/demonstration tool. It is not "industrial strength". In particular, it does not run in parallel, so will likely be slow on very large datasets (if it runs at all). Also, only the SEG-Y -> NetCDF direction is implemented.

To install: `pip install netcdf_segy`

To convert a SEG-Y file to NetCDF from the command line: `segy2netcdf <path to input SEG-Y file> <path to output NetCDF file>`. For additional options, look at the help: `segy2netcdf --help`.

The tool can also be called from a Python script:
```from netcdf_segy import segy2netcdf

segy2netcdf(segy_path, netcdf_path)
```
