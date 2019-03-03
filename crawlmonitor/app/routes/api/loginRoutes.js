"use strict";
/* Load Modules */
const express = require('express');
const passport = require('passport');
const router = express.Router();

const LoginController = require('../../controllers/LoginController');
const loginController = new LoginController();
router.post('/', function (req, res) 
{
    loginController.login(req, res) ;
});

module.exports = router;

