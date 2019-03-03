"use strict";
/* Load User entity */
const User = require('../models/User');

/* Load DAO Common functions */
const daoCommon = require('./commons/daoCommon');
class UserDao {
    constructor() {
        this.common = new daoCommon();
    }
    findByName(name) {
        let sqlRequest = "SELECT id, name,password FROM user WHERE name=$name";
        let sqlParams = {$name: name};
        
        return this.common.findOne(sqlRequest, sqlParams).then(row =>{
            
            return new User(row.id, row.name, row.password);
        });
            
    };
}    
module.exports = UserDao;