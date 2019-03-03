'use strict';

const express = require('express');
const router = express.Router();
/* API routes */
router.use('/act', require('./api/ActRouter'));
router.use('/nsw', require('./api/NswRouter'));
router.use('/nswtest', require('./api/NswTestRouter'));
router.use('/tas', require('./api/TasRouter'));
router.use('/wa', require('./api/WaRouter'));
router.use('/sa', require('./api/SaRouter'));
router.use('/nt', require('./api/NtRouter'));
router.use('/qld', require('./api/QldRouter'));
router.use('/address', require('./api/StreetRouter'));
router.use('/legal', require('./api/LegalRouter'));
router.use('/ntlegal', require('./api/NtDCDBRouter'));
router.use('/actlegal', require('./api/ActDCDBRouter'));
router.use('/state', require('./api/StateRouter'));
module.exports = router;