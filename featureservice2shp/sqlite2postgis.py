#!/usr/bin/env python
# -*- coding: utf-8 -*-
ogr2ogr -f "PostgreSQL" PG:"host=localhost port=5432 user=scdbuser password=scdb1234 dbname=postgis_scdb"  -nln ACT_scdb ACT_scdb.sqlite 

create database postgis_scdb with  owner= scdbUser TABLESPACE= tablespace_scdb;
scdbUser@1234
