
"use strict";
/* Load modules */
const express = require("express");
const app = express();
const bodyParser = require("body-parser");
const path = require('path')
/* Database configuration */
const database = require('./app/config/dbconfig');
const passportConfig=require('./app/passport/passport');
/* Init database */
database.init();

/* Init server listening */
const port = process.argv[2] || 3000;
app.listen(port, function () {
    console.log("Server listening on port : " + port);
});
app.use(express.static(path.join(__dirname, 'html')));
passportConfig(app);
/* Express configuration */
app.use(bodyParser.urlencoded({extended: true}));
app.use(bodyParser.json());


/* Router configuration */
const REST_API_ROOT = '/api';
app.use(REST_API_ROOT, require('./app/routes/Router'));