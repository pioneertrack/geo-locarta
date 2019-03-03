#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import codecs
import json
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
import requests
from urllib import urlencode

def requireIds(url):
    myRequest=url+"/query?where=1%3D1&returnIdsOnly=true&f=json"
    print myRequest
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
    if jobj.has_key("error"):
        return None
    return jobj["objectIds"]
def makeUrl(url,query,type):
    myRequest=url+"/query?returnGeometry=true&returnIdsOnly=false&outSR=3857&outFields=*&f="+type+"&where="+query
    return myRequest
def makeUrls(url,maxcount,size,jsonpath,persize):   
    urls=[]
    max=int(math.ceil(maxcount/ size)) +1
    for i in range(max):
        of=jsonpath+"/"+str(i)+"_out.json"
        query ="objectid < "+str((i+1)*size)+" and objectid >= "+str(i*size)
        singleUrl = makeUrl(url,query,"json")
        urls.append([singleUrl,of])
    return urls

def saveResult(response,of):
        fwobj = codecs.open(of, "w", "utf-8")
        fwobj.write(json.dumps(response))
        fwobj.close()
def fetchData(ourl,proxyIp):
    req = requests.get(ourl)
    result= req.json()
    return result
def downloadData(ourl,proxyIp):
    try:
        r = requests.get(ourl[0],stream=True)
        if r.status_code ==200  :
            open(ourl[1], 'wb').write(r.content)
            return "OK"
        return None
    except:
        return None
    
    return r.content  
'''
def fetchData(ourl,proxyIp):
    time.sleep(0.1)
    try:
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
        curl.perform()   
        curl.close()
        myJSON= f.getvalue()   
        print myJSON
        jobj=json.loads(myJSON)

        if len(jobj["features"])>0:
            return jobj
        else:
            return None 
        
    except Exception, e:
        print e
        return None
'''
def calOIDs(features):
    oids=[]
    for feature in features:
        oid = feature["attributes"]["OBJECTID"]
        oids.append(oid)
    return oids
def makeImageUrl(url,ids):
    strids = ','.join(map(str, ids))
    myRequest=url+"/"+"download?geometryType=esriGeometryEnvelope&f=json&rasterIds="+strids
    return myRequest
def makeImageUrls(url,oids,jsonpath,persize):
    size=len(oids)     
    urls=[]
    max=int(math.ceil(size/ persize)) +1
    for i in range(max):
        of=jsonpath+"/"+str(i)+"image_out.json"
        ids = []
        if (i + 1) * persize < size:
            ids = oids[i * persize:(i * persize) + persize]
        else:
            ids = oids[i * persize:size]
        singleUrl = makeImageUrl(url,ids)
        urls.append([singleUrl,of])
    return urls
def makeRasterUrl(url,rasterId,objId):
    url=url+"/file?rasterId="+str(objId)+"&id="+rasterId
    return url
def makeRasterUrls(url,rasterFiles,imagePath):
    urls=[]
    for rasterFile in rasterFiles:
        id = rasterFile["rasterIds"][0]
        rpath=imagePath+"/"+str(id)
        if not os.path.exists(rpath):
            os.mkdir(rpath)
        opath = rpath + "/"+rasterFile["id"].split("\\")[-1]
        downloadUrl = makeRasterUrl(url,rasterFile["id"],id)
        urls.append([downloadUrl,opath,rasterFile["size"]])
    return urls
def downloadAllIamges(alliImageUrls,proxys):
    errors=[]
    while True:
        for rurl in alliImageUrls: 
            l=len(proxys)
            index =random.randint(0, l-1)
            proxy = proxys[index]
           
            res= downloadData(rurl,proxy)
            if res==None:
                print "error"
                print rurl[0]
                errors.append(rurl)
                #proxys.remove(proxy)
           

        if len(errors) >0:
            urls=errors
            print "urls"
            errors = []
            print "sleep"
            print len(proxys)
            time.sleep(60*20) #wait 5 min   
        else:
            print "break"
            break  
def exportJSON(url,dirpath,name,proxys,presize=1000):
    print url
    #print mc
    jsonpath=dirpath+"/"+name
    os.mkdir(jsonpath)

    imagejsonpath=dirpath+"/"+name+"_image_json"
    os.mkdir(imagejsonpath)
    imagepath=dirpath+"/"+name+"_image"
    os.mkdir(imagepath)
    urls=makeUrls(url,1000000,500,jsonpath,presize)
    print len(urls)
    errors=[]
    conut=0
    oids=[]
    alliImageUrls=[]
    while True:
        for rurl in urls[0:3]: 
            l=len(proxys)
            index =random.randint(0, l-1)
            proxy = proxys[index]
            print proxy
            res= fetchData(rurl[0],proxy)
           
            if res==None:
                print "error"
                print rurl[0]
                errors.append(rurl)
                #proxys.remove(proxy)
            else:
                if len(res["features"])>0:
                    saveResult(res,rurl[1])
                    oids=calOIDs(res["features"])
                    imageUrls=makeImageUrls(url,oids,imagejsonpath,20)
                    alliImageUrls.extend(imageUrls)
        if len(errors) >0:
            urls=errors
            print "urls"
            errors = []
            print "sleep"
            print len(proxys)
            time.sleep(60*20) #wait 5 min   
        else:
            print "break"
            break           
    #exportFromFile(jsonpath,name)
    downloadAllIamgeJson(alliImageUrls,proxys,imagepath,url)
def downloadAllIamgeJson(alliImageUrls,proxys,imagepath,url):
    errors=[]
    urls=[]
    while True:
        for rurl in alliImageUrls[0:3]: 
            l=len(proxys)
            index =random.randint(0, l-1)
            proxy = proxys[index]
           
            res= fetchData(rurl[0],proxy)
           
            if res==None:
                print "error"
   
                errors.append(rurl)
                #proxys.remove(proxy)
            else:
                saveResult(res,rurl[1])
                rasterUrsl=makeRasterUrls(url,res["rasterFiles"],imagepath)
                urls.extend(rasterUrsl)
        if len(errors) >0:
            urls=errors
            print "urls"
            errors = []
            print "sleep"
            print len(proxys)
            time.sleep(60*20) #wait 5 min   
        else:
            print "break"
            break    
    downloadAllIamges(urls,proxys)       
def exportFromFile(rootdir,name):
    dirs = os.listdir(rootdir)
    for i in range(0,len(dirs)):
        path = os.path.join(rootdir,dirs[i])
        if os.path.isfile(path):
            filename= os.path.split(path)[1]
                #print filename
            if filename.find("out.json") >0:
                cmd = 'ogr2ogr -t_srs EPSG:3857 -s_srs EPSG:3857 -f  "sqlite" "'+rootdir+'/'+name+'.sqlite" '+path+' -append' 
                print cmd 
                commands.getstatusoutput(cmd)
    cmd = 'ogr2ogr -f "geojson" "'+rootdir+'/'+name+'.geojson" "'+rootdir+'/'+name+'.sqlite" '
    commands.getstatusoutput(cmd)

  
def exportQLDImage(path,proxys):
    url ='https://gisservices.information.qld.gov.au/arcgis/rest/services/Imagery/QldArchive_AerialPhotos/ImageServer'
    name='QlD'  
    exportJSON(url,path,name,proxys,500)
def download():
    dt=datetime.datetime.now()
    dirpath =dt.strftime('%Y-%m-%d-%H-%M-%S-images')
    os.mkdir('./'+dirpath)
    currentPath=os.path.dirname(os.path.abspath("__file__"))
    path = currentPath+"/"+dirpath
    
    proxys=[]
    fobj = codecs.open("proxy.txt", "r", "utf-8")
    lines = fobj.readlines()
    for line in lines: 
        proxy=line.strip()
        proxys.append(proxy)
    fobj.close()
    exportQLDImage(path,proxys)
if __name__ == '__main__':
    download()
    #url='https://gisservices.information.qld.gov.au/arcgis/rest/services/Imagery/QldArchive_AerialPhotos/ImageServer/query?returnGeometry=true&returnIdsOnly=false&outSR=3857&outFields=*&f=json&objectIds=592044,592045,592046,592047,592048,592049,592050,592051,592052,592053,592054,592055,592056,592057,592058,592059,592060,592061,592062,592069,592073,592075,592076,592077,592078,592079,592080,592081,592082,592083,592084,592085,592087,592088,592089,592090,592091,592092,592093,592094,592095,592096,592097,592098,592099,592100,592101,592102,592103,592104,592105,592106,592107,592108,592109,592110,592111,592112,592113,592114,592115,592116,592117,592118,592119,592120,592121,592122,592123,592124,592125,592126,592127,592128,592129,592130,592131,592132,592133,592134,592135,592136,592137,592138,592139,592140,592141,592142,592143,592144,592145,592146,592147,592148,592149,592150,592151,592152,592153,592154,592155,592156,592157,592158,592159,592160,592161,592162,592163,592164,592165,592166,592167,592168,592169,592170,592171,592172,592173,592174,592175,592176,592177,592178,592179,592180,592181,592182,592183,592184,592185,592186,592187,592188,592189,592190,592191,592192,592193,592194,592195,592196,592197,592198,592199,592200,592201,592202,592203,592204,592205,592206,592207,592208,592209,592215,592216,592217,592218,592219,592220,592221,592222,592223,592224,592225,592226,592227,592228,592229,592230,592231,592232,592233,592234,592235,592236,592237,592238,592239,592240,592241,592242,592243,592244,592245,592246,592247,592248,592249,592250,592251,592252,592253,592254,592255,592256,592257,592258,592259,592260,592261,592262,592263,592264,592265,592266,592267,592268,592269,592270,592271,592272,592273,592274,592275,592276,592277,592278,592279,592280,592281,592282,592283,592284,592285,592286,592287,592288,592289,592290,592291,592292,592293,592294,592295,592296,592297,592298,592299,592300,592301,592302,592303,592304,592305,592306,592307,592308,592309,592310,592311,592312,592313,592314,592315,592316,592317,592318,592319,592320,592321,592322,592323,592324,592325,592326,592327,592328,592329,592330,592331,592332,592333,592334,592335,592336,592337,592338,592339,592340,592341,592342,592343,592344,592345,592346,592347,592348,592349,592350,592351,592352,592353,592354,592355,592356,592357,592358,592359,592360,592361,592362,592363,592364,592365,592366,592367,592368,592369,592370,592371,592372,592373,592374,592375,592376,592377,592378,592379,592380,592381,592382,592383,592384,592385,592386,592387,592388,592389,592390,592391,592392,592393,592394,592395,592396,592397,592398,592399,592400,592401,592402,592403,592404,592405,592406,592407,592408,592409,592410,592411,592412,592413,592414,592415,592416,592417,592418,592419,592420,592421,592422,592423,592424,592425,592426,592427,592428,592429,592430,592431,592432,592433,592434,592435,592436,592437,592438,592439,592440,592441,592442,592443,592444,592445,592446,592447,592448,592449,592450,592451,592452,592453,592454,592455,592456,592457,592458,592459,592460,592461,592462,592463,592464,592465,592466,592467,592468,592469,592470,592471,592472,592473,592474,592475,592476,592477,592478,592479,592480,592481,592482,592483,592484,592485,592486,592487,592488,592489,592490,592491,592492,592493,592494,592495,592496,592497,592498,592499,592500,592501,592502,592503,592504,592505,592506,592507,592508,592509,592510,592511,592512,592513,592514,592515,592516,592517,592518,592519,592520,592521,592522,592523,592524,592525,592526,592527,592528,592529,592530,592531,592532,592533,592534,592535,592536,592537,592538,592539,592540,592541,592542,592543,592544,592545,592546,592547,592548,592549,592550,592551,592552,592553,592554,592555,592556,592557,592558,592559'
    #fetchData(url,"")