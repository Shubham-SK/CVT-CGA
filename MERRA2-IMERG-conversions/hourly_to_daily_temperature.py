from ConversionIO import *
import numpy as np

# path variables
DATA_DIR = '/home/centos/data/covid19/temperature_humidity/hourly'
INSTALL_DIR = '/home/centos/data/covid19/temperature_humidity/daily/Temperature'
HOURLY_TXT = 'new_files.txt'

# setting up objects
extractor = Extract(DATA_DIR, HOURLY_TXT, 'MERRA2_400.tavg1_2d_slv_Nx.%Y%m%d')
writer = WriteFile(INSTALL_DIR, 'daily_T2M', 'daily-2-meter_temperature', 'K', 'daily_MEAN_T_')

# create list of file paths
files, n_files = extractor.get_data_from_path()

# extract appropriate
for i in range(n_files):
    try:
        file_current = files[i]
        path = os.path.join(DATA_DIR, file_current)
        temper_data_hourly = extractor.read_nc4(['T2M'], file_current)

        lats = extractor.read_nc4('lat', file_current)
        lons = extractor.read_nc4('lon', file_current)

    except Exception as e:
        print(f'Error: {e} when processing {file_current}.')
        continue

    # find average
    average_temper_data_day = np.nanmean(temper_data_hourly, axis=0)
    isif = average_temper_data_day.shape

    # write out the nc4
    writer.netcdf(extractor.get_date(file_current), average_temper_data_day, lats, lons, isif)
