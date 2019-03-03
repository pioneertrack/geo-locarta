#!/usr/bin/env python
# -*- coding: utf-8 -*-
import getpass, poplib
import email
from email import parser
import os
import commands
import time
from datetime import datetime
import urllib2
from urllib import urlencode
from apscheduler.schedulers.background import BackgroundScheduler
from mapbox import Uploader
import pycurl
def orderQldSCDB():
    mail="data@bmrk.co"
    url ="https://gisservices2.information.qld.gov.au/arcgis/rest/services/QSC/ClipZipShip/GPServer/ClipZipShip/submitJob?"
    url=url+urlencode({'f':'json','env':'outSR=102100','Layers_to_Clip':'["Survey Control"]','Feature_Format':'Shapefile - SHP - .shp','Spatial_Reference':'3857','To_Email':mail,'Prepackaged_Data_URLs':'','Output_Title':'Extract'})
    print url
    response = urllib2.urlopen(url,timeout = 30)
    print response.code
def orderQldDCDB():  
    mail="data@bmrk.co" 
    url ="https://gisservices2.information.qld.gov.au/arcgis/rest/services/QSC/ClipZipShip/GPServer/ClipZipShip/submitJob?"

    url=url+urlencode({'f':'json','env':'outSR=102100','Layers_to_Clip':'[]','Feature_Format':'','Spatial_Reference':'','To_Email':mail,'Prepackaged_Data_URLs':'DP_QLD_DCDB_WOS_CUR.zip:undefined','Output_Title':'Extract'})
    print url
    response = urllib2.urlopen(url,timeout = 30)
    print response.code
def downloadVICData(filePath,url):
    if not os.path.exists("./vicData"):
        os.mkdir('./vicData')
    if not os.path.isfile(filePath):
        cmd ="curl -o "+filePath+' "'+url+'"'
        print cmd
        #commands.getstatusoutput(cmd)
        '''
        with open(filePath, 'wb') as f:
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.WRITEDATA, f)
            c.setopt(pycurl.SSL_VERIFYPEER, 0)  
            c.setopt(pycurl.SSL_VERIFYHOST, 0) 
        #c.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_1_0) 
            c.perform()
            c.close()
        '''
    path = filePath.replace(".zip","")
    unzipcmd="unzip "+filePath +' -d '+path
    print unzipcmd
    print commands.getstatusoutput(unzipcmd)
    for fpath,dirs,fs in os.walk(path):
        for f in fs:
            shpPath=os.path.join(fpath, f)
            geojsonPath=shpPath.replace("shp","geojson")
            mbtilesPath=shpPath.replace("shp","mbtiles")
            if os.path.isfile(shpPath) and f.find("shp")>=0:
                geojsonCmd='ogr2ogr -f "GeoJSON" -t_srs EPSG:3857 '+geojsonPath+' '+shpPath
                print geojsonCmd
                print commands.getstatusoutput(geojsonCmd)
                tippecanoeCmd='tippecanoe -z16  -o '+mbtilesPath+'  -ap -as -X  -r -B -ad  -s EPSG:3857  -f '+geojsonPath
                print tippecanoeCmd
                print commands.getstatusoutput(tippecanoeCmd)
                mapid = f.replace(".shp","")
                access_token='sk.eyJ1IjoiYmVuY2htcmsiLCJhIjoiY2piNmtzY2ZhM20ydjJxbzF4d2M0ZHZoMSJ9.gy69hvwbwSEIyP57Hg_Gsw'
                upload(mbtilesPath,mapid,access_token)

def downloadQldSCDBdata(filePath,url):
    if not os.path.exists("./qldSCDBData"):
        os.mkdir('./qldSCDBData')
    if not os.path.isfile(filePath):
        cmd ="curl -o "+filePath+' "'+url+'"'
        print cmd
        commands.getstatusoutput(cmd)
        path = filePath.replace(".zip","")
        unzipcmd="unzip "+filePath +' -d ./qldSCDBData/'
        print unzipcmd
        print commands.getstatusoutput(unzipcmd)
            
        shpPath= path
        geojsonCmd='ogr2ogr -f "GeoJSON" -t_srs EPSG:3857 '+shpPath+'/Survey_Control.geojson '+shpPath+'/Survey_Control.shp'
        print geojsonCmd
        print commands.getstatusoutput(geojsonCmd)
        tippecanoeCmd='tippecanoe -z16  -o '+shpPath+'/Survey_Control.mbtiles -ap -as -X  -r -B -ad  -s EPSG:3857  -f '+shpPath+'/Survey_Control.geojson'
        print tippecanoeCmd
        print commands.getstatusoutput(tippecanoeCmd)
        access_token='sk.eyJ1IjoiYmVuY2htcmsiLCJhIjoiY2piNmtzY2ZhM20ydjJxbzF4d2M0ZHZoMSJ9.gy69hvwbwSEIyP57Hg_Gsw'
        upload(shpPath+'/Survey_Control.mbtiles','Survey_Control',access_token)
def downloadQldDCDBdata(filePath,url):
    if not os.path.exists("./qldDCDBData"):
        os.mkdir('./qldDCDBData')
    if not os.path.isfile(filePath):
        cmd ="curl -o "+filePath+' "'+url+'"'
        print cmd
        commands.getstatusoutput(cmd)
        path = filePath.replace(".zip","")
        unzipcmd="unzip "+filePath +' -d '+path
        print unzipcmd
        print commands.getstatusoutput(unzipcmd)
    #path = filePath.replace(".zip","")
        layers=["QLD_CADASTRE_DCDB","QLD_CADASTRE_NATBDY","QLD_CADASTRE_ROAD","QLD_CADASTRE_BUP_LOT"]
        for layer in layers:

            geojsonCmd='ogr2ogr -f "GeoJSON" '+path+'/'+layer+'.geojson -t_srs EPSG:3857 '+path+'/DP_QLD_DCDB_WOS_CUR.gdb '+' "'+layer+'"'
            print geojsonCmd
            print commands.getstatusoutput(geojsonCmd)
            tippecanoeCmd='tippecanoe -z16  -o '+path+'/'+layer+'.mbtiles '+' -ap -as -X  -r -B -ad  -s EPSG:3857  -f '+path+'/'+layer+'.geojson '
            print tippecanoeCmd
            print commands.getstatusoutput(tippecanoeCmd)
            access_token='sk.eyJ1IjoiYmVuY2htcmsiLCJhIjoiY2piNmtzY2ZhM20ydjJxbzF4d2M0ZHZoMSJ9.gy69hvwbwSEIyP57Hg_Gsw'
            upload(path+'/'+layer+'.mbtiles',layer,access_token)
def downloaddata():
    server= poplib.POP3('simplemail.pop.co')
    server.user("data@bmrk.co")
    server.pass_('x9G-eMG-BB7-8Qb')
    print server.stat()
    numMessages = len(server.list()[1])
    
    data =[]
    for i in range(numMessages):
        data.append(server.retr(numMessages-i))
    server.quit()

    for (server_msg, body, octets) in data:
        isFindQldSCDB=False
        isFindQldDCDB=False
        isFindVIC=False
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
            filePath= "./qldSCDBData/"+url.split("/")[-1]
            print filePath
            downloadQldSCDBdata(filePath,url)
        qIndex2= result.find("http://qldspatial.information.qld.gov.au/DownloadService/Download.aspx")
        if  qIndex2>=0 and not isFindQldDCDB:
            isFindQldDCDB=True
            name="DP_QLD_DCDB_WOS_CUR.zip"
            
            
            right = result.find(">",qIndex2)
            url = result[qIndex2:right]
            print url
            filePath= "./qldDCDBData/"+name
            print filePath
            downloadQldDCDBdata(filePath,url)
            

        index3=result.find("http://services.land.vic.gov.au/SpatialDatamart/publicAccessOrderDownload.html")
        if index3 >=0 and not isFindVIC:
            isFindVIC=True
            index=result.find("URL :",0)
            right = result.find(">",index3)
            url = result[index3:right-1]
            print url
            filePath= "./vicData/"+url.split("&")[0].split("=")[-1]
            print filePath
            downloadVICData(filePath,url)
        
            
    
def upload(ufile,mapid,access_token):

    service = Uploader(access_token=access_token)
    with open(ufile, 'rb') as src:
        upload_resp = service.upload(src, mapid)
        print upload_resp.status_code


if __name__ == '__main__':
    '''
    scheduler = BackgroundScheduler()
    sched.add_job(orderQldSCDB, 'cron', day_of_week='sun', hour=22, minute=00)
    sched.add_job(orderQldDCDB, 'cron', day='1-31', hour=22, minute=00)
    sched.add_job(downloaddata, 'cron', day='1-31', hour=23, minute=30)
    scheduler.start()    
    '''
    #orderQldSCDB()
    #orderQldDCDB()
    downloaddata()
    
