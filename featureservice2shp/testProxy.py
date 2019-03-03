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
import StringIO
import pycurl
def testProxy(porxy):
    try:
        httpProxy=porxy
        proxy = urllib2.ProxyHandler({'http': httpProxy})
        opener = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)
        myRequest="https://www.google.com"
        response = urllib2.urlopen(myRequest,timeout = 2)
        print response.code
        if response.code ==200:
            return True
        else:
            return False
    except:
        return False
def testProxyWithAuth(porxy):
    try:
        np=porxy.split(":")
        strP="http://"+np[2]+":"+np[3]+"@"+np[0]+":"+np[1]
        httpProxy=strP
        print strP
        proxy = urllib2.ProxyHandler({'http': httpProxy})
        opener = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)
        myRequest="http://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Survey_Mark/MapServer/0"
        response = urllib2.urlopen(myRequest,timeout = 20)
        print response.code
        if response.code ==200:
            return True
        else:
            return False
    except:
        return False
def testProxyWithAuthCurl(porxy):
    myRequest="http://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Cadastre/MapServer/9/query"
    f = StringIO.StringIO() 
    curl=pycurl.Curl()
    curl.setopt(curl.URL, myRequest)
    curl.setopt(pycurl.WRITEFUNCTION, f.write)    
    if myRequest.find("https://")>=0:
        curl.setopt(pycurl.SSL_VERIFYPEER, 0)  
        curl.setopt(pycurl.SSL_VERIFYHOST, 0) 
    pproxys =porxy.split(":")
    print pproxys
        #curl.setopt(pycurl.PROXY, pproxys[0])
        #curl.setopt(pycurl.PROXYPORT, int(pproxys[1]))
    ip='http://'+pproxys[0]+":"+pproxys[1]
    curl.setopt(pycurl.PROXY, ip)
    usrpwd=pproxys[2]+":"+pproxys[3]
    print usrpwd
    curl.setopt(pycurl.PROXYUSERPWD, usrpwd)
    curl.setopt(pycurl.TIMEOUT, 90) 
    curl.perform()   
    curl.close()
    myJSON= f.getvalue()   
    print myJSON

if __name__ == '__main__':
    testProxyWithAuthCurl('107.160.254.148:80:bmrkadmin:zq2fatu9qlfp')
    '''
    proxyCmd='proxy-lists getProxies --output-file="proxy_src"'
    print proxyCmd
    print commands.getstatusoutput(proxyCmd)
    fobj = codecs.open("proxy_src.txt", "r", "utf-8")
    fwobj = codecs.open("proxy.txt", "w", "utf-8")
    lines = fobj.readlines()
    i=0
    for line in lines: 
        if i>500:
            break
        proxy=line.strip()
        if testProxy(proxy):
            print proxy
            fwobj.write(proxy+"\n")
            fwobj.flush()
        else:
            print "proxy error"
        i=i+1
    fwobj.close()
    fobj.close()
    #proxy-lists getProxies --output-file="proxy_src.txt"
    '''