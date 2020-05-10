# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 13:02:55 2018

This module is for converting discharge-stage
data (downloaded from the NFIE HAND inundation mapping
dataset) into rating curves. The stage for a particular
discharge is computed by linear interpolation between 
adjacent NFIE data points. 

@author: cesny
"""
import numpy as np
import arcpy
import pandas as pn

def createRatingCurveDict(csvFile, gisCatchLayer):
    """
    This function creates the rating curve
    dictionary for a hydropop csv file and catchments
    specified in GIS
    WARNING: make sure you set the arc env space in
    the right directory
    csvFile: csv file with hydropop data
    gisCatchLayer: layer in GIS with catchments
    Note that:
    The discharge units is m3s-1
    The stage units is m
    """
    # import data frame
    dat = pn.read_csv(csvFile)
    # import catchments from GIS and initialize dictionary with COMIDs
    fc = gisCatchLayer
    fields = ['FEATUREID']
    COMIDs = dict()
    try:
        for row in sorted(arcpy.da.SearchCursor(fc, fields)):
            COMIDs[row[0]] = dict()
            COMIDs[row[0]]['stage'] = list()
            COMIDs[row[0]]['discharge'] = list()
    except:
        print('Error reading catchments')
    # create dictionary with values from catchments
    for COMID in COMIDs:
        for idx, row in dat.loc[dat['CatchId'] == COMID].iterrows():
            COMIDs[COMID]['stage'].append(row['Stage'])
            COMIDs[COMID]['discharge'].append(row['Discharge (m3s-1)'])    
    return COMIDs


def getStage(COMIDs, catchment, discharge):
    """
    this function generates the stage heights for a specific
    discharge value at a specific catchment
    WARNING: make sure you set the arc env space in
    the right directory
    COMIDs: dictionary from createRatingCurveDict
    catchment: catchment for which stage is desired
    discharge: discharge for which stage is desired
    """
    return np.interp(discharge, COMIDs[catchment]['discharge'], COMIDs[catchment]['stage'])

def writeStage(roadLayer, COMIDs):
    """
    for a list of NWM discharge forecasts in the GIS road newtork layer,
    this function writes the corresponding stage height
    COMIDs is the dictionary for all COMIDs
    """
    rdfields = ['CatchFEATUREID', 'NWM', 'stage']
    with arcpy.da.UpdateCursor(roadLayer, rdfields) as cursor:
        for row in cursor:
            if row[1] is not None:
                row[2] = getStage(COMIDs, row[0], row[1])
            cursor.updateRow(row)
    return None

def writeInundation(roadlayer):
    """
    writes the inundation to the GIS layer
    """
    rdfields = ['HAND', 'stage', 'inundation']
    with arcpy.da.UpdateCursor(roadLayer, rdfields) as cursor:
        for row in cursor:
            if (row[1] is not None) and (row[0] is not None):
                row[2] = max(row[1] - row[0],0)  # inundation always positive
            cursor.updateRow(row)
    return None

if __name__ == '__main__':
    csvFile = r"C:\Users\cesny\Dropbox\UT\Courses\Fall 2018\GISWR\project\data\NFIE-HAND\hydroprop-fulltable-120401.csv"
    arcpy.env.workspace = r"C:\Users\cesny\Dropbox\UT\Courses\Fall 2018\GISWR\project\data\proj\proj.gdb"
    arcpy.env.OverwriteOutput = True
    roadLayer = r"C:\Users\cesny\Dropbox\UT\Courses\Fall 2018\GISWR\project\data\proj\proj.gdb\TxDOT_H_R_clean_split_gt300_SJoin3_HAND_NWM"
    gisCatchLayer = r"C:\Users\cesny\Dropbox\UT\Courses\Fall 2018\GISWR\project\data\proj\proj.gdb\Catchment_H_utm14"
    COMIDs = createRatingCurveDict(csvFile, gisCatchLayer)
    # print(getStage(COMIDs, 1440457, 300))
    writeStage(roadLayer, COMIDs)
    writeInundation(roadLayer)