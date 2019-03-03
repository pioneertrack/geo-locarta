#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import commands
import psycopg2
import logging  
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
def updateTableName(cur,state,tableName):
    sql ="INSERT INTO current(state_name,tbl_name)  VALUES ('"+state+"','"+tableName+"') ON CONFLICT (state_name) DO UPDATE SET tbl_name = '"+tableName+"';"
    print sql
    cur.execute(sql)
def createIndex(cur,state,tableName):
    sql =''
    if state =="vic_dcdb":
        sql = 'create index idx_'+state+' on '+state+'(pc_lotno,pc_planno);'
    elif  state =="qld_dcdb":
        sql = 'create index idx_'+state+' on '+state+'(lot,plan);'
    elif  state =="nsw_dcdb":
        sql = 'create index idx_'+state+' on '+state+'(lotnumber,plannumber);'
    elif  state =="nt_dcdb":
        sql = 'create index idx_'+state+' on '+state+'(survey_plan_number,parcel);'
    elif  state =="tas_dcdb":
        sql = 'create index idx_'+state+' on '+state+'(folio,volume);'
    elif  state =="act_dcdb":
        sql = 'create index idx_'+state+' on '+state+'(section_number,block_number,district_name,division_name);'
    print sql
    if sql != '':
        cur.execute(sql)
def cpnfigPG(pgstring):
    conn = psycopg2.connect(pgstring)
    cur = conn.cursor()
    cur.execute("select * from information_schema.tables where table_name=%s", ('current',))
    isExist=bool(cur.rowcount)
    print isExist
    if not isExist:
        sql = "create table current (state_name VARCHAR(255) unique,tbl_name  VARCHAR(255))"
        cur.execute(sql)
    cur.close()
    conn.commit()
def importSCDBData(pgstring):
    conn = psycopg2.connect(pgstring)
    cur = conn.cursor()
    cmd = 'sshpass -p "qKwGMY9458jzTy5D" scp root@159.89.200.216:/mnt/volume-sgp1-02/crawl/pathfile.txt pathfile.txt' 
    print cmd
    print commands.getstatusoutput(cmd)
    f = open('pathfile.txt','r')
    filePath = f.read()
    #filePath='2018-03-10-13-00-00'
    print(filePath)
    f.close()
    filePath='/mnt/volume-sgp1-02/crawl/2019-02-14-07-24-36'
    '''
    scdbs=[("nt","NT_scdb/NT_scdb.geojson")
    ,("vic","VIC_scdb/VIC_scdb.geojson")
    ,("act","ACT_scdb/ACT_scdb.sqlite"),("nsw","NSW_scdb/NSW_scdb.sqlite")
    ,("qld", "QLD_scdb/QLD_scdb/QLD_scdb.geojson")
    ,("sa", "SA_scdb/SurveyMarks_shp/SA_scdb.geojson")
    ,("tas", "TAS_scdb/TAS_scdb.sqlite")
    ,("wa","WA_scdb/WA_scdb.sqlite")
    ,("nt_dcdb","NT_dcdb/NT_dcdb.geojson")
    ,("act_dcdb","ACT_dcdb/ACT_dcdb.sqlite")
    ,("nsw_dcdb","NSW_dcdb/NSW_dcdb.sqlite")
    ,("qld_dcdb","QLD_dcdb/DP_QLD_DCDB_WOS_CUR/QLD_dcdb.geojson")
    ,("vic_dcdb","VIC_dcdb/VIC_dcdb.geojson")
    ,("tas_dcdb","TAS_dcdb/TAS_dcdb.sqlite")]
    '''
    
    scdbs=[
    ("wa","WA_scdb/WA_scdb.sqlite")
    ]
    
    localPath=filePath.split('/')[-1].strip()
    localName=localPath.replace("-","")
    print localName
    if not os.path.exists(localPath):
        os.mkdir(localPath)

    for scdb in scdbs:
        ds = scdb[1]
        state=scdb[0]
        npath="./"+localPath+"/"+ds
        cpath='/'.join(npath.split('/')[0:-1])
        if not os.path.exists(cpath):
            os.makedirs(cpath)
        cpcmd = 'sshpass -p "qKwGMY9458jzTy5D" scp root@159.89.200.216:'+ filePath+"/"+ds +" "+localPath+"/"+ds
        print cpcmd
        commands.getstatusoutput(cpcmd)
        if os.path.exists(npath):
            if state =="sa" or state =="vic" or state =="nt"  or state =="nt_dcdb":
                impcmd='ogr2ogr -f "PostgreSQL" PG:"'+pgstring+'"   -s_srs EPSG:4326 -t_srs EPSG:3857 -nln '+scdb[0]+localName+' '+localPath+"/"+ds
            else:
                impcmd='ogr2ogr -f "PostgreSQL" PG:"'+pgstring+'"   -nln '+scdb[0]+localName+' '+localPath+"/"+ds
            print impcmd
            print commands.getstatusoutput(impcmd)
            createIndex(cur,state,scdb[0]+localName)
            updateTableName(cur,state,scdb[0]+localName)
            # delete the file
            os.remove( npath ) 
        else:
            print "no file"
    cur.close()
    conn.commit()
def importData():
    pgstring='host=localhost port=5432  user=scdbuser  password=scdbuser1234 dbname=postgis_scdb'
    #pgstring='host=localhost port=5432   dbname=postgis_scdb'
    cpnfigPG(pgstring)
    importSCDBData(pgstring)      
if __name__ == '__main__':
    '''
    scheduler = BlockingScheduler()
    scheduler.add_job(importData, 'cron', day='1-31', hour=9, minute=0)
    #scheduler.add_job(downloadAllData, 'cron', day='1-31', hour=13, minute=5)
    logger = logging.getLogger('apscheduler.executors.default')  
    logger.setLevel(logging.DEBUG)  
  
    # 创建一个handler，用于写入日志文件  
    fh = logging.FileHandler('task.log')  
    fh.setLevel(logging.DEBUG)  
  
    # 再创建一个handler，用于输出到控制台  
    ch = logging.StreamHandler()  
    ch.setLevel(logging.DEBUG)  
  
    # 定义handler的输出格式  
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    ch.setFormatter(formatter)  
  
    # 给logger添加handler  
    logger.addHandler(fh)  
    logger.addHandler(ch)  

    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        scheduler.start()  #采用的是阻塞的方式，只有一个线程专职做调度的任务
    except (KeyboardInterrupt, SystemExit):
    # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()
        print('Exit The Job!')
    '''
    importData()

