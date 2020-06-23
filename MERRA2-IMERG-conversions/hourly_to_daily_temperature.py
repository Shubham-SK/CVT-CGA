from ConversionIO import *

# path variables
DATA_DIR = '/home/centos/data/covid19/temperature_humidity/hourly'
INSTALL_DIR = '/home/centos/data/covid19/temperature_humidity/daily/Temperature'
HOURLY_TXT = 'new_files.txt'

# setting up objects
extractor = Extract(DATA_DIR, HOURLY_TXT)
writer = WriteFile(INSTALL_DIR, 'daily_T2M', 'daily-2-meter_temperature', 'K', 'daily_MEAN_T_')

# create list of file paths
files, n_files = extractor.get_data_from_path()

# extract appropriate
for i in range(n_files):
    try:
        path = os.path.join(DATA_DIR, files[i])
        temper_data_hourly = extractor.read_nc4(path, 'T2M')

        lats = extractor.read_nc4(path, 'lat')
        lons = extractor.read_nc4(path, 'lon')
        isif = temper_data_hourly.shape

    except Exception as e:
        print(f'Error: {e} when processing {files[i]}.')
        continue

    # find average
    temper_data_day = np.nanmean(temper_data_hourly, axis=0)

    # write out the nc4
    writer.netcdf(date, average_temper_data_day, lats, lons, isif)
