"use strict";
/* Load Modules */
const express = require('express');
const router = express.Router();
const passport = require('passport');
/* Load controller */
const TaskItemController = require('../../controllers/TaskItemController');
const taskItemController = new TaskItemController();

/**
 * Driver Entity routes
 */
router.get('/count',  passport.authenticate('jwt', { session: false }),function (req, res) {
    taskItemController.countAll(res);
});

router.get('/exists/:id',   passport.authenticate('jwt', { session: false }),function (req, res) {
    taskItemController.exists(req, res);
});
router.put('/updateStatus/:id',   passport.authenticate('jwt', { session: false }),function (req, res) {
    taskItemController.updateStatus(req, res);
});
router.get('/queryByTaskId/:id',   passport.authenticate('jwt', { session: false }),function (req, res) {
    taskItemController.findByTaskId(req, res);
});
router.get('/:id',   passport.authenticate('jwt', { session: false }),function (req, res) {
    taskItemController.findById(req, res)
});

router.get('/',   passport.authenticate('jwt', { session: false }),function (req, res) {
    taskItemController.findAll(req,res);
});

router.put('/:id',   passport.authenticate('jwt', { session: false }),function (req, res) {
    taskItemController.update(req, res)
});

router.post('/create',  passport.authenticate('jwt', { session: false }), function (req, res) {
    taskItemController.create(req, res);
});

router.delete('/:id',   passport.authenticate('jwt', { session: false }),function (req, res) {
    taskItemController.deleteById(req, res)
});

module.exports = router;