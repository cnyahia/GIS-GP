# -*- coding: utf-8 -*-
"""
Created on Mon Dec  3 15:59:19 2018

This module processes NWM data and 
adds the maximum NWM predicition on 08-28-17
to each road in GIS based on its associated
catchment
Note that discharge units is m3s-1
@author: cesny
"""
import arcpy
import xarray
import numpy as np

if __name__ == '__main__':
    # set appropriate GIS directory
    arcpy.env.workspace = r"C:\Users\cesny\Dropbox\UT\Courses\Fall 2018\GISWR\project\data\proj\proj.gdb"
    arcpy.env.OverwriteOutput = True
    roadLayer = r"C:\Users\cesny\Dropbox\UT\Courses\Fall 2018\GISWR\project\data\proj\proj.gdb\TxDOT_H_R_clean_split_gt300_SJoin3_HAND_NWM"

    # get NWM data
    NWM = xarray.open_dataset(r'C:\Users\cesny\Dropbox\UT\Courses\Fall 2018\GISWR\project\data\code\120200_channel_rt.nc')
    NWMCatchIds = set(NWM.feature_id.values) # store the COMIDs for the NWM data
    rdfields = ['CatchFEATUREID', 'NWM']
    with arcpy.da.UpdateCursor(roadLayer, rdfields) as cursor:
        for row in cursor:
            if row[0] not in NWMCatchIds:
                print('road catchment is not in NWM data: ', row[0])
            else:
                index = np.where(NWM.feature_id.isin(row[0]))[0][0]
                row[1] = max(NWM.streamflow[:,index].values)
            cursor.updateRow(row)

