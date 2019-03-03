"use strict";
/* Load Task Data Access Object */
const UserDao = require('../dao/UserDao');

/* Load Controller Common function */
const ControllerCommon = require('./common/controllerCommon');
const jwt = require('jsonwebtoken');
const seckey=require("../config/config");
/* Load User entity */
const User = require('../models/User');
class LoginController {
    
        constructor() {
            this.userDao = new UserDao();
            this.common = new ControllerCommon();
        }
        login(req, res)
        {
            if(req.body.name && req.body.password)
            { 
                let name = req.body.name;
                let password = req.body.password;     
                this.userDao.findByName(name).then(user =>{
                    
                    if(user.password === req.body.password) 
                    {
                        // from now on we'll identify the user by the id and the id is the only personalized value that goes into our token
                        let payload = {name: user.name};
                        let token = jwt.sign(payload, seckey);
                        //console.log(token);
                        res.json({message: "ok", token: token});
                    } 
                    else 
                    {
                        res.status(401).json({message:"passwords did not match"});
                    }
                  }).catch(error=>{
                    res.status(401).json({message:error});
                  });
                                    
            }
            else
            {
                es.status(401).json({message:"param error"});
            }
              // usually this would be a database call:
              
        }
         
    }
module.exports = LoginController;