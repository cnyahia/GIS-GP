# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 23:28:39 2018

This module is for extracting NWM data for the
catchments of interest. 

###
This code is based on the following
hydroshare resource by Anthony Castronova
Castronova, A. (2018). Hurricane Harvey NWM 
Subsetting Exercise, HydroShare, 
http://www.hydroshare.org/resource/3db192783bcb4599bab36d43fc3413db
###

@author: cesny
"""
import arcpy
import re
import requests
import xarray
import xml.etree.ElementTree as ET
import numpy as np

def getCOMIDs(Catchs):
    """
    retrieves the CatchIds from GIS
    """
    CatchIds = set()
    fields = ['FEATUREID']
    try:
        for row in sorted(arcpy.da.SearchCursor(Catchs, fields)):
            CatchIds.add(row[0])
    except:
        print('Error reading catchments')
    return list(CatchIds)

if __name__ == '__main__':
    # Note that the streamflow unit is m3s-1
    # get catchments from GIS
    arcpy.env.workspace = r"C:\Users\cesny\Dropbox\UT\Courses\Fall 2018\GISWR\project\data\proj\proj.gdb"
    arcpy.env.OverwriteOutput = True
    gisCatchLayer = r"C:\Users\cesny\Dropbox\UT\Courses\Fall 2018\GISWR\project\data\proj\proj.gdb\Catchment_H_utm14"
    CatchIds = getCOMIDs(gisCatchLayer)
    
    # get NWM data
    thredds_base ='http://thredds.hydroshare.org/thredds'
    date = '20170828'
    configuration = 'short_range'
    output_type = 'channel_rt'
    catalog = '%s/catalog/nwm/harvey/nwm.%s/%s/catalog.xml' % (thredds_base, date, configuration)
    namespaces = {'unidata': 'http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0'}
    r = requests.get(catalog)
    tree = ET.ElementTree(ET.fromstring(r.text))
    root = tree.getroot()
    unidata_datasets = root.findall('unidata:dataset/unidata:dataset', namespaces)
    pattern = "^.*t00z.%s.%s.*$" % (configuration, output_type)
    paths = [] 
    for ds in unidata_datasets:
        name = ds.attrib['name']
        if re.match(pattern, name) is not None:
            paths.append('/'.join([thredds_base, 'dodsC', ds.attrib['urlPath']]))
    channel_ds = xarray.open_mfdataset(paths)
    indices = np.where(channel_ds.feature_id.isin(CatchIds))[0]
    # Subset the complete `channel_rt` dataset using this list of indices.
    # This will reduce the overall size of our dataset from 2,716,897 to number of reaches in dataset
    channel_subset = channel_ds.isel(feature_id=indices)
    data = channel_subset.load()
    data.to_netcdf(path='120200_channel_rt.nc')
    
    '''
    comids = np.random.randint(5522, size=5)

    fig, axes = plt.subplots(nrows=len(comids), figsize=(15,3*len(comids)))
    axid = 0
    for comid in comids:
        channel_subset.streamflow[:, comid].plot(ax=axes[axid])
        axid +=1
    plt.tight_layout()
    '''
    
    