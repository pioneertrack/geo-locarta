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
from urlparse import urlparse
from threading import Thread
import httplib
import commands
from Queue import Queue
class fs2sqlite:
    concurrent=0
    q=None
    def __init__(self, concurrent):
        print concurrent
        self.concurrent=concurrent
        self.q = Queue(concurrent * 2)
    def requireIds(self,url):
        myRequest=url+"/query?where=1%3D1&returnIdsOnly=true&f=json"
        #print myRequest
        response = urllib2.urlopen(myRequest)
        myJSON = response.read()
        jobj=json.loads(myJSON)
        return jobj["objectIds"]
    def makeUrl(self,url,ids,type):
        strids = ','.join(map(str, ids))
        myRequest=url+"/query?returnGeometry=true&returnIdsOnly=false&outFields=*&f="+type+"&objectIds="+strids
        return myRequest
    def makeUrls(self,url,oids,jsonpath):
        size=len(oids)
        persize =1000
        urls=[]
        max=int(math.ceil(size/ persize)) +1
        for i in range(max):
            of=jsonpath+"/"+str(i)+"_out.json"
            ids = []
            if (i + 1) * persize < size:
                ids = oids[i * persize:(i * persize) + persize]
            else:
                ids = oids[i * persize:size]
            singleUrl = self.makeUrl(url,ids,"json")
            urls.append([singleUrl,of])
        return urls

    def saveResult(self,response,of):
        fwobj = codecs.open(of, "w", "utf-8")
        fwobj.write(json.dumps(response))
        fwobj.close()
    def fetchData(self,ourl):
        try:
            response = urllib2.urlopen(ourl)
            myJSON = response.read()
            jobj=json.loads(myJSON)
            return jobj
        except:
            return "error"
    def doWork(self):
        while True:
            url = self.q.get()
            
            response = self.fetchData(url[0])
            self.saveResult(response, url[1])
            self.q.task_done()
    def exportJSON(self,url,dirpath,name):
        jsonpath=dirpath+"/"+name
        os.mkdir(jsonpath)
        oids= self.requireIds(url)
        urls=self.makeUrls(url,oids,jsonpath)
        for i in range(self.concurrent):
            t = Thread(target=self.doWork)
            t.daemon = True
            t.start()
        try:
            for rurl in urls:
                self.q.put(rurl)
            self.q.join()   
            self.exportFromFile(jsonpath,name)
        except KeyboardInterrupt:
            sys.exit(1)
    def exportFromFile(self,rootdir,name):
        dirs = os.listdir(rootdir)
        for i in range(0,len(dirs)):
            path = os.path.join(rootdir,dirs[i])
            if os.path.isfile(path):
                filename= os.path.split(path)[1]
                #print filename
                if filename.find("out.json") >0:
                    cmd = 'ogr2ogr -f "SQLite" "'+rootdir+'/'+name+'.sqlite" '+path+' -append' 
                    print cmd 
                    commands.getstatusoutput(cmd)
def exportFromFile(rootdir,name):
        dirs = os.listdir(rootdir)
        for i in range(0,len(dirs)):
            path = os.path.join(rootdir,dirs[i])
            if os.path.isfile(path):
                filename= os.path.split(path)[1]
                #print filename
                if filename.find("out.json") >0:
                    cmd = 'ogr2ogr -f "SQLite" "'+rootdir+'/'+name+'.sqlite" '+path+' -append' 
                    print cmd 
                    commands.getstatusoutput(cmd)    
if __name__ == '__main__':
    ticks = time.time()
    print ticks
    url ='http://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Cadastre/MapServer/9/query'
    dirpath =datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    os.mkdir('./'+dirpath)
    currentPath=os.path.dirname(os.path.abspath("__file__"))
    path = currentPath+"/"+dirpath
    print path
    name='NSW_Cadastre'
    f2sql=fs2sqlite(1)
    f2sql.exportJSON(url,path,name)

    url ='https://gisservices.information.qld.gov.au/arcgis/rest/services/PlanningCadastre/LandParcelPropertyFramework/MapServer/4/query'
    name='Cadastral_Parcels'
    f2sql2=fs2sqlite(1)
    f2sql2.exportJSON(url,path,name)

    url ='http://data.actmapi.act.gov.au/arcgis/rest/services/data_extract/Land_Administration/MapServer/4/query'
    name='ACT_Blocks'
    f2sql3=fs2sqlite(1)
    f2sql3.exportJSON(url,path,name)

    url ='http://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreParcels/MapServer/0/query'
    name='Cadastral_Parcels_2'
    f2sql4=fs2sqlite(1)
    f2sql4.exportJSON(url,path,name)

    url ='https://services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/Property_and_Planning/MapServer/2/query'
    name='Cadastre'
    f2sql5=fs2sqlite(1)
    f2sql5.exportJSON(url,path,name)


    url="http://location.sa.gov.au/arcgis/rest/services/DEWNRext/MapTheme_StreetBasemap/MapServer/1/query"
    name='ParcelCadastreCombined'
    f2sql6=fs2sqlite(1)
    f2sql6.exportJSON(url,path,name)
  
    end  = time.time()
    print end
    print (end-ticks)

