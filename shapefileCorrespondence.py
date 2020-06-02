import h5py
import numpy as np
import rasterio
from rasterio.mask import mask
from geopandas import *
import geopandas as geopd
import osgeo


def readHE5(filename, dataset):
    """
    Returns a (720, 1440) Matrix containing requested data
    ---
    filename: path to he5 file
    dataset: requested data
    options: ColumnAmountNO2, ColumnAmountNO2CloudScreened,
             ColumnAmountNO2Trop, ColumnAmountNO2TropCloudScreened,
             Weight
    ---
    Output Numpy array
    """
    with h5py.File(filename, "r") as f:
        # print(f['HDFEOS']['GRIDS']['ColumnAmountNO2']['Data Fields'].keys())
        ds = f['HDFEOS']['GRIDS']['ColumnAmountNO2']['Data Fields'][dataset]

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


def readShapefile(filename, keyFieldName, dataset):
    """
    Read shapefile and clean contents
    ---
    filename: path to shp file
    keyFieldName: column name (e.g. GID_0, NAME_0, FIPS etc.)
    ---
    Output
    """
    shpdata = geopd.GeoDataFrame.from_file(filename)
    xyValues = [[keyFieldName, 'Max', 'Mean', 'Min']]

    # loop through the shape data
    for i in range(len(shpdata)):
        # load the polygons into variables
        geo = shpdata.geometry[i]
        feature = [geo.__geo_interface__]
        # extract the requested column with using field name
        itemindex = np.argwhere(shpdata.columns == keyFieldName)[0][0]
        # apply raster mask
        out_image, out_transform = mask(dataset, feature, all_touched=True, crop=True, nodata=0)
        if i == 1:
            print(out_image)
            print()
            print(out_transform)

    return shpdata


ds = readHE5('OMI-Aura_L3-OMNO2d_2020m0518_v003-2020m0520t003149.he5', 'ColumnAmountNO2')
print(type(ds))
# print(ds.shape)

shp = readShapefile('USA_admin2/USA_admin2.shp', 'NAME_1', ds)
print(shp)
