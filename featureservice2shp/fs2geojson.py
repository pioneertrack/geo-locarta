#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import codecs
import json
import ogr
import math
import urllib2
import time
import os
import datetime
import multiprocessing
import commands
import pycurl
import StringIO
import re
import random
import hashlib
from urllib import urlencode
import xml.etree.ElementTree as ET
from mapbox import Uploader
from bs4 import BeautifulSoup
import getpass, poplib
import email
from email import parser
import logging  
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from crawlMonitor import MonitorClient
from multiprocessing import Pool
import victoria
import uuid
import os
import requests
from osgeo import ogr
from osgeo import osr
def deleteAllOutJson(path):
    for root, dirs, files in os.walk(path):
        for name in files:
            if(name.endswith("_out.json")):
                os.remove(os.path.join(root, name))
def deleteAllMBtiles(path):
    for root, dirs, files in os.walk(path):
        for name in files:
            if(name.endswith(".mbtiles")):
                print os.path.join(root, name)
                os.remove(os.path.join(root, name))
def isKeep(fileName):

    keeps=["NT_scdb.geojson","NT_dcdb.geojson","VIC_scdb.geojson","SA_scdb.geojson","QLD_scdb.geojson","VIC_dcdb.geojson","QLD_dcdb.geojson"]
    if fileName in keeps:
        return True
    else:
        return False
def deleteVicScdbFiles(path):
    for root, dirs, files in os.walk(path):
        for name in files:
            fp=os.path.join(root, name)
            if(name.endswith(".json") and "files/" in fp):
                print fp
                os.remove(fp)
def deleteGeoJson(path):
    for root, dirs, files in os.walk(path):
        for name in files:
            fp=os.path.join(root, name)
            if(name.endswith(".geojson") ):
                if isKeep(name):
                    print fp+"  keep"
                else:
                    print fp
                    os.remove(fp)
def clear(path):
    deleteAllOutJson(path)
    deleteGeoJson(path)
    deleteVicScdbFiles(path)
    deleteAllMBtiles(path)
def genProxys():
    myRequest="https://panel.proxy-hub.com/index.php/Client/api/26eef06b5ada756d994d85878c46bc9c94a5d492d54f38a76227bedf975b8631"
    f = StringIO.StringIO() 
    curl=pycurl.Curl()
    curl.setopt(curl.URL, myRequest)
    curl.setopt(pycurl.WRITEFUNCTION, f.write)    
    curl.perform()   
    curl.close()
    myJSON= f.getvalue()   
    jobj=json.loads(myJSON)
    strProxy= jobj[0][u"API Key"]
    index=strProxy.find(":PASSWORD")
    strProxy = strProxy[index+9:-1]
    strProxy=strProxy.strip()
    return strProxy.split('\r\n')

def upload(ufile,mapid,access_token):

    service = Uploader(access_token=access_token)
    
    with open(ufile, 'rb') as src:
        upload_resp = service.upload(src, mapid)
        print upload_resp.status_code
    
def requireIds(url,proxyIp):
    myRequest=url+"/query?where=1%3D1&returnIdsOnly=true&f=json"
    f = StringIO.StringIO() 
    curl=pycurl.Curl()
    curl.setopt(curl.URL, myRequest)
    curl.setopt(pycurl.WRITEFUNCTION, f.write)    
    if myRequest.find("https://")>=0:
        curl.setopt(pycurl.SSL_VERIFYPEER, 0)  
        curl.setopt(pycurl.SSL_VERIFYHOST, 0) 
    curl.perform()   
    curl.close()
    myJSON= f.getvalue()   
    jobj=json.loads(myJSON)
    return jobj["objectIds"]
def makeUrl(url,ids,type,isWGS84):
    sr="3857"
    if isWGS84:
        sr="4326"
    strids = ','.join(map(str, ids))
    myRequest=url+"/query?returnGeometry=true&returnIdsOnly=false&outSR="+sr+"&outFields=*&f="+type+"&objectIds="+strids
    return myRequest
def makeUrls(url,oids,jsonpath,persize,isWGS84):
    size=len(oids)     
    urls=[]
    max=int(math.ceil(size/ persize)) +1
    for i in range(max):
        of=jsonpath+"/"+str(i)+"_out.json"
        ids = []
        if (i + 1) * persize < size:
            ids = oids[i * persize:(i * persize) + persize]
        else:
            ids = oids[i * persize:size]
        if(len(ids)>0):
            singleUrl = makeUrl(url,ids,"json",isWGS84)
            urls.append([singleUrl,of])
    return urls

def saveResult(response,of):
        fwobj = codecs.open(of, "w", "utf-8")
        fwobj.write(json.dumps(response))
        fwobj.close()
def fetchData2(ourl,proxyIp,isWFS=False,logger=None):
    time.sleep(0.1)
    try:
        logger.info(ourl)
        pproxys =proxyIp.split(":")
        pproxyurl='http://'+pproxys[2]+":"+pproxys[3]+"@"+pproxys[0]+":"+pproxys[1]
    #print pproxyurl
        proxies = {
            'http': pproxyurl,
        }
        s = requests.Session()
        s.proxies = proxies
        response = s.get(ourl)
        if not response.status_code // 100 == 2:
            logger.error("Error: Unexpected response {}".format(response))
            return None
        myJSON = response.content 
        jobj=json.loads(myJSON)
        if isWFS:
            if jobj.has_key("features"):
                return jobj
            else:
                return None 
        else:
            if len(jobj["features"])>0:
                return jobj
            else:
                return None 
        
    except requests.exceptions.RequestException as e:
        logger.error("Error: {}".format(e))
        return None

def fetchData(ourl,proxyIp,isWFS=False,logger=None):
    time.sleep(0.1)
    try:
        logger.info(ourl)
        f = StringIO.StringIO() 
        curl=pycurl.Curl()
        curl.setopt(curl.URL, ourl)
        curl.setopt(pycurl.WRITEFUNCTION, f.write)    
        if ourl.find("https://")>=0:
            curl.setopt(pycurl.SSL_VERIFYPEER, 0)  
            curl.setopt(pycurl.SSL_VERIFYHOST, 0) 
        if not proxyIp =="" :
            pproxys =proxyIp.split(":")
            #print pproxys
            #curl.setopt(pycurl.PROXY, pproxys[0])
            #curl.setopt(pycurl.PROXYPORT, int(pproxys[1]))
            ip='http://'+pproxys[0]+":"+pproxys[1]
            curl.setopt(pycurl.PROXY, ip)
            usrpwd=pproxys[2]+":"+pproxys[3]
            
            curl.setopt(pycurl.PROXYUSERPWD, usrpwd)
        if not isWFS:
            curl.setopt(pycurl.TIMEOUT, 90) 
        else:
            curl.setopt(pycurl.TIMEOUT, 240) 
        curl.perform()   
        curl.close()
        myJSON= f.getvalue()   
        jobj=json.loads(myJSON)
        if isWFS:
            if jobj.has_key("features"):
                return jobj
            else:
                return None 
        else:
            if isinstance(jobj,dict) and len(jobj["features"])>0:
                return jobj
            else:
                return None      
    except pycurl.error as e:
        return None
    except ValueError:
        return None
    except :
        return None    
def exportJSON(url,dirpath,name,proxys,presize=1000,includes=None,access_token="",isWGS84=False,taskItemId=None,mc=None,logger=None):

    jsonpath=dirpath+"/"+name
    os.mkdir(jsonpath)

    oids= requireIds(url,proxys[0])
    mc.updateTaskItemStatus(taskItemId,"downloading",None,str(len(oids)),"")
    #print proxys
    urls=makeUrls(url,oids,jsonpath,presize,isWGS84)
    errors=[]
    conut=0
    retry=0
    isFailed=False
    while True:
        for rurl in urls: 
            l=len(proxys)
            index =random.randint(0, l-1)
            proxy = proxys[index]
           
            res= fetchData(rurl[0],proxy,False,logger)
            if res==None:
                logger.error(rurl[0])
                errors.append(rurl)
                #proxys.remove(proxy)
            else:
                conut=conut+len(res["features"])
                mc.updateTaskItemStatus(taskItemId,"downloading",str(conut),None,"")
                saveResult(res,rurl[1])
        if len(errors) >0:
            retry=retry+1
            if retry>10:
                isFailed=True
                break
            urls=errors
            errors = []
            logger.error("sleep")
            #time.sleep(60*20) #wait 5 min   
            time.sleep(60*10)
        else:
            print "break"
            break
    if isFailed:
        mc.updateTaskItemStatus(taskItemId,"failed",None,None,"")
    else:
        exportFromFile(jsonpath,name,includes,access_token,isWGS84,taskItemId,mc)
        mc.updateTaskItemStatus(taskItemId,"completed",None,None,"")

def exportFromFile(rootdir,name,includes,access_token,isWGS84=False,taskItemId=None,mc=None):
    dirs = os.listdir(rootdir)
    srs= 'EPSG:3857'
    if isWGS84:
       srs= 'EPSG:4326'
    for i in range(0,len(dirs)):
        path = os.path.join(rootdir,dirs[i])
        if os.path.isfile(path):
            filename= os.path.split(path)[1]
                #print filename
            if filename.find("out.json") >0:
                cmd = 'ogr2ogr -t_srs EPSG:3857 -s_srs '+srs+' -f  "sqlite" "'+rootdir+'/'+name+'.sqlite" '+path+' -append' 
                print cmd 
                commands.getstatusoutput(cmd)
    addUUIDFieldForSqlite(rootdir+'/'+name+'.sqlite')
    cmd = 'ogr2ogr -f "geojson" "'+rootdir+'/'+name+'.geojson" "'+rootdir+'/'+name+'.sqlite" '
    commands.getstatusoutput(cmd)
    mc.updateTaskItemStatus(taskItemId,"export to geojson",None,None,cmd)
    
    if includes is None:
        tippecanoeCmd='tippecanoe -z16  -o '+rootdir+'/'+name+'.mbtiles -ap -as     -ad  -s EPSG:3857  -f '+rootdir+'/'+name+'.geojson '
    else:
        tippecanoeCmd='tippecanoe -z16  -o '+rootdir+'/'+name+'.mbtiles -ap -as   '+ includes+'   -ad  -s EPSG:3857   -f '+rootdir+'/'+name+'.geojson '
    print  tippecanoeCmd
    mc.updateTaskItemStatus(taskItemId,"create mbtiles",None,None,tippecanoeCmd)
    commands.getstatusoutput(tippecanoeCmd)
    mc.updateTaskItemStatus(taskItemId,"uploading to mapbox",None,None,"")
    upload(rootdir+'/'+name+'.mbtiles',name,access_token)
    fileSize=os.path.getsize(rootdir+'/'+name+'.mbtiles')
    print "--------"+str(fileSize)
    mc.updateTaskItemStatus(taskItemId,"uploaded to mapbox",None,None,"",str(fileSize))
def downloadLayer(url,opath,layerName,proxyIp=None,logger=None):  
    layerUrl=url+'?request=GetFeature&outputformat=json&typename='+layerName
    logger.info(layerUrl)
    #layerUrl=url+'?request=GetFeature&outputformat=GML&typename='+layerName
    layerName=layerName.replace(":","_")
    path=opath+"/"+layerName+".geojson"
    downFile = open(path, 'wb')
    
    print layerUrl
    curl=pycurl.Curl()
    curl.setopt(curl.URL, layerUrl)
    curl.setopt(pycurl.WRITEDATA, downFile)    
    curl.setopt(pycurl.SSL_VERIFYPEER, 0)  
    curl.setopt(pycurl.SSL_VERIFYHOST, 0) 
    #if proxyIp is not None:
    #    pproxys =proxyIp.split(":")
        #curl.setopt(pycurl.PROXY, pproxys[0])
        #curl.setopt(pycurl.PROXYPORT, int(pproxys[1]))
    #curl.setopt(pycurl.TIMEOUT, 180)
    curl.perform()   
    curl.close() 
    downFile.close()
    addUUIDField(downFile)
def fetchAllLayers(url,layers,outLayerNames,outpath,proxys,taskItemId,mc,taskId,stateName,dbName,isNeedClip,logger):
    
    f = StringIO.StringIO() 
    wfsurl = url+'request=GetCapabilities'
    logger.info(wfsurl)
    rtn =0
    l=len(proxys)
    index =random.randint(0, l-1)
    proxy = proxys[index]

    try:
        curl=pycurl.Curl()
        curl.setopt(curl.URL, wfsurl)
        curl.setopt(pycurl.WRITEFUNCTION, f.write)    
        pproxys =proxy.split(":")
        ip='http://'+pproxys[0]+":"+pproxys[1]
        curl.setopt(pycurl.PROXY, ip)
        usrpwd=pproxys[2]+":"+pproxys[3]
        curl.setopt(pycurl.PROXYUSERPWD, usrpwd)

        curl.perform()   
        xmldata= f.getvalue() 
        
        root = ET.fromstring(xmldata)
        for FeatureType in root.iter('{http://www.opengis.net/wfs/2.0}FeatureType'):
            name = FeatureType.find('{http://www.opengis.net/wfs/2.0}Name').text
            box=FeatureType.find('{http://www.opengis.net/ows/1.1}WGS84BoundingBox')
            lc= box.find('{http://www.opengis.net/ows/1.1}LowerCorner').text
            uc= box.find('{http://www.opengis.net/ows/1.1}UpperCorner').text
            xmin=float(lc.split(" ")[0])
            ymin=float(lc.split(" ")[1])
            xmax=float(uc.split(" ")[0])
            ymax=float(uc.split(" ")[1])
            if name not in layers:
                continue
            idx = layers.index(name)
            if idx>=0 :
                oLayer = outLayerNames[idx]
                taskItemId2=mc.createTaskItem(taskId,stateName,dbName,oLayer+".mbtiles","0","downloading","0","0","script","startDownload")
                count = int(countLayer(url,name))
                if count <1000 and count >0:
                #print "small"
                    layerUrl=url+'request=GetFeature&srsName=EPSG:3857&outputformat=json&typename='+name
                    logger.info(layerUrl)
                    layerName=oLayer
                    lpath=outpath+"/"+layerName
                    os.mkdir(lpath)
                    
                    jsonName=layerName+".geojson"
                    mc.updateTaskItemStatus(taskItemId,"downloading file",None,None,layerName)
                    downloadLayer2(layerUrl,lpath+"/"+jsonName,logger)
                    mbtilesName=layerName+".mbtiles"
                    mkMbtiles(lpath+"/"+mbtilesName,lpath+"/"+jsonName,layerName,layerName,taskItemId2,mc,isNeedClip,logger)
                else:
                    bbox =(xmin,ymin,xmax,ymax)
                    downloadLargeLayer(url,proxys,name,oLayer,count,bbox,outpath,taskItemId2,mc,isNeedClip,logger)
        rtn =1
    except  ValueError as e:
        logger.error("error ~~:"+e)
        mc.updateTaskItemStatus(taskItemId,"GetCapabilities failed",None,None,wfsurl)
    finally:
        return rtn
        
def mergeWFSFromFile(rootdir,outfile,logger):
    print rootdir
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
    with open(rootdir+"/"+outfile, 'w') as f:
        for chunk in json.JSONEncoder().iterencode(result):
            f.write(chunk)
    f.close()
    logger.info(rootdir+"/"+outfile+" merged")
def exportNT(path,proxys,access_token,taskId,mc):
    ntPath=path+"/NT_dcdb"
    os.mkdir(ntPath)
    logger = logging.getLogger('exportNT') 
    fh = logging.FileHandler(ntPath+'/exportNT.log')  
    fh.setLevel(logging.INFO)  
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    logger.addHandler(fh)  

    url="http://ogc.ntlis.nt.gov.au/gs/ntlis/wfs?"
    taskItemId=mc.createTaskItem(taskId,"NT","DCDB","NT","0","downloading","0","0","script","startDownload")
   
    layerNames=["ntlis:CADASTRE"]
    #layerNames=["ntlis:CADASTRE_PROPOSED","ntlis:CADASTRE_PROPOSED_SATOVERLAY","ntlis:CADASTRE_SATOVERLAY","ntlis:CADASTRE","ntlis:CADASTRE_OVERLAY_GREY"]
    #layerNames=["ntlis:CADASTRE_PROPOSED"]
    #outLayerNames=["ntlis_CADASTRE_PROPOSED","ntlis_CADASTRE_PROPOSED_SATOVERLAY","ntlis_CADASTRE_SATOVERLAY","ntlis_CADASTRE","ntlis_CADASTRE_OVERLAY_GREY"]
    outLayerNames=["NT_dcdb"]

    rtn = fetchAllLayers(url,layerNames,outLayerNames,ntPath,proxys,taskItemId,mc,taskId,"NT","DCDB",True,logger)
    if rtn ==1:
        mc.updateTaskItemStatus(taskItemId,"completed",None,None,"")
def exportNT_scdb_qgis(path,proxys,access_token,taskId,mc):
    logger = logging.getLogger('exportNT_scdb_qgis') 
    fh = logging.FileHandler(path+'/exportNT_scdb_qgis.log')  
    fh.setLevel(logging.INFO)  
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    logger.addHandler(fh)  
    sh.setFormatter(formatter)  
    logger.addHandler(sh)  
    ntPath=path+"/NT_scdb"
    logger.info(ntPath)
    taskItemId=mc.createTaskItem(taskId,"NT_scdb","SCDB","NT_scdb","0","downloading","0","0","script","startDownload")
    os.mkdir(ntPath)

    url="\"http://ogc.ntlis.nt.gov.au/gs/ows?SERVICE=WFS&REQUEST=GetFeature&outputFormat=application/json&VERSION=2.0.0&TYPENAMES=survey:SURVEY_MARKS&COUNT=1000000&SRSNAME=urn:ogc:def:crs:EPSG::4326\""
    cmd ="curl -o "+ntPath+"/NT_scdb.geojson "+url
    print cmd 
    mc.updateTaskItemStatus(taskItemId,"downloading file",None,None,cmd)
    msg=commands.getstatusoutput(cmd)
    addUUIDField(ntPath+'/NT_scdb.geojson')
    tippecanoeCmd='tippecanoe -z16  -o '+ntPath+'/NT_scdb.mbtiles -ap -as     -ad  -s EPSG:4326  -f '+ntPath+'/NT_scdb.geojson '
    logger.info(tippecanoeCmd)
    print tippecanoeCmd
    msg=commands.getstatusoutput(tippecanoeCmd)
    print msg
    mc.updateTaskItemStatus(taskItemId,"make mbtiles",None,None,tippecanoeCmd)
    logger.info(msg)
    mc.updateTaskItemStatus(taskItemId,"upload to mapbox",None,None,"uploading...")
    upload(ntPath+'/NT_scdb.mbtiles','NT_scdb',access_token)
    fileSize=os.path.getsize(ntPath+'/NT_scdb.mbtiles')
    mc.updateTaskItemStatus(taskItemId,"completed",None,None,"uploaded",str(fileSize))
def exportNT_dcdb_qgis(path,proxys,access_token,taskId,mc):
    logger = logging.getLogger('exportNT_dcdb_qgis') 
    fh = logging.FileHandler(path+'/exportNT_dcdb_qgis.log')  
    fh.setLevel(logging.INFO)  
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    logger.addHandler(fh)  
    sh.setFormatter(formatter)  
    logger.addHandler(sh)  
    ntPath=path+"/NT_dcdb"
    logger.info(ntPath)
    taskItemId=mc.createTaskItem(taskId,"NT_dcdb","DCDB","NT_dcdb","0","downloading","0","0","script","startDownload")
    os.mkdir(ntPath)

    url="\"http://ogc.ntlis.nt.gov.au/gs/ntlis/wfs?SERVICE=WFS&REQUEST=GetFeature&outputFormat=application/json&VERSION=2.0.0&TYPENAMES=ntlis:CADASTRE&STARTINDEX=0&COUNT=1000000&SRSNAME=urn:ogc:def:crs:EPSG::4326\""
    cmd ="curl -o "+ntPath+"/NT_dcdb.geojson "+url
    print cmd 
    mc.updateTaskItemStatus(taskItemId,"downloading file",None,None,cmd)
    msg=commands.getstatusoutput(cmd)
    addUUIDField(ntPath+'/NT_dcdb.geojson')
    tippecanoeCmd='tippecanoe -z16  -o '+ntPath+'/NT_dcdb.mbtiles -ap -as     -ad  -s EPSG:4326  -f '+ntPath+'/NT_dcdb.geojson '
    logger.info(tippecanoeCmd)
    mc.updateTaskItemStatus(taskItemId,"make mbtiles",None,None,tippecanoeCmd)
    msg= commands.getstatusoutput(tippecanoeCmd)
    logger.info(msg)
    mc.updateTaskItemStatus(taskItemId,"upload to mapbox",None,None,"uploading...")
    upload(ntPath+'/NT_dcdb.mbtiles','NT_dcdb',access_token)
    fileSize=os.path.getsize(ntPath+'/NT_dcdb.mbtiles')
    mc.updateTaskItemStatus(taskItemId,"completed",None,None,"uploaded",str(fileSize))
   

def exportNT_scdb(path,proxys,access_token,taskId,mc):
    logger = logging.getLogger('exportNT_scdb') 
    fh = logging.FileHandler(path+'/exportNT_scdb.log')  
    fh.setLevel(logging.INFO)  
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    logger.addHandler(fh)  
    sh.setFormatter(formatter)  
    logger.addHandler(sh)  

    url="http://ogc.ntlis.nt.gov.au/gs/ows?service=wfs&"
    
    ntPath=path+"/NT_scdb"
    logger.info(ntPath)
    taskItemId=mc.createTaskItem(taskId,"NT_scdb","SCDB","NT_scdb","0","downloading","0","0","script","startDownload")
    os.mkdir(ntPath)
   
    layerNames=["survey:SURVEY_MARKS"]
    outLayerNames=["NT_scdb"]
    rtn=fetchAllLayers(url,layerNames,outLayerNames,ntPath,proxys,taskItemId,mc,taskId,"NT_scdb","SCDB",False,logger)
    if rtn ==1:
        mc.updateTaskItemStatus(taskItemId,"completed",None,None,"")


''' 
def exportVIC(path,proxys,access_token,taskid,mc):
    os.mkdir(path+"/VIC")
    url="https://maps.land.vic.gov.au/geolassi/wfs"
    fetchAllLayers(url,path,proxys)
def exportQLD(path,proxys,includes,access_token,taskId,mc):
    url="https://gisservices.information.qld.gov.au/arcgis/rest/services/PlanningCadastre/LandParcelPropertyFramework/MapServer/4"
    name="QLD"
    exportJSON(url,path,name,proxys,300,includes,access_token,False,taskItemId,mc)
'''
def exportNSW(path,proxys,includes,access_token,taskId,mc):
    logger = logging.getLogger('exportNSW') 
    fh = logging.FileHandler(path+'/exportNSW.log')  
    fh.setLevel(logging.INFO)  
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    logger.addHandler(fh)  

    url ='http://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Cadastre/MapServer/9'
    name='NSW_dcdb'
    taskItemId=mc.createTaskItem(taskId,"NSW","DCDB",name+".mbtiles","0","downloading","0","0","script","startDownload")
    exportJSON(url,path,name,proxys,800,includes,access_token,False,taskItemId,mc,logger)
def exportACT(path,proxys,includes,access_token,taskId,mc):
    logger = logging.getLogger('exportACT') 
    fh = logging.FileHandler(path+'/exportACT.log')  
    fh.setLevel(logging.INFO)  
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    logger.addHandler(fh)  
    url ="http://data.actmapi.act.gov.au/arcgis/rest/services/data_extract/Land_Administration/MapServer/4"
    name ='ACT_dcdb'
    taskItemId=mc.createTaskItem(taskId,"ACT","DCDB",name+".mbtiles","0","downloading","0","0","script","startDownload")
    exportJSON(url,path,name,proxys,500,includes,access_token,False,taskItemId,mc,logger)
def exportTAS(path,proxys,includes,access_token,taskId,mc):
    logger = logging.getLogger('exportTAS') 
    fh = logging.FileHandler(path+'/exportTAS.log')  
    fh.setLevel(logging.INFO)  
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    logger.addHandler(fh)  
    url ="http://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreParcels/MapServer/0"
    name="TAS_dcdb"
    taskItemId=mc.createTaskItem(taskId,"TAS","DCDB",name+".mbtiles","0","downloading","0","0","script","startDownload")
    exportJSON(url,path,name,proxys,500,includes,access_token,False,taskItemId,mc,logger)
def exportSA(path,proxys,includes,access_token,taskId,mc):
    logger = logging.getLogger('exportSA') 
    fh = logging.FileHandler(path+'/exportSA.log')  
    fh.setLevel(logging.INFO)  
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    logger.addHandler(fh)  
    url ="http://location.sa.gov.au/arcgis/rest/services/DEWNRext/MapTheme_StreetBasemap/MapServer/1"
    name="SA_dcdb"
    taskItemId=mc.createTaskItem(taskId,"SA","DCDB",name+".mbtiles","0","downloading","0","0","script","startDownload")
    exportJSON(url,path,name,proxys,200,includes,access_token,False,taskItemId,mc,logger)
def exportWA(path,proxys,includes,access_token,taskId,mc):
    logger = logging.getLogger('exportWA') 
    fh = logging.FileHandler(path+'/exportWA.log')  
    fh.setLevel(logging.INFO)  
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    logger.addHandler(fh)  

    url ="https://services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Property_and_Planning/MapServer/2"
    name="WA_dcdb"
    taskItemId=mc.createTaskItem(taskId,"WA","DCDB",name+".mbtiles","0","downloading","0","0","script","startDownload")
    exportJSON(url,path,name,proxys,400,includes,access_token,True,taskItemId,mc,logger)


def exportVIC_scdb(path,access_token,taskid,mc):
    
    vicPath= path+"/VIC_scdb"
    os.mkdir(vicPath)
    logger = logging.getLogger('exportVIC_scdb') 
    fh = logging.FileHandler(vicPath+'/exportVIC_scdb.log')  
    fh.setLevel(logging.INFO)  
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    logger.addHandler(fh)  

    name="VIC"
    taskItemId=mc.createTaskItem(taskid,name,"SCDB","VIC_scdb.mbtiles","0","downloading","0","0","script","startDownload")
    victoria.downloadData(vicPath+"/files",vicPath+"/VIC_scdb.geojson")
    #geojsonCmd='ogr2ogr -f "GeoJSON" -t_srs EPSG:3857 '+vicPath+'/out.geojson '+vicPath+'/output.geojson '
    #print geojsonCmd
    #mc.updateTaskItemStatus(taskItemId,"export to geojson ",None,None,geojsonCmd)
    #print commands.getstatusoutput(geojsonCmd)
    addUUIDField(vicPath+'/VIC_scdb.geojson')
    tippecanoeCmd='tippecanoe -z16  -o '+vicPath+'/VIC_scdb.mbtiles -ap -as    -ad    -f '+vicPath+'/VIC_scdb.geojson '
    logger.info(tippecanoeCmd) 
    mc.updateTaskItemStatus(taskItemId,"make mbtiles ",None,None,tippecanoeCmd)
    msg= commands.getstatusoutput(tippecanoeCmd)
    logger.info(msg) 
    mapid = 'VIC_scdb'
    access_token='sk.eyJ1IjoiYmVuY2htcmsiLCJhIjoiY2piNmtzY2ZhM20ydjJxbzF4d2M0ZHZoMSJ9.gy69hvwbwSEIyP57Hg_Gsw'
    mc.updateTaskItemStatus(taskItemId,"uploading to mapbox ",None,None,mapid)
    upload(vicPath+'/VIC_scdb.mbtiles',mapid,access_token)
    fileSize=os.path.getsize(vicPath+'/VIC_scdb.mbtiles')
    mc.updateTaskItemStatus(taskItemId,"uploading finish ",None,None,mapid,str(fileSize))

def exportNSW_scdb(path,proxys,includes,access_token,taskId,mc):
    logger = logging.getLogger('exportNSW_scdb') 
    fh = logging.FileHandler(path+'/exportNSW_scdb.log')  
    fh.setLevel(logging.INFO)  
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    logger.addHandler(fh)  
    url ='http://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Survey_Mark/MapServer/0'
    name='NSW_scdb'
    taskItemId=mc.createTaskItem(taskId,name,"SCDB","NSW_scdb.mbtiles","0","downloading","0","0","script","startDownload")
    exportJSON(url,path,name,proxys,300,includes,access_token,False,taskItemId,mc,logger)
def exportACT_scdb(path,proxys,includes,access_token,taskId,mc):
    logger = logging.getLogger('exportACT_scdb') 
    fh = logging.FileHandler(path+'/exportACT_scdb.log')  
    fh.setLevel(logging.INFO)  
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    logger.addHandler(fh)  
    url ="http://data.actmapi.act.gov.au/arcgis/rest/services/actmapi/scm_layer/MapServer/0"
    name ='ACT_scdb'
    taskItemId=mc.createTaskItem(taskId,name,"SCDB","ACT_scdb.mbtiles","0","downloading","0","0","script","startDownload")
    exportJSON(url,path,name,proxys,800,includes,access_token,False,taskItemId,mc,logger)
def exportTAS_scdb(path,proxys,includes,access_token,taskId,mc):
    logger = logging.getLogger('exportTAS_scdb') 
    fh = logging.FileHandler(path+'/exportTAS_scdb.log')  
    fh.setLevel(logging.INFO)  
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    logger.addHandler(fh)  
    url ="https://services.thelist.tas.gov.au/arcgis/rest/services/Public/OpenDataWFS/MapServer/40"
    name="TAS_scdb"
    

    logger.info(url) 
    taskItemId=mc.createTaskItem(taskId,name,"SCDB","TAS_scdb.mbtiles","0","downloading","0","0","script","startDownload")
    print  taskItemId
    exportJSON(url,path,name,proxys,50,includes,access_token,False,taskItemId,mc,logger)
def exportSA_scdb(path,proxys,includes,access_token,taskId,mc):
    logger = logging.getLogger('exportSA_scdb') 
    fh = logging.FileHandler(path+'/exportSA_scdb.log')  
    fh.setLevel(logging.INFO)  
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    logger.addHandler(fh)  

    url ="http://www.dptiapps.com.au/dataportal/SurveyMarks_shp.zip"
    name="SA_scdb"
    taskItemId=mc.createTaskItem(taskId,name,"SCDB","SA_scdb.mbtiles","0","downloading","0","0","script","startDownload")
    filePath=path+"/"+name
    os.mkdir(filePath)
    filePath=filePath+"/SurveyMarks_shp.zip"
    cmd ="curl -o "+filePath+" "+url
    logger.info(cmd) 
    mc.updateTaskItemStatus(taskItemId,"downloading file",None,None,cmd)
    msg=commands.getstatusoutput(cmd)
    logger.info(msg)
    fpath = filePath.replace(".zip","")
    unzipcmd="unzip "+filePath +' -d '+fpath
    logger.info(unzipcmd)
    mc.updateTaskItemStatus(taskItemId,"unzip file",None,None,unzipcmd)
    msg= commands.getstatusoutput(unzipcmd)
    logger.info(msg)
            
    shpPath= fpath
    geojsonCmd='ogr2ogr -f "GeoJSON" '+shpPath+'/SA_scdb.geojson '+shpPath+'/SurveyMarks_GDA94.shp '
    logger.info(geojsonCmd)
    mc.updateTaskItemStatus(taskItemId,"export to geojson",None,None,geojsonCmd)
    msg= commands.getstatusoutput(geojsonCmd)
    logger.info(msg)

    addUUIDField(shpPath+'/SA_scdb.geojson')
    tippecanoeCmd='tippecanoe -z16  -o '+shpPath+'/SA_scdb.mbtiles -ap -as     -ad  -s EPSG:4326  -f '+shpPath+'/SA_scdb.geojson '
    logger.info(tippecanoeCmd)
    mc.updateTaskItemStatus(taskItemId,"make mbtiles",None,None,tippecanoeCmd)
    msg= commands.getstatusoutput(tippecanoeCmd)
    logger.info(msg)
    mc.updateTaskItemStatus(taskItemId,"upload to mapbox",None,None,"uploading...")
    upload(shpPath+'/SA_scdb.mbtiles','SA_scdb',access_token)
    fileSize=os.path.getsize(shpPath+'/SA_scdb.mbtiles')
    mc.updateTaskItemStatus(taskItemId,"completed",None,None,"uploaded",str(fileSize))

def exportWA_scdb(path,proxys,includes,access_token,taskId,mc):
    logger = logging.getLogger('exportWA_scdb') 
    fh = logging.FileHandler(path+'/exportWA_scdb.log')  
    fh.setLevel(logging.INFO)  
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    logger.addHandler(fh)  

    url ="https://services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Property_and_Planning/MapServer/1"
    name="WA_scdb"
    taskItemId=mc.createTaskItem(taskId,name,"SCDB","WA_scdb.mbtiles","0","downloading","0","0","script","startDownload")
    exportJSON(url,path,name,proxys,300,includes,access_token,False,taskItemId,mc,logger)
def downloadLargeLayer(url,proxys,name,layerName,count,bbox,opath,taskItemId,mc,isneedClip,logger):
    
    jsonName=layerName+".geojson"
    lpath=opath+"/"+layerName
    os.mkdir(lpath)
    size=2
    print "count="+str(count)
    if count <100000:
        size =64
    elif count>=100000 and count <200000:
        size =128
    elif count>=200000 and count <400000:
        size = 256
    else:
        size=512
    xmin= bbox[0]
    ymin= bbox[1]
    xmax= bbox[2]
    ymax= bbox[3]
    dx = xmax-xmin
    dy = ymax-ymin
    stepx=dx/size
    stepy=dy/size
    index=0
    urls=[]
    for i in range(size):
        for j in range(size):
            filter='<Filter xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml"><Intersects><PropertyName>GEOMETRY</PropertyName><gml:Envelope srsName="EPSG:4326"><gml:lowerCorner>'+str(xmin+i*stepx)+" "+str(ymin+j*stepy)+'</gml:lowerCorner>      <gml:upperCorner>'+str(xmin+(i+1)*stepx)+" "+str(ymin+(j+1)*stepy)+'</gml:upperCorner> </gml:Envelope></Intersects></Filter>'
            layerurl =url+'request=GetFeature&outputformat=json&srsName=EPSG:3857&typename='+name+"&"+urlencode({"Filter":filter})
            
            urls.append([layerurl,lpath+"/"+str(index)+".geojson"])
            index=index+1
    errors=[]
    retry=0
    isFailed=False
    while True:
        for rurl in urls: 
            l=len(proxys)
            index =random.randint(0, l-1)
            proxy = proxys[index]
            #sleep 0.1 avoid return http 407 
            time.sleep(0.1) 
            res= fetchData2(rurl[0],proxy,True,logger)
           
            if res==None:
                logger.error(rurl[0])
                errors.append(rurl)
            else:
                saveResult(res,rurl[1])
        if len(errors) >0:
            retry = retry+1
            if retry >4:
                isFailed=True
                break
            urls=errors
            errors = []
            logger.info("sleep 5 min")
            time.sleep(60*5) #wait 5 min   
        else:
            print "break"
            break
    if isFailed:
        mc.updateTaskItemStatus(taskItemId,"failed",None,None,"","")
    else:
        mergeWFSFromFile(lpath,jsonName,logger)
        mbtilesName=layerName+".mbtiles"
        mkMbtiles(lpath+"/"+mbtilesName,lpath+"/"+jsonName,layerName,layerName,taskItemId,mc,isneedClip,logger)
def mkMbtiles(outMbtile,jsonFile,layerName,mapid,taskItemId,mc,isneedClip=True,logger=None):
    p=" "
    addUUIDField(jsonFile)
    if isneedClip:
        p=" -X "
    tippecanoeCmd='tippecanoe -z16  -o '+outMbtile+' -ap -as '+p+'    -ad  -s EPSG:3857  -f '+jsonFile
    logger.info(tippecanoeCmd)  
    mc.updateTaskItemStatus(taskItemId,"create mbtiles",None,None,"")
    commands.getstatusoutput(tippecanoeCmd)
    mc.updateTaskItemStatus(taskItemId,"uploading to mapbox",None,None,mapid)
    access_token='sk.eyJ1IjoiYmVuY2htcmsiLCJhIjoiY2piNmtzY2ZhM20ydjJxbzF4d2M0ZHZoMSJ9.gy69hvwbwSEIyP57Hg_Gsw'
    upload(outMbtile,mapid,access_token)
    logger.info(outMbtile+" uploaded")  
    fileSize=os.path.getsize(outMbtile)
    logger.info(outMbtile+":"+str(fileSize)+" byte")  
    mc.updateTaskItemStatus(taskItemId,"uploading finish",None,None,mapid,str(fileSize))
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


def countLayer(url,layerName):
    layerUrl=url+'request=GetFeature&version=1.1.0&resultType=hits&typename='+layerName
    print layerUrl
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
def orderQldSCDB():
    mail="data@bmrk.co"
    url ="https://gisservices2.information.qld.gov.au/arcgis/rest/services/QSC/ClipZipShip/GPServer/ClipZipShip/submitJob?"
    url=url+urlencode({'f':'json','env':'outSR=102100','Layers_to_Clip':'["Survey Control"]','Feature_Format':'Shapefile - SHP - .shp','Spatial_Reference':'3857','To_Email':mail,'Prepackaged_Data_URLs':'','Output_Title':'Extract'})
    print url
    headers = {
        "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language":"en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6,so;q=0.5,ja;q=0.4"
    }
    request = urllib2.Request(url, headers=headers)
    print urllib2.urlopen(request).code
def orderQldDCDB():  
    mail="data@bmrk.co" 
    url ="https://gisservices2.information.qld.gov.au/arcgis/rest/services/QSC/ClipZipShip/GPServer/ClipZipShip/submitJob?"

    url=url+urlencode({'f':'json','env':'outSR=102100','Layers_to_Clip':'[]','Feature_Format':'','Spatial_Reference':'','To_Email':mail,'Prepackaged_Data_URLs':'DP_QLD_DCDB_WOS_CUR.zip:undefined','Output_Title':'Extract'})
    print url
    headers = {
        "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language":"en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6,so;q=0.5,ja;q=0.4"
    }
    request = urllib2.Request(url, headers=headers)
    print urllib2.urlopen(request).code
def VICDscbToMbTiles(logger,fileP,filePath,name,taskId,mc):
   
    unzipcmd="unzip -o "+fileP +'  -d '+filePath
    print unzipcmd
    #logger.info(unzipcmd) 
    #commands.getoutput(unzipcmd)
    os.system(unzipcmd)
    geojsonPath=filePath+"/VIC_dcdb.geojson"
    mbtilesPath=filePath+"/VIC_dcdb.mbtiles"
    #mc.updateTaskItemStatus(taskItemId,"unzip file completed",None,None,unzipcmd)
    for fpath,dirs,fs in os.walk(filePath):
        for f in fs:

            shpPath=os.path.join(fpath, f)
            
            
            if os.path.isfile(shpPath) and f.find("shp")>=0:
                name = f.replace("shp","mbtiles")
                taskItemId2=mc.createTaskItem(taskId,"VIC","DCDB",name,"0","downloading","0","0","mail","startDownload")
                geojsonCmd='ogr2ogr -f "GeoJSON" -t_srs EPSG:3857 '+geojsonPath+' '+shpPath
                mc.updateTaskItemStatus(taskItemId2,"export to geojson ",None,None,geojsonCmd)
                print geojsonPath
                
                #logger.info(geojsonCmd) 
                msg=commands.getstatusoutput(geojsonCmd)
                #logger.info(msg) 
                #addUUIDField(geojsonPath)
                tippecanoeCmd='tippecanoe -z16  -o '+mbtilesPath+'  -ap -as -X    -ad  -s EPSG:3857  -f '+geojsonPath
                #logger.info(tippecanoeCmd) 
                mc.updateTaskItemStatus(taskItemId2,"make mbtiles ",None,None,tippecanoeCmd)
                msg= commands.getstatusoutput(tippecanoeCmd)
                #logger.info(msg) 
            
                mapid = "VIC_dcdb"
                access_token='sk.eyJ1IjoiYmVuY2htcmsiLCJhIjoiY2piNmtzY2ZhM20ydjJxbzF4d2M0ZHZoMSJ9.gy69hvwbwSEIyP57Hg_Gsw'
                mc.updateTaskItemStatus(taskItemId2,"uploading to mapbox ",None,None,mapid)
                upload(mbtilesPath,mapid,access_token)
                mc.updateTaskItemStatus(taskItemId2,"uploaded ",None,None,mapid)
                fileSize=os.path.getsize(mbtilesPath)
                mc.updateTaskItemStatus(taskItemId2,"completed",None,None,"",str(fileSize))
                break
    #mc.updateTaskItemStatus(taskItemId,"completed",None,None,"")

def downloadVICData(filePath,name,url,taskId,mc):
    
    print url
    taskItemId=mc.createTaskItem(taskId,"VIC","DCDB",name,"0","downloading","0","0","mail","startDownload")
    if not os.path.exists(filePath):
        os.mkdir(filePath)
    logger = logging.getLogger('downloadVICData') 
    fh = logging.FileHandler(filePath+'/downloadVICData.log')  
    fh.setLevel(logging.INFO)  
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    logger.addHandler(fh)  

    fileP = filePath+name
    if not os.path.isfile(fileP):
        cmd = "export ec=18; while [ $ec -eq 18 ]; do /usr/bin/curl  -L -o "+fileP+" -O -C - \""+url+"\" ; export ec=$?; done"
        print cmd
        #cmd ="curl -L -o "+fileP+' "'+url+'"'
        logger.info(cmd)
        mc.updateTaskItemStatus(taskItemId,"downloading file",None,None,cmd)
        '''
        with open(fileP, 'wb') as f:
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.WRITEDATA, f)
            c.setopt(pycurl.SSL_VERIFYPEER, 0)  
            c.setopt(pycurl.SSL_VERIFYHOST, 0) 
            c.perform()
            c.close()
        '''
        msg=commands.getstatusoutput(cmd)
      
        fileSize=os.path.getsize(fileP)
        if fileSize <2*1024*1024:
            mc.updateTaskItemStatus(taskItemId,"download failed",None,None,"can't find the data")
            return
        VICDscbToMbTiles(logger,fileP,filePath,name,taskId,mc)
       
def getACTTruncated(feature):
    type=''
    v=feature.GetField("type")
    if v is None:
        v= ''
    else:
        v= v.lower()
    if v =='null' or v=='':
        type ='null'
    elif v =='am':
        type ='alpha mark'
    elif v =='crm':
        type ='coordinated reference mark'
    elif v =='kbm':
        type ='kerb bench mark'
    elif v =='mc':
        type ='major control'
    elif v =='misc':
        type ='miscellaneous mark'
    elif v =='pcm':
        type ='photo control mark'
    elif v =='rbm':
        type ='rural bench mark'
    elif v =='recm':
        type ='recovery mark'
    elif v =='sc':
        type ='sectional control'
    elif v =='sr':
        type ='steel rod'
    elif v =='srm':
        type ='subdivisional reference mark'
    return type
def getWATruncated(feature):
    cadastral_connection=''
    filter_value=''
    point_type=''
    v=feature.GetField("cadastral_connection")
    v2=feature.GetField("filter_value")
    v3=feature.GetField("point_type")
    
    if v is None:
        v= ''
    else:
        v= v.lower()
    if v =='null' or v=='':
        cadastral_connection ='null'
    elif v =='e':
        cadastral_connection ='exists'
    elif v =='n':
        cadastral_connection ='no'
    else:
        cadastral_connection=v
    if v2 is None:
        v2= 0
    if v2 ==1:
        filter_value='standard survey mark'
    elif v2==2:
        filter_value='benchmark'
    else:
        filter_value=''

    if v3 is None:
        v3= ''
    else:
        v3= v3.lower()
    if v3 =='s':
        point_type='standard survey mark'
    elif v3=='b':
        point_type='benchmark'
    else:
        point_type=v3


    return cadastral_connection,filter_value,point_type
def getSATruncated(feature):
    zone =None
    v_datum=''
    v_purpose=''
    h_adjusted=''
    h_datum=''
    h_fixing=''
    h_purpose=''
    h_authorit=''
    specattrib=''
    wasnow=''
    gone=''
    v_adjusted=''
    v_authorit=''
    marktype=''
    v_fixing=''

    v=feature.GetField("zone")
    v2=feature.GetField("v_datum")
    v3=feature.GetField("v_purpose")
    v4=feature.GetField("h_adjusted")
    v5=feature.GetField("h_datum")
    v6=feature.GetField("h_fixing")
    v7=feature.GetField("h_purpose")
    v8=feature.GetField("h_authorit")
    v9=feature.GetField("specattrib")
    v10=feature.GetField("wasnow")
    v11=feature.GetField("gone")
    v12=feature.GetField("v_adjusted")
    v13=feature.GetField("v_authorit")
    v14=feature.GetField("marktype")
    v15=feature.GetField("v_fixing")
    '''
    if v ==2:
        zone =52
    elif v==3:
        zone =53
    elif v==4:
        zone = 54
    else:
        zone = v
    '''
    zone=v
        
  

    if v2 is None:
        v2= ''
    else:
        v2= v2.lower()
    if v2 =='null' or v2=='':
        v_datum ='null'
    elif v2 =='a':
        v_datum='ahd'
    elif v2 =='m':
        v_datum='msl'
    
    if v3 is None:
        v3= ''
    else:
        v3= v3.lower()
    if v3 =='null' or v3=='':
        v_purpose ='null'
    elif v3 =='cad':
        v_purpose='cadastral'
    elif v3 =='eng':
        v_purpose='engineering'
    elif v3 =='geo':
        v_purpose='geodetic'
    elif v3 =='hyd':
        v_purpose='hydrographic'
    elif v3 =='m1':
        v_purpose='1:1000 mapping'
    elif v3 =='m10':
        v_purpose='1:10000 mapping'
    elif v3 =='m100':
        v_purpose='1:100,000 mapping'
    elif v3 =='m2.5':
        v_purpose='1:2,500 mapping'
    elif v3 =='m50':
        v_purpose='1:50,000 mapping'
    elif v3 =='oth':
        v_purpose='other'
    elif v3 =='pro':
        v_purpose='project mapping'
    elif v3 =='uns':
        v_purpose='unspecified'
   
    if v4 is None:
        v4= ''
    else:
        v4= v4.lower()
    if v4 =='null' or v4=='':
        h_adjusted ='null'
    elif v4 =='n':
        h_adjusted='no'
    elif v4 =='r':
        h_adjusted='radiated'
    elif v4 =='y':
        h_adjusted='yes'

    if v5 is None:
        v5= ''
    else:
        v5= v5.lower()
    if v5 =='null' or v5=='':
        h_datum ='null'
    elif v5 =='m':
        h_datum='mga94'
    elif v5 =='t':
        h_datum='transformed'
    
    if v6 is None:
        v6= ''
    else:
        v6= v6.lower()
    if v6 =='null' or v6=='':
        h_fixing ='null'
    elif v6 =='aus':
        h_fixing='aus-pos'
    elif v6 =='dig':
        h_fixing='digitised'
    elif v6 =='dop':
        h_fixing='doppler'
    elif v6 =='fug':
        h_fixing='fug-fugro'
    elif v6 =='gph':
        h_fixing='gps handheld'
    elif v6 =='gpk':
        h_fixing='gps kinematic'
    elif v6 =='gpr':
        h_fixing='gps rapid static'
    elif v6 =='gps':
        h_fixing='gps static'
    elif v6 =='pho':
        h_fixing='photogrammetry'
    elif v6 =='sca':
        h_fixing='scaled'
    elif v6 =='terrestrial':
        h_fixing='ter'
    elif v6 =='unspecified':
        h_fixing='uns'

    if v7 is None:
        v7= ''
    else:
        v7= v7.lower()
    if v7 =='null' or v7=='':
        h_purpose ='null'
    elif v7 =='cad':
        h_purpose='cadastral'
    elif v7 =='eng':
        h_purpose='engineering'
    elif v7 =='geo':
        h_purpose='geodetic'
    elif v7 =='hyd':
        h_purpose='hydrographic'
    elif v7 =='m1':
        h_purpose='1:1000 mapping'
    elif v7 =='m10':
        h_purpose='1:100,000 mapping'
    elif v7 =='m2.5':
        h_purpose='1:2,500 mapping'
    elif v7 =='m50':
        h_purpose='1:50,000 mapping'
    elif v7 =='mm':
        h_purpose='mark maintenance'
    elif v7 =='oth':
        h_purpose='other'
    elif v7 =='pro':
        h_purpose='project mapping'
    elif v7 =='uns':
        h_purpose='unspecified'

    if v8 is None:
        v8= ''
    else:
        v8= v8.lower()
    if v8 =='null' or v8=='':
        h_authorit =''
    elif v8 =='an':
        h_authorit='australian national'  
    elif v8 =='army':
        h_authorit='army'   
    elif v8 =='ausl':
        h_authorit='admin services auslig'   
    elif v8 =='cpb':
        h_authorit='coastal protection board'   
    elif v8 =='deh':
        h_authorit='dept environment & heritage'   
    elif v8 =='etsa':
        h_authorit='electricity trust of sa'   
    elif v8 =='ews':
        h_authorit='engineering & water supply'   
    elif v8 =='ga':
        h_authorit='geoscience australia'   
    elif v8 =='me':
        h_authorit='mines and energy'  
    elif v8 =='mh':
        h_authorit='marine and harbours'   
    elif v8 =='navy':
        h_authorit='navy'   
    elif v8 =='nsw':
        h_authorit='new south whales'   
    elif v8 =='nt':
        h_authorit='northern territory'   
    elif v8 =='psf':
        h_authorit='private survey firms'   
    elif v8 =='qld':
        h_authorit='queensland'   
    elif v8 =='saw':
        h_authorit='sa water corp'  
    elif v8 =='sg':
        h_authorit='surveyor general' 
    elif v8 =='tafe':
        h_authorit='tafe' 
    elif v8 =='tsa':
        h_authorit='transport sa'  
    elif v8 =='uns':
        h_authorit='unspecified' 
    elif v8 =='usa':
        h_authorit='university of sa' 
    elif v8 =='vic':
        h_authorit='victoria'  
    elif v8 =='wa':
        h_authorit='western australia' 

    if v9 is None:
        v9= ''
    else:
        v9= v9.lower()
    if v9 =='null' or v9=='':
        specattrib ='null'
    elif v9 =='a':
        specattrib='network psm'  
    elif v9 =='b':
        specattrib='trig station'  
    elif v9 =='c':
        specattrib='network psm & trig station'  

    if v10 is None:
        v10= ''
    else:
        v10= v10.lower()
    if v10 =='null' or v10=='':
        wasnow =''
    elif v10 =='w':
        wasnow= 'was'
    elif v10 =='n':
        wasnow= 'is'

    if v11 is None:
        v11= ''
    else:
        v11= v11.lower()
    if v11 =='null' or v11=='':
        gone =''
    elif v11 =='y':
        gone= 'existing'
    elif v11 =='n':
        gone= 'gone'
    
    if v12 is None:
        v12= ''
    else:
        v12= v12.lower()
    if v12 =='null' or v12=='':
        v_adjusted =''
    elif v12 =='n':
        v_adjusted= 'no'
    elif v12 =='r':
        v_adjusted= 'radiated'
    elif v12 =='y':
        v_adjusted= 'yes'

    if v13 is None:
        v13= ''
    else:
        v13= v13.lower()
    if v13 =='null' or v13=='':
        v_authorit ='null'
    elif v13 =='an':
        v_authorit= 'australian national'
    elif v13 =='army':
        v_authorit= 'army'
    elif v13 =='ausl':
        v_authorit= 'admin services auslig'
    elif v13 =='bhp':
        v_authorit= 'bhp'
    elif v13 =='cpb':
        v_authorit= 'coastal protection board'
    elif v13 =='deh':
        v_authorit= 'dept environment & heritage'
    elif v13 =='etsa':
        v_authorit= 'electricity trust of sa'
    elif v13 =='ews':
        v_authorit= 'engineering & water supply'
    elif v13 =='lg':
        v_authorit= 'local government'
    elif v13 =='me':
        v_authorit= 'mines and energy'
    elif v13 =='navy':
        v_authorit= 'navy'
    elif v13 =='nsw':
        v_authorit= 'new south wales'
    elif v13 =='nt':
        v_authorit= 'northern territory'
    elif v13 =='psf':
        v_authorit= 'private survey firms'
    elif v13 =='qld':
        v_authorit= 'queensland'
    elif v13 =='sac':
        v_authorit= 'sacon'
    elif v13 =='saw':
        v_authorit= 'sa water corp'
    elif v13 =='sg':
        v_authorit= 'surveyor general'
    elif v13 =='tele':
        v_authorit= 'telstra'
    elif v13 =='tsa':
        v_authorit= 'transport sa'
    elif v13 =='uns':
        v_authorit= 'unspecified'
    elif v13 =='usa':
        v_authorit= 'university of sa'
    elif v13 =='vic':
        v_authorit= 'victoria'
    elif v13 =='wa':
        v_authorit= 'western australia'

    if v14 is None:
        v14= ''
    else:
        v14= v14.lower()


    if v14 =='null' or v14=='':
        marktype ='null'
    elif v14 ==' a/h':
        marktype= 'auger hole in timber'
    elif v14 =='bcnr':
        marktype= 'building corner'
    elif v14 =='concrete block':
        marktype= 'cond'
    elif v14 =='crn':
        marktype= 'stone cairn'
    elif v14 =='d/h':
        marktype= 'mark type drill hole in concrete'
    elif v14 =='dpm':
        marktype= 'double psm without plaque'
    elif v14 =='dpmp':
        marktype= 'double psm with plaque'
    elif v14 =='dropper':
        marktype= 'dpr'
    elif v14 =='f/i':
        marktype= 'fence intersection'
    elif v14 =='gip':
        marktype= 'galvanised iron pipe'
    elif v14 =='ligh':
        marktype= 'lighthouse light'
    elif v14 =='lp/c':
        marktype= 'lead plug in concrete'
    elif v14 =='lp/r':
        marktype= 'lead plug in rock'
    elif v14 =='m/t':
        marktype= 'mark on tree'
    elif v14 =='mn':
        marktype= 'monument psm without plaque'
    elif v14 =='mnp':
        marktype= 'monument psm with plaque'
    elif v14 =='mop':
        marktype= 'mark on post/pole'
    elif v14 =='mp':
        marktype= 'metal pin'
    elif v14 =='n/c':
        marktype= 'nail in concrete/masonry'
    elif v14 =='n/f':
        marktype= 'natural feature'
    elif v14 =='nail':
        marktype= 'nail'
    elif v14 =='oth':
        marktype= 'other'
    elif v14 =='peg':
        marktype= 'peg'
    elif v14 =='pill':
        marktype= 'pillar'
    elif v14 =='post':
        marktype= 'post'
    elif v14 =='pp':
        marktype= 'plastic peg/monoblock'
    elif v14 =='pp/c':
        marktype= 'plastic plug in concrete'
    elif v14 =='pp/k':
        marktype= 'plastic plug in kerb'
    elif v14 =='pp/p':
        marktype= 'plastic plug in path'
    elif v14 =='psm':
        marktype= 'psm without plaque'
    elif v14 =='psmp':
        marktype= 'psm with plaque'
    elif v14 =='rail':
        marktype= 'rail'
    elif v14 =='ram':
        marktype= 'ramset pin'
    elif v14 =='ramk':
        marktype= 'ramset pin in kerb'
    elif v14 =='ramp':
        marktype= 'ramset pin in path'
    elif v14 =='ramw':
        marktype= 'ramset pin in watertable'
    elif v14 =='rod':
        marktype= 'deep bench mark (rod)'
    elif v14 =='spk':
        marktype= 'spike'
    elif v14 =='spkp':
        marktype= 'spike in bitumen path'
    elif v14 =='spkr':
        marktype= 'spike in bitumen road'
    elif v14 =='str':
        marktype= 'strainer post'
    elif v14 =='tsm':
        marktype= 'temporary survey mark'
    elif v14 =='uns':
        marktype= 'unspecified'
    if v15 is None:
        v15= ''
    else:
        v15= v15.lower()
    if v15 =='null' or v15=='':
        v_fixing ='null'
    elif v15=='1st':
        v_fixing ='1st order'
    elif v15=='2nd':
        v_fixing ='2nd order'
    elif v15=='3rd':
        v_fixing ='3rd order'
    elif v15=='4th':
        v_fixing ='4th order'
    elif v15=='aus':
        v_fixing ='aus-pos'
    elif v15=='dop':
        v_fixing ='doppler'
    elif v15=='gpk':
        v_fixing ='gps kinematic'
    elif v15=='gpr':
        v_fixing ='gps rapid static'
    elif v15=='gps':
        v_fixing ='gps static'
    elif v15=='ine':
        v_fixing ='inertial'
    elif v15=='oth':
        v_fixing ='other'
    elif v15=='pho':
        v_fixing ='photogrammetry'
    elif v15=='sca':
        v_fixing ='scaled'
    elif v15=='vas':
        v_fixing ='vertical angles'

    return zone,v_datum,v_purpose,h_adjusted,h_datum,h_fixing,h_purpose,h_authorit,specattrib,wasnow,gone,v_adjusted,v_authorit,marktype,v_fixing
def getVICTruncated(feature):
    coverexists=''
    markpostexists=''

    v=feature.GetField("coverExists")
    v2=feature.GetField("markPostExists")
   
    if v is None:
        v= ''
    else:
        v= v.lower()
    if v =='null' or v=='':
        coverexists =''
    elif v =='y':
        coverexists ='yes'
    elif v =='n':
        coverexists ='no'
    else :
        coverexists=v

    if v2 is None:
        v2= ''
    else:
        v2= v2.lower()
    if v2 =='null' or v2=='':
        markpostexists =''
    elif v2 =='y':
        markpostexists ='yes'
    elif v2 =='n':
        markpostexists ='no'
    else:
        markpostexists =v2
    
    return coverexists,markpostexists


def getNSWTruncated(feature):
    monumentlocation=''
    markstatus=''
    trigtype=''
    marktype=''
    v_fixing=''
    v=feature.GetField("monumentlocation")
    v2=feature.GetField("markstatus")
    v3=feature.GetField("trigtype")
    v4=feature.GetField("marktype")
    #v5=feature.GetField("v_fixing")

    if v is None:
        v= ''
    else:
        v= v.lower()
    if v =='null' or v=='':
        monumentlocation ='null'
    elif v =='g':
        monumentlocation ='ground level'
    elif v =='b':
        monumentlocation ='building or structure'
    elif v =='r':
        monumentlocation ='reservoir or tank'
    elif v =='o':
        monumentlocation ='other structure'
    elif v =='s':
        monumentlocation ='silo'
    if v2 is None:
        v2= ''
    else:
        v2= v2.lower()
    if v2 =='null' or v2=='':
        markstatus ='null'
    elif v2 =='d':
        markstatus='destroyed'
    elif v2 =='n':
        markstatus='not found'
    elif v2 =='u':
        markstatus='uncertain'
    elif v2 =='r':
        markstatus='restricted access'
    elif v2 =='s':
        markstatus='subsidence area'

    if v3 is None:
        v3= ''
    else:
        v3= v3.lower()
    if v3 =='null' or v3=='':
        trigtype ='null'
    elif v3 =='s':
        trigtype='surface mark'
    elif v3 =='p':
        trigtype='pillar'
    elif v3 =='m':
        trigtype='monument'

    if v4 is None:
        v4= ''
    else:
        v4= v4.lower()
    if v4 =='null' or v4=='':
        marktype ='null'
    elif v4=='pm':
        marktype ='permanent mark'
    elif v4=='ss':
        marktype ='state survey mark'
    elif v4=='ts':
        marktype ='trigonometrical station'
    elif v4=='gb':
        marktype ='geodetic bench mark'
    elif v4=='mm':
        marktype ='miscellaneous survey mark'
    elif v4=='cp':
        marktype ='mapping control point'
    elif v4=='cr':
        marktype ='cadastral reference mark'

    #return monumentlocation,markstatus,trigtype,marktype,v_fixing
    return monumentlocation,markstatus,trigtype,marktype

def getTASTruncated(feature):
    target_str=''
    hor_order=''
    hor_class=''
    hgt_class=''
    hgt_order=''
    hgt_datum=''
    v=feature.GetField("target_str")
    v2 = feature.GetField("hor_order")
    v3 = feature.GetField("hor_class")
    v4 = feature.GetField("hgt_class")
    v5=feature.GetField("hgt_order")
    v6=feature.GetField("hgt_datum")
 
    if v is None:
        v= ''
    else:
        v= v.lower()
    if v =='null':
        target_str ='null'
    elif v =='bcn':
        target_str ='beacon'
    elif v =='crn':
        target_str ='cairn'
    elif v =='rt':
        target_str ='radio tower'    
    elif v =='mwt':
        target_str ='microwave tower' 
    elif v =='lt':
        target_str ='navigation light'
    elif v =='pil':
        target_str ='pillar'
    elif v =='lh':
        target_str ='light house'
    elif v =='ft':
        target_str ='fire tower'
    elif v =='fc':
        target_str ='fire cabin'
    elif v =='mtt':
        target_str ='mobile telephone tower'
    elif v =='po':
        target_str ='pole'
    elif v =='mon':
        target_str ='monument'
    elif v =='tvt':
        target_str ='t.v. tower'
    elif v =='spi':
        target_str ='spire'
    elif v =='wt':
        target_str ='wind tower'
    elif v =='bld':
        target_str ='building'
    elif v =='mst':
        target_str ='mast'

    if v2 is None:
        v2= ''
    else:
        v2 = v2.lower()
    if v2 =='2nd':
        hor_order ='second'
    elif v2 =='sca':
        hor_order ='scaled'
    elif v2 =='4th':
        hor_order ='fourth'
    elif v2 =='prv':
        hor_order ='provisional'
    elif v2 =='3rd':
        hor_order ='third'
    elif v2 =='1st':
        hor_order ='first'
    elif v2 =='hheld':
        hor_order ='handheld gps standard'
    elif v2 =='zero':
        hor_order ='zero'
    if v3 is None:
        v3= ''
    else:
        v3 = v3.lower()
    if v3 =='tra':
        hor_class ='traverse'
    elif v3 =='b':
        hor_class ='class b'
    elif v3 =='gps':
        hor_class ='satellite - gps'
    elif v3 =='a':
        hor_class ='class a'
    elif v3 =='unc':
        hor_class ='unclosed traverse'
    elif v3 =='rad':
        hor_class ='radiation'
    elif v3 =='unknown':
        hor_class ='unknown'
    elif v3 =='rtk':
        hor_class ='rtk used to upgrade sca class marks'
    elif v3 =='c':
        hor_class ='class c'
    elif v3 =='null':
        hor_class ='null'
    elif v3 =='int':
        hor_class ='intersection'
    elif v3 =='aaa':
        hor_class ='class aaa'
    elif v3 =='d':
        hor_class ='d'
    if v4 is None:
        v4= ''
    else:
        v4 = v4.lower()
        
    if v4=='lev3':
        hgt_class='third order levelling'
    elif v4=='gps':
        hgt_class='gps    satellite'
    elif v4=='levu':
        hgt_class='levelling - unspecified'
    elif v4=='null':
        hgt_class='null'
    elif v4=='trig':
        hgt_class='trigonometric heighting'
    elif v4=='lev4':
        hgt_class='fourth order levelling'
    elif v4=='lev41way':
        hgt_class='one way fourth order levelling'
    elif v4=='direct':
        hgt_class='direct measurement'
    elif v4=='unk':
        hgt_class='unknown'
    elif v4=='rtk':
        hgt_class='rtk used to upgrade sca class marks with null hgt'
    elif v4=='lev1':
        hgt_class='first order levelling'
    elif v4=='res':
        hgt_class='resection'
    elif v4=='dop':
        hgt_class='satellite - doppler'
    elif v4=='int':
        hgt_class='intersection'
    elif v4=='a':
        hgt_class='class a'
    elif v4=='b':
        hgt_class='class b'
    elif v4=='bar':
        hgt_class='barometric heighting'
    elif v4=='c':
        hgt_class='class c'
    elif v4=='lev2':
        hgt_class='second order levelling'
    if v5 is None:
        v5= ''
    else:
        v5 = v5.lower()
    if v5=='l3rd':
        hgt_order= 'third order differential'
    elif v5=='null':
        hgt_order= 'null'
    elif v5=='3rd':
        hgt_order= 'third'
    elif v5=='4th':
        hgt_order= 'fourth'
    elif v5=='l4th':
        hgt_order= 'fourth order differential'
    elif v5=='l3rdlc':
        hgt_order= '3rd order differential and part of level cluster'
    elif v5=='prv':
        hgt_order= 'provisional'
    elif v5=='5th':
        hgt_order= 'fifth'
    elif v5=='1st':
        hgt_order= 'first'
    elif v5=='2nd':
        hgt_order= 'second'
    if v6 is None:
        v6= ''
    else:
        v6 = v6.lower()
    if v6=='ahd83':
        hgt_datum= 'aust height datum (tas) 1983'
    elif v6=='state':
        hgt_datum= 'state datum'
    elif v6=='ahd79':
        hgt_datum= 'aust height datum (tas) 1979'
    elif v6=='local':
        hgt_datum= 'local datum'
    elif v6=='none':
        hgt_datum= 'none'
    elif v6=='gda94':
        hgt_datum= 'geocentric datum of aust 1994'    
        
    #print target_str,hor_order,hor_class,hgt_class,hgt_order,hgt_datum
    return  target_str,hor_order,hor_class,hgt_class,hgt_order,hgt_datum

def getSymByName(name,feature):  
    sym=''
    sym_sel=''
    if name =="ACT_scdb":
        v=feature.GetField("type")
        sym="act_"+v
        sym_sel = "act_"+v+"_sel"
    elif name =="NSW_scdb":
        v=feature.GetField("marksymbol").lower()
       
        sym="nsw_"+v
        sym_sel = "nsw_"+v+"_sel"
    elif name =="WA_scdb":
        v=feature.GetField("render_value")
        sym="wa_"+v
        sym_sel = "wa_"+v+"_sel"
    elif name == "TAS_scdb":
        v=feature.GetField("order_symb")
        sym="tas_"+v
        sym_sel = "tas_"+v+"_sel"
    elif name == "NT_scdb":
        v=feature.GetField("MARKTYPE")
        if v is None:
            return sym,sym_sel
        v1=v.lower()
        v2 = feature.GetField("ADJSTATUS")
        if v1 == 'crm':
            if v2 =='Adopted':
                sym='nt_crmad'
                sym_sel = sym+"_sel"
            elif v2 =='Lodged':
                sym='nt_crml'
                sym_sel = sym+"_sel"
            elif v2 =='Approved':
                sym='nt_crmap'
                sym_sel = sym+"_sel"
            elif v2 =='Gone':
                sym='nt_crmg'
                sym_sel = sym+"_sel"
            elif v2 =='Proposed':
                sym='nt_crmp'
                sym_sel = sym+"_sel"
            elif v2 =='Disturbed':
                sym='nt_crmd'
                sym_sel = sym+"_sel"
        elif v1 == 'bm':
            if v2 =='Adopted':
                sym='nt_bmad'
                sym_sel = sym+"_sel"
            elif v2 =='Lodged':
                sym='nt_bml'
                sym_sel = sym+"_sel"
            elif v2 =='Approved':
                sym='nt_bmap'
                sym_sel = sym+"_sel"
            elif v2 =='Gone':
                sym='nt_bmg'
                sym_sel = sym+"_sel"
            elif v2 =='Proposed':
                sym='nt_bmp'
                sym_sel = sym+"_sel"
            elif v2 =='Disturbed':
                sym='nt_bmd'
                sym_sel = sym+"_sel"
        elif v1 == 'other':
            if v2 =='Adopted':
                sym='nt_otherad'
                sym_sel = sym+"_sel"
            elif v2 =='Lodged':
                sym='nt_otherl'
                sym_sel = sym+"_sel"
            elif v2 =='Approved':
                sym='nt_otherap'
                sym_sel = sym+"_sel"
            elif v2 =='Gone':
                sym='nt_otherg'
                sym_sel = sym+"_sel"
            elif v2 =='Proposed':
                sym='nt_otherp'
                sym_sel = sym+"_sel"
            elif v2 =='Disturbed':
                sym='nt_otherd'
                sym_sel = sym+"_sel"      
        elif v1 == 'pcp':
            if v2 =='Adopted':
                sym='nt_pcpad'
                sym_sel = sym+"_sel"
            elif v2 =='Lodged':
                sym='nt_pcpl'
                sym_sel = sym+"_sel"
            elif v2 =='Approved':
                sym='nt_pcpap'
                sym_sel = sym+"_sel"
            elif v2 =='Gone':
                sym='nt_pcpg'
                sym_sel = sym+"_sel"
            elif v2 =='Proposed':
                sym='nt_pcpp'
                sym_sel = sym+"_sel"
            elif v2 =='Disturbed':
                sym='nt_pcpd'
                sym_sel = sym+"_sel"    
        elif v1 == 'cm':
            if v2 =='Adopted':
                sym='nt_cmad'
                sym_sel = sym+"_sel"
            elif v2 =='Lodged':
                sym='nt_cml'
                sym_sel = sym+"_sel"
            elif v2 =='Approved':
                sym='nt_cmap'
                sym_sel = sym+"_sel"
            elif v2 =='Gone':
                sym='nt_cmg'
                sym_sel = sym+"_sel"
            elif v2 =='Proposed':
                sym='nt_cmp'
                sym_sel = sym+"_sel"
            elif v2 =='Disturbed':
                sym='nt_cmd'
                sym_sel = sym+"_sel"  
        elif v1 == 'o':
            if v2 =='Adopted':
                sym='nt_oad'
                sym_sel = sym+"_sel"
            elif v2 =='Lodged':
                sym='nt_ol'
                sym_sel = sym+"_sel"
            elif v2 =='Approved':
                sym='nt_oap'
                sym_sel = sym+"_sel"
            elif v2 =='Gone':
                sym='nt_og'
                sym_sel = sym+"_sel"
            elif v2 =='Proposed':
                sym='nt_op'
                sym_sel = sym+"_sel"
            elif v2 =='Disturbed':
                sym='nt_od'
                sym_sel = sym+"_sel"
        elif v1 == 'cors':
            sym='nt_cors'
            sym_sel = sym+"_sel"  
    elif name == "QLD_scdb":
        iconid= feature.GetField("ICON_ID")
        sym='qld_'+str(iconid)
        sym_sel='qld_'+str(iconid)+'_sel'
    elif name == "VIC_scdb":
        value= feature.GetField("symbol") 
        if value == 'mark-scn-gda94-pm-16':
            sym='vic_st'
            sym_sel='vic_st_sel'
        elif value == 'mark-scn-gda94-pcm-16':
            sym='vic_sp'
            sym_sel='vic_sp_sel'
        elif value == 'mark-scn-gda94+ahd-pm-16':
            sym='vic_sct'
            sym_sel='vic_sct_sel'
        elif value == 'mark-scn-gda94+ahdapprox-pm-16':
            sym='vic_sst'
            sym_sel='vic_sst_sel'
        elif value == 'mark-ahdapprox-pm-16':
            sym='vic_ns'
            sym_sel='vic_ns_sel'
        elif value == 'mark-scn-ahd-pm-16':
            sym='vic_sc'
            sym_sel='vic_sc_sel'
        elif value == 'mark-gda94approx-pm-16':
            sym='vic_na'
            sym_sel='vic_na_sel'
        elif value == 'mark-defective-16':
            sym='vic_d'
            sym_sel='vic_d_sel'
    elif name =="SA_scdb":
        value= feature.GetField("SYMBOLOGY")
        if value ==0:
            sym='sa_3'
            sym_sel='sa_3_sel'
        elif value >=1 and value <2:
            sym='sa_1'
            sym_sel='sa_1_sel'
        elif value >=2 and value <3:
            sym='sa_2'
            sym_sel='sa_2_sel' 
        elif value >=3 and value <4:
            sym='sa_3'
            sym_sel='sa_3_sel' 
        elif value >=4 and value <5:
            sym='sa_4'
            sym_sel='sa_4_sel' 
        elif value >=5 and value <6:
            sym='sa_5'
            sym_sel='sa_5_sel' 
        elif value >=6:
            sym='sa_6'
            sym_sel='sa_6_sel'            
 
    return sym,sym_sel
def addUUIDFieldForSqlite(sqliteFile):
    filename_w_ext = os.path.basename(sqliteFile)
    filename, file_extension = os.path.splitext(filename_w_ext)

    driverName = "sqlite"
    driver = ogr.GetDriverByName( driverName ) 
    dataSource = driver.Open(sqliteFile, 1) 
    lyr = dataSource.GetLayer("ogrgeojson")
    #lyr = dataSource.GetLayer("test")
    field_name = ogr.FieldDefn("mb_id", ogr.OFTString)      
    field_name.SetWidth(24)
    lyr.CreateField(field_name)
    field_name2 = ogr.FieldDefn("zone", ogr.OFTInteger)      
    lyr.CreateField(field_name2)
    if filename =="WA_scdb":
        field_name = ogr.FieldDefn("filter_value2", ogr.OFTString)      
        field_name.SetWidth(24)
        lyr.CreateField(field_name)
    if filename =="NSW_scdb":
        field_name = ogr.FieldDefn("fullMarkType", ogr.OFTString)      
        field_name.SetWidth(24)
        lyr.CreateField(field_name)
    symIndex = filename.find("_scdb")
    if symIndex>0:
        field_name = ogr.FieldDefn("sym", ogr.OFTString)      
        field_name.SetWidth(24)
        lyr.CreateField(field_name)
        field_name2 = ogr.FieldDefn("sym_sel", ogr.OFTString)      
        lyr.CreateField(field_name2)

    id=[]
    j=0
    lyr.StartTransaction()
    for f in lyr:
        id.append(f.GetFID())
    for i in id:
        feature=lyr.GetFeature(i)
        j=j+1
       
        
        uid = uuid.uuid4()
        feature.SetField("mb_id", str(uid))
        geom = feature.GetGeometryRef()
        type =geom.GetGeometryType()
        if type <=2:
            x =  geom.GetX()
            y = geom.GetY()
            zone =getZone(x,y)
    
            feature.SetField("zone", zone)
        fieldIndex=feature.GetFieldIndex("render_value")
        if(fieldIndex>=0):
           render_value=feature.GetFieldAsString("render_value")
           render_value=render_value.strip()
           feature.SetField("render_value", render_value)
        if symIndex>0:
            sym,sym_sel=getSymByName(filename,feature)
            feature.SetField("sym", sym)
            feature.SetField("sym_sel", sym_sel)
        if filename =="TAS_scdb":
            target_str,hor_order,hor_class,hgt_class,hgt_order,hgt_datum=getTASTruncated(feature)
            feature.SetField("target_str", target_str)
            feature.SetField("hor_order", hor_order)
            feature.SetField("hor_class", hor_class)
            feature.SetField("hgt_class", hgt_class)
            feature.SetField("hgt_order", hgt_order)
            feature.SetField("hgt_datum", hgt_datum)
        if filename == 'NSW_scdb':
            monumentlocation,markstatus,trigtype,marktype=getNSWTruncated(feature)
            feature.SetField("monumentlocation", monumentlocation)
            feature.SetField("markstatus", markstatus)
            feature.SetField("trigtype", trigtype)
            feature.SetField("fullMarkType", marktype)
            #feature.SetField("v_fixing", v_fixing)
        if filename =="ACT_scdb":
            type= getACTTruncated(feature)
            feature.SetField("type", type)
        if filename =="WA_scdb":
            cadastral_connection,filter_value,point_type=getWATruncated(feature)
            feature.SetField("cadastral_connection", cadastral_connection)
            feature.SetField("filter_value2", filter_value)
            feature.SetField("point_type", point_type)

        lyr.SetFeature(feature)
 
    lyr.CommitTransaction()
    dataSource.Destroy()
def getZone(x,y):
    source = osr.SpatialReference()
    source.ImportFromEPSG(3857)
    target = osr.SpatialReference()
    target.ImportFromEPSG(4326)
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(x, y)
    transform = osr.CoordinateTransformation(source, target)
    point.Transform(transform)
    
    x = point.GetX()
    zone = int((x+6.0)/6.0)+30
    return zone
def getGDA94Coor(zone,x,y):
    source = osr.SpatialReference()
    source.ImportFromEPSG(3857)
    target = osr.SpatialReference()
    target.ImportFromEPSG(28300+zone)
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(x, y)
    transform = osr.CoordinateTransformation(source, target)
    point.Transform(transform)

    return point 

def addUUIDField(geojsonFile):
    filename_w_ext = os.path.basename(geojsonFile)
    filename, file_extension = os.path.splitext(filename_w_ext)
  
    driverName = "GeoJSON"
    #driverName = "ESRI shapefile"
    driver = ogr.GetDriverByName( driverName ) 
    dataSource = driver.Open(geojsonFile, 1) 
    lyr = dataSource.GetLayer(0)

    field_name = ogr.FieldDefn("mb_id", ogr.OFTString)      
    field_name.SetWidth(24)
    lyr.CreateField(field_name)
    if filename != "SA_scdb":
        
        field_name2 = ogr.FieldDefn("zone", ogr.OFTString)  
        field_name2.SetWidth(24)    
        lyr.CreateField(field_name2)
    
    
    if filename == "QLD_scdb":
        field_name3 = ogr.FieldDefn("easting", ogr.OFTString)   
        field_name3.SetWidth(255)   
        lyr.CreateField(field_name3)

        field_name4 = ogr.FieldDefn("northing", ogr.OFTString)   
        field_name4.SetWidth(255)   
        print lyr.CreateField(field_name4)
    
    
    symIndex = filename.find("_scdb")
    if symIndex>0:

        field_name4 = ogr.FieldDefn("sym", ogr.OFTString)   
        field_name4.SetWidth(24)   
        lyr.CreateField(field_name4)

        field_name5 = ogr.FieldDefn("sym_sel", ogr.OFTString)   
        field_name5.SetWidth(24)   
        lyr.CreateField(field_name5)

    
    feature = lyr.GetNextFeature()
    while feature:
        uid = uuid.uuid4()
        feature.SetField("mb_id", str(uid))
        geom = feature.GetGeometryRef()
        type =geom.GetGeometryType()

        if type <=2:
            if  filename != "SA_scdb":
                print filename
                if filename == "VIC_scdb":
                    x = geom.GetX()
                    zone = int((x+6.0)/6.0)+30
                else:
                    x =  geom.GetX()
                    y = geom.GetY()
                    zone =getZone(x,y)
                feature.SetField("zone", str(zone))
           
            if filename == "QLD_scdb":
                outPoint = getGDA94Coor(zone,geom.GetX(),geom.GetY())
                feature.SetField("easting", str(outPoint.GetX()))
                feature.SetField("northing", str(outPoint.GetY()))
        fieldIndex=feature.GetFieldIndex("render_value")
        if(fieldIndex>=0):
           render_value=feature.GetFieldAsString("render_value")
           render_value=render_value.strip()
           feature.SetField("render_value", render_value)
        if symIndex>0:
            sym,sym_sel=getSymByName(filename,feature)
            feature.SetField("sym", sym)
            feature.SetField("sym_sel", sym_sel)
        if filename == "SA_scdb":
            zone,v_datum,v_purpose,h_adjusted,h_datum,h_fixing,h_purpose,h_authorit,specattrib,wasnow,gone,v_adjusted,v_authorit,marktype,v_fixing=getSATruncated(feature)
            feature.SetField("zone", zone)
            feature.SetField("v_datum", v_datum)
            feature.SetField("v_purpose", v_purpose)
            feature.SetField("h_adjusted", h_adjusted)
            feature.SetField("h_datum", h_datum)
            feature.SetField("h_fixing", h_fixing)
            feature.SetField("h_purpose", h_purpose)
            feature.SetField("h_authorit", h_authorit)
            feature.SetField("specattrib", specattrib)
            feature.SetField("wasnow", wasnow)
            feature.SetField("gone", gone)
            feature.SetField("v_adjusted", v_adjusted)
            feature.SetField("v_authorit", v_authorit)
            feature.SetField("marktype", marktype)
            feature.SetField("v_fixing", v_fixing)
            
        if filename == "VIC_scdb":
            coverexists,markpostexists=getVICTruncated(feature)
            feature.SetField("coverExists", coverexists)
            feature.SetField("markPostExists", markpostexists)
        lyr.SetFeature(feature)
        feature = lyr.GetNextFeature()
    
    dataSource.Destroy()

def downloadQldSCDBdata(filePath,name,url,taskId,mc):
    taskItemId=mc.createTaskItem(taskId,"QLD_scdb","SCDB","QLD_scdb.mbtiles","0","downloading","0","0","mail","startDownload")
    if not os.path.exists(filePath):
        os.mkdir(filePath)
    fileP = filePath+name
    logger = logging.getLogger('downloadQldSCDBdata') 
    fh = logging.FileHandler(filePath+'/downloadQldSCDBdata.log')  
    fh.setLevel(logging.INFO)  
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    logger.addHandler(fh)  
    if not os.path.isfile(fileP):
        print "downloading qld"
        cmd = "export ec=18; while [ $ec -eq 18 ]; do /usr/bin/curl  -L -o "+fileP+" -O -C - \""+url+"\" ; export ec=$?; done"
        print cmd
        #cmd ="curl -L -o "+fileP+' "'+url+'"'
        logger.info(cmd)
        mc.updateTaskItemStatus(taskItemId,"downloading file",None,None,cmd)
        '''
        with open(fileP, 'wb') as f:
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.WRITEDATA, f)
            c.setopt(pycurl.SSL_VERIFYPEER, 0)  
            c.setopt(pycurl.SSL_VERIFYHOST, 0) 
            c.perform()
            c.close()
        '''
        msg=commands.getstatusoutput(cmd)
        logger.info(msg)
        print msg
        path = fileP.replace(".zip","")
        unzipcmd="unzip "+fileP +' -d '+filePath
        logger.info(unzipcmd)
        mc.updateTaskItemStatus(taskItemId,"unzip file",None,None,unzipcmd)
        msg= commands.getstatusoutput(unzipcmd)
        logger.info(msg)
        renameCMd = 'mv '+filePath+'/QSC_Extracted_Data* ' +filePath+"/QLD_scdb"
        msg= commands.getstatusoutput(renameCMd)
        logger.info(msg) 
            
        shpPath= filePath+"/QLD_scdb"

        geojsonCmd='ogr2ogr -f "GeoJSON" -t_srs EPSG:3857 '+shpPath+'/QLD_scdb.geojson '+shpPath+'/Survey_Control.shp'
        logger.info(geojsonCmd)
        mc.updateTaskItemStatus(taskItemId,"export to geojson ",None,None,geojsonCmd)
        msg= commands.getstatusoutput(geojsonCmd)
        logger.info(msg)
        addUUIDField(shpPath+'/QLD_scdb.geojson')
        tippecanoeCmd='tippecanoe -z16  -o '+shpPath+'/QLD_scdb.mbtiles -ap -as    -ad  -s EPSG:3857  -f '+shpPath+'/QLD_scdb.geojson'
        logger.info(tippecanoeCmd)
        print tippecanoeCmd
        mc.updateTaskItemStatus(taskItemId,"make mbtiles ",None,None,tippecanoeCmd)
        msg= commands.getstatusoutput(tippecanoeCmd)
        print msg
        logger.info(msg)
        mapid = 'QLD_SCDB'
        access_token='sk.eyJ1IjoiYmVuY2htcmsiLCJhIjoiY2piNmtzY2ZhM20ydjJxbzF4d2M0ZHZoMSJ9.gy69hvwbwSEIyP57Hg_Gsw'
        mc.updateTaskItemStatus(taskItemId,"uploading to mapbox ",None,None,mapid)
        upload(shpPath+'/QLD_scdb.mbtiles',mapid,access_token)
        fileSize=os.path.getsize(shpPath+'/QLD_scdb.mbtiles')
        mc.updateTaskItemStatus(taskItemId,"uploading finish ",None,None,mapid,str(fileSize))
    mc.updateTaskItemStatus(taskItemId,"completed",None,None,"")
def downloadQldDCDBdata(filePath,name,url,taskId,mc,proxyIp):
    
    taskItemId=mc.createTaskItem(taskId,"QLD","DCDB",name,"0","downloading","0","0","mail","startDownload")
    if not os.path.exists(filePath):
        os.mkdir(filePath)
    logger = logging.getLogger('downloadQldDCDBdata') 
    fh = logging.FileHandler(filePath+'/downloadQldDCDBdata.log')  
    fh.setLevel(logging.INFO)  
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    logger.addHandler(fh)  
    fileP=filePath+name
    if not os.path.isfile(fileP):
        cmd = "export ec=18; while [ $ec -eq 18 ]; do /usr/bin/curl  -L -o "+fileP+" -O -C - \""+url+"\" ; export ec=$?; done"
        print cmd
        #cmd ="curl -o "+fileP+' "'+url+'"'
        logger.info(cmd)
        msg=commands.getstatusoutput(cmd)
        logger.info(msg)
        print msg
        mc.updateTaskItemStatus(taskItemId,"downloading file",None,None,cmd)
        '''
        with open(fileP, 'wb') as f:
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.WRITEDATA, f)
            c.setopt(pycurl.SSL_VERIFYPEER, 0)  
            c.setopt(pycurl.SSL_VERIFYHOST, 0) 
            pproxys =proxyIp.split(":")
            ip='http://'+pproxys[0]+":"+pproxys[1]
            c.setopt(pycurl.PROXY, ip)
            usrpwd=pproxys[2]+":"+pproxys[3]
            
            c.setopt(pycurl.PROXYUSERPWD, usrpwd)
            c.setopt(pycurl.HTTPHEADER, ['Expect:', '100-continue', 'Connection: Keep-Alive'])
            c.perform()
            c.close()
        '''
        path = fileP.replace(".zip","")
        unzipcmd="unzip "+fileP +' -d '+path
        logger.info(unzipcmd)
       
        mc.updateTaskItemStatus(taskItemId,"unzip file completed",None,None,unzipcmd)
        msg= commands.getstatusoutput(unzipcmd)
        logger.info(msg)
        #path = filePath.replace(".zip","")
        layer="QLD_CADASTRE_DCDB"
       
        geojsonCmd='ogr2ogr -f "GeoJSON" '+path+'/QLD_dcdb.geojson -t_srs EPSG:3857 '+path+'/DP_QLD_DCDB_WOS_CUR.gdb '+' "'+layer+'"'
        logger.info(geojsonCmd)
        mc.updateTaskItemStatus(taskItemId,"export to geojson ",None,None,geojsonCmd)
        msg= commands.getstatusoutput(geojsonCmd)
        logger.info(msg)
        
        tippecanoeCmd='tippecanoe -z16  -o '+path+'/QLD_dcdb.mbtiles '+' -ap -as --include="LOT_AREA" --include="PARCEL_TYP"     -ad  -s EPSG:3857  -f '+path+'/QLD_dcdb.geojson '
        logger.info(tippecanoeCmd)
        mc.updateTaskItemStatus(taskItemId,"make mbtiles ",None,None,tippecanoeCmd)
        msg= commands.getstatusoutput(tippecanoeCmd)
        logger.info(msg)
        access_token='sk.eyJ1IjoiYmVuY2htcmsiLCJhIjoiY2piNmtzY2ZhM20ydjJxbzF4d2M0ZHZoMSJ9.gy69hvwbwSEIyP57Hg_Gsw'
        mc.updateTaskItemStatus(taskItemId,"uploading to mapbox ",None,None,layer)
        upload(path+'/QLD_dcdb.mbtiles',"QLD_dcdb",access_token)
        fileSize=os.path.getsize(path+'/QLD_dcdb.mbtiles')           
        mc.updateTaskItemStatus(taskItemId,"uploading finish ",None,None,"",str(fileSize))

    mc.updateTaskItemStatus(taskItemId,"completed",None,None,"")
def downloaddata(path,taskId,mc,isSunday,proxys):
    server= poplib.POP3('simplemail.pop.co')
    server.user("data@bmrk.co")
    server.pass_('x9G-eMG-BB7-8Qb')
    print server.stat()
    numMessages = len(server.list()[1])
    #print numMessages
    data =[]
    for i in range(numMessages):
        data.append(server.retr(numMessages-i))
    server.quit()
    isFindQldSCDB=False
    isFindQldDCDB=False
    isFindVIC=False
    i=0
    for (server_msg, body, octets) in data:
        result=''
        if isFindQldSCDB and isFindQldDCDB and isFindVIC:
            break
        for msg in body:
            result = result+msg
        #print result
        qIndex=result.find("https://gisservices2.information.qld.gov.au")
        #print result
        if qIndex>=0 and not isFindQldSCDB:
            isFindQldSCDB=True
            left=result.find("<",qIndex-2)
            right = result.find(">",qIndex-2)
            
            url = result[left+1:right]
            print url
            filePath= path+"/QLD_scdb/"
            name="QLD_scdb.zip"
         
            #downloadQldSCDBdata(filePath,name,url,taskId,mc)
        qIndex2= result.find("http://qldspatial.information.qld.gov.au/DownloadService/Download.aspx")
        if  qIndex2>=0 and not isFindQldDCDB:
            isFindQldDCDB=True
            name="DP_QLD_DCDB_WOS_CUR.zip"

            right = result.find(">",qIndex2)
            url = result[qIndex2:right]
            print url
            filePath=path+ "/QLD_dcdb/"
            '''
            if isSunday:
                downloadQldDCDBdata(filePath,name,url,taskId,mc,proxys[0])
            '''

        index3=result.find("http://services.land.vic.gov.au/SpatialDatamart/publicAccessOrderDownload.html")
        if index3 >=0 and not isFindVIC:
            isFindVIC=True
            index=result.find("URL :",0)
            right = result.find(">",index3)
            url = result[index3:right-1]
            filePath= path+"/VIC_dcdb/"
            name =url.split("&")[0].split("=")[-1]
            
            if isSunday:
                downloadVICData(filePath,name,url,taskId,mc)
            
def isSunday(dt):
    if dt.weekday() ==6:
        return True
    else:
        return False
def downloadFromEmail(path,taskId,mc,isSunday,proxys):
    
    if isSunday:
        orderQldDCDB()
    orderQldSCDB()
    time.sleep(60*5)
    
    downloaddata(path,taskId,mc,isSunday,proxys)
def downloadAllData():
    
    mc=MonitorClient()
    access_token='sk.eyJ1IjoiYmVuY2htcmsiLCJhIjoiY2piNmtzY2ZhM20ydjJxbzF4d2M0ZHZoMSJ9.gy69hvwbwSEIyP57Hg_Gsw'
    dt=datetime.datetime.now()
    bisSunday= isSunday(dt)
    dirpath =dt.strftime('%Y-%m-%d-%H-%M-%S')
    os.mkdir('./'+dirpath)
   
    currentPath=os.path.dirname(os.path.abspath("__file__"))
    path = currentPath+"/"+dirpath
    taskid= mc.createTask(dirpath,"start")
    pfile = open('pathfile.txt','w') 
    pfile.write(path) 
    pfile.close() 
    proxys=genProxys()
    #exportSA_scdb(path,proxys,None,access_token,taskid,mc)
    #exportWA(path,proxys,None,access_token,taskid,mc)
    #exportNSW(path,proxys,None,access_token,taskid,mc)
    #exportNSW_scdb(path,proxys,None,access_token,taskid,mc)
    #exportNT(path,proxys,access_token,taskid,mc)

    #exportNT_scdb_qgis(path,proxys,access_token,taskid,mc)
    #exportNT_dcdb_qgis(path,proxys,access_token,taskid,mc)
    #path="/mnt/volume-sgp1-02/crawl/2019-01-21-15-00-00/VIC_dcdb/SDM560356.zip"
    #filePath="/mnt/volume-sgp1-02/crawl/2019-01-21-15-00-00/VIC_dcdb"
    #downloadFromEmail(path,taskid,mc,True,proxys)
    #downloaddata(path,taskid,mc,True,proxys)
    #logger = logging.getLogger('downloadVICData') 
    #VICDscbToMbTiles(logger,path,filePath,"VIC_dcdb",taskid,mc)
    #exportACT_scdb(path,proxys,"-X",access_token,taskid,mc)
    #bisSunday=True

    #path='/Users/gis/Documents/project/featureservice2shp/2018-04-24-22-08-59/VIC_scdb'
    #exportVIC_scdb(path,access_token,taskid,mc)
    
    #exportVIC_scdb(path,access_token,taskid,mc)
    #exportWA_scdb(path,proxys,None,access_token,taskid,mc)
    #exportWA(path,proxys,None,access_token,taskid,mc)
    
    result = []
    p = Pool(processes=8)
    #bisSunday=True
    result.append(p.apply_async(exportTAS_scdb, args = (path,proxys,None,access_token,taskid,mc)))
    result.append(p.apply_async(exportNSW_scdb, args = (path,proxys,None,access_token,taskid,mc)))
    result.append(p.apply_async(exportACT_scdb, args = (path,proxys,None,access_token,taskid,mc)))
    result.append(p.apply_async(exportSA_scdb, args = (path,proxys,None,access_token,taskid,mc)))
    result.append(p.apply_async(exportWA_scdb, args = (path,proxys,None,access_token,taskid,mc)))
    result.append(p.apply_async(downloadFromEmail, args = (path,taskid,mc,True,proxys)))
    
    result.append(p.apply_async(exportNT_scdb_qgis, args = (path,proxys,access_token,taskid,mc)))
    
    #result.append(p.apply_async(exportVIC_scdb, args = (path,access_token,taskid,mc)))
    if bisSunday:
        result.append(p.apply_async(exportNSW,  args = (path,proxys,"-X",access_token,taskid,mc)))
        result.append(p.apply_async(exportACT, args = (path,proxys,"-X",access_token,taskid,mc)))
        result.append(p.apply_async(exportTAS, args = (path,proxys,"-X",access_token,taskid,mc)))
        result.append(p.apply_async(exportSA, args = (path,proxys,"-X",access_token,taskid,mc)))
        result.append(p.apply_async(exportWA, args = (path,proxys,"-X",access_token,taskid,mc)))
        result.append(p.apply_async(exportNT_dcdb_qgis, args = (path,proxys,access_token,taskid,mc)))
    
    p.close()
    p.join()
    p=None
    exportVIC_scdb(path,access_token,taskid,mc)
    
    clear(path)
    
    mc.updateTaskStatus(taskid,"finished")
    

if __name__ == '__main__':
    
    logger = logging.getLogger('apscheduler.executors.default')  
    logging.basicConfig()
    logger.setLevel(logging.INFO)  
  
    # 创建一个handler，用于写入日志文件  
    fh = logging.FileHandler('task.log')  
    print fh
    fh.setLevel(logging.INFO)  
  
    # 再创建一个handler，用于输出到控制台  
    ch = logging.StreamHandler()  
    ch.setLevel(logging.INFO)  
  
    # 定义handler的输出格式  
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    ch.setFormatter(formatter)  
  
    # 给logger添加handler  
    logger.addHandler(fh)  
    logger.addHandler(ch)  
  
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    
    
    
    scheduler = BlockingScheduler()
    scheduler.add_job(downloadAllData, 'cron', day='1-31', hour=15, minute=0)
    #scheduler.add_job(downloadAllData, 'cron', day='1-31', hour=13, minute=5)
    try:
        scheduler.start()  #采用的是阻塞的方式，只有一个线程专职做调度的任务
    except (KeyboardInterrupt, SystemExit):
    # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()
        print('Exit The Job!')
    
    #downloadAllData()
    
    '''
    #name="WA_dcdb"
    rootdir="/mnt/volume-sgp1-02/crawl/2018-10-08-02-59-59"+"/"+name
    addUUIDField(rootdir+'/'+name+'.geojson')
    addUUIDFieldForSqlite("/Users/gis/Downloads/TAS_scdb.sqlite")
    '''
    
    #addUUIDField('/Users/gis/Downloads/VIC_scdb.geojson')
    #addUUIDFieldForSqlite('/Users/gis/Downloads/NSW_scdb.sqlite')
    #addUUIDField('/Users/gis/Documents/AU/benchmrk-national-gis/featureservice2shp/2018-12-19-12-09-50/QLD_scdb/QLD_scdb/QLD_scdb.geojson')
    #addUUIDField('/Users/gis/Documents/AU/benchmrk-national-gis/featureservice2shp/2018-12-19-12-09-50/QLD_scdb/QLD_scdb/QLD_scdb.geojson')
  
    
    
    
    


