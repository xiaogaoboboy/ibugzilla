# -*- coding: utf-8 -*-

import re
import os
import MySQLdb
import shutil
import pickle
import base64
import base_model

class SPRD_Product(base_model.base):

    def __init__(self, id):
        self.db=MySQLdb.connect(host='10.0.0.175',port=3306,user='iadmin', passwd='itask#ADMIN89', db='itask',charset='utf8')
        self.db_imanage=MySQLdb.connect(host='10.0.0.175',port=3306,user='iadmin', passwd='itask#ADMIN89', db='imanage',charset='utf8')
        #self.db = MySQLdb.connect(host='172.16.14.60',port=3306,user='iadmin', passwd='itask#ADMIN89', db='itask',charset='utf8')
        #self.db_imanage = MySQLdb.connect(host='172.16.14.60',port=3306,user='iadmin', passwd='itask#ADMIN89', db='imanage',charset='utf8')
        self.fields = []
        self.fields.append({'name':'Name', 'control':'input'})
        base_model.base.__init__(self, id, 'Product',self.fields, self.db)

    #def Get_Product(self, ):
    #    return self.select({})

    def Get_Prj_Percent(self,UserName,myDate, Data_Type):
        result={}
        tmp=[]
        mySum=0.0
        cursor = self.db.cursor()
        sql = "SELECT t2.ProductName ,SUM(t1.CostTime) from TaskComment t1,Task t2 where t2.ProductName is not NULL and t2.ProductName<>'' and t1.TaskID=t2.ID and t1.Submitter=%s and SUBSTRING(t1.SubmittedDate,1,7)=%s  group by ProductName"
        cursor.execute(sql,(UserName,myDate))
        for ProductName,a_sum in cursor:
            tmp.append({'ProductName':ProductName,'Sum':float(a_sum)})
            mySum = mySum + float(a_sum)
        if mySum==0:
            mySum=1
        for a_tmp in tmp:
            if Data_Type=="Percent":
                result.update({a_tmp['ProductName']: round(a_tmp['Sum']/mySum,2)})
            if Data_Type=="Hours":
                result.update({a_tmp['ProductName']: a_tmp['Sum']})
        return result

    def Get_Fill_Worklog(self,UserName,myDate):
        result=0
        cursor = self.db.cursor()
        sql = "SELECT t2.ProductName ,SUM(t1.CostTime) from TaskComment t1,Task t2 where t2.ProductName is not NULL and t2.ProductName<>'' and t1.TaskID=t2.ID and t1.Submitter=%s and SUBSTRING(t1.SubmittedDate,1,7)=%s  group by ProductName"
        cursor.execute(sql,(UserName,myDate))
        for ProductName,a_sum in cursor:
            if a_sum>0:
                result = 1
                break
        return result
        

    # come from imanage 
    def Get_myProject(self, UserName):
        result = []
        cursor_idata = self.db_imanage.cursor()
        cursor_idata.execute("select Project_Name from myProject  where  Submitter=%s", (UserName, ))
        for Project_Name in cursor_idata:
            if Project_Name[0] not in result:
                result.append(Project_Name[0])
        if len(result)==0:
           result = self.Get_Product()
        result.sort()
        return result
        
    def Get_Product(self,):
        result = []
        cursor_itask = self.db.cursor()
        cursor_itask.execute("select Product.Name from Product")
        for Project_Name in cursor_itask:
            if Project_Name[0] not in result:
                result.append(Project_Name[0])
        result.sort()
        return result
        
        
