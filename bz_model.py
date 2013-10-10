


import re
import os
import MySQLdb
import shutil
import pickle

import base_model

import bz_web
import bz_gl
import bz_utils
              
def Schedule_SynBugList(env, req, db_conn, bugz, cc):  
    import sprd_user_model
    a_user_obj = sprd_user_model.SPRD_User(None)
    all_Users = []
    all_mem = a_user_obj.Get_All_Member('leo.li')             
    if all_mem is not None:
        all_users = [ a_user['EName'].lower().replace(' ', '.') for a_user in all_mem]             
    all_users.append(('leo.li'))     
    env.log.error('Schedule_SynBugList: all_users=%s', all_users)
    
    #env.log.error('Schedule_SynBugList: ++ all_units=%s', bz_gl.bz_sprd_all_usr(env)) 
    Syn_Bugz_BugList(env, req, db_conn, bugz, all_users, cc)     
    Syn_Bugz_BugList_Depart(env, req, db_conn, all_users, cc)
    env.log.error('Schedule_SynBugList: --') 
      
    
def Syn_Bugz_BugList_Depart(env, req, db_conn, all_units, cc):   #10min
        a_Ower_table = Bugz_Ower(None, db_conn) 
        a_BugList_table = Bugz_BugList(None, db_conn) 
        env.log.error('Syn_Bugz_BugList_Depart: all_units= %s', all_units)         
        
        lenth = len(all_units)
        a_QF = {}  
        b_QF = {}     
        for a_user in all_units:              
            
            level = {}            
            
            a_QF['field_ower'] = a_user            
            a_row = a_Ower_table.select(a_QF)
            length = len(a_row)  
            env.log.error('Syn_Bugz_BugList_Depart: lenth=%s, a_user=%s', lenth, a_user) 
            if length == 1:  
                for Item in a_row:
                    level['level1'] = Item['level1']
                    level['level2'] = Item['level2']
                    level['level3'] = Item['level3']
                    level['level4'] = Item['level4']
                    break
            else:
                continue                
            
            b_QF['field_assigned_to'] = a_user + '@spreadtrum.com'  
            b_row = a_BugList_table.select(b_QF)
            for Item in b_row:                 
                ID = Item['ID']
                b_Ower_table = Bugz_BugList(ID, db_conn)  
                b_Ower_table['level4'] = level['level4']
                b_Ower_table['level3'] = level['level3']
                b_Ower_table['level2'] = level['level2']
                b_Ower_table['level1'] = level['level1']
                b_Ower_table.save_changes()             
            lenth = lenth -1             
            env.log.error('save_changes: a_user=%s', a_user) 
        env.log.error('Syn_Bugz_BugList_Depart finish %s', cc)                


def Syn_Bugz_BugList(env, req, db_conn, bugz, all_units, cc):   #4hours
        env.log.error('Syn_Bugz_BugList: all_units %s', all_units)  
        
        collist = bz_web.bz_old_collist(req) 
        QF = {}   
        
        lenth = len(all_units)
        a_Bugz_table = Bugz_BugList(None, db_conn)
        
        for a_user in all_units:  
            assigned_to = a_user
            assigned_to += '@spreadtrum.com' 
            
            env.log.error('Syn_Bugz_BugList: lenth=%s, a_user=%s', lenth, a_user)      
            rows = []
            query_url = bugz.BG_SearchUrl('', assigned_to=assigned_to, collist=collist)
            bugz.BG_Search(query_url, rows, collist=collist)
            
            import sys
            reload(sys)
            sys.setdefaultencoding('utf-8')
           
            for row in rows:
                QF = {}   
                QF['field_bug_id'] = row['bug_id']
                row_Bugz_table = a_Bugz_table.select(QF)
                length = len(row_Bugz_table)    

                #env.log.error('Syn_Bugz_BugList row=%s', row)
                if length == 0:            
                    for f in a_Bugz_table.fields:
                        fname = f['name']
                        if fname == 'level4' or fname == 'level3' \
                                or fname == 'level2' or fname == 'level1':
                            pass
                        elif fname == 'start_time':
                            a_Bugz_table[fname] = bz_utils.timestring2week(env, row['opendate'])  
                        elif fname == 'end_time':
                            if row['cf_fixeddate'] is not None and row['cf_fixeddate'] != '':
                                a_Bugz_table[fname] = bz_utils.timestring2week(env, row['cf_fixeddate'])
                            elif row['cf_closeddate'] is not None and row['cf_closeddate'] != '':
                                a_Bugz_table[fname] = bz_utils.timestring2week(env, row['cf_closeddate'])
                            else:
                                a_Bugz_table[fname] = 'NULL'                                                        
                        else:
                            a_Bugz_table[fname] = row[fname].encode('utf-8')
                    a_Bugz_table.insert()
                    env.log.error('Syn_Bugz_BugList insert bug_id=%s', row['bug_id'])
                elif length == 1:  
                    for Query_Item in row_Bugz_table:   
                        ID = Query_Item['ID'] 
                        break
                    b_Bugz_table = Bugz_BugList(ID, db_conn)  
                    #env.log.error('Syn_Bugz_BugList save_changes ++ bug_id=%s', row['bug_id'])
                    for f in a_Bugz_table.fields:
                        fname = f['name']
                        if fname == 'ID' or fname == 'level4' or fname == 'level3' \
                                or fname == 'level2' or fname == 'level1':
                            pass
                        elif fname == 'start_time':
                            b_Bugz_table[fname] =  bz_utils.timestring2week(env, row['opendate'])  
                        elif fname == 'end_time':
                            #env.log.error('Syn_Bugz_BugList save_changes ++ cf_fixeddate=%s', row['cf_fixeddate'])
                            #env.log.error('Syn_Bugz_BugList save_changes ++ cf_closeddate=%s', row['cf_closeddate'])
                            if row['cf_fixeddate'] is not None and row['cf_fixeddate'] != '':
                                b_Bugz_table[fname] = bz_utils.timestring2week(env, row['cf_fixeddate'])
                            elif row['cf_closeddate'] is not None and row['cf_closeddate'] != '':
                                b_Bugz_table[fname] = bz_utils.timestring2week(env, row['cf_closeddate'])
                            else:
                                b_Bugz_table[fname] = 'NULL'                       
                        else:
                            b_Bugz_table[fname] = row[fname].encode('utf-8')   
                    b_Bugz_table.save_changes() 
                    #env.log.error('Syn_Bugz_BugList save_changes -- bug_id=%s', row['bug_id'])
                else:
                    #del
                    for Query_Item in row_Bugz_table:   
                        ID = Query_Item['ID'] 
                        b_Bugz_table = Bugz_BugList(ID, db_conn)  
                        env.log.error('Syn_Bugz_BugList del %s, bug_id=%s, assigned_to=%s', ID, b_Bugz_table['bug_id'], b_Bugz_table['assigned_to'])                        
                        b_Bugz_table.delete()                   
                
            lenth = lenth -1         
        env.log.error('Syn_Bugz_BugList finish %s', cc)



def Syn_Bugz_Depart_leader(env, req, db_conn, all_units, cc):   
        #录入三级部门领导
        import sprd_user_model
        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')        
        
        env.log.error('Syn_Bugz_Depart_leader start %s', cc)
        a_user_obj = sprd_user_model.SPRD_User(None) 
        a_Bugz_table = Bugz_Depart(None, db_conn)
        rows = []  
        
        all_Dep_Level_1 = a_user_obj.Get_Dep_Level_1()
        env.log.error('Syn_Bugz_Depart_leader all_Dep_Level_1= %s', all_Dep_Level_1) 
        
        for a_dep_l1 in all_Dep_Level_1:
            fields = {}   
            fields['leader'] = '--'
            rows.append(fields)
            
            all_Dep_Level_2 = a_user_obj.Get_Dep_Level_2(a_dep_l1)
            env.log.error('Syn_Bugz_Depart_leader a_dep_l1=%s, all_Dep_Level_2= %s', a_dep_l1, all_Dep_Level_2) 
            for a_dep_l2 in all_Dep_Level_2:
                fields = {}    
                fields['leader'] = '--'
                rows.append(fields) 
                
                all_Dep_Level_3 = a_user_obj.Get_Dep_Level_3(a_dep_l1, a_dep_l2)
                env.log.error('Syn_Bugz_Depart_leader a_dep_l2=%s, all_Dep_Level_3= %s', a_dep_l2, all_Dep_Level_3) 
                for a_dep_l3 in all_Dep_Level_3:
                    fields = {}          
                    fields['leader'] = '--'
                    rows.append(fields)                  
                    env.log.error('Syn_Bugz_Depart_leader a_dep_l3=%s', a_dep_l3)                    

        env.log.error('Syn_Bugz_Depart_leader start in DB %s', cc)            
        for row in rows:            
            QF = {}   
            a_key = row['name']
            QF['field_name'] = a_key
            row_Bugz_table = a_Bugz_table.select(QF)
            length = len(row_Bugz_table)    
            env.log.error('Syn_Bugz_Depart_leader %s %s ', a_key, length)   
            if length == 1:  
                for Query_Item in row_Bugz_table:
                    ID = Query_Item['ID']
                    break
                b_Bugz_table = Bugz_Depart(ID, db_conn)  
                for f in a_Bugz_table.fields:
                    fname = f['name']
                    if fname == 'leader':
                        b_Bugz_table[fname] = row[fname].encode('utf-8')   
                b_Bugz_table.save_changes()    
                env.log.error('Syn_Bugz_Depart_leader save_changes- %s', a_key)        
        env.log.error('Syn_Bugz_Depart_leader finish %s', cc)


def Syn_Bugz_Depart_3levels(env, req, db_conn, all_units, cc):   
        #录入三级部门
        import sprd_user_model
        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')        
        
        env.log.error('Syn_Bugz_Depart_3levels start %s', cc)
        a_user_obj = sprd_user_model.SPRD_User(None) 
        a_Bugz_table = Bugz_Depart(None, db_conn)
        rows = []  
        
        all_Dep_Level_1 = a_user_obj.Get_Dep_Level_1()
        env.log.error('_P_SynchronizeDepart_3levels all_Dep_Level_1= %s', all_Dep_Level_1) 
        for a_dep_l1 in all_Dep_Level_1:
            fields = {}              
            fields['name'] = a_dep_l1
            fields['level_type'] = 'level1'
            fields['up_name'] = '--'
            fields['leader'] = '--'
            rows.append(fields)
            
            all_Dep_Level_2 = a_user_obj.Get_Dep_Level_2(a_dep_l1)
            env.log.error('_P_SynchronizeDepart_3levels a_dep_l1=%s, all_Dep_Level_2= %s', a_dep_l1, all_Dep_Level_2) 
            for a_dep_l2 in all_Dep_Level_2:
                fields = {}              
                fields['name'] = a_dep_l2
                fields['level_type'] = 'level2'
                fields['up_name'] = a_dep_l1
                fields['leader'] = '--'
                rows.append(fields) 
                
                all_Dep_Level_3 = a_user_obj.Get_Dep_Level_3(a_dep_l1, a_dep_l2)
                env.log.error('_P_SynchronizeDepart_3levels a_dep_l2=%s, all_Dep_Level_3= %s', a_dep_l2, all_Dep_Level_3) 
                for a_dep_l3 in all_Dep_Level_3:
                    fields = {}              
                    fields['name'] = a_dep_l3
                    fields['level_type'] = 'level3'
                    fields['up_name'] = a_dep_l2
                    fields['leader'] = '--'
                    rows.append(fields)                  
                    env.log.error('_P_SynchronizeDepart_3levels a_dep_l3=%s', a_dep_l3)                    

        env.log.error('Syn_Bugz_Depart_3levels start in DB %s', cc)            
        for row in rows:            
            QF = {}   
            a_key = row['name']
            QF['field_name'] = a_key
            row_Bugz_table = a_Bugz_table.select(QF)
            length = len(row_Bugz_table)    
            env.log.error('Syn_Bugz_Depart_3levels %s %s ', a_key, length)   
            if length == 0: 
                for f in a_Bugz_table.fields:
                    fname = f['name']
                    a_Bugz_table[fname] = row[fname].encode('utf-8') 
                a_Bugz_table.insert()
                env.log.error('Syn_Bugz_Depart_3levels insert- %s', a_key)
            elif length == 1:  
                for Query_Item in row_Bugz_table:
                    ID = Query_Item['ID']
                    break
                b_Bugz_table = Bugz_Depart(ID, db_conn)  
                for f in a_Bugz_table.fields:
                    fname = f['name']
                    if fname == 'level_type' or fname == 'leader' \
                                or fname == 'up_name':
                        b_Bugz_table[fname] = row[fname].encode('utf-8')   
                b_Bugz_table.save_changes()    
                env.log.error('Syn_Bugz_Depart_3levels save_changes- %s', a_key)        
        env.log.error('Syn_Bugz_Depart_3levels finish %s', cc)


def Syn_Bugz_Ower_3levels(env, req, db_conn, all_units, cc):   
        #录入三级个人部门信息
        import sprd_user_model
        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')        
        
        env.log.error('Syn_Bugz_Ower_3levels start %s', cc)
        a_user_obj = sprd_user_model.SPRD_User(None) 
        a_Bugz_table = Bugz_Ower(None, db_conn)

        rows = []  
        for a_user in all_units: 
            fields = {}  
            a_sn = a_user_obj.Get_Badge(a_user) 
            fields['ower'] = a_user
            fields['level1'] = a_user_obj.Get_Dep1(a_sn)
            fields['level2'] = a_user_obj.Get_Dep2(a_sn)
            fields['level3'] = a_user_obj.Get_Dep3(a_sn)
            fields['level4'] = '--'
            rows.append(fields)

        env.log.error('Syn_Bugz_Ower_3levels start in DB %s', cc)            
        for row in rows:            
            QF = {}   
            a_user = row['ower']
            QF['field_ower'] = a_user
            row_Bugz_table = a_Bugz_table.select(QF)
            length = len(row_Bugz_table)    
            env.log.error('Syn_Bugz_Ower %s %s ', a_user, length)   
            if length == 0: 
                for f in a_Bugz_table.fields:
                    fname = f['name']
                    if fname == 'level4' or fname == 'level3' \
                                or fname == 'level2' or fname == 'level1' \
                                or fname == 'ower':
                        a_Bugz_table[fname] = row[fname].encode('utf-8') 
                a_Bugz_table.insert()
                #env.log.error('Syn_Bugz_Ower_3levels insert- %s', a_user)
            elif length == 1:  
                for Query_Item in row_Bugz_table:
                    ID = Query_Item['ID']
                    break
                b_Bugz_table = Bugz_Ower(ID, db_conn)  
                for f in a_Bugz_table.fields:
                    fname = f['name']
                    if fname == 'level4' or fname == 'level3' \
                                or fname == 'level2' or fname == 'level1':
                        b_Bugz_table[fname] = row[fname].encode('utf-8')   
                b_Bugz_table.save_changes()    
                env.log.error('Syn_Bugz_Ower_3levels save_changes- %s', a_user)        
        env.log.error('Syn_Bugz_Ower_3levels finish %s', cc)

def Syn_Bugz_Depart(env, req, db_conn, all_units, cc):   
        #录入一个部门
        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')        
        
        env.log.error('Syn_Bugz_Depart start %s', cc)
        a_Bugz_table = Bugz_Depart(None, db_conn)

        Level = req.args.get(bz_gl.gl_DepartmentLevel)
        Name = req.args.get(bz_gl.gl_DepartmentName)
        Leader = req.args.get(bz_gl.gl_DepartmentLeader)
        UpName = req.args.get(bz_gl.gl_DepartmentUpName)
            
        rows = []  
        if 1: 
            fields = {}  
            fields['name'] = Name
            fields['level_type'] = Level
            fields['leader'] = Leader
            fields['up_name'] = UpName
            rows.append(fields)               

        env.log.error('Syn_Bugz_Depart start in DB %s', cc)            
        for row in rows:            
            a_key = row['name']
            QF = {}   
            QF['field_name'] = a_key                        
            row_Bugz_table = a_Bugz_table.select(QF)
            length = len(row_Bugz_table)    
            env.log.error('Syn_Bugz_Depart %s %s ', a_key, length)
            if length == 0: 
                for f in a_Bugz_table.fields:
                    fname = f['name']
                    a_Bugz_table[fname] = row[fname].encode('utf-8')
                a_Bugz_table.insert()
                env.log.error('Syn_Bugz_Depart insert- %s', a_key)
            elif length == 1:  
                for Query_Item in row_Bugz_table:
                    ID = Query_Item['ID']
                    break
                b_Bugz_table = Bugz_Depart(ID, db_conn)  
                for f in a_Bugz_table.fields:
                    fname = f['name']
                    if fname != 'name':
                        if row[fname] is not None and row[fname] != '':
                            b_Bugz_table[fname] = row[fname].encode('utf-8')
                b_Bugz_table.save_changes()    
                env.log.error('Syn_Bugz_Depart save_changes- %s', a_key)                
        env.log.error('Syn_Bugz_Depart finish %s', cc)


def Syn_Bugz_Ower(env, req, db_conn, all_units, cc):   
        #录入一个级别的部门
        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')        
        
        env.log.error('Syn_Bugz_Ower start %s', cc)
        a_Bugz_table = Bugz_Ower(None, db_conn)

        level = req.args.get(bz_gl.gl_DepartmentLevel)
        value = req.args.get(bz_gl.gl_DepartmentName)
        if value is None:  
            value = ''

        rows = []  
        for a_user in all_units: 
            fields = {}  
            fields['ower'] = a_user
            fields['level'] = level
            fields['value'] = value
            rows.append(fields)               

        env.log.error('Syn_Bugz_Ower start in DB %s', cc)            
        for row in rows:            
            a_user = row['ower']
            level = row['level']
            value = row['value']
            QF = {}   
            QF['field_ower'] = a_user                        
            row_Bugz_table = a_Bugz_table.select(QF)
            length = len(row_Bugz_table)    
            env.log.error('Syn_Bugz_Ower %s %s ', a_user, length)
            if length == 0: 
                for f in a_Bugz_table.fields:
                    fname = f['name']
                    if fname == level:
                        a_Bugz_table[fname] = value 
                    elif fname == 'ower':
                        a_Bugz_table[fname] = a_user
                a_Bugz_table.insert()
                env.log.error('Syn_Bugz_Ower insert- %s', a_user)
            elif length == 1:  
                for Query_Item in row_Bugz_table:
                    ID = Query_Item['ID']
                    break
                b_Bugz_table = Bugz_Ower(ID, db_conn)  
                for f in a_Bugz_table.fields:
                    fname = f['name']
                    if fname == level:
                        b_Bugz_table[fname] = value   
                b_Bugz_table.save_changes()    
                env.log.error('Syn_Bugz_Ower save_changes- %s', a_user)                
        env.log.error('Syn_Bugz_Ower finish %s', cc)


def sqldb():
    #db=MySQLdb.connect(host='172.16.0.230',port=3306,user='ibuildadmin', passwd='SPD#ibuildapp', db='ibuild',charset='utf8')
    #db=MySQLdb.connect(host='10.0.0.175',port=3306,user='iadmin', passwd='itask#ADMIN89', db='imanage',charset='utf8')
    db=MySQLdb.connect(host='10.0.0.175',port=3306,user='ilogadmin', passwd='SPD@ilogservice99', db='ilog',charset='utf8')
    return db

class BugzReminder(base_model.base):
    def __init__(self, id, db):
        self.fields = []
        self.fields.append({'name':'Headline', 'control':'input'})
        self.fields.append({'name':'Submitter', 'control':'input'})

        self.fields.append({'name':'SubmittedDate', 'control':'input'}) 
        self.fields.append({'name':'State', 'control':'input'})  
        self.fields.append({'name':'RemindType', 'control':'input'})      
        self.fields.append({'name':'RemindWeek', 'control':'input'})  


        self.fields.append({'name':'RemindMonth', 'control':'input'}) 
        self.fields.append({'name':'RemindInterval', 'control':'input'})  
        self.fields.append({'name':'RemindCounter', 'control':'input'})      
        self.fields.append({'name':'RemindStartDate', 'control':'input'})         

        self.fields.append({'name':'RemindEndDate', 'control':'input'}) 
        
        self.fields.append({'name':'EmailTo', 'control':'input'})  
        self.fields.append({'name':'EmailCc', 'control':'input'})  
        self.fields.append({'name':'EmailContent', 'control':'input'})  
        
        self.fields.append({'name':'ElapseTime', 'control':'input'})      
        self.fields.append({'name':'BugzQueryID', 'control':'input'})  
        self.fields.append({'name':'RemindTime', 'control':'input'})      
        self.fields.append({'name':'RemindAction', 'control':'input'}) 

        base_model.base.__init__(self, id, 'BugzReminder',self.fields, db)

    def select_enable(self):
        AllRows=[]
        all_fileds = ['ID'] + [f['name'] for f in self.fields if f['control'] != 'list']         
        cursor = self.db.cursor()
        where_str = " where State<>'disable'" 
        sql = "SELECT " + ','.join(all_fileds)  +  "  FROM  " +   self.table_name  + where_str + ' order by ID desc'            
        assert sql is not None, sql
        cursor.execute(sql)
    
        for row in cursor:
            tmp={}
            if row:
                for i, field in enumerate(all_fileds) : 
                    if row[i]:
                        tmp[field]=unicode(row[i]).strip()
                    else :
                        tmp[field]=''
            AllRows.append(tmp)
        return AllRows


class BugzQuery(base_model.base):

    def __init__(self, id, db):
        self.fields = []
        self.fields.append({'name':'ower', 'control':'input'})         
        self.fields.append({'name':'name', 'control':'input'})
        
        self.fields.append({'name':'product', 'control':'input'})
        self.fields.append({'name':'component', 'control':'input'})
        self.fields.append({'name':'bug_status', 'control':'input'})        
        self.fields.append({'name':'bug_severity', 'control':'input'})
        self.fields.append({'name':'cf_come_from', 'control':'input'})
        
        self.fields.append({'name':'f3', 'control':'input'})
        self.fields.append({'name':'o3', 'control':'input'})
        self.fields.append({'name':'v3', 'control':'input'})  
        
        self.fields.append({'name':'f1', 'control':'input'})
        self.fields.append({'name':'o1', 'control':'input'})  
        self.fields.append({'name':'v1', 'control':'input'}) 

        self.fields.append({'name':'f2', 'control':'input'})
        self.fields.append({'name':'o2', 'control':'input'})  
        self.fields.append({'name':'v2', 'control':'input'}) 
        
        self.fields.append({'name':'columnlist', 'control':'input'})  
        self.fields.append({'name':'ibugz_col', 'control':'input'}) 
        self.fields.append({'name':'custom_statics', 'control':'input'}) 

        self.fields.append({'name':'advance_field', 'control':'input'}) 
        self.fields.append({'name':'tree', 'control':'input'}) 
        self.fields.append({'name':'treetype', 'control':'input'}) 
        
        self.fields.append({'name':'orderby', 'control':'input'}) 
        self.fields.append({'name':'csv_start_time', 'control':'input'})  
        self.fields.append({'name':'csv_end_time', 'control':'input'})    
        self.fields.append({'name':'csv_history', 'control':'input'})          

        self.fields.append({'name':'chfield', 'control':'input'}) 
        self.fields.append({'name':'chfieldfrom', 'control':'input'}) 
        self.fields.append({'name':'chfieldto', 'control':'input'})    
        self.fields.append({'name':'product_ower', 'control':'input'})
        base_model.base.__init__(self, id, 'BugzQuery',self.fields, db)


class Bugz_BugList(base_model.base):    
    #bug_id, short_desc, assigned_to,product,component,bug_severity,bug_status,cf_base_on_ver,cf_fix_on_ver,
    #reporter,cf_come_from,changeddate,opendate,cf_assigneddate,cf_rootcauseddate,cf_fixeddate,cf_closeddate   

    #resolution
    def __init__(self, id, db):
        self.fields = []
        self.fields.append({'name':'bug_id', 'control':'input'})        
        self.fields.append({'name':'short_desc', 'control':'input'})
        self.fields.append({'name':'assigned_to', 'control':'input'})
        self.fields.append({'name':'product', 'control':'input'})        
        self.fields.append({'name':'component', 'control':'input'})        
        self.fields.append({'name':'bug_severity', 'control':'input'})
        self.fields.append({'name':'bug_status', 'control':'input'})
        self.fields.append({'name':'cf_base_on_ver', 'control':'input'})        
        self.fields.append({'name':'cf_fix_on_ver', 'control':'input'})  
        
        self.fields.append({'name':'reporter', 'control':'input'})
        self.fields.append({'name':'cf_come_from', 'control':'input'})        
        self.fields.append({'name':'changeddate', 'control':'input'})   
        self.fields.append({'name':'opendate', 'control':'input'}) 
        self.fields.append({'name':'cf_assigneddate', 'control':'input'}) 
        self.fields.append({'name':'cf_rootcauseddate', 'control':'input'})  
        self.fields.append({'name':'cf_fixeddate', 'control':'input'})      
        self.fields.append({'name':'cf_closeddate', 'control':'input'})   

        self.fields.append({'name':'level4', 'control':'input'}) 
        self.fields.append({'name':'level3', 'control':'input'})  
        self.fields.append({'name':'level2', 'control':'input'})      
        self.fields.append({'name':'level1', 'control':'input'})     

        self.fields.append({'name':'start_time', 'control':'input'})   
        self.fields.append({'name':'end_time', 'control':'input'}) 
        self.fields.append({'name':'resolution', 'control':'input'}) 
        
        base_model.base.__init__(self, id, 'Bugz_BugList',self.fields, db)

    

class Bugz_Ower(base_model.base):
    def __init__(self, id, db):
        self.fields = []
        self.fields.append({'name':'ower', 'control':'input'})
        self.fields.append({'name':'report_to', 'control':'input'})

        self.fields.append({'name':'level4', 'control':'input'}) 
        self.fields.append({'name':'level3', 'control':'input'})  
        self.fields.append({'name':'level2', 'control':'input'})      
        self.fields.append({'name':'level1', 'control':'input'})                    
        base_model.base.__init__(self, id, 'Bugz_Ower',self.fields, db)

class Bugz_Depart(base_model.base):
    def __init__(self, id, db):
        self.fields = []
        self.fields.append({'name':'name', 'control':'input'})
        self.fields.append({'name':'level_type', 'control':'input'})

        self.fields.append({'name':'leader', 'control':'input'}) 
        self.fields.append({'name':'up_name', 'control':'input'})                  
        base_model.base.__init__(self, id, 'Bugz_Depart',self.fields, db)


