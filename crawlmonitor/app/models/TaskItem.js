"use strict";
class TaskItem {
    constructor(id, taskId,stateName, dbName,fileName,fileSize,status,startTime,allcount,downloadCount,source,msg) {
        this.id = id;
        this.taskId=taskId;
        this.stateName = stateName;
        this.dbName = dbName;
        this.fileName = fileName;
        this.fileSize=fileSize;
        this.status = status;
        this.startTime=startTime;
        this.allcount=allcount;
        this.downloadCount=downloadCount;
        this.source=source;//email,directly
        this.msg=msg;
    }
}

module.exports = TaskItem;