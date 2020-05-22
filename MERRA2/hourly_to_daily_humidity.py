import glob, os,sys
import numpy as np
from scipy.io import netcdf
from netCDF4 import Dataset
import h5py


def get_files(dir,ext):
    allfiles=[]
    os.chdir(dir)
    for file in glob.glob(ext):
        allfiles.append(file)
    return allfiles, len(allfiles)


def extract_nc3_by_name(filename, dsname):
    nc_data = netcdf.netcdf_file(filename, "r")
    ds = np.array(nc_data.variables[dsname][:])
    nc_data.close()
    return ds


def extract_h5_by_name(filename,dsname):
    h5_data = h5py.File(filename)
    ds = np.array(h5_data[dsname][:])
    h5_data.close()
    return ds


def extract_h4_by_name(filename,dsname):
    h4_data = Dataset(filename)
    ds = np.array(h4_data[dsname][:])
    h4_data.close()
    return ds


if __name__ == '__main__':
    infolder='/datavolume/covid19/temperature_humidity/hourly/'
    output_dir='/datavolume/covid19/temperature_humidity/daily/humidity/'
    all_nc_files, n_all=get_files(infolder,'*.nc4')
    all_nc_files=np.sort(all_nc_files)

    for i in range(n_all):
        the_filename = all_nc_files[i]
        try:
            # print(extract_h4_by_name(the_filename, 'QV2M'))
            theQV2M = np.array(extract_h4_by_name(the_filename, 'QV2M'))
            lats = extract_h4_by_name(the_filename, 'lat')
            lons = extract_h4_by_name(the_filename, 'lon')
        except:
            print(f'skipped {the_filename}')
            continue

        print(f'{the_filename} successfully read.')
        # print(theQV2M, type(the_filename), theQV2M.size)
        dailyQV2M=np.nanmean(theQV2M,axis=0)
        idate = the_filename.split('Nx.')[1][:8]
        isif = dailyQV2M.shape

        # print allRF_mean1,allMR_mean1,allCR_mean1
        # print allRF_std1,allMR_std1,allCR_std1

        outfile = output_dir+ 'daily_MEAN_'+idate+'.nc4'
        # create nc file
        fid = netcdf.netcdf_file(outfile, 'w')
        # create dimension variable, so we can use it in the netcdf
        fid.createDimension('longitude', isif[1])
        fid.createDimension('latitude', isif[0])

        nc_var = fid.createVariable('nlat', 'f4', ('latitude',))
        nc_var[:] = lats
        nc_var.long_name = 'latitude'
        nc_var.standard_name = 'latitude'
        nc_var.units = 'degrees_north'

        nc_var = fid.createVariable('nlon', 'f4', ('longitude',))
        nc_var[:] = lons
        nc_var.long_name = 'longitude'
        nc_var.standard_name = 'longitude'
        nc_var.units = 'degrees_east'

        nc_var = fid.createVariable('daily_QV2M', 'f4', ('latitude','longitude',))
        nc_var[:] = dailyQV2M
        nc_var.long_name = "daily-2-meter_specific_humidity"
        nc_var.units = "kg kg-1"

        fid.close()
        print(f'{outfile} successfully written.')

