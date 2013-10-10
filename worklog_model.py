# -*- coding: utf-8 -*-

import re
import os
import MySQLdb
import shutil
import pickle

import base_model

class Worklog(base_model.base):

    def __init__(self, id, db):
        self.fields = []
        self.fields.append({'name':'Task_ID', 'control':'input'})
        self.fields.append({'name':'User_SN', 'control':'input'})
        self.fields.append({'name':'UserName', 'control':'input'})
        self.fields.append({'name':'UserName_CN', 'control':'input'})
        self.fields.append({'name':'Project_Name', 'control':'input'})
        self.fields.append({'name':'DepID1', 'control':'input'})
        self.fields.append({'name':'DepID2', 'control':'input'})
        self.fields.append({'name':'DepID3', 'control':'input'})
        self.fields.append({'name':'Percent', 'control':'input'})
        self.fields.append({'name':'Hours', 'control':'input'})
        self.fields.append({'name':'Submitter', 'control':'input'})
        self.fields.append({'name':'Year_Months', 'control':'input'})
        base_model.base.__init__(self, id, 'Worklog',self.fields, db)
    

    def Get_Fill_Sum(self,Task_ID,filler_user):
        all_SN = [a_user['Badge']  for a_user in filler_user]
        cursor = self.db.cursor()
        result = []
        cursor.execute("SELECT User_SN,sum(Percent) as PercentSum  FROM  Worklog  WHERE Year_Months=(select YearMonth from Task where ID=%s) group by Task_ID,User_SN", (Task_ID,))
        for User_SN,PercentSum in cursor:
            if User_SN in all_SN and PercentSum==100:
                result.append({'User_SN':User_SN, 'PercentSum':PercentSum})
        return result

    def insert(self,):
        QF={}
        QF.update({'field_Task_ID':self.values['Task_ID']})
        QF.update({'field_User_SN':self.values['User_SN']})
        QF.update({'field_Project_Name':self.values['Project_Name']})
        if len(self.select(QF))==1:
            cursor = self.db.cursor()
            cursor.execute("UPDATE Worklog set Percent=%s WHERE Task_ID=%s and User_SN=%s and Project_Name=%s", (self.values['Percent'], self.values['Task_ID'],self.values['User_SN'],self.values['Project_Name']))
            self.db.commit()
        else:
            super(Worklog, self).insert()
        return True

    def delete(self,):
        cursor = self.db.cursor()
        cursor.execute("delete from Worklog where Task_ID=%s and User_SN=%s and Project_Name=%s", (self.values['Task_ID'],self.values['User_SN'],self.values['Project_Name']))
        self.db.commit()
        return True

    def delete_from_YM(self,User_SN, Year_Month):
        cursor = self.db.cursor()
        cursor.execute("delete from Worklog where User_SN=%s and Year_Months=%s", (User_SN, Year_Month))
        self.db.commit()
        return True
        
    def select(self,req_dict):
        import sprd_user_model
        
        AllRows=[]
        all_fileds = ['t1.ID'] + ['t1.' + f['name'] for f in self.fields if f['control'] != 'list'] 
        
        where_str=' where 1=1 '

        cursor = self.db.cursor()
        
        a_user_obj = sprd_user_model.SPRD_User(None)
        
        for k, v in req_dict.iteritems():
            if k.startswith('field_') and v:
                control=''
                fieldname = k[6:]
                if fieldname=='YearMonth_Start':
                    where_str = where_str + " and t1.Year_Months>='" + unicode(v) + "'"
                elif fieldname=='YearMonth_End':
                    where_str = where_str + " and t1.Year_Months<='" + unicode(v) + "'"
                elif fieldname=='Project_Name':
                    if type(v)!=type(list()):
                        v=[v]
                    where_str = where_str + ' and t1.Project_Name in (\'' +  '\',\''.join(v)   + '\')'
                elif fieldname=='User_SN':
                    if type(v)!=type(list()):
                        v=[v]
                    where_str = where_str + ' and t1.User_SN in (\'' +  '\',\''.join(v)   + '\')'
                elif fieldname=='DepID2':
                    if type(v)!=type(list()):
                        v=[v]
                    all_user = a_user_obj.Get_Users(v)
                    all_user_query = [f['Badge'] for f in all_user ] 
                    where_str = where_str + ' and t1.User_SN in (\'' +  '\',\''.join(all_user_query)   + '\')'
                else:
                    where_str = where_str + ' and ' + fieldname + "='" +  unicode(v) + "'"

        sql = "SELECT " + ','.join(all_fileds)  +  " FROM  Worklog t1 " +  where_str + ' order by t1.ID'
        assert sql is  not  None, sql
        cursor.execute(sql)
        for row in cursor:
            tmp={}
            if row:
                for i, field in enumerate(all_fileds) : 
                    field_tmp = field
                    field_tmp = field_tmp.replace('t1.', '')
                    if row[i]:
                        tmp[field_tmp]=unicode(row[i]).strip()
                    else :
                        tmp[field_tmp]=''
            AllRows.append(tmp)
        return AllRows

    # 以人+月 过滤，去掉重复信息
    def show(self,req_dict):
        import sprd_user_model
        AllRows=[]
        all_fileds = ['t1.User_SN', 't1.Year_Months', 't1.UserName', 't1.UserName_CN', 't1.DepID1', 't1.DepID2', 't1.DepID3'] 
        
        where_str=' where 1=1  '

        cursor = self.db.cursor()
        a_user_obj = sprd_user_model.SPRD_User(None)
        
        for k, v in req_dict.iteritems():
            if k.startswith('field_') and v:
                control=''
                fieldname = k[6:]
                if fieldname=='YearMonth_Start':
                    where_str = where_str + " and t1.Year_Months>='" + unicode(v) + "'"
                elif fieldname=='YearMonth_End':
                    where_str = where_str + " and t1.Year_Months<='" + unicode(v) + "'"
                elif fieldname=='Project_Name':
                    if type(v)!=type(list()):
                        v=[v]
                    where_str = where_str + ' and t1.Project_Name in (\'' +  '\',\''.join(v)   + '\')'
                elif fieldname=='User_SN':
                    if type(v)!=type(list()):
                        v=[v]
                    where_str = where_str + ' and t1.User_SN in (\'' +  '\',\''.join(v)   + '\')'
                elif fieldname=='DepID2':
                    if type(v)!=type(list()):
                        v=[v]
                    all_user = a_user_obj.Get_Users(v)
                    all_user_query = [f['Badge'] for f in all_user ] 
                    where_str = where_str + ' and t1.User_SN in (\'' +  '\',\''.join(all_user_query)   + '\')'
                else:
                    where_str = where_str + ' and ' + fieldname + "='" +  unicode(v) + "'"

        sql = "SELECT distinct " + ','.join(all_fileds)  +  " FROM  Worklog t1 " +  where_str + ' order by t1.Task_ID,t1.ID'
        assert sql is  not  None, sql
        cursor.execute(sql)

        for row in cursor:
            tmp={}
            if row:
                for i, field in enumerate(all_fileds) : 
                    field_tmp = field
                    field_tmp = field_tmp.replace('t1.', '')
                    if row[i]:
                        tmp[field_tmp]=unicode(row[i]).strip()
                    else :
                        tmp[field_tmp]=''
                    if field_tmp=="User_SN":
                        a_user = a_user_obj.Get_User_From_SN(tmp[field_tmp])
                        if a_user:
                            tmp.update({'Dep_Name':a_user['DepID3']})
                            tmp.update({'Name':a_user['Name']})
                            tmp.update({'English_Name':a_user['EName']})
                            tmp.update({'Department_ID':a_user['DepID3']})
            AllRows.append(tmp)
        return AllRows
        

    def Project_YM(self,req_dict, Data_Type):
        import sprd_user_model
        
        AllRows=[]
        all_fileds = ['t1.Project_Name', 't1.Year_Months'] 
        
        where_str=' where 1=1  '

        cursor = self.db.cursor()
        a_user_obj = sprd_user_model.SPRD_User(None)
        
        for k, v in req_dict.iteritems():
            if k.startswith('field_') and v:
                control=''
                fieldname = k[6:]
                if fieldname=='YearMonth_Start':
                    where_str = where_str + " and t1.Year_Months>='" + unicode(v) + "'"
                elif fieldname=='YearMonth_End':
                    where_str = where_str + " and t1.Year_Months<='" + unicode(v) + "'"
                elif fieldname=='Project_Name':
                    if type(v)!=type(list()):
                        v=[v]
                    where_str = where_str + ' and t1.Project_Name in (\'' +  '\',\''.join(v)   + '\')'
                elif fieldname=='User_SN':
                    if type(v)!=type(list()):
                        v=[v]
                    where_str = where_str + ' and t1.User_SN in (\'' +  '\',\''.join(v)   + '\')'
                elif fieldname=='DepID2':
                    if type(v)!=type(list()):
                        v=[v]
                    all_user = a_user_obj.Get_Users(v)
                    all_user_query = [f['Badge'] for f in all_user ] 
                    where_str = where_str + ' and t1.User_SN in (\'' +  '\',\''.join(all_user_query)   + '\')'
                else:
                    where_str = where_str + ' and ' + fieldname + "='" +  unicode(v) + "'"

        sql = "SELECT " + ','.join(all_fileds)  +  ",sum(t1." + Data_Type + ") as " + Data_Type + " FROM  Worklog t1 " +  where_str + ' group by ' + ','.join(all_fileds) 
        assert sql is not None, sql
        cursor.execute(sql)

        for row in cursor:
            tmp={}
            if row:
                for i, field in enumerate(all_fileds + [Data_Type]) : 
                    field_tmp = field
                    field_tmp = field_tmp.replace('t1.', '').replace('t2.', '')
                    if row[i]:
                        tmp[field_tmp]=unicode(row[i]).strip()
                    else :
                        tmp[field_tmp]=''
            AllRows.append(tmp)
        return AllRows
        
    def Department_YM(self,req_dict, Data_Type):
        import sprd_user_model
        
        AllRows=[]
        all_fileds = ['t1.DepID2', 't1.Year_Months'] 
        
        where_str=' where 1=1 '

        cursor = self.db.cursor()
        a_user_obj = sprd_user_model.SPRD_User(None)
        
        for k, v in req_dict.iteritems():
            if k.startswith('field_') and v:
                control=''
                fieldname = k[6:]
                if fieldname=='YearMonth_Start':
                    where_str = where_str + " and t1.Year_Months>='" + unicode(v) + "'"
                elif fieldname=='YearMonth_End':
                    where_str = where_str + " and t1.Year_Months<='" + unicode(v) + "'"
                elif fieldname=='Project_Name':
                    if type(v)!=type(list()):
                        v=[v]
                    where_str = where_str + ' and t1.Project_Name in (\'' +  '\',\''.join(v)   + '\')'
                elif fieldname=='User_SN':
                    if type(v)!=type(list()):
                        v=[v]
                    where_str = where_str + ' and t1.User_SN in (\'' +  '\',\''.join(v)   + '\')'
                elif fieldname=='DepID2':
                    if type(v)!=type(list()):
                        v=[v]
                    all_user = a_user_obj.Get_Users(v)
                    all_user_query = [f['Badge'] for f in all_user ] 
                    where_str = where_str + ' and t1.User_SN in (\'' +  '\',\''.join(all_user_query)   + '\')'
                else:
                    where_str = where_str + ' and ' + fieldname + "='" +  unicode(v) + "'"

        sql = "SELECT " + ','.join(all_fileds)  +  ",sum(t1." + Data_Type + ") as "  + Data_Type + " FROM  Worklog t1 " +  where_str + ' group by ' + ','.join(all_fileds) 
        assert sql is not None, sql
        cursor.execute(sql)

        for row in cursor:
            tmp={}
            if row:
                for i, field in enumerate(all_fileds + [Data_Type]) : 
                    field_tmp = field
                    field_tmp = field_tmp.replace('t1.', '').replace('t2.', '').replace('t3.', '')
                    if row[i]:
                        tmp[field_tmp]=unicode(row[i]).strip()
                    else :
                        tmp[field_tmp]=''
            AllRows.append(tmp)
        return AllRows

    def insert_last_month(self,taskid, myUser):
        import sprd_user_model
        import task_model
        a_user_obj = sprd_user_model.SPRD_User(None)
        a_task_obj = task_model.Task(taskid, self.db) 

        QF={}
        last_ym = self.Get_Last_Year_Month(a_task_obj['YearMonth'])
        QF.update({'field_YearMonth':last_ym})
        all_task = a_task_obj.select(QF)
        if len(all_task)>0:
                last_taskid = all_task[0]['ID']
                
                all_Users = []
                a_user_obj.Get_All_User_Line(myUser,all_Users)
                all_Users = [a_user['Badge'] for a_user  in all_Users]
                QF={}
                QF.update({'field_User_SN':all_Users})
                QF.update({'field_Task_ID':last_taskid})
                all_worklog = self.select(QF)
                cursor = self.db.cursor()
                User_Counter={}
                for a_worklog in all_worklog:
                    if a_worklog['Percent']:
                        QF={}
                        QF.update({'field_Task_ID':taskid})
                        QF.update({'field_User_SN':a_worklog['User_SN']})
                        if a_worklog['User_SN'] in User_Counter.keys() or len(self.select(QF))==0:
                            User_Counter.update({a_worklog['User_SN']:1})
                            sql = "INSERT INTO Worklog (Task_ID,User_SN,DepID1,DepID2,DepID3,Project_Name,Percent,Submitter) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                            myPercent = int(a_worklog['Percent'])
                            Dep1 = a_user_obj.Get_Dep1(a_worklog['User_SN'])
                            Dep2 = a_user_obj.Get_Dep2(a_worklog['User_SN'])
                            Dep3 = a_user_obj.Get_Dep3(a_worklog['User_SN'])
                            cursor.execute(sql ,(taskid,a_worklog['User_SN'],Dep1, Dep2, Dep3,a_worklog['Project_Name'],myPercent, myUser))
                            self.db.commit()
        return True

        
    def Get_Last_Year_Month(self, ym):
        result = ''
        a_ym_list = re.split(r'[-]+', ym)
        if a_ym_list[1]=="01":
            result = str(int(a_ym_list[0])-1) + '-12'
        else:
            tmp_m = str(int(a_ym_list[1])-1)
            if len(tmp_m)==1:
                tmp_m = '0' + tmp_m
            result = a_ym_list[0] + '-' + tmp_m
        return result


