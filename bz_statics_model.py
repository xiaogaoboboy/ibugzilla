
import re
import os
import MySQLdb
import shutil
import pickle

import base_model

class Bugz_Statics(base_model.base):


    def __init__(self, id, db):
        self.fields = []
        self.fields.append({'name':'Assignee', 'control':'input'})
        
        self.fields.append({'name':'TotalBugs', 'control':'input'})
        self.fields.append({'name':'TodoBugs', 'control':'input'})
        self.fields.append({'name':'DoneBugs', 'control':'input'}) 
        
        self.fields.append({'name':'open2assign', 'control':'input'})
        self.fields.append({'name':'assign2root_cause', 'control':'input'})
        self.fields.append({'name':'root_cause2fix', 'control':'input'})        
        self.fields.append({'name':'fix2close', 'control':'input'})  
        
        base_model.base.__init__(self, id, 'Bugz_Statics',self.fields, db)

    
    def synchronize(self, env, rows, db_conn,a_Bugz_Statics):   
        import thread
        #env.log.error('synchronize  in')      
        #self.log.error('synchronize  in2')    
        thread.start_new_thread(self.synchronize_db, (env, rows,db_conn,a_Bugz_Statics, 'haha'))  
        #env.log.error('synchronize  out')
        #self.log.error('synchronize  out2') 


    def synchronize_db(self, env, rows,db_conn,a_Bugz_Statics, cc): 
        #env.log.error('synchronize_db start \nrows=%s', rows)
        for row in rows: 
                #env.log.error('synchronize_db start \nrow=%s', row)
                for idx,col in enumerate(row):                 
                    if idx == 0:
                        a_Bugz_Statics['Assignee'] = col
                    elif idx == 1:
                        a_Bugz_Statics['TotalBugs'] = col  
                    elif idx == 2:
                        a_Bugz_Statics['TodoBugs'] = col                          
                    elif idx == 3:
                        a_Bugz_Statics['DoneBugs'] = col   
                    elif idx == 4:
                        a_Bugz_Statics['open2assign'] = col   
                    elif idx == 5:
                        a_Bugz_Statics['assign2root_cause'] = col 
                    elif idx == 6:
                        a_Bugz_Statics['root_cause2fix'] = col 
                    elif idx == 7:
                        a_Bugz_Statics['fix2close'] = col   

                QF = {}   
                QF['field_Assignee'] = a_Bugz_Statics['Assignee']
                env.log.error('synchronize_db assignee 1= %s', a_Bugz_Statics['Assignee'])
                rows_Bugz_Statics = a_Bugz_Statics.select(QF)
                length = len(rows_Bugz_Statics)
                env.log.error('synchronize_db assignee 2= %s,length=%s', a_Bugz_Statics['Assignee'], length)
                if length == 0:
                    #env.log.error('synchronize_db insert 1assignee = %s', a_Bugz_Statics['Assignee'])
                    a_Bugz_Statics.insert()
                    #env.log.error('synchronize_db insert 2assignee = %s', a_Bugz_Statics['Assignee'])
                elif length == 1:
                    #env.log.error('synchronize_db update 1assignee = %s', a_Bugz_Statics['Assignee'])
                    for Query_Item in rows_Bugz_Statics:   
                        ID = Query_Item['ID']  
                    #env.log.error('synchronize_db update 2 = %s,%s', rows_Bugz_Statics,ID)
                    b_Bugz_Statics = Bugz_Statics(ID, db_conn)   
                    b_Bugz_Statics['TotalBugs'] = a_Bugz_Statics['TotalBugs']
                    b_Bugz_Statics['TodoBugs'] = a_Bugz_Statics['TodoBugs']
                    b_Bugz_Statics['DoneBugs'] = a_Bugz_Statics['DoneBugs']
                    b_Bugz_Statics['open2assign'] = a_Bugz_Statics['open2assign']
                    b_Bugz_Statics['assign2root_cause'] = a_Bugz_Statics['assign2root_cause']
                    b_Bugz_Statics['root_cause2fix'] = a_Bugz_Statics['root_cause2fix']
                    b_Bugz_Statics['fix2close'] = a_Bugz_Statics['fix2close']
                    b_Bugz_Statics.save_changes()
                    #env.log.error('synchronize_db update 2assignee = %s', a_Bugz_Statics['Assignee'])
        env.log.error('synchronize_db finish %s', cc)




