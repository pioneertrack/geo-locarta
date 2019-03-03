#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import sleep
from random import randint
from mapbox import Uploader
def upload(ufile,mapid,access_token):
    print ufile
    service = Uploader(access_token=access_token)
    with open(ufile, 'rb') as src:
       
        upload_resp = service.upload(src, mapid)
        print upload_resp.status_code

if __name__ == '__main__':
    #access_token='sk.eyJ1IjoiYmVuY2htcmsiLCJhIjoiY2piNmtzY2ZhM20ydjJxbzF4d2M0ZHZoMSJ9.gy69hvwbwSEIyP57Hg_Gsw'
    #ufile='/root/crawl/data/20171209/vic_16_x.mbtiles'
    access_token='sk.eyJ1IjoiamFja3poYW5nZ2lzZXIiLCJhIjoiY2piNzllbGdmMTJ2bjJxbXp1ajFkMXRmcSJ9.o_jaIBSLHiKMt7-QP4AGow'
    ufile='/mnt/volume-sgp1-02/crawl/2018-01-04-01-11-56/TAS_scdb/TAS_scdb.mbtiles'
    #upload(ufile,'TAS_scdb',access_token)
    ufile='/mnt/volume-sgp1-02/crawl/2018-01-04-01-11-56/TAS/TAS.mbtiles'
    #upload(ufile,'TAS',access_token)

    ufile='/mnt/volume-sgp1-02/crawl/2018-01-04-01-11-56/ACT_scdb/ACT_scdb.mbtiles'
    #upload(ufile,'ACT_scdb',access_token)
    ufile='/mnt/volume-sgp1-02/crawl/2018-01-04-01-11-56/ACT/ACT.mbtiles'
    #upload(ufile,'ACT',access_token)


    ufile='/mnt/volume-sgp1-02/crawl/2018-01-18-03-10-53/WA_scdb/WA_scdb.mbtiles'
    upload(ufile,'WA_scdb',access_token)
    ufile='/mnt/volume-sgp1-02/crawl/2018-01-04-01-11-56/WA/WA.mbtiles'
    #upload(ufile,'WA',access_token)

    ufile='/mnt/volume-sgp1-02/crawl/2018-01-04-01-11-56/NSW_scdb/NSW_scdb.mbtiles'
    #upload(ufile,'NSW_scdb',access_token)

    ufile='/mnt/volume-sgp1-02/crawl/2018-01-04-01-11-56/SA_scdb/SurveyMarks_shp/SurveyMarks.mbtiles'
    #upload(ufile,'SurveyMarks',access_token)

    ufile='/mnt/volume-sgp1-02/crawl/2018-01-04-01-11-56/SA_scdb/SurveyMarks_shp/SurveyMarks.mbtiles'
    #upload(ufile,'SurveyMarks',access_token)

    ufile='/mnt/volume-sgp1-02/crawl/2018-01-04-01-11-56/SA/SA.mbtiles'
    #upload(ufile,'SA',access_token)
    