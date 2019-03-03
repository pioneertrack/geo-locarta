"use strict";
const express = require('express');
const router = express.Router();
/* API routes */

router.use('/task', require('./api/taskRoutes'));
router.use('/taskitem', require('./api/taskItemRoutes'));
router.use('/login', require('./api/loginRoutes'));
module.exports = router;