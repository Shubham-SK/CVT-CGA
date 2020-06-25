import glob, os, sys
import numpy as np
from scipy.io import netcdf
from netCDF4 import Dataset
from datetime import datetime
import h5py

class Extract:
    def __init__(self, input_dir, in_contents_name, exp):
        self.input_dir = input_dir
        self.in_contents_name = in_contents_name
        self.dir_list = os.path.join(input_dir, in_contents_name)
        self.exp = exp

        # store all files in a class list attribute
        with open(self.dir_list, 'r') as f:
            self.files = [i.strip() for i in f.readlines()]

    def get_date(self, nc4_fname):
        date = datetime.strptime(nc4_fname[:len(self.exp)+2], self.exp).strftime('%Y%m%d')
        return date

    def get_date_range(self):
        date_range = list(set([self.get_date(i) for i in self.files]))
        return sorted(date_range)

    def get_data_from_path(self, date=None):
        # support date specific filter
        if date is None:
            return sorted(self.files), len(self.files)
        else:
            files = []
            for i in self.files:
                if date == self.get_date(i):
                    files.append(i)
            return sorted(files), len(files)

    def read_nc4(self, datasets, nc4_fname):
        file = os.path.join(self.input_dir, nc4_fname)

        # open file and extract read to np array
        h4_data = Dataset(file)

        # create dictionary to store the requested data
        res = {}

        # support depth access
        for ds_name, dataset in datasets.items():
            dataset.reverse()
            ds = h4_data[dataset.pop()]
            while len(dataset) > 0:
                ds = ds[dataset.pop()]
            ds = np.array(ds)
            res.update({ds_name: ds})

        # close dataset
        h4_data.close()

        return res


class WriteFile:
    def __init__(self, output_dir, out_contents_name, var_name, long_name, units, out_file_prefix):
        self.output_dir = output_dir
        self.out_contents_name = out_contents_name
        self.var_name = var_name
        self.long_name = long_name
        self.units = units
        self.out_file_prefix = out_file_prefix

    def netcdf(self, idate, extracted_data, lats, lons, isif):
        # define file path and open using netcdf
        outfile = os.path.join(self.output_dir, self.out_file_prefix+idate+'.nc4')
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

        return outfile

    def write_file_paths(self, content_paths):
        out_file_path = os.path.join(self.output_dir, self.out_contents_name)
        with open(out_file_path, 'a') as f:
            f.writelines(content_paths)
