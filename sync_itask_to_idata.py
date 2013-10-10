# -*- coding: utf-8 -*-

import re
import os
import MySQLdb
import shutil
import pickle
import time

class Sync_Worklog():

    def Year_Month_Process(self, ym):
        result = []
        ym.sort()
        if ym[0]==ym[1]:
            return [ym[0]]
            
        a_ym = ym[0]
        if a_ym not in result:
            result.append(a_ym)

        next_ym = ''
        while next_ym!=ym[1]:
            a_ym_list = re.split(r'[-]+', a_ym)
            if a_ym_list[1]=="12":
                next_ym = str(int(a_ym_list[0])+1) + '-01'
            else:
                tmp_m = str(int(a_ym_list[1])+1)
                if len(tmp_m)==1:
                    tmp_m = '0' + tmp_m
                next_ym = a_ym_list[0] + '-' + tmp_m
            if next_ym not in result:
                result.append(next_ym)
            a_ym = next_ym
        return result
        
    def Sync_iTask_To_iData(self, UserName,myDate, db_conn):
        import sprd_product_model
        import sprd_user_model
        import worklog_model
        a_worklog = worklog_model.Worklog(None, db_conn)
        a_sprd_product = sprd_product_model.SPRD_Product(None)
        Task_Percent = a_sprd_product.Get_Prj_Percent(UserName, myDate, 'Percent')
        Task_Hours = a_sprd_product.Get_Prj_Percent(UserName, myDate, 'Hours')
        a_sprd_product.db.close()
        a_sprd_product.db=None
        a_sprd_product=None
        a_user_obj = sprd_user_model.SPRD_User(None)
        a_user = a_user_obj.Get_User(UserName)
        a_user_obj.db.close()
        a_user_obj=None
        a_worklog.delete_from_YM(a_user['Badge'],myDate)

        for  a_Prj in Task_Percent:
            if Task_Percent[a_Prj]!=0 or Task_Hours[a_Prj]!=0:
                a_worklog['Task_ID'] = 0
                a_worklog['User_SN'] = a_user['Badge']
                a_worklog['DepID1'] = a_user['DepID1']
                a_worklog['DepID2'] = a_user['DepID2']
                a_worklog['DepID3'] = a_user['DepID3']
                a_worklog['Project_Name'] = a_Prj
                a_worklog['Percent'] = int(Task_Percent[a_Prj]*100)
                a_worklog['Hours'] = int(Task_Hours[a_Prj])
                a_worklog['Year_Months'] = myDate
                a_worklog['Submitter'] = UserName
                a_worklog.insert()

    def Sync_All_iTask_To_iData(self, ):
        all_para = []
        all_date=['2011-01', '2013-04']
        all_date = self.Year_Month_Process(all_date)
        db=MySQLdb.connect(host='172.16.0.230',port=3306,user='iadmin', passwd='itask#ADMIN89', db='itask',charset='utf8')
        db_conn=MySQLdb.connect(host='172.16.0.230',port=3306,user='iadmin', passwd='itask#ADMIN89', db='imanage',charset='utf8')
        cursor = db.cursor()
        cursor.execute("select distinct Submitter from  TaskComment" )
        for a_user in cursor:
            for a_date in all_date:
                all_para.append([a_user[0],a_date])
        cursor.close()
        db.close()
        for a_para in all_para:
            print a_para[0] 
            print a_para[1]
            self.Sync_iTask_To_iData(a_para[0],a_para[1], db_conn)
            time.sleep(0.2)

