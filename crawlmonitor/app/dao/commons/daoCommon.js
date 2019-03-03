"use strict";
/* Load database & database configuration */
const database = require('../../config/dbconfig');

/* Load bluebird Promise */
const Promise = require('bluebird');

/* Load DAO Error entity */
const DaoError = require('./daoError');

/**
 * DAOs Common functions
 */
class Common {

    findAll(sqlRequest) {
        return new Promise(function (resolve, reject) {
            database.db.all(sqlRequest, function (err, rows) {
                if (err) {
                    reject(
                        new DaoError(20, "Internal server error")
                    );
            
                } else {
                    resolve(rows);
                }
            })
        });
    }
    findByWhereClause(sqlRequest,sqlParams) {
        return new Promise(function (resolve, reject) {
            let stmt = database.db.prepare(sqlRequest);
            stmt.all(sqlParams, function (err, rows) {
                if (err) {
                    reject(
                        new DaoError(20, "Internal server error")
                    );
                
                } else {
                    resolve(rows);
                }
            })
        });
    }
    findOne(sqlRequest, sqlParams) {
        return new Promise(function (resolve, reject) {
            let stmt = database.db.prepare(sqlRequest);
            stmt.all(sqlParams, function (err, rows) {
                if (err) {
                    reject(
                        new DaoError(11, "Invalid arguments")
                    );   
                } else {
                    let row = rows[0];
                    resolve(row);
                }
            })
        });
    }
    create(sqlRequest, sqlParams) {
        return new Promise(function (resolve, reject) {
            let stmt = database.db.prepare(sqlRequest);
            stmt.run(sqlParams, function (err) {
                if (this.changes === 1) {
                    resolve({"id":this.lastID});

                } else if (this.changes === 0) {
                    reject(
                        new DaoError(21, "Entity not found")
                    )
                } else {
                    console.log(err);
                    reject(
                        new DaoError(11, "Invalid arguments")
                    )
                }
            })
        });
    }
    existsOne(sqlRequest, sqlParams) {
        return new Promise(function (resolve, reject) {
            let stmt = database.db.prepare(sqlRequest);
            stmt.each(sqlParams, function (err, row) {
                if (err) {
                    reject(
                        new DaoError(20, "Internal server error")
                    );
                } else if (row && row.found === 1) {
                    resolve(true);
                } else {
                    reject(
                        new DaoError(21, "Entity not found")
                    );
                }
            })
        });
    }
    paging(countsql,pagesql){
        return new Promise(function (resolve, reject) {
            database.db.all(countsql, function (err, rows) {
                if (err) {
                    //console.log(err);
                    reject(
                        new DaoError(20, "Internal server error")
                    );
                } else if (rows === null || rows.length === 0) {
                    reject(
                        new DaoError(21, "Entity not found")
                    );
                } else {
                   let row = rows[0];
                    database.db.all(pagesql, function (err, rows) {
                        
                        if (err) {
                            reject(
                                new DaoError(20, "Internal server error")
                            );
                        } else if (rows === null || rows.length === 0) {
                            reject(
                                new DaoError(21, "Entity not found")
                            )
                        }
                        else
                        {
                            resolve({"count":row.count,"data":rows});
                        }
                    });
                }
            });
        });
       };
    run(sqlRequest, sqlParams) {
        return new Promise(function (resolve, reject) {
            let stmt = database.db.prepare(sqlRequest);
            stmt.run(sqlParams, function (err) {
                if (this.changes === 1) {
                    resolve(true);
                } else if (this.changes === 0) {
                    reject(
                        new DaoError(21, "Entity not found")
                    )
                } else {
                    console.log(err);
                    reject(
                        new DaoError(11, "Invalid arguments")
                    )
                }
            })
        });
    }
}

module.exports = Common;