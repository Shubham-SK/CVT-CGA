from ConversionIO import *
import numpy as np
from tqdm import tqdm

# path variables
DATA_DIR = '/home/centos/data/covid19/precipitation/hourly_hdf5'
INSTALL_DIR = '/home/centos/data/covid19/precipitation/daily'
HOURLY_TXT = 'new_files.txt'
DAILY_TXT = 'new_files.txt'

# setting up objects
extractor = Extract(DATA_DIR, HOURLY_TXT, '3B-HHR-E.MS.MRG.3IMERG.%Y%m%d')
writer = WriteFile(INSTALL_DIR, 'daily_precipitation', 'daily_precipitation', 'mm/hr', 'daily_precipitation_')

# get date range for files, data files given for multiple parts of day
date_range = extractor.get_date_range()

# new file paths
content_paths = []

# iterate through date range and create list of file paths
for date in date_range:
    files, n_files = extractor.get_data_from_path(date=date)
    prec_data_day =  []

    # print(f'Processing Data for {date}...')

    # extract appropriate
    for i in tqdm(range(n_files), desc=f'Processing Precipitation | {date}'):
        try:
            file_current = files[i]
            path = os.path.join(DATA_DIR, file_current)
            prec_data_sub = extractor.read_nc4(['Grid', 'precipitationCal'], file_current).squeeze()
            prec_data_sub = np.transpose(prec_data_sub)

            lats = extractor.read_nc4(['Grid', 'lat'], file_current)
            lons = extractor.read_nc4(['Grid', 'lon'], file_current)
            isif = prec_data_sub.shape

            prec_data_day.append(prec_data_sub)
        except OSError:
            # print(f'Error: {e} when processing {file_current}.')
            continue

    # print('Saving...')

    # calculate average
    prec_data_day = np.array(prec_data_day)
    average_prec_data_day = np.nanmean(prec_data_day, axis=0)

    # write out the nc4
    outfile = writer.netcdf(date, average_prec_data_day, lats, lons, isif)
    content_paths.append(outfile+'\n')

# write resultant files
writer.write_file_paths(DAILY_TXT, content_paths)
print('New Files Logged.')
