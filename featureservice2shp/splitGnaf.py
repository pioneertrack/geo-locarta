#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import commands
import psycopg2
import re
import codecs
from psycopg2 import sql
def cpnfigPG(pgstring):
    conn = psycopg2.connect(pgstring)
    cur = conn.cursor()
    print cur
    cur.execute("select * from information_schema.tables where table_name=%s", ('address_principals_lot',))
    isExist=bool(cur.rowcount)
    print isExist
    if  not isExist:
        cur.execute("create  TABLE address_principals_lot AS (select * from \"public\".address_principals)")
        cur.execute("ALTER TABLE address_principals_lot ADD COLUMN plot varchar(50);")
        cur.execute("ALTER TABLE address_principals_lot ADD COLUMN plan varchar(50);")

    cur.close()
    conn.commit()
def importSA(pgstring):
    of="legal_sa.csv"
    fwobj = codecs.open(of, "w", "utf-8")
    conn = psycopg2.connect(pgstring)
    conn.set_session(readonly=False, autocommit=False)
    cur = conn.cursor()
    cur.execute("SELECT gid,legal_parcel_id from address_principals_lot where state ='SA'")
    rows = cur.fetchall()
    count=0
    sql_template = "UPDATE address_principals_plot SET (plot,plan)=(%s,%s)  where gid=%s"

    for row in rows:

        legalInfo=row[1]
        plan=''
        plot=''
        if legalInfo:
            items=legalInfo.split("/")
            if len(items)==2:
                plan=items[0]
                
                result=re.findall(r"\d+\.?\d*",items[1])
                if len(result)>0:
                    plot = result[0]
                    fwobj.write(str(row[0])+","+plot+","+plan+"\n")
               
    cur.close()
    conn.commit()
    fwobj.close()
def importNSW(pgstring):
    of="legal_nsw.csv"
    fwobj = codecs.open(of, "w", "utf-8")
    conn = psycopg2.connect(pgstring)
    conn.set_session(readonly=False, autocommit=False)
    cur = conn.cursor()
    cur.execute("SELECT gid,legal_parcel_id from address_principals_plot where state ='NSW'")
    rows = cur.fetchall()
    for row in rows:

        legalInfo=row[1]
        plan=''
        plot=''
        if legalInfo:
            items=legalInfo.split("/")
            if len(items)==3:
                plot=items[0]
                plan=items[2]
                fwobj.write(str(row[0])+","+plot+","+plan+"\n")
               
    cur.close()
    conn.commit()
    fwobj.close()
def importQLD(pgstring):
    of="legal_qld.csv"
    fwobj = codecs.open(of, "w", "utf-8")
    conn = psycopg2.connect(pgstring)
    conn.set_session(readonly=False, autocommit=False)
    cur = conn.cursor()
    cur.execute("SELECT gid,legal_parcel_id from address_principals_plot where state ='QLD'")
    rows = cur.fetchall()
    for row in rows:

        legalInfo=row[1]
        plan=''
        plot=''
        if legalInfo:
            items=legalInfo.split("/")
            if len(items)==2:
                plot=items[0]
                plan=items[1]
                fwobj.write(str(row[0])+","+plot+","+plan+"\n")
               
    cur.close()
    conn.commit()
def importVIC(pgstring):
    of="legal_vic.csv"
    fwobj = codecs.open(of, "w", "utf-8")
    conn = psycopg2.connect(pgstring)
    conn.set_session(readonly=False, autocommit=False)
    cur = conn.cursor()
    cur.execute("SELECT gid,legal_parcel_id from address_principals_plot where state ='VIC'")
    rows = cur.fetchall()
    for row in rows:

        legalInfo=row[1]
        plan=''
        plot=''
        if legalInfo:
            items=legalInfo.split("/")
            if len(items)==6:
                plot=items[0]
                plan=items[1].replace("~","")
                fwobj.write(str(row[0])+","+plot+","+plan+"\n")
               
    cur.close()
    conn.commit()  
def importWA(pgstring):
    of="legal_wa.csv"
    fwobj = codecs.open(of, "w", "utf-8")
    conn = psycopg2.connect(pgstring)
    conn.set_session(readonly=False, autocommit=False)
    cur = conn.cursor()
    cur.execute("SELECT gid,legal_parcel_id from address_principals_plot where state ='WA'")
    rows = cur.fetchall()
    for row in rows:

        legalInfo=row[1]
        plan=''
        plot=''
        if legalInfo:
            if legalInfo.find("/") >=0:
                items=legalInfo.split("/")
                if len(items)==2:
                    plot=items[0]
                    plan=items[1]
                    fwobj.write(str(row[0])+","+plot+","+plan+"\n")
            else:
                items=legalInfo.split()
                plot=items[1]
                plan=items[0]
                fwobj.write(str(row[0])+","+plot+","+plan+"\n")

               
    cur.close()
    conn.commit()  
def importNTDCDB(pgstring):
    of="legal_nt_dcdb.csv"
    fwobj = codecs.open(of, "w", "utf-8")
    conn = psycopg2.connect(pgstring)
    conn.set_session(readonly=False, autocommit=False)
    cur = conn.cursor()
    cur.execute("SELECT ogc_fid,survey_plan_number from nt_dcdb")
    rows = cur.fetchall()
    for row in rows:
        planNumber=row[1]
        if planNumber:
            planNumber=planNumber.replace(" ","")
            fwobj.write(str(row[0])+";"+planNumber+"\n")
               
    cur.close()
    conn.commit()
def importTAS(pgstring):
    of="legal_tas.csv"
    fwobj = codecs.open(of, "w", "utf-8")
    conn = psycopg2.connect(pgstring)
    conn.set_session(readonly=False, autocommit=False)
    cur = conn.cursor()
    cur.execute("SELECT gid,legal_parcel_id from address_principals_plot where state ='TAS'")
    rows = cur.fetchall()
    for row in rows:
        legalInfo=row[1]
        plan=''
        plot=''
        if legalInfo:
            items=legalInfo.split("/")
            if len(items)==2:
                plot=items[0]
                plan=items[1]
                fwobj.write(str(row[0])+","+plot+","+plan+"\n")
               
    cur.close()
    conn.commit()
if __name__ == '__main__':
    #pgstring='host=localhost port=5432  user=scdbuser  password=scdbuser1234 dbname=postgis_scdb'
    pgstring='host=localhost port=5432   dbname=postgis_scdb'
    #cpnfigPG(pgstring)
    #importSA(pgstring)
    #importNSW(pgstring)
    #importQLD(pgstring)
    #importVIC(pgstring)
    #importWA(pgstring)
    #importTAS(pgstring)
    importNTDCDB(pgstring)
