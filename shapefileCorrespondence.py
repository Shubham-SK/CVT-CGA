import h5py
import numpy as np
import rasterio
from rasterio.mask import mask
from geopandas import *
import geopandas as geopd
import gdal
import osgeo
import glob
import os


def read_he5(he5_filename, dataset):
    """
    Returns a (720, 1440) Matrix containing requested data
    ---
    he5_filename: path to he5 file
    dataset: requested data
    options: ColumnAmountNO2, ColumnAmountNO2CloudScreened,
             ColumnAmountNO2Trop, ColumnAmountNO2TropCloudScreened,
             Weight
    ---
    Output Numpy Array
    """
    with h5py.File(he5_filename, "r") as f:
        # print(f['HDFEOS']['GRIDS']['ColumnAmountNO2']['Data Fields'].keys())
        ds = np.array(f['HDFEOS']['GRIDS']['ColumnAmountNO2']['Data Fields'][dataset])

        # ds_no2 = np.array(f['HDFEOS']['GRIDS']['ColumnAmountNO2']['Data Fields']['ColumnAmountNO2'])
        # ds_cs = np.array(f['HDFEOS']['GRIDS']['ColumnAmountNO2']['Data Fields']['ColumnAmountNO2CloudScreened'])
        # ds_not = np.array(f['HDFEOS']['GRIDS']['ColumnAmountNO2']['Data Fields']['ColumnAmountNO2Trop'])
        # ds_tcs = np.array(f['HDFEOS']['GRIDS']['ColumnAmountNO2']['Data Fields']['ColumnAmountNO2TropCloudScreened'])
        # ds_wht = np.array(f['HDFEOS']['GRIDS']['ColumnAmountNO2']['Data Fields']['Weight'])

        # print(f'ColumnAmountNO2: {ds_no2.shape}')
        # print(f'ColumnAmountNO2CloudScreened: {ds_cs.shape}')
        # print(f'ColumnAmountNO2Trop: {ds_not.shape}')
        # print(f'ColumnAmountNO2TropCloudScreened: {ds_tcs.shape}')
        # print(f'Weight: {ds_wht.shape}')

    return ds


def read_shape_file(shape_filename, key_field_name, dataset, temp_tiff):
    """
    Read shapefile and clean contents
    ---
    shape_filename: path to shp file
    key_field_name: column name (e.g. GID_0, NAME_0, FIPS etc.)
    dataset: Numpy Array (720, 1440) containing the grid data
    temp_tiff: Temporary tiff dataset object for Rasterio compatibility
    ---
    Output Standard Array
    """
    # read shape file and create output template
    shp_data = geopd.GeoDataFrame.from_file(shape_filename)
    xy_values = [[key_field_name, 'Max', 'Mean', 'Min']]

    # loop through the shape data
    for i in range(len(shp_data)):

        # load the polygons into variables
        geo = shp_data.geometry[i]
        feature = [geo.__geo_interface__]

        # extract the requested column with using field name
        item_index = np.argwhere(shp_data.columns == key_field_name)[0][0]
        name = shp_data.iloc[i][itemindex]

        # apply raster mask
        out_image, out_transform = mask(temp_tiff, feature, all_touched=True, crop=True, nodata=temp_tiff.nodata)

        # extract values from out_image
        values = out_image.tolist()
        values = values[0]

        # delete errors
        min_data = dataset[~np.isnan(dataset)].min()
        max_data = dataset[~np.isnan(dataset)].max()
        out_data = []

        for i in range(len(values)):
            for j in range(len(values[k])):
                if values[k][j] >= min_data and values[k][j] <= maxdata:
                    out_data.append(values[k][j])

        values = np.array(out_data)
        maxes = values.max()
        means = values.mean()
        mins = values.min()

        # add elements to output array
        xy_values.append([name, maxes, means, mins])

    # remove loop variables
    del feature, shp_data

    return shp_data


def export_to_CSV(shape_filename, he5_directory, key_field_name, dataset, temp_tiff, lat_resolution, lon_resolution, csv_dir):
    """
    Creates CSV file with requested data
    ---
    shape_filename: path to shp file
    key_field_name: column name (e.g. GID_0, NAME_0, FIPS etc.)
    dataset: Numpy Array (720, 1440) containing the grid data
    temp_tiff: Temporary tiff dataset object for Rasteio compatibility
    lat_resolution: 0.25
    lon_resolution: 0.25
    csv_dir: directory to save csv files
    ---
    Returns None
    """
    files = []

    # record all he5 files
    os.chdir(he5_directory)
    for file in glob.glob('*.he5'):
        files.append(file)

    print(files)

    # main loop
    for i in range(len(files)):

        # record path essentials
        save_dir = csv_dir
        original_filename = files[i]
        observation_date = original_filename.split('.he5')[0][19:28]

        # extract data
        data = read_he5(original_filename, dataset)
        print(data)

        # create temporary TIFF file
        spei_ds = gdal.GetDriverByName('Gtiff').Create(temp_tiff, 1440, 720, 1, gdal.GDT_Float32)
        print(spei_ds)

        raster_data = rasterio.open(temp_tiff)
        print(raster_data)



# ds = read_he5('OMI-Aura_L3-OMNO2d_2020m0518_v003-2020m0520t003149.he5', 'ColumnAmountNO2')
# print(type(ds))
# print(ds.shape)

# shp = read_shape_file('USA_admin2/USA_admin2.shp', 'NAME_1', ds)
# print(shp)

export_to_CSV('USA_admin2/USA_admin2.shp', 'he5_files/', 'FIPS', 'ColumnAmountNO2', 'temp.tif', 0, 0, 'test.csv')
