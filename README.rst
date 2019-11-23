===============================
netcdf_segy
===============================


.. image:: https://img.shields.io/pypi/v/netcdf_segy.svg
        :target: https://pypi.python.org/pypi/netcdf_segy

Convert between SEG-Y and NetCDF

This is currently only a research/demonstration tool. It is not "industrial strength". In particular, it does not run in parallel, so will likely be slow on very large datasets (if it runs at all). Also, only the SEG-Y -> NetCDF direction is implemented.

To install: ``pip install netcdf_segy``

`SegyIO <https://github.com/equinor/segyio>`_ is a dependency.

To convert a SEG-Y file to NetCDF from the command line: ``segy2netcdf <path to input SEG-Y file> <path to output NetCDF file>``. For additional options, look at the help: ``segy2netcdf --help``.

The tool can also be called from a Python script::

    from netcdf_segy.segy2netcdf import segy2netcdf

    segy2netcdf(segy_path, netcdf_path)

I have created a Jupyter Notebook to discuss the advantages of NetCDF compared to SEG-Y, show an example of ``segy2netcdf`` being used, and demonstrate the attractions of loading the resulting NetCDF file with `xarray <http://xarray.pydata.org/>`_: `Alternatives to SEG-Y <https://github.com/ar4/netcdf_segy/blob/master/notebooks/netcdf_segy.ipynb>`_.

One of the "additional options" mentioned above is to use specified headers as dimensions. This allows you to use 'FieldRecord' as a dimension if your data is stored as shot gathers, for example (as in the Notebook). If you don't do this, the NetCDF file will store the data as a 2D array with Time/Depth/SampleNumber and Traces as the dimensions. As ``netcdf_segy`` currently uses `SegyIO <https://github.com/equinor/segyio>`_ to read the SEG-Y file, the header names are those used by that package. For your convenience, here is the list (from ``segyio.TraceField``):

'AliasFilterFrequency', 'AliasFilterSlope', 'CDP', 'CDP_TRACE', 'CDP_X', 'CDP_Y', 'CROSSLINE_3D', 'CoordinateUnits', 'Correlated', 'DataUse', 'DayOfYear', 'DelayRecordingTime', 'ElevationScalar', 'EnergySourcePoint', 'FieldRecord', 'GainType', 'GapSize', 'GeophoneGroupNumberFirstTraceOrigField', 'GeophoneGroupNumberLastTraceOrigField', 'GeophoneGroupNumberRoll1', 'GroupStaticCorrection', 'GroupUpholeTime', 'GroupWaterDepth', 'GroupX', 'GroupY', 'HighCutFrequency', 'HighCutSlope', 'HourOfDay', 'INLINE_3D', 'InstrumentGainConstant', 'InstrumentInitialGain', 'LagTimeA', 'LagTimeB', 'LowCutFrequency', 'LowCutSlope', 'MinuteOfHour', 'MuteTimeEND', 'MuteTimeStart', 'NStackedTraces', 'NSummedTraces', 'NotchFilterFrequency', 'NotchFilterSlope', 'OverTravel', 'ReceiverDatumElevation', 'ReceiverGroupElevation', 'ScalarTraceHeader', 'SecondOfMinute', 'ShotPoint', 'ShotPointScalar', 'SourceDatumElevation', 'SourceDepth', 'SourceEnergyDirectionExponent', 'SourceEnergyDirectionMantissa', 'SourceGroupScalar', 'SourceMeasurementExponent', 'SourceMeasurementMantissa', 'SourceMeasurementUnit', 'SourceStaticCorrection', 'SourceSurfaceElevation', 'SourceType', 'SourceUpholeTime', 'SourceWaterDepth', 'SourceX', 'SourceY', 'SubWeatheringVelocity', 'SweepFrequencyEnd', 'SweepFrequencyStart', 'SweepLength', 'SweepTraceTaperLengthEnd', 'SweepTraceTaperLengthStart', 'SweepType', 'TRACE_SAMPLE_COUNT', 'TRACE_SAMPLE_INTERVAL', 'TRACE_SEQUENCE_FILE', 'TRACE_SEQUENCE_LINE', 'TaperType', 'TimeBaseCode', 'TotalStaticApplied', 'TraceIdentificationCode', 'TraceIdentifier', 'TraceNumber', 'TraceValueMeasurementUnit', 'TraceWeightingFactor', 'TransductionConstantMantissa', 'TransductionConstantPower', 'TransductionUnit', 'UnassignedInt1', 'UnassignedInt2', 'WeatheringVelocity', 'YearDataRecorded',
