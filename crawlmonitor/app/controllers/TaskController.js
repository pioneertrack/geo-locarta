"use strict";
/* Load Task Data Access Object */
const TaskDao = require('../dao/TaskDao');

/* Load Controller Common function */
const ControllerCommon = require('./common/controllerCommon');

/* Load Task entity */
const Task = require('../models/Task');

/**
 * Task Controller
 */
class TaskController {

    constructor() {
        this.taskDao = new TaskDao();
        this.common = new ControllerCommon();
    }

    /**
     * Tries to find an entity using its Id / Primary Key
     * @params req, res
     * @return entity
     */
    findById(req, res) {
        let id = req.params.id;

        this.taskDao.findById(id)
            .then(this.common.findSuccess(res))
            .catch(this.common.findError(res));
    };

    /**
     * Finds all entities.
     * @return all entities
     */
    findAll(req,res) {
        this.taskDao.findAll()
        .then(this.common.findSuccess(res))
        .catch(this.common.findError(res));
    };
    query(req,res) {
        let pageNum = req.query.pageNum;
        let pageCount = req.query.pageCount;
        if (pageNum)
        {
            this.taskDao.findByPaging(pageNum,pageCount)
            .then(this.common.findSuccess(res))
            .catch(this.common.findError(res));
        }
    };
    /**
     * Counts all the records present in the database
     * @return count
     */
    countAll(res) {

        this.taskDao.countAll()
            .then(this.common.findSuccess(res))
            .catch(this.common.serverError(res));
    };

    /**
     * Updates the given entity in the database
     * @params req, res
     * @return true if the entity has been updated, false if not found and not updated
     */
    update(req, res) {
        let task = new Task();
        task.id = req.params.id;
        task.name = req.body.name;
        task.status = req.body.status;

        return this.taskDao.update(task)
            .then(this.common.editSuccess(res))
            .catch(this.common.serverError(res));
    };
    updateStatus(req, res) {
       
        let taskid= req.params.id;
        let status = req.body.status;
        return this.taskDao.updateStatus(taskid,status)
            .then(this.common.editSuccess(res))
            .catch(this.common.serverError(res));
    };
    /**
     * Creates the given entity in the database
     * @params req, res
     * returns database insertion status
     */
    create(req, res) {
        let task = new Task();
        if (req.body.id) {
            task.id = req.body.id;
        }
        task.name = req.body.name;
        task.status = req.body.status;
        task.startTime = req.body.startTime;

        if (req.body.id) {
            return this.taskDao.createWithId(task)
                .then(this.common.createSuccess(res))
                .catch(this.common.serverError(res));
        }
        else {
            return this.taskDao.create(task)
                .then(this.common.createSuccess(res))
                .catch(this.common.serverError(res));
        }

    };

    /**
     * Deletes an entity using its Id / Primary Key
     * @params req, res
     * returns database deletion status
     */
    deleteById(req, res) {
        let id = req.params.id;

        this.taskDao.deleteById(id)
            .then(this.common.editSuccess(res))
            .catch(this.common.serverError(res));
    };

    /**
     * Returns true if an entity exists with the given Id / Primary Key
     * @params req, res
     * @return
     */
    exists(req, res) {
        let id = req.params.id;

        this.taskDao.exists(id)
            .then(this.common.existsSuccess(res))
            .catch(this.common.findError(res));
    };
}

module.exports = TaskController;