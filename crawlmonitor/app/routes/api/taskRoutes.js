"use strict";
/* Load Modules */
const express = require('express');
const router = express.Router();
const passport = require('passport');
/* Load controller */
const TaskController = require('../../controllers/TaskController');
const taskController = new TaskController();

/**
 * Task Entity routes
 */
router.get('/query',   passport.authenticate('jwt', { session: false }),function (req, res) {
    taskController.query(req,res);
});
router.get('/count',   passport.authenticate('jwt', { session: false }),function (req, res) {
    taskController.countAll(res);
});

router.get('/exists/:id',   passport.authenticate('jwt', { session: false }),function (req, res) {
    taskController.exists(req, res);
});


router.get('/:id',   passport.authenticate('jwt', { session: false }),function (req, res) {
    taskController.findById(req, res);
});

router.get('/',   passport.authenticate('jwt', { session: false }),function (req, res) {
    taskController.findAll(req,res);
});

router.put('/:id',   passport.authenticate('jwt', { session: false }),function (req, res) {
    taskController.update(req, res);
});
router.put('/updateStatus/:id', function (req, res) {
    taskController.updateStatus(req, res);
});
router.post('/create',   passport.authenticate('jwt', { session: false }),function (req, res) {
    
    taskController.create(req, res);
});

router.delete('/:id',   passport.authenticate('jwt', { session: false }),function (req, res) {
    taskController.deleteById(req, res);
});

module.exports = router;