
"use strict";

const passport = require("passport");
const passportJWT = require("passport-jwt");
const ExtractJwt = passportJWT.ExtractJwt;
const JwtStrategy = passportJWT.Strategy;
const User = require("../models/User");
const UserDao= require("../dao/UserDao");
const seckey=require("../config/config");
let userDao=new UserDao()
const passportConfig = (app) => {
   
    let jwtOptions = {}
    jwtOptions.jwtFromRequest = ExtractJwt.fromAuthHeaderWithScheme("jwt");
    jwtOptions.secretOrKey = seckey;
    
    let strategy = new JwtStrategy(jwtOptions, function(jwt_payload, next) {
      //console.log('payload received', jwt_payload);
      // usually this would be a database call:
      userDao.findByName(jwt_payload.name).then(user =>{
        if (user) {
          next(null, user);
        } else {
          next(null, false);
        }
      }).catch((error)=>{
        next(null, false);
      });
      
    });  
    passport.use(strategy);
    app.use(passport.initialize());

  };
  
  module.exports = passportConfig;

