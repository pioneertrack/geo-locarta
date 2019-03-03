#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from datetime import timedelta
class MonitorClient:
    def __init__(self):
         self.baseUrl = 'http://localhost:3000/api/'
         self.token=""
         self.login()

    def login(self):
        url=self.baseUrl+"login"
        print url
        req = requests.post(url, data = {'name': 'data', 'password':'data@1234'})
        result= req.json()
        self.token=result['token']
        #print self.token
    def createTask(self,name,status):
        url=self.baseUrl+"task/create"
        headers = {"Authorization": "JWT "+self.token}
        req = requests.post(url, data = {'name':name,"status":status},headers=headers)
        print req
        result= req.json()
        if result.has_key("id"):
            return result["id"]
        else:
            return -1
    def updateTaskStatus(self,taskId,status):
        headers = {"Authorization": "JWT "+self.token}
        url=self.baseUrl+"task/updateStatus/"+str(taskId)
        req = requests.put(url, data = {"status":status},headers=headers)
       


    def createTaskItem(self,taskId,stateName, dbName,fileName,fileSize,status,allcount,downloadCount,source,msg):
        url=self.baseUrl+"taskItem/create"
        headers = {"Authorization": "JWT "+self.token}
        print url
        req = requests.post(url, data = {"taskId":taskId,"stateName":stateName,"dbName":dbName,"fileName":fileName,\
                                        "fileSize":fileSize,"status":status,"allcount":allcount ,"downloadCount":downloadCount,\
                                        "source":source,"msg":msg},headers=headers)
        result= req.json()
        if result.has_key("id"):
            return result["id"]
        else:
            return -1
    def updateTaskItemStatus(self,taskItemId,status,downloadCount,allCount,msg,fileSize=None):
        url=self.baseUrl+"taskItem/updateStatus/"+str(taskItemId)
        headers = {"Authorization": "JWT "+self.token}
        req = requests.put(url, data = {"status":status,"downloadCount":downloadCount,"allcount":allCount,"msg":msg,"fileSize":fileSize},headers=headers)

if __name__ == '__main__':
    mc =  MonitorClient()
    taskid= mc.createTask("name","0")
    mc.updateTaskStatus(taskid,"1")
    print mc.createTaskItem(taskid,"WA","DCDB","","dcdb","downloading","100","0","script","msg")
    mc.updateTaskItemStatus(taskid,"1","s","s",None,"111")