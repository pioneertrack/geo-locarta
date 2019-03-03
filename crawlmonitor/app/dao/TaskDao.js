"use strict";
/* Load Task entity */
const Task = require('../models/Task');

/* Load DAO Common functions */
const daoCommon = require('./commons/daoCommon');

/**
 * Task Data Access Object
 */
class TaskDao {

    constructor() {
        this.common = new daoCommon();
    }
    /**
     * Updates the given entity in the database
     * @params Task
     * @return true if the entity has been updated, false if not found and not updated
     */
    update(Task) {
        let sqlRequest = "UPDATE Task SET " +
            "name=$name, " +
            "status=$status " 
            "WHERE id=$id";

        let sqlParams = {
            $name: Task.name,
            $status: Task.status,
            $id: Task.id
        };
        return this.common.run(sqlRequest, sqlParams);
    };
    updateStatus(id,status) {
        let sqlRequest = "UPDATE Task SET " +
            "status=$status " +
            "WHERE id=$id";

         let sqlParams = {
            $status: status,
            $id: id
        };
        return this.common.run(sqlRequest, sqlParams);
    }

    /**
     * Creates the given entity in the database
     * @params Task
     * returns database insertion status
     */
    create(Task) {
        let sqlRequest = "INSERT into task (name,status, startTime) " +
            "VALUES ($name, $status, $startTime) ;";
        let sqlParams = {
            $name: Task.name,
            $status: Task.status,
            $startTime: new Date()
        };
        return this.common.create(sqlRequest, sqlParams);
    };
    
    /**
     * Creates the given entity with a provided id in the database
     * @params Task
     * returns database insertion status
     */
    createWithId(Task) {
        let sqlRequest = "INSERT into task (id, name,status, startTime) " +
            "VALUES ($id, $name, $status, $startTime)";
        let sqlParams = {
            $id: Task.id,
            $name: Task.name,
            $status: Task.status,
            $startTime: Task.startTime
        };
        return this.common.create(sqlRequest, sqlParams);
    };

    /**
     * Deletes an entity using its Id / Primary Key
     * @params id
     * returns database deletion status
     */
    deleteById(id) {
        let sqlRequest = "DELETE FROM task WHERE id=$id";
        let sqlParams = {$id: id};
        return this.common.run(sqlRequest, sqlParams);
    };

    /**
     * Returns true if an entity exists with the given Id / Primary Key
     * @params id
     * returns database entry existence status (true/false)
     */

    /**
     * Tries to find an entity using its Id / Primary Key
     * @params id
     * @return entity
     */
    findById(id) {
        let sqlRequest = "SELECT id, name,status, startTime FROM task WHERE id=$id";
        let sqlParams = {$id: id};
        return this.common.findOne(sqlRequest, sqlParams).then(row =>
            new Task(row.id, row.name, row.status,row.startTime));
    };

    /**
     * Finds all entities.
     * @return all entities
     */
    findAll() {
        let sqlRequest = "SELECT * FROM task order by id desc";
        return this.common.findAll(sqlRequest).then(rows => {
            let tasks = [];
            for (const row of rows) {
                tasks.push(new Task(row.id, row.name, row.status,row.startTime));
            }
            return tasks;
        });
    };
    findByPaging(pageNum,pageCount){
        let countSql = "SELECT COUNT(*) AS count FROM task";
        let pagingSql = "SELECT *  FROM task Limit "+pageCount+" offset "+pageNum*pageCount;
        return this.common.paging(countSql,pagingSql).then(data =>{
                return data;
            });
                
    };
    
    /**
     * Counts all the records present in the database
     * @return count
     */
    countAll() {
        let sqlRequest = "SELECT COUNT(*) AS count FROM task";
        return this.common.findOne(sqlRequest);
    };

    
    exists(id) {
        let sqlRequest = "SELECT (count(*) > 0) as found FROM task WHERE id=$id";
        let sqlParams = {$id: id};
        return this.common.run(sqlRequest, sqlParams);
    };
}

module.exports = TaskDao;