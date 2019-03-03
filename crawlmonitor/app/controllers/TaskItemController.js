"use strict";
/* Load TaskItem Data Access Object */
const TaskItemDao = require('../dao/TaskItemDao');

/* Load Controller Common function */
const controllerCommon = require('./common/controllerCommon');

/* Load TaskItem entity */
const TaskItem = require('../models/TaskItem');

/**
 * TaskItem Controller
 */
class TaskItemController {

    constructor() {
        this.taskItemDao = new TaskItemDao();
        this.common = new controllerCommon();
    }

    /**
     * Tries to find an entity using its Id / Primary Key
     * @params req, res
     * @return entity
     */
    findById(req, res) {
        let id = req.params.id;
        this.taskItemDao.findById(id)
            .then(this.common.findSuccess(res))
            .catch(this.common.findError(res));
    };

    /**
     * Finds all entities.
     * @return all entities
     */
    findAll(req,res) {
            this.taskItemDao.findAll()
            .then(this.common.findSuccess(res))
            .catch(this.common.findError(res));
    };

    /**
     * Counts all the records present in the database
     * @return count
     */
    countAll(res) {
        this.taskItemDao.countAll()
            .then(this.common.findSuccess(res))
            .catch(this.common.serverError(res));
    };

    /**
     * Updates the given entity in the database
     * @params req, res
     * @return true if the entity has been updated, false if not found and not updated
     */
    update(req, res) {
        let taskid = id = req.params.id;
        let status = req.body.status;
        let taskItem = new TaskItem();
        taskItem.id = req.params.id;
        taskItem.taskId= req.body.taskId;;
        taskItem.stateName= req.body.stateName;
        taskItem.dbName= req.body.dbName;
        taskItem.fileName= req.body.fileName;
        taskItem.fileSize= req.body.fileSize;
        taskItem.status= req.body.status;
        taskItem.startTime= req.body.startTime;
        taskItem.allcount= req.body.allcount;
        taskItem.downloadCount= req.body.downloadCount;
        taskItem.source= req.body.source;
        taskItem.msg= req.body.msg;

        return this.taskItemDao.update(taskItem)
            .then(this.common.editSuccess(res))
            .catch(this.common.serverError(res));
    };
    updateStatus(req, res) {
        let id = req.params.id;
        let status= req.body.status;
        let downloadCount= req.body.downloadCount;
        let allcount= req.body.allcount;
        let msg= req.body.msg;
        let fileSize=req.body.fileSize;
    

        return this.taskItemDao.updateStatus(id,status,msg,downloadCount,allcount,fileSize)
            .then(this.common.editSuccess(res))
            .catch(this.common.serverError(res));
    };
    findByTaskId(req, res) {
        let taskId = req.params.id;

        return this.taskItemDao.findByTaskId(taskId)
            .then(this.common.findSuccess(res))
            .catch(this.common.serverError(res));
    };
    /**
     * Creates the given entity in the database
     * @params req, res
     * returns database insertion status
     */
    create(req, res) {
        let taskItem = new TaskItem();
        if (req.body.id) {
            taskItem.id = req.body.id;
        }
        taskItem.taskId= req.body.taskId;
        taskItem.stateName= req.body.stateName;
        taskItem.dbName= req.body.dbName;
        taskItem.fileName= req.body.fileName;
        taskItem.fileSize= req.body.fileSize;
        taskItem.status= req.body.status;
        taskItem.startTime= req.body.startTime;
        taskItem.allcount= req.body.allcount;
        taskItem.downloadCount= req.body.downloadCount;
        taskItem.source= req.body.source;
        taskItem.msg= req.body.msg;


        if (req.body.id) {
            return this.taskItemDao.createWithId(taskItem)
                .then(this.common.createSuccess(res))
                .catch(this.common.serverError(res));
        }
        else {
            return this.taskItemDao.create(taskItem)
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

        this.taskItemDao.deleteById(id)
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

        this.taskItemDao.exists(id)
            .then(this.common.existsSuccess(res))
            .catch(this.common.findError(res));
    };
}

module.exports = TaskItemController;