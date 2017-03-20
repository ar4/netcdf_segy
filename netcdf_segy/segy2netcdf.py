"""Make a NetCDF file from a SEG-Y
"""

def segy2netcdf(segy_path, netcdf_path, dimensions):
    import re
    import segyio

    print('segy', segy_path)
    print('netcdf', netcdf_path)
    print('num d', len(dimensions))
    r = re.compile(r'(\w+),(\d+)')
    for i,d in enumerate(dimensions):
        m = r.match(d)
        dimensions[i] = {'name': m.group(1), 'len': m.group(2)}
    print(dimensions)

    with segio.open(segy_path) as segy:



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('segy', help="path to input SEG-Y file")
    parser.add_argument('netcdf', help="path to output NetCDF file")
    parser.add_argument('-d', required=True, nargs='+',
        help="dimension name,length")
    args = parser.parse_args()
    segy2netcdf(args.segy, args.netcdf, args.d)
