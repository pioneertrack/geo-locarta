"use strict";
class Task {
    constructor(id, name, status,startTime) {
        this.id = id;
        this.name = name;
        this.status = status;
        this.startTime=startTime;
    }
}

module.exports = Task;