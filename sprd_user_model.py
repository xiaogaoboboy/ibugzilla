# -*- coding: utf-8 -*-

import re
import os
import MySQLdb
import shutil
import pickle
import base64
import base_model

class SPRD_User(base_model.base):

    def __init__(self, id):
        db=MySQLdb.connect(host='10.0.0.175',port=3306,user='iadmin', passwd='itask#ADMIN89', db='imanage',charset='utf8')
        #db=MySQLdb.connect(host='172.16.14.60',port=3306,user='iadmin', passwd='itask#ADMIN89', db='imanage',charset='utf8')
        self.fields = []
        self.fields.append({'name':'Badge', 'control':'input'})
        self.fields.append({'name':'EName', 'control':'input'})
        self.fields.append({'name':'Name', 'control':'input'})
        self.fields.append({'name':'Status', 'control':'input'})
        self.fields.append({'name':'DepID1', 'control':'input'})
        self.fields.append({'name':'DepID2', 'control':'input'})
        self.fields.append({'name':'DepID3', 'control':'input'})
        self.fields.append({'name':'ReportTo', 'control':'input'})
        self.fields.append({'name':'ReportTo_Dep', 'control':'input'})
        base_model.base.__init__(self, id, 'User_List',self.fields, db)

        
    def Get_All_Member(self,UserName):
        all_Users = []
        SN = self.Get_Badge(UserName)
        self._Get_All_Member(SN,all_Users)
        return all_Users
            
    def _Get_All_Member(self,SN,all_Users):
        fields = [a_field['name'] for a_field in self.fields]
        cursor = self.db.cursor()
        cursor.execute("select " + ','.join(fields) + " from  User_List where ReportTo='" + SN + "' and Status='" + u'在职' +"'" )
        for row in cursor:
            tmp={}
            for i, field in enumerate(fields) : 
                if row[i]:
                    tmp[field]=unicode(row[i]).strip()
                else :
                    tmp[field]=''
            if tmp not in all_Users:
                all_Users.append(tmp)
            if tmp['Badge']!=SN:
                self._Get_All_Member(tmp['Badge'],all_Users)

    def Get_Direct_Member(self,UserName):
        all_Users = []
        SN = self.Get_Badge(UserName)
        fields = [a_field['name'] for a_field in self.fields]
        cursor = self.db.cursor()
        cursor.execute("select " + ','.join(fields) + " from  User_List where ReportTo='" + SN + "' and Status='" + u'在职' +"'" )
        for row in cursor:
            tmp={}
            for i, field in enumerate(fields) : 
                if row[i]:
                    tmp[field]=row[i]
                else :
                    tmp[field]=u''
            if tmp not in all_Users:
                all_Users.append(tmp)
        return all_Users

    def Get_Direct_Team(self,UserName):
        all_Users = []
        SN = self.Get_Badge(UserName)
        fields = [a_field['name'] for a_field in self.fields]
        cursor = self.db.cursor()
        cursor.execute("select " + ','.join(fields) + " from  User_List t1 where t1.ReportTo='" + SN + "' and t1.Status='" + u'在职' +"' and (select count(*) from User_List t2 where t2.Status='" + u'在职' +"' and t2.ReportTo=t1.Badge)>0" )
        for row in cursor:
            tmp={}
            for i, field in enumerate(fields) : 
                if row[i]:
                    tmp[field]=row[i]
                else :
                    tmp[field]=u''
            if tmp not in all_Users:
                all_Users.append(tmp)
        if not all_Users:
            if self.Get_Direct_Member(UserName):
                tmp=self.Get_User_From_SN(SN)
                if tmp:
                    all_Users.append(tmp)
        if all_Users:
            tmp=self.Get_User_From_SN(SN)
            if tmp:
                if tmp not in all_Users:
                    all_Users = [tmp] + all_Users
        return all_Users
 
    def Get_ReportTo_list(self,UserName):
        all_SN = []
        all_Users = []
        SN = self.Get_Badge(UserName)
        self._Get_ReportTo(SN,all_SN)
        cursor = self.db.cursor()
        if len(all_SN)>0:
            fields = [a_field['name'] for a_field in self.fields]
            cursor.execute("select " + ','.join(fields) + " from  User_List where Badge in ('" + "','".join(all_SN) + "')")
            for row in cursor:
                tmp={}
                for i, field in enumerate(fields) : 
                    if row[i]:
                        tmp[field]=unicode(row[i])
                    else :
                        tmp[field]=''
                if tmp not in all_Users:
                    all_Users.append(tmp)
        return all_Users

    def Get_ReportToUserName(self,UserName):
        Result=''
        cursor = self.db.cursor()
        cursor.execute("select ReportTo from  User_List where lower(replace(EName,' ','.'))=%s", (UserName,))
        obj = cursor.fetchone()
        if obj:
            Result = obj[0]
        cursor.execute("select EName from  User_List where Badge=%s", (Result,))
        obj = cursor.fetchone()
        if obj:
            Result = obj[0].replace(' ','.').lower()
        return Result
        
    def _Get_ReportTo(self,SN,all_SN):
        fields = [a_field['name'] for a_field in self.fields]
        cursor = self.db.cursor()
        cursor.execute("select ReportTo from  User_List where Badge='" + SN + "'")
        obj = cursor.fetchone()
        if obj:
            tmp = obj[0]
            if tmp not in all_SN:
               all_SN.append(tmp)
               if tmp!=SN:
                self._Get_ReportTo(tmp,all_SN)
            
    def Get_Badge(self,UserName):
        Result=''
        cursor = self.db.cursor()
        cursor.execute("select Badge from  User_List where lower(replace(EName,' ','.'))=%s", (UserName,))
        obj = cursor.fetchone()
        if obj:
            Result = obj[0]
        return Result
        
    def Get_Dep_Level_1(self,):
        Result=[]
        cursor = self.db.cursor()
        cursor.execute("SELECT distinct DepID1 FROM  User_List where Status='" + u'在职' +"'")
        for DepID1 in cursor:
            if DepID1:
                tmp = DepID1[0].strip()
                if tmp:
                    Result.append(tmp)
        return Result

    def Get_Dep_Level_2(self,Level1_Name):
        Result=[]
        cursor = self.db.cursor()
        if Level1_Name:
            cursor.execute("SELECT distinct DepID2 FROM  User_List where DepID1=%s and Status=%s",(Level1_Name, u'在职'))
        else:
            cursor.execute("SELECT distinct DepID2 FROM  User_List where Status='" + u'在职' +"'")
        for DepID2 in cursor:
            if DepID2:
                tmp = DepID2[0].strip()
                if tmp:
                    Result.append(tmp)
        if Level1_Name in Result:
            Result.remove(Level1_Name)
        return Result

        
    def Get_DEV_Dep_Level_2(self,):
        Result=[]
        #QC = ['Comm Sys', 'Product', 'Platform SW', 'TD', 'GSM', 'ASIC', 'SPRD US', 'SE', 'IR', 'SPRD KR', 'SPRD TJ', 'SPRD TPE', 'Mobilepeak', 'SPRD India']
        cursor = self.db.cursor()
        #cursor.execute("SELECT distinct DepID2 FROM  User_List where DepID1 in ('" + "','".join(QC)  + "')" + " and Status='" + u'在职' +"'")
        cursor.execute("SELECT distinct DepID2 FROM  User_List where Status='" + u'在职' +"'")
        for DepID2 in cursor:
            if DepID2:
                tmp = DepID2[0].strip()
                if tmp:
                    Result.append(tmp)
        Result.sort()
        return Result
        
    def Get_Dep_Level_3(self,Level1_Name,Level2_Name):
        Result=[]
        cursor = self.db.cursor()
        if Level2_Name:
            cursor.execute("SELECT distinct DepID3 FROM  User_List where DepID1=%s and DepID2=%s and Status=%s",(Level1_Name,Level2_Name,u'在职'))
        else:
            cursor.execute("SELECT distinct DepID3 FROM  User_List where DepID1=%s and (DepID2 is null or DepID2='') and Status=%s",(Level1_Name,u'在职'))
        for DepID3 in cursor:
            if DepID3:
                tmp = DepID3[0].strip()
                if tmp:
                    Result.append(tmp)
        if Level1_Name in Result:
            Result.remove(Level1_Name)
        if Level2_Name in Result:
            Result.remove(Level2_Name)
        return Result

    def Get_Assisant(self,):
        all_Users = []
        cursor = self.db.cursor()
        cursor.execute("select Assisant from  Dep_Assisant ")
        for Assisant in cursor:
            if Assisant:
                if Assisant[0]:
                    all_Users.append(Assisant[0])
        return all_Users
 
    def Get_myAssisant(self,UserName):
        Dep = []
        cursor = self.db.cursor()
        cursor.execute("select DepID1,DepID2,DepID3 from  User_List where lower(replace(EName,' ','.'))=%s", (UserName,))
        for DepID1,DepID2,DepID3 in cursor:
            if DepID2:
                Dep=[DepID1,DepID2]
            else:
                if DepID3:
                    Dep=[DepID1,DepID3]
                else:
                    Dep=[DepID1,DepID1]
        result = []
        if Dep:
            cursor.execute("select Assisant from  Dep_Assisant where Dep1Name=%s and DepName=%s", (Dep[0],Dep[1]))
            for Assisant in cursor:
              if Assisant:
                 if Assisant[0]:
                    result.append(Assisant[0])
        return result
        
    def Get_DepUsers(self,Level1_Name,Level2_Name,Level3_Name):
        all_Users = []
        where = " where Status='" + u'在职' +"' "
        if Level1_Name:
            where = where + " and DepID1='" + Level1_Name + "'"
        if Level2_Name:
            where = where + " and DepID2='" + Level2_Name + "'"
        if Level3_Name:
            where = where + " and DepID3='" + Level3_Name + "'"
        fields = [a_field['name'] for a_field in self.fields]
        cursor = self.db.cursor()
        cursor.execute("select " + ','.join(fields) + " from  User_List " + where)
        for row in cursor:
            tmp={}
            for i, field in enumerate(fields) : 
                if row[i]:
                    tmp[field]=unicode(row[i])
                else :
                    tmp[field]=''
            if tmp not in all_Users:
                all_Users.append(tmp)
        return all_Users

    def Get_Worklog_Admin(self,):
        all_Users = []
        where = " where 1=1 "
        Worklog_Admin_DepID3_List = ['CEO Office','HR','Fin','FP']
        where = where + " and DepID3 in ('" + "','".join(Worklog_Admin_DepID3_List) + "')"
        fields = [a_field['name'] for a_field in self.fields]
        cursor = self.db.cursor()
        cursor.execute("select " + ','.join(fields) + " from  User_List " + where)
        for row in cursor:
            tmp={}
            for i, field in enumerate(fields) : 
                if row[i]:
                    tmp[field]=unicode(row[i])
                else :
                    tmp[field]=''
            if tmp not in all_Users:
                all_Users.append(tmp)
        return all_Users
        
    def _Dep_Filter(self,tmp):
        Result=''
        if tmp:
            pattern=re.compile(ur'^D\d+(.*)$')
            m=pattern.match(tmp)
            if m:
                Result = m.group(1)
        return Result         


    def Get_User_From_SN(self, SN):
        QC = {'field_Badge':SN}
        tmp = self.select(QC)
        if len(tmp)>0:
            return tmp[0]
        else:
            return None
            
    def Get_User(self, UserName):
        SN = self.Get_Badge(UserName)
        QC = {'field_Badge':SN}
        tmp = self.select(QC)
        if len(tmp)>0:
            return tmp[0]
        else:
            return None

    def Get_UnAgent_User(self,UserName):
        result = []
        all_Users = []
        self.Get_All_User_Line_UnAgentSelf(UserName, all_Users)
        my_Users = []
        my_Users = self.Get_All_Member(UserName)
        for a_user in my_Users:
            if a_user not in all_Users:
                result.append(a_user)
        return result

    def Get_All_User_Line_UnAgentSelf(self,UserName,all_Users):
        import filler_model
        all_Agent = []
        a_filler_obj = filler_model.Filler(None, self.db)
        a_filler_obj.Get_All_Agent_UnAgentSelf(UserName, all_Agent)
        for a_user in all_Agent:
            tmp = self.Get_All_Member(a_user)
            for a_tmp in tmp:
                if a_tmp not in all_Users:
                    all_Users.append(a_tmp)

    def Get_All_User_Line(self,UserName,all_Users):
        import filler_model
        all_Users.append(self.Get_User(UserName))
        all_Agent = []
        a_filler_obj = filler_model.Filler(None, self.db)
        a_filler_obj.Get_All_Agent(UserName, all_Agent)
        for a_user in all_Agent:
            tmp = self.Get_All_Member(a_user)
            for a_tmp in tmp:
                if a_tmp not in all_Users:
                    all_Users.append(a_tmp)

    def Get_Users(self, dep_list):
        result=[]
        for a_dep in dep_list:
            tmp = self.Get_DepUsers('',a_dep, '')
            for a_tmp in tmp:
                if a_tmp not in result:
                    result.append(a_tmp)
        return result

    def Get_Dep1(self,SN):
        result = ''
        tmp =  self.Get_User_From_SN(SN)
        if tmp:
            result = tmp['DepID1']
        return result
        
    def Get_Dep2(self,SN):
        result = ''
        tmp =  self.Get_User_From_SN(SN)
        if tmp:
            result = tmp['DepID2']
        return result
        
    def Get_Dep3(self,SN):
        result = ''
        tmp =  self.Get_User_From_SN(SN)
        if tmp:
            result = tmp['DepID3']
        return result

