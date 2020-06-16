import glob, os, sys
import numpy as np
from netCDF4 import Dataset
from osgeo import gdal, gdal_array, osr, ogr
import rasterio
from rasterio.mask import mask
from geopandas import *;
import geopandas as geopd


def get_files(dir, ext):
    allfiles = []
    os.chdir(dir)
    for file in glob.glob(ext):
        allfiles.append(file)
    os.chdir('/home/skumar/CVT-CGA')
    return allfiles, len(allfiles)


def extract_h4_by_name(filename, dsname):
    h4_data = Dataset(filename)
    #    print(h4_data)
    ds = np.array(h4_data[dsname][:])
    h4_data.close()
    return ds


"""
search all the vectors, return the statistical 2D array
"""


def readShapefileFrom2DNCFile(shpdir, datas, xReSolution, yReSolution, ncData, keyFieldName):
    shpdata = geopd.GeoDataFrame.from_file(shpdir)
    # get the location of factors
    xyValues = [[keyFieldName, 'Max', 'Mean', 'Min']]

    for i in range(0, len(shpdata)):
        # get features of vector data
        geo = shpdata.geometry[i]
        feature = [geo.__geo_interface__]

        itemindex = np.argwhere(shpdata.columns == keyFieldName)[0][0]
        name = shpdata.iloc[i][itemindex]
        #        print(len(shpdata.columns),str(shpdata.columns[itemindex]),name,itemindex)
        # cut the .nc4 file through features, rasterio.mask.mask
        out_image, out_transform = mask(datas, feature, all_touched=True, crop=True, nodata=datas.nodata)
        # get overlap area of features
        #        out_image, out_transform = mask(datas, geometry, all_touched=True, crop=True, nodata=datas.nodata)
        values = out_image.tolist()
        values = values[0]

        # delete errors
        mindata = ncData[~np.isnan(ncData)].min()
        maxdata = ncData[~np.isnan(ncData)].max()
        out_data = []
        #        print(values)
        for k in range(len(values)):
            for j in range(len(values[k])):
                if values[k][j] >= mindata and values[k][j] <= maxdata:
                    out_data.append(values[k][j])
        #        values=np.array(values)
        #        maxs=np.max(values)
        #        means=np.mean(values)
        #        mins=np.min(values)
        values = np.array(out_data)
        maxs = values.max()
        means = values.mean()
        mins = values.min()

        xyValues.append([name, maxs, means, mins])

    del feature, shpdata

    return xyValues


"""
Calculate the max, min and mean of the raster(image) data according to the polygon, and save to .csv file
inuputShapefile:path of shapefile
inputRasterDir：path of daily environmental factor data, with .nc4 format
(lonResolution,latResolution)：resolution of input environmental factor data
attributeField：name of the input environmental factor, e.g. daily_QV2M
nLon：longititude of environmental factor data
nLat：latitude of environmental factor data
keyField：attribute of Polygon data (shapefile)
dataTypes：used for the names of output results
saveCSVDir：saving path
Dimesion：dimension of input environmental factor data
tempTif：path of temp data
@author: LW, QL
"""


def exportStatisticToCSV(inuputShapefile, inputRasterDir, lonResolution, latResolution, attributeField, nLon, nLat,
                         keyField, dataTypes, saveCSVDir, Dimesion, tempTif):
    all_nc_files, n_files = get_files(inputRasterDir, '*.nc4')
    all_nc_files = np.sort(all_nc_files)
    for i in range(n_files):
        savedir = saveCSVDir
        the_filename = all_nc_files[i]
        date = the_filename.split('.nc4')[0][-8:]
        filename = inputRasterDir + the_filename
        data = extract_h4_by_name(filename, attributeField)
        if Dimesion == '3D':
            data = np.squeeze(data)
        #        data=np.array(data)
        #        data=dat.transpose((1,0))
        lats = extract_h4_by_name(filename, nLat)
        lons = extract_h4_by_name(filename, nLon)
        x_min = lons.min()
        x_max = lons.max()
        y_min = lats.min()
        y_max = lats.max()

        N_Lat = len(lats)
        N_Lon = len(lons)

        spei_ds = gdal.GetDriverByName('Gtiff').Create(tempTif, N_Lon, N_Lat, 1, gdal.GDT_Float32)
        # 3.4 set the range of image visualization
        geotransform = (x_min, lonResolution, 0, y_min, 0, latResolution)
        spei_ds.SetGeoTransform(geotransform)

        # coordinates information
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        spei_ds.SetProjection(srs.ExportToWkt())

        # 3.6 output data
        spei_ds.GetRasterBand(1).WriteArray(data)  #
        spei_ds.FlushCache()  #
        spei_ds = None  #

        rasterdata = rasterio.open(tempTif)
        #        Transform = rasterdata._transform

        # search all the vectors, retuen 2D array and save to .csv file
        csvfile = []
        csvfile = readShapefileFrom2DNCFile(inuputShapefile, rasterdata, lonResolution, latResolution, data, keyField)

        csvfile = np.array(csvfile)
        savedir = savedir + date + '_' + dataTypes + '.csv'
        print(' CSVFile is saving  ', savedir)
        np.savetxt(savedir, csvfile, delimiter=',', fmt='%s')

        del rasterdata


if __name__ == "__main__":
    # data paths
    input_precipitation = r'/home/centos/data/covid19/precipitation/daily/'
    input_humidity = r'/home/centos/data/covid19/temperature_humidity/daily/humidity/'
    input_temperature = r'/home/centos/data/covid19/temperature_humidity/daily/Temperature/'

    admin1_USA = r'shapefiles/USA_admin1/USA_admin1.shp'
    admin2_USA = r'shapefiles/USA_admin2/USA_admin2.shp'
    global_basemap = r'shapefiles/global_basemap/global_basemap.shp'
    admin1_AUS = r'shapefiles/AUS_admin1/AUS_admin1.shp'
    admin1_AUT = r'shapefiles/AUT_admin1/AUT_admin1.shp'
    admin1_BRA = r'shapefiles/BRA_admin1/BRA_admin1.shp'
    admin1_CAN = r'shapefiles/CAN_admin1/CAN_admin1.shp'
    admin1_HRV = r'shapefiles/HRV_admin1/HRV_admin1.shp'
    admin1_DEU = r'shapefiles/DEU_admin1/DEU_admin1.shp'
    admin1_HUN = r'shapefiles/HUN_admin1/HUN_admin1.shp'
    admin1_India = r'shapefiles/India_admin1/India_admin1.shp'
    admin1_ITA = r'shapefiles/ITA_admin1/ITA_admin1.shp'
    admin1_Japan = r'shapefiles/Japan_admin1/Japan_admin1.shp'
    admin1_RUS = r'shapefiles/RUS_admin1/RUS_admin1.shp'
    admin1_SWE = r'shapefiles/SWE_admin1/SWE_admin1.shp'
    admin1_ZAF = r'shapefiles/ZAF_admin1/ZAF_admin1.shp'

    shapefile_list = [[admin1_USA, 'USA_admin1', 'HASC_1'],
                      [admin2_USA, 'USA_admin2', 'HASC_2'],
                      [global_basemap, 'global_basemap', 'iso3'],
                      [admin1_AUS,'AUS_admin1', 'HASC_1'],
                      [admin1_AUT, 'AUT_admin1', 'HASC_1'],
                      [admin1_BRA, 'BRA_admin1', 'HASC_1'],
                      [admin1_CAN, 'CAN_admin1', 'HASC_1'],
                      [admin1_HRV, 'HRV_admin1', 'HASC_1'],
                      [admin1_DEU, 'DEU_admin1', 'HASC_1'],
                      [admin1_HUN, 'HUN_admin1', 'HASC_1'],
                      [admin1_India, 'India_admin1', 'HASC_1'],
                      [admin1_ITA, 'ITA_admin1', 'HASC_1'],
                      [admin1_Japan, 'Japan_admin1', 'HASC_1'],
                      [admin1_RUS, 'RUS_admin1', 'HASC_1'],
                      [admin1_SWE, 'SWE_admin1', 'HASC_1'],
                      [admin1_ZAF, 'ZAF_admin1', 'HASC_1']]

    data_types = [[input_humidity, 'Humidity', 'daily_QV2M', (0.625, 0.5)],
                 [input_precipitation, 'Precipitation', 'daily_precipitation', (0.1, 0.1)],
                 [input_temperature, 'Temper_T2MMEAN', 'daily_T2M', (0.625, 0.5)]]

    # admin1_worldwide_top50_EU = r'F:\GMU-COVID-19\basemap_shp\basemap\admin1_worldwide(conti)\admin1_worldwide_top50_EU.shp'
    # admin0_worldwide = r'F:\GMU-COVID-19\basemap_shp\basemap\admin0_worldwide\admin0_worldwide.shp'

    # savedirs = r'RESULT_CSVS/'
    # tempDir = r'TESTS/test_nc4s/temp.tif'
    #
    # # start calculation, save to CSV
    # dataType='Humidity'
    # exportStatisticToCSV(admin1_ZFA, inputRHRasterDir, 0.625, 0.5, 'daily_QV2M', 'nlon', 'nlat', 'HASC_1', dataType, r'RESULT_CSVS/', '2D', tempDir)
    #
    # dataType='Precipitation'
    # exportStatisticToCSV(admin1_ZFA, inputPrecipRasterDir, 0.1, 0.1, 'daily_precipitation', 'nlon', 'nlat', 'HASC_1', dataType, r'RESULT_CSVS/', '2D', tempDir)
    #
    # dataType = 'Temper_T2MMEAN'
    # exportStatisticToCSV(admin1_ZFA, inputTempRasterDir, 0.625, 0.5, 'daily_T2M', 'nlon', 'nlat', 'HASC_1', dataType, r'RESULT_CSVS/', '2D', tempDir)

    temp_dir = r'/home/skumar/CVT-CGA/TESTS/test_nc4s/temp.tif'

    for shp in shapefile_list:
        path_shp, name_shp, attribute = shp
        for dt in data_types:
            path_dt, name_dt, ds_var_name, resolution = dt
            save_dir = f'/home/skumar/CVT-CGA/RESULT_CSVS/{name_shp}/{name_dt}/'
            exportStatisticToCSV(path_shp, path_dt, resolution[0], resolution[1], ds_var_name, 'nlon', 'nlat', attribute, name_dt, save_dir, '2D', temp_dir)
            print(f'\n Finished {name_dt} for {name_shp}. \n')
        print(f'\n Finished {name_shp} \n')
    print('Finished')
