#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import codecs
import json
import math
import urllib2
import time
import commands
import os
import pycurl
import StringIO
import urllib
import random
import ogr2ogr
from arcgis2geojson import arcgis2geojson
def trans(input,output):
    fwobj = codecs.open(output, "w", "utf-8")
    json_data =open(input)
    obj = json.load(json_data)
    output = arcgis2geojson(obj)
    fwobj.write(json.dumps(output))
    fwobj.close()
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
def requireIds(url):
    myRequest=url+"/query?where=1%3D1&returnIdsOnly=true&f=json&outSR=3857"
    f = StringIO.StringIO() 
    curl=pycurl.Curl()
    curl.setopt(curl.URL, myRequest)
    curl.setopt(pycurl.WRITEFUNCTION, f.write)  
    curl.setopt(pycurl.SSL_VERIFYPEER, 0)  
    curl.setopt(pycurl.SSL_VERIFYHOST, 0)   
    curl.perform()   
    curl.close()
    myJSON= f.getvalue()   
    jobj=json.loads(myJSON)
    '''
    response = urllib2.urlopen(myRequest)
    myJSON = response.read()
    jobj=json.loads(myJSON)
    '''
    print jobj
   #return jobj["objectIds"]
    return jobj["objectIds"]
def requireFSKMZ(url,ids,of):
    
    strids = ','.join(map(str, ids))
    minid=ids[0]
    maxid=ids[-1]
    where = "objectid >="+str(minid)+" AND objectid <="+str(maxid)
    f = { 'returnGeometry' : 'true', 'outFields' : '*', 'f' : 'kmz', 'outSR' : '4326', 'where' : where}
 
    
    myRequest=url+"/query?"+urllib.urlencode(f)
    print myRequest
    
    '''
    response = urllib2.urlopen(myRequest)
    myJSON = response.read()
    jobj=json.loads(myJSON)
    '''
   
    curl=pycurl.Curl()
    curl.setopt(curl.URL, myRequest)
    curl.setopt(pycurl.WRITEDATA, of)
    curl.setopt(pycurl.SSL_VERIFYPEER, 0)  
    curl.setopt(pycurl.SSL_VERIFYHOST, 0)   
    curl.perform()   
    curl.close()
def exportKMZ():
    url ='https://mrgis.mainroads.wa.gov.au/arcgis/rest/services/SurveyPortal2014/MapServer/9'
    oids= requireIds(url)
    size=len(oids)
    persize =300
    max=int(math.ceil(size/ persize)) +1
    fs={}
    for i in range(max):
        of="./"+str(i)+"_out.kmz"
        fp = open(of, "wb")
        ids = []
        if (i + 1) * persize < size:
            ids = oids[i * persize:(i * persize) + persize]
        else:
            ids = oids[i * persize:size]

        requireFSKMZ(url,ids,fp)
        fp.close()
def exportFeatures():
    url ='https://mrgis.mainroads.wa.gov.au/arcgis/rest/services/SurveyPortal2014/MapServer/8'
    oids= requireIds(url)
    size=len(oids)
    fs=[]
    of="./f_8_out.json"
    proxys=genProxys()

    fwobj = codecs.open(of, "w", "utf-8")
    for i in range(size):
        l=len(proxys)
        index =random.randint(0, l-1)
        proxy = proxys[index]
        jobj=requireFeature(url,oids[i],proxy)
        fs.append(jobj)
    fwobj.write(json.dumps(fs))
    fwobj.close()
def requireFeature(url,id,proxy):
    time.sleep(1)
    myRequest=url+"/"+str(id)+"?f=json"
    print myRequest
    f = StringIO.StringIO() 
    print proxy
   
    curl=pycurl.Curl()
    curl.setopt(curl.URL, myRequest)
    curl.setopt(pycurl.WRITEFUNCTION, f.write)  
    curl.setopt(pycurl.SSL_VERIFYPEER, 0)  
    curl.setopt(pycurl.SSL_VERIFYHOST, 0)   
    pproxys =proxy.split(":")
    ip='http://'+pproxys[0]+":"+pproxys[1]
   # curl.setopt(pycurl.PROXY, ip)
    usrpwd=pproxys[2]+":"+pproxys[3]
    #curl.setopt(pycurl.PROXYUSERPWD, usrpwd)
   
    curl.perform()   
    curl.close()
    myJSON= f.getvalue()   
    jobj=json.loads(myJSON)
    return jobj
def requireFS(url,ids,type):
    strids = ','.join(map(str, ids))
    myRequest=url+"/query?returnGeometry=true&returnIdsOnly=false&outFields=*&f="+type+"&objectIds="+strids
    print myRequest
    
    '''
    response = urllib2.urlopen(myRequest)
    myJSON = response.read()
    jobj=json.loads(myJSON)
    '''
    f = StringIO.StringIO() 
    curl=pycurl.Curl()
    curl.setopt(curl.URL, myRequest)
    curl.setopt(pycurl.WRITEFUNCTION, f.write)  
    curl.setopt(pycurl.SSL_VERIFYPEER, 0)  
    curl.setopt(pycurl.SSL_VERIFYHOST, 0)   
    curl.perform()   
    curl.close()
    myJSON= f.getvalue()   
    jobj=json.loads(myJSON)
    return jobj
def exportJSON(outpath,url):
    os.mkdir(outpath)
   
    oids= requireIds(url)
    size=len(oids)
    persize =100
    max=int(math.ceil(size/ persize)) +1
    fs={}
    for i in range(max):
        of=outpath+str(i)+"_out.geojson"
        fwobj = codecs.open(of, "w", "utf-8")
        ids = []
        if (i + 1) * persize < size:
            ids = oids[i * persize:(i * persize) + persize]
        else:
            ids = oids[i * persize:size]

        fs=requireFS(url,ids,"json")
        fwobj.write(json.dumps(fs))
        fwobj.close()

def export():
    url ='https://services.arcgis.com/H6Mh1bySxR4oHx6x/arcgis/rest/services/KC_Taxlots/FeatureServer/0'
    oids= requireIds(url)
    size=len(oids)
    of="./out.json"
    fwobj = codecs.open(of, "w", "utf-8")
    max=int(math.ceil(size/ 100)) +1
    fs={}
    for i in range(max):
        ids = []
        if (i + 1) * 100 < size:
            ids = oids[i * 100:(i * 100) + 100]
        else:
            ids = oids[i * 100:size]
        if i==0:
            fs=requireFS(url,ids,"geojson")
            print fs["features"]
        else:
            tempfs= requireFS(url,ids,"geojson")
            if tempfs.has_key("features"):
                #fs.features.extend(tempfs["features"])
                fs["features"].extend(tempfs["features"])
                
            else:
                print "---features---" 
    fwobj.write(json.dumps(fs))
    fwobj.close()
    print "---------"
    print size

def exportFromFile(rootdir,outName):
    dirs = os.listdir(rootdir)
    for i in range(0,len(dirs)):
        path = os.path.join(rootdir,dirs[i])
        if os.path.isfile(path):
            filename= os.path.split(path)[1]
            #print filename
            if filename.find("out.geojson") >0:
                cmd = 'ogr2ogr -f "SQLite" '+rootdir+ outName+ ' '+path+' -append' 
                print cmd
                commands.getstatusoutput(cmd)

if __name__ == '__main__':
    ticks = time.time()
    print ticks
    '''
    outpath ="./Contours/"
    url ='http://cityplan2014maps.brisbane.qld.gov.au/arcgis/rest/services/CityPlan/Contours/MapServer/0'
   # exportKMZ()
    outName="contours10.sqlite"
    exportJSON(outpath,url)
    exportFromFile(outpath,outName)
    '''
    outpath ="./Contours5m/"
    url ='http://cityplan2014maps.brisbane.qld.gov.au/arcgis/rest/services/CityPlan/Contours/MapServer/1'
   # exportKMZ()
    outName="Contours5m.sqlite"
    exportJSON(outpath,url)
    exportFromFile(outpath,outName)

    outpath ="./Contours1m/"
    url ='http://cityplan2014maps.brisbane.qld.gov.au/arcgis/rest/services/CityPlan/Contours/MapServer/2'
   # exportKMZ()
    outName="Contours1m.sqlite"
    exportJSON(outpath,url)
    exportFromFile(outpath,outName)

    outpath ="./Contourh1m/"
    url ='http://cityplan2014maps.brisbane.qld.gov.au/arcgis/rest/services/CityPlan/Contours/MapServer/3'
   # exportKMZ()
    outName="Contoursh1m.sqlite"
    exportJSON(outpath,url)
    exportFromFile(outpath,outName)


    #export()
    #ogr2ogr.main(["","-f", "ESRI Shapefile", "out.shp", "9.geojson"])
    #trans("9.geojson","90.geojson")
    end  = time.time()
    print end
    print (end-ticks)

