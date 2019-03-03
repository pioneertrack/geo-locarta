"use strict";
/* Load TaskItem entity */
const TaskItem = require('../models/TaskItem');

/* Load DAO Common functions */
const daoCommon = require('./commons/daoCommon');

/**
 * TaskItem Data Access Object
 */
class TaskItemDao {

    constructor() {
        this.common = new daoCommon();
    }

    /**
     * Tries to find an entity using its Id / Primary Key
     * @params id
     * @return entity
     */
    findById(id) {
        let sqlRequest = "SELECT id, taskId,stateName, dbName,fileName,fileSize,status,startTime,allcount,downloadCount,source,msg FROM taskItem WHERE id=$id";
        let sqlParams = {$id: id};
        return this.common.findOne(sqlRequest, sqlParams).then(row =>
            new TaskItem(row.id, row.taskId,row.stateName, row.dbName,row.fileName,row.fileSize,row.status,row.startTime,row.allcount,row.downloadCount,row.source,row.msg));
    };

    /**
     * Finds all entities.
     * @return all entities
     */
    findAll() {
        let sqlRequest = "SELECT * FROM taskItem";
        return this.common.findAll(sqlRequest).then(rows => {
            let taskItems = [];
            for (const row of rows) {
                taskItems.push(new TaskItem(row.id, row.taskId,row.stateName, row.dbName,row.fileName,row.fileSize,row.status,row.startTime,row.allcount,row.downloadCount,row.source,row.msg));
            }
            return taskItems;
        });
    };
    findByTaskId(taskId) {
        let sqlRequest = "SELECT * FROM taskItem"+" WHERE taskId=$taskId";
        let sqlParams = {
            $taskId: taskId
          
        };
        return this.common.findByWhereClause(sqlRequest,sqlParams).then(rows => {
            let taskItems = [];
            for (const row of rows) {
                taskItems.push(new TaskItem(row.id, row.taskId,row.stateName, row.dbName,row.fileName,row.fileSize,row.status,row.startTime,row.allcount,row.downloadCount,row.source,row.msg));
            }
            return taskItems;
        });
    };

    /**
     * Counts all the records present in the database
     * @return count
     */
    countAll() {
        let sqlRequest = "SELECT COUNT(*) AS count FROM taskItem";
        return this.common.findOne(sqlRequest);
    };

    updateStatus(id,status,msg,downloadCount,allcount,fileSize) {
        
        let sqlRequest = "UPDATE taskItem SET " ;
        let sqlParams = {};
        if (!(status  === undefined))
        {
            sqlRequest+="status=$status, "
            sqlParams["$status"]=status;
        }
        if (!(msg  === undefined))
        {
            sqlRequest+="msg=$msg, " ;
            sqlParams["$msg"]=msg;
            
        }

        if (!(downloadCount  === undefined))
        {
            sqlRequest+="downloadCount=$downloadCount, "
            sqlParams["$downloadCount"]=downloadCount;
        }
        if (!(allcount === undefined))
        {
            sqlRequest+="allcount=$allcount, "
            sqlParams["$allcount"]=allcount;
        }
        if (!(fileSize === undefined))
        {
            sqlRequest+="fileSize=$fileSize, "
            sqlParams["$fileSize"]=fileSize;
        }
    
        
        sqlParams["$id"]=id;
        sqlRequest = sqlRequest.slice(0, -2);   
         
        sqlRequest+=" WHERE id=$id";
    
        return this.common.run(sqlRequest, sqlParams);
    }
    /**
     * Updates the given entity in the database
     * @params TaskItem
     * @return true if the entity has been updated, false if not found and not updated
     */
    update(TaskItem) {
        let sqlRequest = "UPDATE taskItem SET " +
            "taskId=$taskId, " +
            "stateName=$stateName, " +
            "dbName=$dbName, " +
            "fileName=$fileName " +
            "fileSize=$fileSize " +
            "status=$status, " +
            "startTime=$startTime, " +
            "allcount=$allcount, " +
            "downloadCount=$downloadCount, " +
            "source=$source, " +
            "msg=$msg " +
            "WHERE id=$id";

        let sqlParams = {
            $taskId: TaskItem.taskId,
            $stateName: TaskItem.stateName,
            $dbName: TaskItem.dbName,
            $fileName: TaskItem.fileName,
            $fileSize: TaskItem.fileSize,
            $status: TaskItem.status,
            $startTime: TaskItem.startTime,
            $allcount: TaskItem.allcount,
            $downloadCount: TaskItem.downloadCount,
            $source: TaskItem.source,
            $msg: TaskItem.msg,
            $id: TaskItem.id
        };
        return this.common.run(sqlRequest, sqlParams);
    };

    /**
     * Creates the given entity in the database
     * @params TaskItem
     * returns database insertion status
     */
    create(TaskItem) {
        let sqlRequest = "INSERT into taskItem ( taskId,stateName, dbName,fileName,fileSize,status,startTime,allcount,downloadCount,source,msg) " +
            "VALUES ( $taskId,$stateName, $dbName,$fileName,$fileSize,$status,$startTime,$allcount,$downloadCount,$source,$msg)";
        let sqlParams = {
            $taskId: TaskItem.taskId,
            $stateName: TaskItem.stateName,
            $dbName: TaskItem.dbName,
            $fileName: TaskItem.fileName,
            $fileSize: TaskItem.fileSize,
            $status: TaskItem.status,
            $startTime: new Date(),
            $allcount: TaskItem.allcount,
            $downloadCount: TaskItem.downloadCount,
            $source: TaskItem.source,
            $msg: TaskItem.msg,
        };
        return this.common.create(sqlRequest, sqlParams);
    };

    /**
     * Creates the given entity with a provided in the database
     * @params TaskItem
     * returns database insertion status
     */
    createWithId(TaskItem) {
        let sqlRequest = "INSERT into taskItem (id, taskId,stateName, dbName,fileName,fileSize,status,startTime,allcount,downloadCount,source,msg) " +
        "VALUES ($id,$taskId,$stateName, $dbName,$fileName,$fileSize,$status,$startTime,$allcount,$downloadCount,$source,$msg)";
    let sqlParams = {
        $id:TaskItem.id,
        $taskId: TaskItem.taskId,
        $stateName: TaskItem.stateName,
        $dbName: TaskItem.dbName,
        $fileName: TaskItem.fileName,
        $fileSize: TaskItem.fileSize,
        $status: TaskItem.status,
        $startTime: TaskItem.startTime,
        $allcount: TaskItem.allcount,
        $downloadCount: TaskItem.downloadCount,
        $source: TaskItem.source,
        $msg: TaskItem.msg,
    };
    return this.common.create(sqlRequest, sqlParams);
    };

    /**
     * Deletes an entity using its Id / Primary Key
     * @params id
     * returns database deletion status
     */
    deleteById(id) {
        let sqlRequest = "DELETE FROM taskItem WHERE id=$id";
        let sqlParams = {$id: id};
        return this.common.run(sqlRequest, sqlParams);
    };

    /**
     * Returns true if an entity exists with the given Id / Primary Key
     * @params id
     * returns database entry existence status (true/false)
     */
    exists(id) {
        let sqlRequest = "SELECT (count(*) > 0) as found FROM taskItem WHERE id=$id";
        let sqlParams = {$id: id};
        return this.common.existsOne(sqlRequest, sqlParams);
    };
}

module.exports = TaskItemDao;