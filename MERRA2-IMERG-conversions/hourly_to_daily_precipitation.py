from ConversionIO import *
import numpy as np

# path variables
DATA_DIR = '/home/centos/data/covid19/precipitation/hourly_hdf5'
INSTALL_DIR = '/home/centos/data/covid19/precipitation/daily'
HOURLY_TXT = 'new_files.txt'

# setting up objects
extractor = Extract(DATA_DIR, HOURLY_TXT, '3B-HHR-E.MS.MRG.3IMERG.%Y%m%d')
writer = WriteFile(INSTALL_DIR, 'daily_precipitation', 'daily_precipitation', 'mm/hr', 'daily_precipitation_')

# get date range for files, data files given for multiple parts of day
date_range = extractor.get_date_range()

# iterate through date range and create list of file paths
for date in date_range:
    files, n_files = extractor.get_data_from_path(date=date)
    prec_data_day =  []

    # extract appropriate
    for i in range(n_files):
        try:
            file_current = files[i]
            path = os.path.join(DATA_DIR, file_current)
            prec_data_sub = extractor.read_nc4(['Grid', 'precipitationCal'], file_current, 'Grid').squeeze()
            prec_data_sub = np.transpose(prec_data_sub)

            lats = extractor.read_nc4('lat', file_current)
            lons = extractor.read_nc4('lon', file_current)
            isif = prec_data_sub.shape

            prec_data_day.append(prec_data_sub)
        except Exception as e:
            print(f'Error: {e} when processing {file_current}.')
            continue

    # calculate average
    prec_data_day = np.array(prec_data_day)
    average_prec_data_day = np.nanmean(prec_data_day, axis=0)

    # write out the nc4
    writer.netcdf(date, average_prec_data_day, lats, lons, isif)
