# -*- coding: utf-8 -*-

import re
import os
import MySQLdb
import shutil
import pickle

import base_model

class Task(base_model.base):

    def __init__(self, id, db):
        self.fields = []
        self.fields.append({'name':'Headline', 'control':'input'})
        self.fields.append({'name':'Submitter', 'control':'input'})
        self.fields.append({'name':'Owner', 'control':'input'})
        self.fields.append({'name':'YearMonth', 'control':'input'})
        self.fields.append({'name':'State', 'control':'input'})
        base_model.base.__init__(self, id, 'Task',self.fields, db)

    def Get_Focus_Task(self,CurrentUser):
        import filler_model
        import sprd_user_model
        QF={}
        focus_task=[]
        focus_user=[]
        a_filler_obj = filler_model.Filler(None, self.db)
        a_user_obj = sprd_user_model.SPRD_User(None)

        myTask = self.select(QF)
        for a_task in myTask:
            a_submitter = a_task['Submitter']
            focus_user.append(a_submitter)
            All_Agent = []
            a_filler_obj.Get_All_Agent(a_submitter, All_Agent)
            tmp=[]
            for a_Agent in All_Agent:
                tmp = tmp + a_user_obj.Get_All_Member(a_Agent)
            tmp = [a_u['EName'].lower().replace(' ', '.')  for a_u in tmp]
            focus_user = focus_user + tmp
            if CurrentUser in focus_user:
                focus_task.append(a_task)
        return focus_task

    def Get_Focus_Email_User(self,CurrentUser):
        import filler_model
        import sprd_user_model
        focus_user=[]
        a_filler_obj = filler_model.Filler(None, self.db)
        a_user_obj = sprd_user_model.SPRD_User(None)
        All_Agent = []
        a_filler_obj.Get_All_Agent(CurrentUser, All_Agent)
        for a_agent in All_Agent:
            focus_user.append(a_agent)
        focus_user = focus_user + a_user_obj.Get_Direct_Member(CurrentUser)
        return focus_user

    def Send_Email_0(self,CurrentUser, a_task_obj):
        import filler_model
        from xmlrpclib import ServerProxy
        TO=[]
        TO = self.Get_Focus_Email_User(CurrentUser)
        out_string =u'<a href="http://172.16.15.41:8082/trac/idata/task/process?taskid='  +  a_task_obj['ID'] +'">' + a_task_obj['Headline'] + '</a>'
        self.remoteSendMail('mingjian.liu', ['mingjian.liu'], ['mingjian.liu'], a_task_obj['Headline'] + u' 请抓紧时间完成！', out_string)
        
    def Send_Email_1(self,CurrentUser, a_task_obj):
        import filler_model
        import user_model
        TO=[]
        TO = self.Get_Focus_Email_User(CurrentUser)
        out_string =u'<a href="http://imanage.sprd.com/idata/task/process?taskid='  +  a_task_obj['ID'] +'">' + a_task_obj['Headline'] + '</a>'
        self.remoteSendMail(CurrentUser, CC, TO, a_task_obj['Headline']+ u' 请抓紧时间完成！', out_string)
        
    def Send_Email_2(self,CurrentUser, a_task_obj):
        import filler_model
        import user_model
        TO=[]
        TO = self.Get_Focus_Email_User(CurrentUser)
        out_string =u'<a href="http://imanage.spreadtrum.com/idata/task/process?taskid='  +  a_task_obj['ID'] +'">' + a_task_obj['Headline'] + '</a>'
        self.remoteSendMail(CurrentUser, CC, TO, a_task_obj['Headline']+ u' 请抓紧时间完成！', out_string)
        
    def remoteSendMail(self,FromStr, CCList, ToList, Subject, Content):
        import sendmail_model
        try:
            aSendmail = sendmail_model.SendMail()
            aSendmail.smtp_server="172.16.0.25"
            aSendmail.From=FromStr
            aSendmail.CCList=CCList
            aSendmail.ToList= ToList
            aSendmail.Subject= Subject
            aSendmail.Content=Content
            aSendmail.Send_Mail()
            #except Exception as ex:        
            #    print "exception", ex        
            #return 0
