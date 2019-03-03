'use strict';
/* Load modules */

const express = require('express');
const app = express();
const bodyParser = require('body-parser');
/* Database configuration */
const database = require('./app/config/dbconfig');

database.init();

/* Init server listening */
const port = 3000;
app.listen(port, function () {
    console.log('Server listening on port : ' + port);
});
/* Express configuration */
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

/* Router configuration */
const REST_API_ROOT = '/api';
app.use(REST_API_ROOT, require('./app/routes/Router'));