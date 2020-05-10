# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 15:44:36 2018

This module is used for processing road segments
by removing duplicates that belong to multiple catchments

@author: cesny
"""
import arcpy

def shapetoDict(path):
    """
    takes shape file of road segments and returns a dictionary with
    values of interest (catchment COMID, min HAND, observed road disruption
    bolean, and location of lowest point)
    """
    return None

def createUniqueTFID(roadShape):
    """
    finds the unique values in target FID
    this function removes duplicates, for example
    if 14 appears twice, then the output list will
    NOT have 14 in it! i.e. removes index completely
    if it is duplicated!
    """
    fc = roadShape
    fields = ['TARGET_FID']
    uniqueVals = set()
    duplicates = set()
    try:
        for row in sorted(arcpy.da.SearchCursor(fc, fields)):
            if row[0] in uniqueVals:
                duplicates.add(row[0])
            uniqueVals.add(row[0])
        for item in duplicates:
            uniqueVals.remove(item)
    except:
        print('Error searching dataset from GIS')    
    return uniqueVals

def cleanRoads(roadShape, uniqueVals):
    """
    takes in a shape file that is a vector feature dataset, and cleans it
    by removing road segments that are not in the basin as well as road
    segments that are present in the dataset due to catchem DEM boundary
    effects
    """
    fc = roadShape
    fields = ['TARGET_FID', 'duplicate']
    with arcpy.da.UpdateCursor(fc, fields) as cursor:
        for row in cursor:
            if row[0] in uniqueVals:
                row[1] = 0
            else:
                row[1] = 1
            cursor.updateRow(row)
    return None


if __name__ == '__main__':
    arcpy.env.workspace = r"C:\Users\cesny\Dropbox\UT\Courses\Fall 2018\GISWR\project\data\proj\proj.gdb"
    arcpy.env.OverwriteOutput = True
    fc = r"C:\Users\cesny\Dropbox\UT\Courses\Fall 2018\GISWR\project\data\proj\proj.gdb\TxDOT_H_R_SJoin20_utm14_Clean"
    uniqVals = createUniqueTFID(fc)
    cleanRoads(fc, uniqVals)
    
