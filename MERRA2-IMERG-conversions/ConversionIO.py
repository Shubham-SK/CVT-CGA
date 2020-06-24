import glob, os, sys
import numpy as np
from scipy.io import netcdf
from netCDF4 import Dataset
from datetime import datetime
import h5py

class Extract:
    def __init__(self, data_path, name):
        self.data_path = data_path
        self.name = name
        self.dir_list = os.path.join(data_path, name)

        with open(self.dir_list, 'r') as f:
            self.files = [i.strip() for i in f.readlines()]

    def get_date_range(self, exp=None):
        for i in self.files():
            date_range = [datetime.strptime(i[len(exp)+2], exp).strftime('%Y%m%d') for i in self.files]
        return date_range

    def get_data_from_path(self, exp=None, date=None):
        if date is None and exp is None:
            return sorted(self.files), len(self.files)
        else:
            files = []
            for i in self.files:
                if date == datetime.strptime(i[len(exp)+2], exp).strftime('%Y%m%d'):
                    files.append(i)
            return sorted(files), len(files)

    def read_nc4(self, dataset, nc4_fname):
        file = os.path.join(self.data_path, nc4_fname)

        # open file and extract read to np array
        h4_data = Dataset(file)
        ds = np.array(h4_data[dataset][:])
        h4_data.close()

        return ds


class WriteFile:
    def __init__(self, output_dir, var_name, long_name, units, file_prefix):
        self.var_name = var_name
        self.long_name = long_name
        self.units = units
        self.output_dir = output_dir
        self.file_prefix = file_prefix

    def netcdf(self, idate, extracted_data, lats, lons, isif):
        # define file path and open using netcdf
        outfile = os.path.join(self.output_dir, self.file_prefix+idate+'.nc4')
        fid = netcdf.netcdf_file(outfile, 'w')

        # creating latitude and longitude dimensions
        fid.createDimension('longitude', isif[1])
        fid.createDimension('latitude', isif[0])

        # creating the longitude variable
        nc_var = fid.createVariable('nlat', 'f4', ('latitude',))
        nc_var[:] = lats
        nc_var.long_name = 'latitude'
        nc_var.standard_name = 'latitude'
        nc_var.units = 'degrees_north'

        # creating the latitude variable
        nc_var = fid.createVariable('nlon', 'f4', ('longitude',))
        nc_var[:] = lons
        nc_var.long_name = 'longitude'
        nc_var.standard_name = 'longitude'
        nc_var.units = 'degrees_east'

        # creating the statistic variable
        nc_var = fid.createVariable(self.var_name, 'f4', ('latitude','longitude',))
        nc_var[:] = extracted_data
        nc_var.long_name = self.long_name
        nc_var.units = self.units

        fid.close()

        print(f'{outfile} successfully written.')
