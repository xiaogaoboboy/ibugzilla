# -*- coding: utf-8 -*-
#
import os
import re
import MySQLdb
import user_model
import department_model

db_conn=MySQLdb.connect(host='172.16.15.41',port=3306,user='root', passwd='root', db='iworklog',charset='utf8')

a_user_obj = user_model.Users(None, db_conn)
a_department_obj = department_model.Department(None, db_conn)

QC = {}
all_user = a_user_obj.select(QC)

for a_user in all_user:
    QC = {}
    UN  = a_user['English_Name'].replace(' ', '.').lower()
    QC.update({'field_Manager':UN})
    QC.update({'field_Level':'2'})
    Manage_level_2 = a_department_obj.select(QC)
    if len(Manage_level_2)==0:
        myDeptID = a_department_obj.Get_Level2_Department_ID(a_user['Department_ID'])
    elif len(Manage_level_2)==1:
        myDeptID = Manage_level_2[0]['ID']
    a_tmp_user_obj = user_model.Users(a_user['ID'], db_conn)
    a_tmp_user_obj['Level_2_Department_ID'] = myDeptID
    a_tmp_user_obj.save_changes()

        
    print a_user['Department_ID']
    print myDeptID
    print '----------------------------------------'

