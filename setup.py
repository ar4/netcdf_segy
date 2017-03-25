#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'Click>=6.0',
    'segyio',
    'netCDF4',
    'numpy'
]

test_requirements = [
    'pytest'
]

setup(
    name='netcdf_segy',
    version='0.1.0',
    description="Convert between SEG-Y and NetCDF",
    long_description=readme,
    author="Alan Richardson",
    author_email='arichar@tcd.ie',
    url='https://github.com/ar4/netcdf_segy',
    packages=[
        'netcdf_segy',
    ],
    package_dir={'netcdf_segy':
                 'netcdf_segy'},
    entry_points={
        'console_scripts': [
            'segy2netcdf=netcdf_segy.segy2netcdf:cli'#,
            #'netcdf2segy=netcdf_segy.netcdf2segy:cli'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='netcdf_segy',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
