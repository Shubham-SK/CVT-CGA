from ConversionIO import *
import numpy as np
from tqdm import tqdm
from types import SimpleNamespace

class AbstractDataFormatInit():
    def __init__(self, input_dir, in_contents_name, exp, output_dir, out_contents_name, var_name, long_name, units, out_file_prefix):
        self.Extractor = Extract(input_dir, in_contents_name, exp)
        self.Writer = WriteFile(output_dir, out_contents_name, var_name, long_name, units, out_file_prefix)


class TempHumid(AbstractDataFormatInit):

    def process(self, datasets):
        # new file paths
        content_paths = []

        # create list of file paths
        files, n_files = self.Extractor.get_data_from_path()

        # extract appropriate
        for i in tqdm(range(n_files), desc=f'Processing {self.Writer.var_name}'):
            # ds_var = dataset_var.copy()
            # ds_lat = dataset_lat.copy()
            # ds_lon = dataset_lon.copy()

            dtemp = datasets.copy()

            try:
                file_current = files[i]
                path = os.path.join(self.Extractor.input_dir, file_current)
                # data_hourly = self.Extractor.read_nc4(ds_var, file_current)
                #
                # lats = self.Extractor.read_nc4(ds_lat, file_current)
                # lons = self.Extractor.read_nc4(ds_lon, file_current)
                dres = SimpleNamespace(**self.Extractor.read_nc4(dtemp, file_current))
                data_hourly = dres.data_hourly
                lats = dres.lats
                lons = dres.lons

            except OSError:
                continue

            # find average
            average_data_day = np.nanmean(data_hourly, axis=0)
            isif = average_data_day.shape

            # write out the nc4
            outfile = self.Writer.netcdf(self.Extractor.get_date(file_current), average_data_day, lats, lons, isif)
            content_paths.append(outfile+'\n')

        # write resultant files
        self.Writer.write_file_paths(content_paths)
        print('New Files Logged.')


class Precipitation(AbstractDataFormatInit):

    def process(self, datasets):
        # get date range for files, data files given for multiple parts of day
        date_range = self.Extractor.get_date_range()

        # new file paths
        content_paths = []

        # iterate through date range and create list of file paths
        for date in date_range:
            files, n_files = self.Extractor.get_data_from_path(date=date)
            data_day =  []

            # print(f'Processing Data for {date}...')

            # extract appropriate
            for i in tqdm(range(n_files), desc=f'Processing {self.Writer.var_name} | {date}'):
                # ds_var = dataset_var.copy()
                # ds_lat = dataset_lat.copy()
                # ds_lon = dataset_lon.copy()

                dtemp = datasets.copy()

                try:
                    file_current = files[i]
                    path = os.path.join(self.Extractor.input_dir, file_current)
                    # data_sub = self.Extractor.read_nc4(ds_var, file_current).squeeze()
                    # data_sub = np.transpose(data_sub)
                    #
                    # lats = self.Extractor.read_nc4(ds_lat, file_current)
                    # lons = self.Extractor.read_nc4(ds_lon, file_current)
                    dres = SimpleNamespace(**self.Extractor.read_nc4(dtemp, file_current))
                    data_sub = np.transpose(dres.data_sub)
                    lats = dres.lats
                    lons = dres.lons

                    isif = data_sub.shape

                    data_day.append(data_sub)
                except OSError:
                    # print(f'Error: {e} when processing {file_current}.')
                    continue

            # print('Saving...')

            # calculate average
            data_day = np.array(data_day)
            average_data_day = np.nanmean(data_day, axis=0)

            # write out the nc4
            outfile = self.Writer.netcdf(date, average_data_day, lats, lons, isif)
            content_paths.append(outfile+'\n')

        # write resultant files
        self.Writer.write_file_paths(content_paths)
        print('New Files Logged.')
