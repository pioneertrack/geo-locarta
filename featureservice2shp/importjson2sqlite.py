#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import requests
import codecs
import sys
from osgeo import ogr
reload(sys)
sys.setdefaultencoding('utf-8')
def createFields(outLayer,fields):
    for key in fields:
        fieldType = ogr.OFTString
        fieldName = key
        type = fields[key]
        length=0
        if type =="string":
            fieldType = ogr.OFTString
            length=200
        elif type =="float":
            fieldType = ogr.OFTReal
        elif type =="int":
            fieldType = ogr.OFTInteger 
        idField = ogr.FieldDefn(fieldName, fieldType)
        if length>0:
            idField.SetWidth(length)
        outLayer.CreateField(idField)
def importJSONData(jsonFile,outdb,out_lyr_name):
    outDriver = ogr.GetDriverByName("sqlite")
    if not os.path.exists(outdb):
        outDataSource = outDriver.CreateDataSource(outdb)
    else:
        outDataSource = outDriver.Open(outdb,1)
    outLayer = outDataSource.CreateLayer( out_lyr_name, geom_type=ogr.wkbPoint )
    fileds={"SVY_HEIGHT": "float",
                "image_url": "string",
                "SVY_TYPE": "string",
                "SVY_ZON_CODE": "string",
                "SVY_COMMENTS": "string",
                "OBJECTID": "int",
                "SVY_REG_ID": "string",
                "SVY_SURVEY_JN": "string",
                "SVY_MODIFIED_BY": "string",
                "SVY_EASTING": "float",
                "SVY_CREATED_DATE": "int",
                "SVY_RDN_CODE": "string",
                "SVY_CREATED_BY": "string",
                "SVY_MODIFIED_DATE": "int",
                "SVY_NORTHING": "float",
                "SVY_POINT": "string"}
    createFields(outLayer,fileds)
    featureDefn = outLayer.GetLayerDefn()

    with open(jsonFile) as json_data:
        j = json.load(json_data)
        i=1
        for feature in j:
            print feature
            outFeature = ogr.Feature(featureDefn)
            point = ogr.Geometry(ogr.wkbPoint)

            point.AddPoint(feature[u"feature"][u'geometry'][u"x"],feature[u"feature"][u"geometry"][u"y"])
            outFeature.SetGeometry(point)
            for key in fileds:
                outFeature.SetField(key,feature[u"feature"][u"attributes"][key])
            outLayer.CreateFeature(outFeature)
            outFeature=None  
    outDataSource=None   



if __name__ == '__main__':
    
    jsonFile="/Users/gis/Documents/project/featureservice2shp/f_out.json"
    outdb="./SurveyPortal2014.sqlite"
    
    lyrName="Minor Control Points"
    importJSONData(jsonFile,outdb,lyrName)
    
    jsonFile="/Users/gis/Documents/project/featureservice2shp/f_8_out.json"
    outdb="./SurveyPortal2014.sqlite"
    
    lyrName="Road Reference Marks"
    #importJSONData(jsonFile,outdb,lyrName)