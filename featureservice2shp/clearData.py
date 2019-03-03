#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import commands
import psycopg2

def getAllTables(cur):
    sql = "select tablename from pg_tables where schemaname ='public';"
    cur.execute(sql)
    rows = cur.fetchall() 
    return rows
def getAllCurrentTables(cur):
    sql = "select tbl_name from current ;"
    cur.execute(sql)
    rows = cur.fetchall() 
    return rows

def isStateTable(tableName):
    states=["nt20","act20","vic20","qld20","sa20","tas20","wa20","nsw20","nt_dcdb","act_dcdb"]
    for state in states:
        if tableName.find(state)==0:
            return True
    return False
def isKeepTable(tableName,currentTables):
    for table in currentTables:
        if table[0] == tableName:
            return True
    return False
def dropTable(cur,tbname):
    print tbname
    sql = "drop table "+tbname+";"
    #cur.execute(sql)
    print sql
    
def clearOldData(pgstring):
    conn = psycopg2.connect(pgstring)
    cur = conn.cursor()
    
    allTables=getAllTables(cur)
    currentTables=getAllCurrentTables(cur)
    for row in allTables:
        tname= row[0]
        if isStateTable(tname) and not isKeepTable(tname,allTables):
            dropTable(cur,tname)
    conn.commit()
    cur.close()
    conn.close()

def clearData():
    pgstring='host=localhost port=5432  user=scdbuser  password=scdbuser1234 dbname=postgis_scdb'
    #pgstring='host=localhost port=5432   dbname=postgis_scdb'
    clearOldData(pgstring)
    
if __name__ == '__main__':
    clearData()

