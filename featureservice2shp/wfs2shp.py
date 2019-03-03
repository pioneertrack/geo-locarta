#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import codecs
import json
import math
import time
import os
import pycurl
import StringIO
import commands
import urllib2
from urllib import urlencode
import hashlib
import xml.etree.ElementTree as ET

def fetchAllLayers(url):
    
    f = StringIO.StringIO() 
    wfsurl = url+"?"+"request=GetCapabilities"    
    curl=pycurl.Curl()
    curl.setopt(curl.URL, wfsurl)
    curl.setopt(pycurl.WRITEFUNCTION, f.write)    
    curl.setopt(pycurl.SSL_VERIFYPEER, 0)  
    curl.setopt(pycurl.SSL_VERIFYHOST, 0) 
    curl.perform()   
    xmldata= f.getvalue() 
    root = ET.fromstring(xmldata)
    #print root
    for FeatureType in root.iter('{http://www.opengis.net/wfs/2.0}FeatureType'):
        name = FeatureType.find('{http://www.opengis.net/wfs/2.0}Name').text
        box=FeatureType.find('{http://www.opengis.net/ows/1.1}WGS84BoundingBox')
        lc= box.find('{http://www.opengis.net/ows/1.1}LowerCorner').text
        uc= box.find('{http://www.opengis.net/ows/1.1}UpperCorner').text
        xmin=float(lc.split(" ")[0])
        ymin=float(lc.split(" ")[1])
        xmax=float(uc.split(" ")[0])
        ymax=float(uc.split(" ")[1])
        if name.find("PARCEL")>=0 or name.find("PROPERTY")>=0 :
            count = int(countLayer(url,name))
            if count <10000 and count >0:
                #print "small"
                layerUrl=url+'?request=GetFeature&outputformat=json&typename='+name
                #downloadLayer(url,name)
            else:
                bbox =(xmin,ymin,xmax,ymax)
                if name =="LASSI_WS:PROPERTY_ADDRESS_NUMBERS_I":
                    downloadLargeLayer(url,name,count,bbox)
                #downloadLargeLayer(url,name,count,bbox)
                #layerUrl=url+'?request=GetFeature&outputformat=json&typename='+name
                #print layerUrl,count
                
            
def downloadLargeLayer(url,name,count,bbox):
    layerName=name.replace(":","_")

    path="./"+name
    if not os.path.exists(path):
        os.mkdir(path)
    size=2
    print "count="+str(count)
    if count <100000:
        size =8
    elif count>=100000 and count <200000:
        size =16
    elif count>=200000 and count <400000:
        siez = 32
    else:
        size=128
    xmin= bbox[0]
    ymin= bbox[1]
    xmax= bbox[2]
    ymax= bbox[3]
    dx = xmax-xmin
    dy = ymax-ymin
    stepx=dx/size
    stepy=dy/size
    index=0
    for i in range(size):
        for j in range(size):
            filter='<Filter xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml"><Intersects><PropertyName>SHAPE</PropertyName><gml:Envelope srsName="EPSG:4326"><gml:lowerCorner>'+str(xmin+i*stepx)+" "+str(ymin+j*stepy)+'</gml:lowerCorner> 	 <gml:upperCorner>'+str(xmin+(i+1)*stepx)+" "+str(ymin+(j+1)*stepy)+'</gml:upperCorner> </gml:Envelope></Intersects></Filter>'
            layerurl =url+'?request=GetFeature&outputformat=json&typename='+name+"&"+urlencode({"Filter":filter})
            downloadLayer2(layerurl,path+"/"+str(index)+".geojson")
            index=index+1

def countLayer(url,layerName):
    layerUrl=url+'?request=GetFeature&version=1.1.0&resultType=hits&typename='+layerName
    f = StringIO.StringIO()  
    curl=pycurl.Curl()
    curl.setopt(curl.URL, layerUrl)
    curl.setopt(pycurl.WRITEFUNCTION, f.write)    
    curl.setopt(pycurl.SSL_VERIFYPEER, 0)  
    curl.setopt(pycurl.SSL_VERIFYHOST, 0) 
    curl.perform()   
    xmldata= f.getvalue() 
    #print xmldata
    root = ET.fromstring(xmldata)
    count =0
    if root.attrib.has_key("numberOfFeatures"):
        count =  root.attrib['numberOfFeatures']
    return count
    
def downloadLayer2(url,outpath):  
    print url
    if os.path.exists(outpath):
        return
    with open(outpath, 'wb') as f:
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, f)
        c.setopt(pycurl.SSL_VERIFYPEER, 0)  
        c.setopt(pycurl.SSL_VERIFYHOST, 0) 
        c.setopt(pycurl.HTTPHEADER, ['Expect:', '100-continue', 'Connection: Keep-Alive'])
        #c.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_1_0) 
        c.perform()
        c.close()
    
def downloadLayer(url,layerName):  
    layerName=layerName.replace(":","_")

    path=layerName+".geojson"
    print url
    downFile = open(path, 'wb')
    curl=pycurl.Curl()
    curl.setopt(curl.URL, url)
    curl.setopt(pycurl.WRITEDATA, downFile)   
    curl.setopt(pycurl.SSL_VERIFYPEER, 0)  
    curl.setopt(pycurl.SSL_VERIFYHOST, 0) 
    
    curl.setopt(pycurl.HTTPHEADER, ['Connection: keep-alive','Cache-Control: max-age=0','User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36','Upgrade-Insecure-Requests: 1','Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8','Accept-Encoding: gzip, deflate, br','Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'])
    #curl.setopt(pycurl.TIMEOUT, 180)
    curl.perform()  
    downFile.close()

def exportFromFile(rootdir):
    dirs = os.listdir(rootdir)
    result={}
    ids={}
    for i in range(0,len(dirs)):
        path = os.path.join(rootdir,dirs[i])
        if os.path.isfile(path):
            filename= os.path.split(path)[1]
            #print filename
            #if filename.find("LASSI_WS_BUA_PROPERTY_MP_APPROVED_BO") >=0:
            if True:
                print filename
                f=open(path)
                jobj=json.loads(f.read())
                f.close()
                if i==0:
                    result=jobj
                    for feature in jobj["features"]:
                        strFeature=json.dumps(feature)
                        key=hashlib.sha224(strFeature).hexdigest()
                        #key=hashlib.md5(strFeature).hexdigest()
                        #key =feature["properties"]["PV_PFI"]
                        type = feature["geometry"]["type"]
                        value=""
                        if type == "Polyline" or type == "polygon":
                            value=str(feature["geometry"]["coordinates"][0][0][0])
                            
                        elif type == "Point":
                            value=str(feature["geometry"]["coordinates"][0])
                        else:
                            value=""

                        ids[key]=value
                else:
                    for feature in jobj["features"]:
                        #key =feature["properties"]["PV_PFI"]
                        strFeature=json.dumps(feature)
                        key=hashlib.sha224(strFeature).hexdigest()
                        #key=hashlib.md5(strFeature).hexdigest()
                        value=""
                        type = feature["geometry"]["type"]
                        if type == "Polyline" or type == "polygon":
                            value=str(feature["geometry"]["coordinates"][0][0][0])
                        elif type == "Point":
                            value=str(feature["geometry"]["coordinates"][0])
                        if ids.has_key(key) and ids[key] == value:
                            print key
                            continue
                        else:
                            ids[key]=value
                            result["features"].append(feature)
    result["totalFeatures"]=len(result["features"])
    print len(result["features"])
    with open("result.geojson", 'w') as f:
        for chunk in json.JSONEncoder().iterencode(result):
            f.write(chunk)
    f.close()


if __name__ == '__main__':
    ticks = time.time()
    print ticks
    #exportJSON()
    url='https://maps.land.vic.gov.au/geolassi/wfs'
    #url="http://ogc.ntlis.nt.gov.au/gs/ows?service=wfs"
    #fetchAllLayers(url)

    #export()
    #ogr2ogr.main(["","-f", "ESRI Shapefile", "out.shp", "out.geojson"])
    #layerName="survey:SURVEY_MARKS"
    #downloadLayer(url,layerName)
    exportFromFile("/root/crawl/LASSI_WS:PROPERTY_ADDRESS_NUMBERS_I")
    end  = time.time()
    print end
    print (end-ticks)