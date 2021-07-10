# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 19:37:20 2018

This module is for computing the minimum HAND value
for each road segment and writing it to the road network
layer

The module also includes methods for identifying the points
with the minimum HAND value at each road segment


@author: cesny
"""
import arcpy
import pickle


def getMinHAND(pointLayer):
    '''
    -----
    :param pointLayer: a point layer with grid code for lines
    and hand value of each point
    :return minHAND: a dictionary with the minimum HAND value 
    for every polyline
    -----
    '''
    ptfields = ['grid_code', 'RASTERVALU']
    minHAND = dict()
    try:
        for row in arcpy.da.SearchCursor(pointLayer, ptfields):
            if row[1] is not None:  # ignore null values that are outside HAND raster extent
                if row[0] in minHAND: # check if road already considered based on the grid code
                    if row[1] < minHAND[row[0]]:  # check if new is minimum so far
                        minHAND[row[0]] = max(row[1], 0)  # ensure HAND values are above zero
                elif row[0] not in minHAND:
                    minHAND[row[0]] = max(row[1], 0)  # ensure HAND values are above zero
    except:
        print('error reading points')
    return minHAND


def findPointMinHAND(pointLayer):
    '''
    -----
    :param pointLayer: GIS layer of points
    :returns None:
    -----
    updates the GIS point layer by indicating if the point
    is the minimum HAND value or not
    this will be useful for extracting the minimum points into 
    a separate shapefile
    -----
    '''
    ptfields = ['grid_code', 'RASTERVALU', 'minPoint']
    minHAND = dict()
    try:
        for row in arcpy.da.SearchCursor(pointLayer, ptfields):
            if row[1] is not None:  # ignore null values that are outside HAND raster extent
                if row[0] in minHAND: # check if road already considered
                    if row[1] < minHAND[row[0]]:  # check if new is minimum so far
                        minHAND[row[0]] = row[1]
                elif row[0] not in minHAND:
                    minHAND[row[0]] = row[1]
    except:
        print('error reading points')
    with arcpy.da.UpdateCursor(pointLayer, ptfields) as cursor:
        for row in cursor:
            if row[1] != minHAND[row[0]]:  # check if point has the minimum HAND value along its line
                row[2] = 0  # if it doesn't assign zero
            else:
                row[2] = 1  # otherwise assign 1
            cursor.updateRow(row)
    return None


def assignHAND(roadLayer, minHAND):
    '''
    -----
    :param roadLayer: GIS layer of road polylines
    :param minHAND: a dictionary with the minimum HAND value on each road
    :returns None:
    -----
    assigns to the roadLayer the minimum HAND values available in the 
    minHAND dict
    -----
    '''
    rdfields = ['OBJECTID_1', 'HAND']
    with arcpy.da.UpdateCursor(roadLayer, rdfields) as cursor:
        for row in cursor:
            if row[0] not in minHAND:
                print('road with more than one incident: ', row[0])
            else:
                row[1] = minHAND[row[0]]
            cursor.updateRow(row)
    return None


def getRoadMinHANDdict(roadLayer, pointLayer):
    '''
    -----
    :param roadLayer: GIS road layer
    :param pointLayer: GIS layer of points with the HAND values
    :return None:
    -----
    creates a dictionary that has for every road: inundation level, 
    minimum HAND value, whether TXDOT observed an incident of not
    -----
    The resulting dictionary is saved as a pickle file
    -----
    '''
    ptfields = ['grid_code', 'POINT_X', 'POINT_Y']
    rdfields = ['OBJECTID_1', 'HAND', 'inundation', 'CNSTRNT_TYPE_CD']
    rdDict = dict()
    try:
        for row in arcpy.da.SearchCursor(roadLayer, rdfields):
            if row[2] is not None:  # ignore roads that do not have NWM or HAND readings
                rdDict[row[0]] = dict()
                rdDict[row[0]]['HAND'] = row[1]
                rdDict[row[0]]['inundation'] = row[2]
                if row[3] is not None:
                    rdDict[row[0]]['damage'] = 1.0
                else:
                    rdDict[row[0]]['damage'] = 0.0
    except:
        print('error reading roads')
    for row in arcpy.da.SearchCursor(pointLayer, ptfields):
        if row[0] in rdDict:
            rdDict[row[0]]['X'] = row[1]
            rdDict[row[0]]['Y'] = row[2]
    
    pickle.dump( rdDict, open( "rdDict.pckl", "wb" ) )
    return None


def sanityCheck(roadLayer):
    '''
    sanity check going through the road layer
    -----
    :return None:
    -----
    '''
    rdfields = ['OBJECTID_1']
    temp = 0
    for row in arcpy.da.SearchCursor(roadLayer, rdfields):
            val = row[0] - temp
            if val != 1:
                print(row[0])
                print('Error')
            temp = row[0]
    return None


if __name__ == '__main__':
    arcpy.env.workspace = r"C:\Users\cesny\Dropbox\UT\Courses\Fall 2018\GISWR\project\data\proj\proj.gdb"
    arcpy.env.OverwriteOutput = True
    # pointLayer = r"C:\Users\cesny\Dropbox\UT\Courses\Fall 2018\GISWR\project\data\proj\proj.gdb\raster2point_withHAND"
    # roadLayer = r"C:\Users\cesny\Dropbox\UT\Courses\Fall 2018\GISWR\project\data\proj\proj.gdb\TxDOT_H_R_clean_split_gt300_SJoin3_HAND_NWM"
    # minHAND = getMinHAND(pointLayer)
    # assignHAND(roadLayer, minHAND)
    # findPointMinHAND(pointLayer)
    #sanityCheck(roadLayer)
    pointLayer = r"C:\Users\cesny\Dropbox\UT\Courses\Fall 2018\GISWR\project\data\proj\proj.gdb\raster2point_withHAND_minPoints"
    roadLayer = r"C:\Users\cesny\Dropbox\UT\Courses\Fall 2018\GISWR\project\data\proj\proj.gdb\TxDOT_H_R_clean_split_gt300_SJoin3_HAND_NWM"
    getRoadMinHANDdict(roadLayer, pointLayer)