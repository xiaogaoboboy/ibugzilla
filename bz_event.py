
# -*- coding: utf-8 -*-
#

import shutil
import calendar
import struct
import posixpath
import os, sys, re 
import time
import re
from datetime import datetime, timedelta

from StringIO import StringIO
from trac.util import format_datetime

import bz_gl
import bz_model
import bz_api

def bz_event_main(env):    
    db_conn = bz_model.sqldb()      
    a_table = bz_model.BugzReminder(None, db_conn)
    QF = {}
    QF['field_State'] = 'enable'
    rows = a_table.select(QF) 
    #rows = a_table.select_enable()
    env.log.error('bz_event_main: datetime.now() = %s', datetime.now() )   
    #env.log.error('bz_event_main: rows = %s', rows ) 
    for row in rows:
        env.log.error('bz_event_main: ID=%s, %s', row['ID'], row)
        bz_event_remind(env, row, db_conn)   
    return  

def bz_event_remind(env, row, db_conn):
    t_currenttime = CurrentTime19()
    #Run_Interval=60*60 
    Run_Interval=bz_gl.gl_Run_Interval      

    if 1:        
        SYSFields=bz_gl.gl_RemindSYSFields
        UIFields=bz_gl.gl_RemindUIFields
        MultiInputFields = bz_gl.gl_RemindUIMultiInputFields
        CheckboxFields=bz_gl.gl_RemindCheckboxFields        
        UIFields = UIFields + CheckboxFields + MultiInputFields
        AllFields = SYSFields + UIFields 
        
        #env.log.error('bz_event_remind: AllFields=%s', AllFields)
        ReaminderValue ={}
        for a_field  in AllFields: 
            if a_field == 'BugzQueryID':
                #env.log.error('bz_event_remind: row[BugzQueryID]=%s', row[a_field])
                ReaminderValue[a_field]=row[a_field]
            else:
                #env.log.error('bz_event_remind: row[a_field]=%s', row[a_field])
                if row[a_field]:
                    ReaminderValue[a_field]=unicode(row[a_field]).strip()
                else :
                    ReaminderValue[a_field]=''  
        #env.log.error('bz_event_remind: ReaminderValue=%s', ReaminderValue)    

    RemindType = ReaminderValue["RemindType"].strip()
    RemindMonth=ReaminderValue['RemindMonth'].strip()
    RemindWeek=ReaminderValue['RemindWeek'].strip()      
    
    RemindInterval=0
    if ReaminderValue['RemindInterval'].strip():
        RemindInterval = int(ReaminderValue['RemindInterval'].strip()) *60*60
    if RemindInterval==0:
        RemindInterval = 60*60

    Start_Time = ReaminderValue['RemindStartDate'].strip()
    End_Time = ReaminderValue['RemindEndDate'].strip()
    if End_Time:
        End_Time=End_Time+':00'
    if Start_Time:
        Start_Time=Start_Time+':00'

    RemindCounter = ReaminderValue['RemindCounter'].strip()      
    if not RemindCounter:
        RemindCounter=0
    else:
        RemindCounter=int(RemindCounter)    
        
    #env.log.error('bz_event_remind: RemindType=%s', RemindType)  
    #env.log.error('bz_event_remind: %s, %s', Start_Time, End_Time)  
    #env.log.error('bz_event_remind: t_currenttime= %s', t_currenttime)  
    ReminderDateArray=[]
            
    #if RemindType=="D" :
    if 0:
        if t_currenttime>=Start_Time and t_currenttime<=End_Time: 
            RemindStartDate = datetime(int(Start_Time[0:4]), int(Start_Time[5:7]),int(Start_Time[8:10]), int(Start_Time[11:13]), int(Start_Time[14:16]),0)
            weekNO = int(datetime.strftime(RemindStartDate,"%U"))
            weekNO_NOW = int(datetime.strftime(RemindStartDate,"%U"))
            str_RemindStartDate = RemindStartDate.strftime("%Y-%m-%d %H-%M-%S") 
            a_week = RemindStartDate.strftime("%w") 
            if a_week=='0':
                weekNO_NOW=weekNO_NOW-1
                weekNO = weekNO -1
                a_week='7'
            int_count=0

            while(str_RemindStartDate<End_Time and int_count<=RemindCounter ):
                if a_week in RemindWeek and  weekNO%2 ==weekNO_NOW%2:
                    ReminderDateArray.append(RemindStartDate)
                    print RemindStartDate.strftime("%Y-%m-%d %H-%M-%S") 

                    int_count=1
                    if RemindInterval:
                        while int_count<RemindCounter:
                            tmp_RemindStartDate = RemindStartDate + timedelta(seconds=int(RemindInterval)*int_count)
                            str_tmp_RemindStartDate = tmp_RemindStartDate.strftime("%Y-%m-%d %H-%M-%S") 
                            if str_tmp_RemindStartDate<=End_Time and int_count<=RemindCounter:
                                int_count+=1
                                ReminderDateArray.append(tmp_RemindStartDate)
                                print tmp_RemindStartDate.strftime("%Y-%m-%d %H-%M-%S") 
                RemindStartDate = RemindStartDate  + timedelta(seconds=RemindInterval*24)
                weekNO_NOW = int(datetime.strftime(RemindStartDate,"%U"))
                str_RemindStartDate = RemindStartDate.strftime("%Y-%m-%d %H-%M-%S") 
                a_week = RemindStartDate.strftime("%w") 
                if a_week=='0':
                    weekNO_NOW=weekNO_NOW-1
                    a_week='7'
                
            
    if RemindType=="F" :
        RemindStartDate = datetime(int(Start_Time[0:4]), int(Start_Time[5:7]),int(Start_Time[8:10]), int(Start_Time[11:13]), int(Start_Time[14:16]),0)
        ReminderDateArray.append(RemindStartDate)        
        #env.log.error('bz_event_remind: RemindStartDate= %s', RemindStartDate.strftime("%Y-%m-%d %H-%M-%S") )  
        #env.log.error('bz_event_remind: ReminderDateArray= %s', ReminderDateArray)  
        #if RemindInterval:
        if 0:
            int_count=1
            RemindStartDate = RemindStartDate + timedelta(seconds=int(RemindInterval))
            str_RemindStartDate = RemindStartDate.strftime("%Y-%m-%d %H-%M-%S") 
            while str_RemindStartDate<End_Time and  int_count<RemindCounter:
                ReminderDateArray.append(RemindStartDate)
                int_count+=1
                print RemindStartDate.strftime("%Y-%m-%d %H-%M-%S")  
                RemindStartDate = RemindStartDate + timedelta(seconds=int(RemindInterval))
                str_RemindStartDate = RemindStartDate.strftime("%Y-%m-%d %H-%M-%S") 

    if RemindType=="W" :
        if t_currenttime>=Start_Time and t_currenttime<=End_Time: 
            RemindStartDate = datetime(int(Start_Time[0:4]), int(Start_Time[5:7]),int(Start_Time[8:10]), int(Start_Time[11:13]), int(Start_Time[14:16]),0)
            str_RemindStartDate = RemindStartDate.strftime("%Y-%m-%d %H-%M-%S") 
            a_week = RemindStartDate.strftime("%w")             
            if a_week=='0':
                a_week='7'
            #int_count=0
            #while(str_RemindStartDate<End_Time  and int_count<=RemindCounter ):
            while(str_RemindStartDate<End_Time):
                if a_week in RemindWeek:
                    ReminderDateArray.append(RemindStartDate)
                    #print RemindStartDate.strftime("%Y-%m-%d %H-%M-%S") 
                    #env.log.error('bz_event_remind: w RemindStartDate= %s', RemindStartDate.strftime("%Y-%m-%d %H-%M-%S") ) 
                    int_count=1
                    if 0:
                    #if RemindInterval:
                        while int_count<RemindCounter:
                            tmp_RemindStartDate = RemindStartDate + timedelta(seconds=int(RemindInterval)*int_count)
                            str_tmp_RemindStartDate = tmp_RemindStartDate.strftime("%Y-%m-%d %H-%M-%S") 
                            if str_tmp_RemindStartDate>End_Time or int_count>RemindCounter:
                                break
                            else:
                                int_count+=1
                            ReminderDateArray.append(tmp_RemindStartDate)
                            print tmp_RemindStartDate.strftime("%Y-%m-%d %H-%M-%S") 
                RemindStartDate = RemindStartDate  + timedelta(seconds=RemindInterval*24)
                str_RemindStartDate = RemindStartDate.strftime("%Y-%m-%d %H-%M-%S") 
                a_week = RemindStartDate.strftime("%w") 
                if a_week=='0':
                    a_week='7'

    if RemindType=="M" :      
        if t_currenttime>=Start_Time and t_currenttime<=End_Time: 
            for a_day in RemindMonth.split(','):
                #env.log.error('bz_event_remind: M a_day= %s', a_day ) 
                if a_day=='':
                    continue;
                RemindStartDate = datetime(int(Start_Time[0:4]), int(Start_Time[5:7]),int(a_day), int(Start_Time[11:13]), int(Start_Time[14:16]),0)
                ReminderDateArray.append(RemindStartDate)
                #print RemindStartDate.strftime("%Y-%m-%d %H-%M-%S") 
                #env.log.error('bz_event_remind: M RemindStartDate= %s', RemindStartDate.strftime("%Y-%m-%d %H-%M-%S") ) 
                #if RemindInterval:
                if 0:
                    int_count=1
                    RemindStartDate = RemindStartDate + timedelta(seconds=int(RemindInterval))
                    str_RemindStartDate = RemindStartDate.strftime("%Y-%m-%d %H-%M-%S") 
                    while str_RemindStartDate<End_Time and  int_count<RemindCounter:
                        ReminderDateArray.append(RemindStartDate)
                        int_count+=1
                        print RemindStartDate.strftime("%Y-%m-%d %H-%M-%S")  
                        RemindStartDate = RemindStartDate + timedelta(seconds=int(RemindInterval))
                        str_RemindStartDate = RemindStartDate.strftime("%Y-%m-%d %H-%M-%S") 
                    
    env.log.error('bz_event_remind: ReminderDateArray= %s', ReminderDateArray) 
    for a_datetime in ReminderDateArray:
        #env.log.error('bz_event_remind: datetime.now() 2= %s', (datetime.now() - timedelta(seconds=Run_Interval)) ) 
        if a_datetime<datetime.now() and a_datetime>=(datetime.now() - timedelta(seconds=Run_Interval)):
            #env.log.error('bz_event_remind: %s', a_datetime.strftime("%Y-%m-%d %H-%M-%S") ) 
            bz_event_handle(env, ReaminderValue, db_conn)
            return           
  
def bz_event_handle(env, ReaminderValue, db_conn):
    import bz_web
    import bz_gl
    import bz_web_ui
    import bz_utils
    bugz = bz_api.bz_connect(env) 
    RemindAction = ReaminderValue['RemindAction']    
    if RemindAction == 'Email':   
        env.log.error("bz_event_handle: ReaminderValue= %s", ReaminderValue) 
        BugzQueryID = ReaminderValue['BugzQueryID']
        env.log.error("bz_event_handle: BugzQueryID= %s", BugzQueryID) 
        a_table = bz_model.BugzQuery(BugzQueryID, db_conn)
        a_values = bz_web_ui._M_GetReqFromDB(env, a_table, bz_gl.gl_BugzQuery)
        bz_event_remind_judge_query(env, ReaminderValue, a_table, a_values)
        cols = []
        rows = [] 
        bz_web_ui._A_SynQuery(env, bugz, db_conn, BugzQueryID, '', cols, rows, a_values)  
        query_url = bugz.BG_SearchUrl2(a_row=a_values) 
        
        query_url = bz_gl.bz_bugz_url(query_url)
        env.log.error("query_url(%s) ", query_url) 
        
        maildic = {}    
        maildic['title'] = ReaminderValue['Headline']
        
        env.log.error("to1(%s) ", ReaminderValue['EmailTo']) 
        maildic['to']=ReaminderValue['EmailTo'] #bz_utils.string2list(env, ReaminderValue['EmailTo']) 
        env.log.error("to2(%s) ", maildic['to'])   

        env.log.error("cc1(%s) ", ReaminderValue['EmailCc']) 
        maildic['cc']=ReaminderValue['EmailCc']#bz_utils.string2list(env, ReaminderValue['EmailCc']) 
        env.log.error("cc2(%s) ", maildic['cc']) 
        
        maildic['decription'] = ReaminderValue['EmailContent'] 
        env.log.error("decription(%s) ", maildic['decription']) 
        
        maildic['QueryLink'] = ''
        maildic['content'] = bz_web.bz_queryurl(query_url, BugzQueryID)         
        maildic['attach_file'] = ''#os.path.join(bz_gl.gl_csv_rootPath+BugzQueryID, BugzQueryID+'.csv')
        env.log.error("maildic=\n%s ", maildic)  
        bz_utils.SendHtmlMail(env, maildic) 
        env.log.error("Sendmail(%s) to %s", maildic['title'], maildic['to']) 
        
def bz_event_remind_judge_query(env, ReaminderValue, a_table, a_values):
    RemindType = ReaminderValue["RemindType"].strip()
    if RemindType=="W" : 
        s = a_values['chfieldfrom']
        e = a_values['chfieldto']
        env.log.error("bz_event_remind_judge_query(%s) to %s", s,e) 
        if s:
            new_s = daysub7(s)#'2013-08-01'
        else:
            new_s = ''
            
        if e == 'Now':
            new_e = e
        elif e:
            new_e = daysub7(e)#'2013-08-07'
        else:
            new_e = ''
        env.log.error("bz_event_remind_judge_query: new %s to %s", new_s,new_e)     
        a_table['chfieldfrom'] = new_s
        a_table['chfieldto'] = new_e           
        a_table.save_changes()  
        a_values['chfieldfrom'] = a_table['chfieldfrom']
        a_values['chfieldto'] = a_table['chfieldto']
        
def daysub7(s):   #daystring
        from datetime import datetime, date, time
        sevenday = timedelta(days=7)
        datetime_s = datetime.strptime(s, "%Y-%m-%d")
        new_datetime_s = datetime_s + sevenday #add 7 days
        new_s = new_datetime_s.strftime("%Y-%m-%d")
        return new_s

def CurrentTime19():
    import time
    from datetime import datetime, timedelta
    Timestr=time.strftime("%Y-%m-%d %X", time.localtime())
    if (len(Timestr)==18):
        Timestr=Timestr.replace(" ", " 0")
    return Timestr
    
      
