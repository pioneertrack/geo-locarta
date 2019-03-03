"use strict";
/* Load modules */
let sqlite3 = require('sqlite3').verbose();

/*
 * Database configuration
 */

/* Load database file (Creates file if not exists) */
let db = new sqlite3.Database('./crawlmonitor.db');

/* Init car and driver tables if they don't exist */
let init = function () {
    
    db.run("CREATE TABLE if not exists task (" +
        "id INTEGER PRIMARY KEY AUTOINCREMENT," +
        " name TEXT," +
        " status TEXT," +
        " startTime INT" +
        ")");
        
    db.run("CREATE TABLE if not exists taskitem (" +
        "id INTEGER PRIMARY KEY AUTOINCREMENT," +
        " taskId TEXT," +
        " stateName TEXT," +
        " dbName TEXT," +
        " fileName TEXT," +
        " fileSize TEXT," +
        " status TEXT," +
        " startTime INT," +
        " allcount TEXT," +
        " downloadCount TEXT," +
        " source TEXT," +
        " msg TEXT" +
        ")");
        db.run("CREATE TABLE if not exists user (" +
        "id INTEGER PRIMARY KEY AUTOINCREMENT," +
        " name TEXT," +
        " password TEXT" +
        ")");
};

module.exports = {
    init: init,
    db: db
};

