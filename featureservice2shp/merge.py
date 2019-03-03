#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import codecs
import json
import math
import urllib2
import time
import os
import commands
def exportFromFile(rootdir,name):
    dirs = os.listdir(rootdir)
    for i in range(0,len(dirs)):
        path = os.path.join(rootdir,dirs[i])
        if os.path.isfile(path):
            filename= os.path.split(path)[1]
                #print filename
            if filename.find("out.json") >0:
                cmd = 'ogr2ogr -f "sqlite" "'+rootdir+'/'+name+'.sqlite" '+path+' -append' 
                print cmd 
                commands.getstatusoutput(cmd)   
if __name__ == '__main__':
    exportFromFile('/root/crawl/2017-12-06-08-22-00/NSW_Cadastre',"NSW")