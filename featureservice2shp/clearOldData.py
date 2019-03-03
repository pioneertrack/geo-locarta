#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
def deleteAllOutJson(path):
    for root, dirs, files in os.walk(path):
        for name in files:
            if(name.endswith("_out.json")):
                print os.path.join(root, name)
                os.remove(os.path.join(root, name))
def deleteAllMBtiles(path):
    for root, dirs, files in os.walk(path):
        for name in files:
            if(name.endswith(".mbtiles")):
                print os.path.join(root, name)
                os.remove(os.path.join(root, name))
def isKeep(fileName):

    keeps=["NT_scdb.geojson","NT_dcdb.geojson","vic_scdb.geojson","ntlis_CADASTRE_PROPOSED","ntlis_CADASTRE_PROPOSED_SATOVERLAY.geojson","ntlis_CADASTRE_SATOVERLAY.geojson","ntlis_CADASTRE.geojson","ntlis_CADASTRE_OVERLAY_GREY.geojson"]
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
if __name__ == '__main__':
    print "start"
    #deleteAllOutJson("/mnt/volume-sgp1-02/crawl")
    deleteGeoJson("/mnt/volume-sgp1-02/crawl")
    deleteVicScdbFiles("/mnt/volume-sgp1-02/crawl")
    deleteAllMBtiles("/mnt/volume-sgp1-02/crawl")