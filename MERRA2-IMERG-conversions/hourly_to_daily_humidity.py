from ConversionIO import *

# path variables
DATA_DIR = '/home/centos/data/covid19/temperature_humidity/hourly'
INSTALL_DIR = '/home/centos/data/covid19/temperature_humidity/daily/humidity'
HOURLY_TXT = 'new_files.txt'

# setting up objects
extractor = Extract(DATA_DIR, HOURLY_TXT)
writer = WriteFile(INSTALL_DIR, 'daily_QV2M', 'daily-2-meter_specific_humidity', 'kg kg-1', 'daily_MEAN_')

# create list of file paths
files, n_files = extractor.get_data_from_path()

# extract appropriate
for i in range(n_files):
    try:
        path = os.path.join(DATA_DIR, files[i])
        humidity_data_hourly = extractor.read_nc4('QV2M', files[i])

        lats = extractor.read_nc4('lat', files[i])
        lons = extractor.read_nc4('lon', files[i])
        isif = humidity_data_hourly.shape

    except Exception as e:
        print(f'Error: {e} when processing {files[i]}.')
        continue

    # find average
    humidity_data_day = np.nanmean(humidity_data_hourly, axis=0)

    # write out the nc4
    writer.netcdf(date, average_humidity_data_day, lats, lons, isif)
