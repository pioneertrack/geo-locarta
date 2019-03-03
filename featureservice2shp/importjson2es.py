#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import requests
import codecs

def importJSONData(jsonFile,es):
    with open(jsonFile) as json_data:
        j = json.load(json_data)
        address_principals = j['address_principals']
        i=1
        for address in address_principals:
            print address
            putDataToES(address,es,i)
            i=i+1
def putDataToES(jdata,es,did):
    url =es+"/"+"gnaf/address_test/"+str(did)
    print url
    headers = {"Content-Type": "application/json"}
    req = requests.post(url, data = json.dumps(jdata),headers=headers)
    print req.json()


if __name__ == '__main__':
    jsonFile="/Users/gis/Desktop/address_principals_201803181042.json"
    es="http://localhost:9200"
    importJSONData(jsonFile,es)