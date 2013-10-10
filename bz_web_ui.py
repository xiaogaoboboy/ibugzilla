# -*- coding: utf-8 -*-
#

import os
import pkg_resources
import re
import shutil
import subprocess
import MySQLdb
import time
import thread
from datetime import datetime, timedelta
from genshi import HTML    
from genshi.builder import tag
from trac.util.text import empty
from api import IModuleProvider
from trac.core import *
from trac.loader import get_plugin_info, get_plugins_dir
from trac.perm import PermissionSystem, IPermissionRequestor
from trac.util.compat import partial
from trac.util.text import exception_to_unicode
from trac.util.translation import _, ngettext
from trac.web import HTTPNotFound, IRequestHandler
from trac.web.chrome import add_notice, add_stylesheet, \
                            add_warning, Chrome, INavigationContributor, \
                            ITemplateProvider
from trac.wiki.formatter import format_to_html
from trac.web.chrome import add_ctxtnav,INavigationContributor, ITemplateProvider, add_stylesheet, add_script

#import sys
#reload(sys)  
#sys.setdefaultencoding('utf-8')

#BZ Module
import trac
from trac.notification import NotifyEmail
from trac.core import *
from trac.util.html import html
from trac.web import IRequestHandler
from trac.web.chrome import INavigationContributor, ITemplateProvider
from trac.web.chrome import add_ctxtnav, add_stylesheet, add_script
from genshi import HTML    
import urllib2

from iData.bz_api import Bugz
from bz_statics_model import Bugz_Statics

import bz_web
import bz_gl
import bz_api
import bz_model
import bz_utils 
import schedule

def _P_EmailManager(env,  req, data, bugz, db_conn):   
       
        add_script(req, 'hw/js/worklog_check.js')
            
        add_stylesheet(req, 'hw/css/datetime.css')
        add_stylesheet(req, 'hw/css/jquery-ui_iManage.css')

        add_script(req, 'hw/js/jquery-ui.min.js')
        add_script(req, 'hw/js/jquery-ui-timepicker-addon.js')
        #add_script(req, 'hw/js/highcharts.src.js')
        
        Current_User = req.session.sid
        js = bz_web.bz_Heart(env, req)
        data.update({'srv_Heart':HTML(js)})  

        QueryRows = _M_Table(env, req, bugz, data, db_conn, bz_gl.gl_BugzQuery)#_M_GetSimpeQuery(env, req, data, db_conn)  
        QueryIDs = []
        for row in QueryRows:    
            #tmp_row['QueryID'] = row['ID']
            #tmp_row['QueryName'] = row['name']#.decode('GBK')
            QueryIDs.append(row['ID'])
        data['QueryIDs']=QueryIDs
        
        ID = req.args.get('ID', '').strip()          
        if ID!='':
            a_table = bz_model.BugzReminder(ID, db_conn)
            if a_table is not None:   
                a_values = _M_GetReqFromDB(env, a_table, bz_gl.gl_BugzReminder)                      
        else:
            a_values = _M_GetReq(env, req, db_conn, bz_gl.gl_BugzReminder)     
        if (req.method == "POST"): 
            a_db_item = _M_GetReqForDB(env, req, bugz, db_conn, bz_gl.gl_BugzReminder, a_values)
            _A_Submit(env, req, db_conn, bz_gl.gl_BugzReminder, a_db_item)
        _ActionDB(env, req, data, db_conn, bz_gl.gl_BugzReminder, a_values)
                    
        _M_Table(env, req, bugz, data, db_conn, bz_gl.gl_BugzReminder)
        #data['RemindTypeList']= [{'ID':'M', 'Name':u'Êúà'}, {'ID':'W', 'Name':u'Âë®'},{'ID':'D', 'Name':u'ÂèåÂë®'},{'ID':'F', 'Name':u'Âà∞Êúü'}]
        #env.log.error('_P_EmailManager: %s', data)
        return data 
        


def _P_Ajax_QueryTree(env, req, data, bugz, db_conn):  
        out_string = ''          
        cols = rows = []
        count = 0   
        result = []  
        columnlist = []
        ibugz_col = []
        a_values = None
        
        columnlist = bz_web.bz_old_collist(req) 
        assignee = req.session.sid
        bz_ajax = req.args.get('bz_ajax', '')
        ID = None
        if bz_ajax == 'bz_ajax_tree':            
            ID = req.args.get('ID', '').strip() 
            name = req.args.get('name', '').strip()             
           
        if ID is None or name is None:
            pass
        elif name == bz_gl.gl_MyToDo:
            status = ['NEW','Assigned','Root-Caused']
            query_url = bugz.BG_SearchUrl2(bug_status=status, \
                    a_assigned_to=assignee, columnlist=columnlist) 
            bugz.BG_Search(query_url, result, collist=columnlist)
            out_string += bz_web.bz_query_disp(req, status=status, assigned_to=assignee) 
            out_string += bz_web.bz_query_url(req, bz_gl.bz_bugz_url(query_url)) 
        elif name == bz_gl.gl_Myall:  
            query_url = bugz.BG_SearchUrl2(a_assigned_to=assignee, \
                    columnlist=columnlist) 
            bugz.BG_Search(query_url, result, collist=columnlist)           
            out_string += bz_web.bz_query_disp(req, assigned_to=assignee) 
            out_string += bz_web.bz_query_url(req, bz_gl.bz_bugz_url(query_url)) 
        else:##TREE by Bugz_Query           
            a_Bugz_Query = bz_model.BugzQuery(ID, db_conn)
            if a_Bugz_Query is not None:   
                a_values = _M_GetReqFromDB(env, a_Bugz_Query, bz_gl.gl_BugzQuery)  
                query_url = bugz.BG_SearchUrl2(a_row=a_values) 
        
                columnlist = a_values['columnlist']#bz_utils.string2list(a_Bugz_Query['columnlist'])
                env.log.error('_P_Ajax_QueryTree: collist3=%s', columnlist)                
                ibugz_col = a_values['ibugz_col']#bz_utils.string2list(a_Bugz_Query['ibugz_col'])               
                bugz.BG_Search(query_url, result, collist=columnlist)                 
                        
                out_string += bz_web.bz_query_disp(req, product = a_Bugz_Query['product'], \
                        status = a_Bugz_Query['bug_status'], \
                        severity = a_Bugz_Query['bug_severity'], \
                        component = a_Bugz_Query['component'], \
                        assigned_to = a_Bugz_Query['assigned_to'], \
                        reporter = a_Bugz_Query['reporter'], \
                        cf_come_from = a_Bugz_Query['cf_come_from'], \
                        cf_base_on_ver = a_Bugz_Query['cf_base_on_ver'], \
                        cf_fix_on_ver = a_Bugz_Query['cf_fix_on_ver'], \
                        orderby = a_Bugz_Query['orderby'])
                out_string += bz_web.bz_query_url(req, bz_gl.bz_bugz_url(query_url))                        

        count = len(result)  
        cols = ['bug_id']+columnlist+ibugz_col
        _M_QueryResult(env, result, bugz, cols, rows, a_values)
        out_string += bz_web.bz_queryresult(req, cols, rows)  
        out_string += u"<br /><br />"   
        req.send(out_string.encode('utf-8')) 
        return

        
def _P_QueryTree(env, req, data, bugz, db_conn):
        add_script(req, 'hw/js/Bz_Dtree.js')
        add_stylesheet(req, 'hw/css/dtree.css')
        
        sid = req.session.sid
        personal_list = []
        common_list = []         
        a_Bugz_Query = bz_model.BugzQuery(None, db_conn)
        
        QF = {}   
        QF['field_ower'] = sid
        QF['field_treetype'] = 'PersonnalQuery'
        rows_personal = a_Bugz_Query.select(QF)
        for Query_Item in rows_personal:   
            personal_list.append((Query_Item['ID'], Query_Item['name'], Query_Item['tree']))
        personal_list.append(('0', 'My To Do', ',PersonnalQuery,'))
        personal_list.append(('0', 'My All', ',PersonnalQuery,'))

        QF = {}   
        QF['field_treetype'] = 'CommonQuery'
        rows_common = a_Bugz_Query.select(QF) 
        for Query_Item in rows_common:   
            common_list.append((Query_Item['ID'], Query_Item['name'], Query_Item['tree']))

        tree_list =   personal_list +    common_list           
        js = bz_web.bz_query_tree(env, req, tree_list) 
        
        data.update({'dtree_js':HTML(js)})
        return data 
        

def _P_AQuery(env, req, data, bugz, db_conn):
        ID = req.args.get('ID', '').strip() 
        env.log.error('_P_AQuery ID=%s',ID)          
        if ID=='':
            jump_url = 'http://tracsrv/idata/Bugzilla/query/Bz_QueryManager'
            req.redirect(jump_url)         
            return data
        #    a_Bugz_Query = bz_model.BugzQuery(ID, db_conn)
        #    if a_Bugz_Query is not None:   
        #        a_values = _M_GetReqFromDB(env, a_Bugz_Query, bz_gl.gl_BugzQuery)                      
        #else:
        #    a_values = _M_GetReq(env, req, db_conn, bz_gl.gl_BugzQuery) 
            
        #query_url = bugz.BG_SearchUrl2(a_row=a_values)   
        
        if bz_gl.gl_Save_Query in req.args:  
            a_values = _M_GetReq(env, req, db_conn, bz_gl.gl_BugzQuery)
            a_db_item = _M_GetReqForDB(env, req, bugz, db_conn, bz_gl.gl_BugzQuery, a_values)
            if a_db_item is None:
                add_notice(req, "Select Invalid!") 
                jump_url = data['SiteRoot']
            else:
                ID = _A_Submit(env, req, db_conn, bz_gl.gl_BugzQuery, a_db_item)            
                jump_url = data['SiteRoot']+"?ID="+ID
            #req.redirect(jump_url)   
        else:
            a_Bugz_Query = bz_model.BugzQuery(ID, db_conn)
            if a_Bugz_Query is not None:   
                a_values = _M_GetReqFromDB(env, a_Bugz_Query, bz_gl.gl_BugzQuery)                      
            
        _ActionDB(env, req, data, db_conn, bz_gl.gl_BugzQuery, a_values)    
        _M_QueryComon(env, req, bugz, data)
        _M_Table(env, req, bugz, data, db_conn, bz_gl.gl_BugzQuery, ID=ID)
        return data
        
def _P_QueryManager(env, req, data, bugz, db_conn):     
        #add_script(req, 'hw/js/bz_jquery.dataTables.min.js')
        #add_script(req, 'hw/js/bz_jquery.dataTables.js')
        #add_script(req, 'hw/js/bz_jquery.js')
        #add_stylesheet(req, 'hw/css/bz_jquery.dataTables.css')   
        #add_stylesheet(req, 'hw/css/bz_jquery.dataTables_themeroller.css')  
        #add_stylesheet(req, 'hw/css/bz_demo_page.css')  
        #add_stylesheet(req, 'hw/css/bz_demo_table.css')  
        #add_stylesheet(req, 'hw/css/bz_demo_table_jui.css')  

        add_script(req, 'hw/js/bz_custom-search.js')
        
        custom_statics = []   
        ID = req.args.get('ID', '').strip() 
        action = req.args.get('action', '').strip() 
        env.log.error('_P_OrinalQuery ID=%s, action=%s',ID, action)          
        if ID!='':
            a_Bugz_Query = bz_model.BugzQuery(ID, db_conn)
            if a_Bugz_Query is not None:   
                a_values = _M_GetReqFromDB(env, a_Bugz_Query, bz_gl.gl_BugzQuery)                      
        else:
            a_values = _M_GetReq(env, req, db_conn, bz_gl.gl_BugzQuery) 
            
        query_url = bugz.BG_SearchUrl2(a_row=a_values)   
        _ActionDB(env, req, data, db_conn, bz_gl.gl_BugzQuery, a_values)
        if bz_gl.gl_Save_Query in req.args:  
            a_values = _M_GetReq(env, req, db_conn, bz_gl.gl_BugzQuery) 
            a_db_item = _M_GetReqForDB(env, req, bugz, db_conn, bz_gl.gl_BugzQuery, a_values)
            if a_db_item is None:
                add_notice(req, "Select Invalid!") 
                jump_url = data['SiteRoot']
            else:
                ID = _A_Submit(env, req, db_conn, bz_gl.gl_BugzQuery, a_db_item)            
                #jump_url = data['SiteRoot']+"?ID="+ID
                jump_url = 'http://tracsrv/idata/Bugzilla/query/Bz_AQuery'+"?ID="+ID
            req.redirect(jump_url)       

        if ID!='':
            cols = []
            rows = []  
            csv_url = ''        
            if action == "syn_query":
                if query_url is None:
                    add_notice(req, "Please Set Query Rule!") 
                else:
                    env.log.error('_P_OrinalQuery _A_SynQuery ID=%s', ID)  
                    csv_file = _A_SynQuery(env, bugz, db_conn, ID, data['CurrentUser'], cols, rows, a_values)                
                    #csv_url = bz_gl.bz_csv_url(csv_file=csv_file)   
                    #full_csv_file = os.path.join(bz_gl.gl_csv_rootPath.replace('iBugzilla','iBugzillaTmp'), csv_file)             
                    jump_url = data['SiteRoot']  
                    req.redirect(jump_url)
            else:                     
                cur_user_dir = bz_gl.gl_csv_rootPath+ID
                csv_file = ID+'.csv'
                a_sheet = a_values['csv_end_time']
                full_csv_file = os.path.join(cur_user_dir, csv_file)                
                ret = _A_ReadQueryResult(env, cols, rows, full_csv_file, a_sheet)
                                                
            if len(rows) > 0:
                env.log.error('_P_OrinalQuery cols=%s',cols)  
                data['cols'] = cols
                data['rows'] = rows              
                email = bz_web.bz_email_box(req, bz_gl.bz_bugz_url(query_url), csv_url)
                data.update({'email':HTML(email)})                 

        custom_statics = a_values['custom_statics'] 
        #env.log.error('_P_OrinalQuery custom_statics=%s', custom_statics) 
        for a_statics in custom_statics:  
            cols2 = []
            rows2 = []
            if a_statics == bz_gl.gl_Statics_bugtotal.decode("GBK"):           
                cols2 = bz_gl.gl_Statics_bugtotal_cols                
                rows2 = _M_StaticsBugtotal(env, bugz, a_values, cols, rows, full_csv_file)  
            elif a_statics == bz_gl.gl_Statics_persontouch.decode("GBK"):
                cols2 = bz_gl.gl_Statics_persontouch_cols
                rows2 = _M_StaticsPersontouch(env, a_values, cols, rows) 
            data['cols2'] = cols2
            data['rows2'] = rows2             

        env.log.error('_M_QueryComon: in')
        _M_QueryComon(env, req, bugz, data)
        env.log.error('_M_Table: in')
        _M_Table(env, req, bugz, data, db_conn, bz_gl.gl_BugzQuery, ID=ID)
        return data

def _P_TrendPic(env, req, data, bugz, db_conn):
        add_script(req, 'hw/js/bz_excanvas.js')
        add_script(req, 'hw/js/jquery-ui.min.js')
        add_script(req, 'hw/js/jquery-ui-timepicker-addon.js')
        add_script(req, 'hw/js/highcharts.js')
        
        ID = req.args.get('ID', '').strip()       
        if ID!='':
            a_Bugz_Query = bz_model.BugzQuery(ID, db_conn)
            if a_Bugz_Query is not None:   
                a_values = _M_GetReqFromDB(env, a_Bugz_Query, bz_gl.gl_BugzQuery)          
        else:
            return data
            
        import line_chart_model
        import column_chart_model
        from genshi import HTML 

        import sys
        reload(sys)
        sys.setdefaultencoding('gb2312')

        Title_name = a_values['name'].encode('utf-8')
        SubTitle_name =  ''#'week period: '+weeks_cols[0]+'-->'+weeks_cols[lenth_week-1]
        Yaxis_Title_name = 'CR ˝¡ø/∏ˆ ˝'.encode('utf-8')#bz_gl.bz_statics_Yaxis_Title(statics_type)
        #Xaxis_name_str = 'Õ≥º∆»’∆⁄'.encode('utf-8')#line_chart_model.Line_Chart.get_line_Xaxis_name(Xaxis_name)

        YM_data_dic = {}         
        cur_user_dir = bz_gl.gl_csv_rootPath+ID
        csv_file = ID+'.csv'
        full_csv_file = os.path.join(cur_user_dir, csv_file)   
        Xaxis_name = []
        _A_StaticsQueryResult(env, YM_data_dic, Xaxis_name, full_csv_file)

        #env.log.error('_P_TrendPic: Xaxis_name=%s', Xaxis_name)
        Xaxis_name_str = line_chart_model.Line_Chart.get_line_Xaxis_name(Xaxis_name)        
        Xaxis_name_str = Xaxis_name_str.encode('utf-8')
        #env.log.error('_P_TrendPic: Xaxis_name_str=%s', Xaxis_name_str)
        #env.log.error('_P_TrendPic: YM_data_dic1=%s', YM_data_dic)

        #sorted(YM_data_dic.items, key=lambda YM_data_dic:YM_data_dic[0])
        items = YM_data_dic.items()
        #env.log.error('_P_TrendPic: items1=%s', items)
        items.sort()
        #env.log.error('_P_TrendPic: items2=%s', items)
        #data_str = line_chart_model.Line_Chart.get_line_Data(items)

        #[(u'2013-08-31', [6]), (u'2013-09-01', [7]), (u'2013-09-02', [8]), (u'2013-09-03', [10]), (u'2013-09-04', [13])]
        result = ''
        a_list = []
        for a_item in items:   
            #env.log.error('_P_TrendPic: a_item %s', a_item)
            #env.log.error('_P_TrendPic: 0 %s', a_item[0])
            #env.log.error('_P_TrendPic: 1 %s', a_item[1])
            
            a_list += [str(a) for a in a_item[1]]
            #env.log.error('_P_TrendPic: a_list %s', a_list)
            
        result = result + "{name:'" + "CR Total" + "',data:[" + ",".join(a_list) + "]},"
        #env.log.error('_P_TrendPic: result %s', result)
        data_str = result
        
        #data_str = line_chart_model.Line_Chart.get_line_Xaxis(YM_data_dic)
        data_str = data_str.encode('utf-8')
        #env.log.error('_P_TrendPic: data_str=%s', data_str)
        if 0:          
            line_str = line_chart_model.Line_Chart.get_line_chart_javascript('line', 'container_line', \
                Title_name, SubTitle_name, Xaxis_name_str , \
                Yaxis_Title_name,  data_str)
        else: 
            line_str = column_chart_model.Column_Chart.get_column_chart_javascript('line', 'container_line', \
                Title_name, Xaxis_name_str , \
                Yaxis_Title_name,  data_str, SubTitle=SubTitle_name)
        
        data.update({'line':HTML(line_str)})
        return data 
    
def _P_Debug(env, req, bugz):
    
    #env.log.error('_P_Debug email_logo=%s',email_logo)   
    return 

def _M_QueryComon(env, req, bugz, data): 
        data['all_product'] = bugz.all_product #Btag_select3('product') 
        data['all_component'] = bugz.all_component#Btag_select3('component')
        data['all_status'] = bugz.all_component#Btag_select3('bug_status')
        data['all_severity'] = bugz.all_component#Btag_select3('bug_severity')
        data['field_s'] = bugz.field_s#Btag_select3('f1')
        data['operation_s'] = bugz.operation_s#Btag_select('o1')  
        
        data['all_cf_come_from'] = ['Customer','Development Area','FAE','FT','Internal_Customer','PLDSQA','Test Area', 'TR_TEST','UEIT']#bugz.Btag_select('cf_come_from')        
        data['TimeFields'] = bz_gl.gl_TimeFields #bugz.Btag_select3('f1')
        data['StringFields'] = bz_gl.gl_StringFilds
        data['StringOperations'] = bz_gl.gl_StringOperations
        data['BugzillaFields'] = bz_gl.gl_BugzillaFields
        data['iBugzillaFields'] = bz_gl.gl_iBugzillaFields
        data['GroupNum_s'] = ['0','1','2']
        data['GroupRules'] = ['','AND','OR']
                
        data['iBugzillaStatics'] = []
        tmp = bz_gl.gl_Statics_bugtotal.decode('GBK')  
        if tmp not in data['iBugzillaStatics']:
            data['iBugzillaStatics'].append(tmp)
        tmp = bz_gl.gl_Statics_persontouch.decode('GBK')  
        if tmp not in data['iBugzillaStatics']:
            data['iBugzillaStatics'].append(tmp)
            
        data['Result1'] = 'BUGÕ≥º∆ ‰≥ˆΩ·π˚'.decode('GBK')
        data['Result2'] = '÷‹∆⁄±‰ªØ«˜ ∆Õº±Ì'.decode('GBK')
        data['SiteTrendRoot'] = data['SiteRoot'].replace('Bz_QueryManager','Bz_TrendPic')
        
def _M_QueryResult(env, result, bugz, cols, rows, a_values):  
    if len(result) > 0:  
        #env.log.error('_M_QueryResult: cols=%s', cols)        
        if bz_gl.gl_PersonTouchCount.decode('GBK') in cols:
            TouchCount_Flag = True
            for i in range(len(cols)): 
                if cols[i] == bz_gl.gl_PersonTouchCount.decode('GBK'):
                    i_TouchCount = i
                elif cols[i] == bz_gl.gl_TouchDetail.decode('GBK'):
                    i_TouchDetail = i
        else:
            TouchCount_Flag = False 

        if bz_gl.gl_ChangeOwnerCount.decode('GBK') in cols:
            ChangeOwner_Flag = True
            for i in range(len(cols)): 
                if cols[i] == bz_gl.gl_ChangeOwnerCount.decode('GBK'):
                    i_ChangeOwnerCount = i
                elif cols[i] == bz_gl.gl_ChangeOwnerDetail.decode('GBK'):
                    i_ChangeOwnerDetail = i
        else:
            ChangeOwner_Flag = False             
            
        for row in result:
            tmp_row = []
            index = 0 
            bug_id = '' 
            col_url = ''  
            for i in range(len(cols)): 
                    if cols[i] == bz_gl.gl_NeedInfoCount.decode('GBK'):
                            tmp_row.append(bugz.F_NeedInfoCount(int(bug_id))) 
                    elif cols[i] == bz_gl.gl_NeedInfoDetail.decode('GBK'):
                            tmp_row.append(bugz.F_NeedInfoDetail(int(bug_id)))   
                    elif cols[i] == bz_gl.gl_PersonTouchCount.decode('GBK') \
                            or cols[i] == bz_gl.gl_TouchDetail.decode('GBK') \
                            or cols[i] == bz_gl.gl_ChangeOwnerCount.decode('GBK') \
                            or cols[i] == bz_gl.gl_ChangeOwnerDetail.decode('GBK'):
                        pass
                    elif cols[i] == bz_gl.gl_ChangedataToNow.decode('GBK'):                                
                            tmp_row.append(bugz.F_ChangedataToNow(row['changeddate']))
                    elif cols[i] == 'assigned_to' or cols[i] == 'reporter':
                            tmp_row.append(row[cols[i]].replace('@spreadtrum.com',''))
                    elif cols[i] == 'bug_id':
                            tmp_row.append(int(row[cols[i]]))
                    else:                                
                        if row[cols[i]] is None:
                            tmp_row.append('None')
                        else:
                            tmp_row.append(row[cols[i]].decode('utf-8'))
                    if index == 0:                            
                        bug_id = row[cols[i]]                                
                        col_url = 'http://10.0.6.58/bugzilla/show_bug.cgi?id='+bug_id 
                    index = index + 1
                    
            if TouchCount_Flag == True:
                product_ower = a_values['product_ower']
                TouchStart = a_values['TouchStart']
                TouchEnd = a_values['TouchEnd']      
                (f_Count, detail_str) = bugz.F_TouchDetail(int(bug_id), product_ower, TouchStart, TouchEnd)
                if f_Count != 0:
                    tmp_row.insert(i_TouchCount,f_Count)  
                    tmp_row.insert(i_TouchDetail,detail_str)
                else:
                    continue
                    
            if ChangeOwner_Flag == True:      
                (f_Count, detail_str) = bugz.F_ChangeOwnerDetail(int(bug_id))
                if f_Count != 0:
                    tmp_row.insert(i_ChangeOwnerCount,f_Count)  
                    tmp_row.insert(i_ChangeOwnerDetail,detail_str) 
                else:
                    continue
                    
            rows.append((tmp_row))

def _M_StaticsPersontouch(env, a_values, cols, rows):
    rows2 = []    

    index = 0
    for idx,col in enumerate(cols):  
        #env.log.error('_M_StaticsPersontouch: %s %s',idx,col)
        if col == bz_gl.gl_TouchDetail:
            index = idx  
                
    product_owers = a_values['product_ower']
    for a_ower in product_owers:
        a_row = []
        
        a_row.append(a_ower)         
        total = 0
            
        #env.log.error('_M_StaticsPersontouch: index = %s',index)
        for row in rows:
            #env.log.error('_M_StaticsPersontouch: %s',row[index])
            results = re.split(r'[\s]+', row[index]) 
            #env.log.error('_M_StaticsPersontouch: results = %s',results)
            for a_result in results:
                if a_ower in a_result:
                    #env.log.error('_M_StaticsPersontouch: a_result = %s',a_result)
                    total += int((a_result.split(':'))[1])
                    break            
        
        a_row.append(total) 
        #env.log.error('_M_StaticsPersontouch: a_row = %s',a_row)
        rows2.append(a_row) 
        
    #env.log.error('_M_StaticsPersontouch: rows2 = %s',rows2)
    return rows2

def _M_StaticsBugtotal(env, bugz, a_values, cols, rows, csv_file):
    comp_index = 0#component µƒŒª÷√
    rows2 = [] 
    for idx,col in enumerate(cols):  
        if col == 'component':
            comp_index = idx  
    #env.log.error('_M_StaticsBugtotal2: comp_index=%s',comp_index)
    ncols = len(cols)

    products = a_values['product']
    #env.log.error('_P_OrinalQuery products=%s', products)        
        
    #if len(products) != 1:
    #    add_notice(req, "Please Choose only one Product!") 
    #    return 
    for a_product in products:        
        comp_owers = bugz.S_ProductOwers(a_product) 
        comp_crtotals = {}
        env.log.error('_M_StaticsBugtotal2: comp_owers=%s',comp_owers)
        for (k,v) in  comp_owers.items(): 
            #self.log.error('%s: %s', k, v)
            comp_crtotals[k] = 0
            #detail_str += (k+':'+str(v)+' ') 
        
        import pyExcelerator as xl
        #Ã·»°excelŒƒº˛÷–µƒ±Ìµ• ˝ƒø
        sheets = xl.parse_xls(csv_file)
        nsheets = len(sheets)
        for n in range(nsheets):
            sheet = sheets[n]
            #Ã·»°±Ìµ•nµƒ√˚≥∆
            sh_name = sheet[0]
            sh_data = sheet[1]
        
            #Õ≥º∆≤ªÕ¨
            #nrows = sheet.nrows                
            #env.log.error('_M_StaticsBugtotal2: lenth=%s',lenth)
            all_data_points = len(sh_data)
            
            #a_component = 'APP-PhoneBook'
            #a_cr_total = 0
            #dirt[a_component] = 0
            for i in range(1, all_data_points):  
                #sheet.cell(i,comp_index).value #0±Ì æipº«¬º‘⁄µ⁄“ª¡–            
                if sh_data.has_key((i,comp_index)):
                    a_data = sh_data[(i,comp_index)]
                    #env.log.error('_M_StaticsBugtotal2: i=%s, a_data=%s',i, a_data)
                    #if a_data == a_component:
                    #temp = a_data[:a_data.rfind('APP-PhoneBook')]
                    #dirt.setdefault(temp, 0)
                    #dirt[a_component] += 1
                    if comp_owers.has_key(a_data):
                        comp_crtotals[a_data] += 1
                else:
                    break 
            #env.log.error('_M_StaticsBugtotal2: a_cr_total=%s',a_cr_total)        
            #fields = []
            #component = ''
        env.log.error('_M_StaticsBugtotal2: comp_crtotals=%s',comp_crtotals)
        
        for (k,v) in  comp_owers.items(): 
            a_row = []
            #0 'Component':
            a_row.append(k)
            a_row.append(v)
            a_row.append(comp_crtotals[k])
            #2 'CR TotalNum'
            rows2.append(a_row) 
    return rows2
                


def _M_Table(env, req, bugz, data, db_conn, table_name, ID=''): 
        Current_User = req.session.sid
        if table_name == bz_gl.gl_BugzQuery:            
            SYSFields=bz_gl.gl_QuerySYSFields
            UIFields=bz_gl.gl_QueryUIFields
            MultiInputFields=bz_gl.gl_QueryUIMultiInputFields
            CheckboxFields=bz_gl.gl_QueryCheckboxFields    
        elif table_name == bz_gl.gl_BugzReminder:            
            SYSFields=bz_gl.gl_RemindSYSFields
            UIFields=bz_gl.gl_RemindUIFields
            MultiInputFields = bz_gl.gl_RemindUIMultiInputFields
            CheckboxFields=bz_gl.gl_RemindCheckboxFields        
        UIFields = UIFields + CheckboxFields + MultiInputFields
        AllFields = SYSFields + UIFields  
        
        DBRows=[]
        QF = {}  
        if table_name == bz_gl.gl_BugzQuery:
            a_table = bz_model.BugzQuery(None, db_conn)
            if ID!='':
                QF['field_ID'] = ID
            if req.session.sid == 'song.shan':
                pass
            else:
                QF['field_ower'] = req.session.sid
        elif table_name == bz_gl.gl_BugzReminder:
            a_table = bz_model.BugzReminder(None, db_conn)  
            QF['field_Submitter'] = req.session.sid
        
        rows = a_table.select(QF) 
        env.log.error('_M_Table: for in')
        for row in rows:                
            tmp_row={}
            #env.log.error('_M_GetQuery: %s', row)
            if table_name == bz_gl.gl_BugzQuery:
                for field in AllFields:  
                    tmp_row[field]=row[field] #(row[field].decode('utf-8'))
                    
                a_Bugz_Query = bz_model.BugzQuery(tmp_row['ID'], db_conn)
                if a_Bugz_Query is not None:   
                    a_values = _M_GetReqFromDB(env, a_Bugz_Query, bz_gl.gl_BugzQuery)                      
                    query_url = bugz.BG_SearchUrl2(a_row=a_values) 
                    tmp_row['bz_url'] = bz_gl.bz_bugz_url(query_url)
                else:        
                    tmp_row['bz_url'] = ''
                tmp_row['csv_url'] = bz_gl.bz_csv_url(ID=tmp_row['ID']) 
                tmp_row['csv_history'] = tmp_row['csv_history'].replace('2013-','')
                
            elif table_name == bz_gl.gl_BugzReminder:
                #env.log.error('_M_GetRemind: %s', row)
                QueryID = None
                for field in AllFields:            
                    tmp_row[field]=row[field]
                    if field == 'BugzQueryID':
                        QueryID = row[field]
                if QueryID in data['QueryIDs']:
                    b_table = bz_model.BugzQuery(QueryID, db_conn)  
                else:
                    b_table = None
                if b_table is not None:
                    QueryName = b_table['name']             
                else:
                    QueryName = 'QueryID not exist,Please Edit'
                tmp_row['QueryName'] = QueryName   
                tmp_row['QueryURL'] = ''
            DBRows.append(tmp_row)
                
        #data['UserListTip']=UserListTip
        if table_name == bz_gl.gl_BugzQuery:
            data['BugzQueryRows']= DBRows
        elif table_name == bz_gl.gl_BugzReminder:    
            data['BugzReminderRows']= DBRows        
        #env.log.error('_M_Table: %s', DBRows)
        return DBRows
                        

def _M_GetReq(env, req, db_conn, table_name):  
        Current_User = req.session.sid
        if table_name == bz_gl.gl_BugzQuery:            
            SYSFields=bz_gl.gl_QuerySYSFields
            UIFields=bz_gl.gl_QueryUIFields
            MultiInputFields=bz_gl.gl_QueryUIMultiInputFields
            CheckboxFields=bz_gl.gl_QueryCheckboxFields  
            ComposeFields = bz_gl.gl_advance_db_field + bz_gl.gl_advance_bz_field + bz_gl.gl_tree
        elif table_name == bz_gl.gl_BugzReminder:            
            SYSFields=bz_gl.gl_RemindSYSFields
            UIFields=bz_gl.gl_RemindUIFields
            MultiInputFields = bz_gl.gl_RemindUIMultiInputFields
            CheckboxFields=bz_gl.gl_RemindCheckboxFields  
            ComposeFields = []
        UIFields = UIFields + CheckboxFields + MultiInputFields
        AllFields = SYSFields + UIFields + ComposeFields  
        
        Values={}           
        for a_field in AllFields:
            if a_field in CheckboxFields:
                Value_List=[]
                tmp_Value_List = req.args.get(a_field, [])
                if type(tmp_Value_List)!=type(list()):
                    Value_List=[tmp_Value_List]
                else:
                    Value_List=tmp_Value_List
                Values[a_field] = Value_List  
            elif a_field in SYSFields:
                Values[a_field] = ''
            elif a_field in MultiInputFields:
                Values[a_field]  = (re.split(r'[;,\s]+', req.args.get(a_field, '').strip()))
                #env.log.error('_M_Get: Values[a_field]=%s', Values[a_field])
            else:
                Values[a_field] = req.args.get(a_field, '').strip()
                        
        if table_name == bz_gl.gl_BugzQuery:
            if bz_gl.gl_ChangedataToNow in Values['ibugz_col']:
                if 'changeddate' not in Values['columnlist']:
                    Values['columnlist'].append('changeddate')
            elif bz_gl.gl_NeedInfoCount in Values['ibugz_col']:  
                if bz_gl.gl_NeedInfoDetail not in Values['ibugz_col']:
                    Values['ibugz_col'].append(bz_gl.gl_NeedInfoDetail)  
            elif bz_gl.gl_PersonTouchCount in Values['ibugz_col']:  
                if bz_gl.gl_TouchDetail not in Values['ibugz_col']:
                    Values['ibugz_col'].append(bz_gl.gl_TouchDetail)   
            elif bz_gl.gl_ChangeOwnerCount in Values['ibugz_col']:  
                if bz_gl.gl_ChangeOwnerDetail not in Values['ibugz_col']:
                    Values['ibugz_col'].append(bz_gl.gl_ChangeOwnerDetail)                     
        elif table_name == bz_gl.gl_BugzReminder:
            QueryID=req.args.get('QueryID', '').strip() 
            env.log.error('_M_Get: QueryID=%s', QueryID)
            if QueryID!='':
                Values['BugzQueryID']=QueryID
                b_table = bz_model.BugzQuery(QueryID, db_conn)
                if b_table is not None:
                    Values['Headline'] = b_table['name']
        return Values

def _M_GetReqFromDB(env, a_table_row, table_name):  
        #Current_User = req.session.sid
        if table_name == bz_gl.gl_BugzQuery:            
            SYSFields=bz_gl.gl_QuerySYSFields
            UIFields=bz_gl.gl_QueryUIFields
            MultiInputFields=bz_gl.gl_QueryUIMultiInputFields
            CheckboxFields=bz_gl.gl_QueryCheckboxFields             
        elif table_name == bz_gl.gl_BugzReminder:            
            SYSFields=bz_gl.gl_RemindSYSFields
            UIFields=bz_gl.gl_RemindUIFields
            MultiInputFields = bz_gl.gl_RemindUIMultiInputFields
            CheckboxFields=bz_gl.gl_RemindCheckboxFields        
        UIFields = UIFields + CheckboxFields + MultiInputFields
        DBFields = SYSFields + UIFields  
        
        Values={}           
        #for a_field in UIFields:
        for a_field in DBFields:
            if a_field in CheckboxFields \
                    or a_field in MultiInputFields:                
                Values[a_field] = bz_utils.string2list(env, a_table_row[a_field]) 
            else:
                Values[a_field] = a_table_row[a_field]
                        
        if table_name == bz_gl.gl_BugzQuery:
            #env.log.error('_M_GetReqFromDB1 Values[ibugz_col]=%s',Values['ibugz_col'])  
            if bz_gl.gl_ChangedataToNow in Values['ibugz_col']:
                if 'changeddate' not in Values['columnlist']:
                    Values['columnlist'].append('changeddate')
            elif bz_gl.gl_NeedInfoCount in Values['ibugz_col']:  
                if bz_gl.gl_NeedInfoDetail not in Values['ibugz_col']:
                    Values['ibugz_col'].append(bz_gl.gl_NeedInfoDetail) 
            elif bz_gl.gl_PersonTouchCount in Values['ibugz_col']:  
                if bz_gl.gl_TouchDetail not in Values['ibugz_col']:
                    Values['ibugz_col'].append(bz_gl.gl_TouchDetail)
            elif bz_gl.gl_ChangeOwnerCount in Values['ibugz_col']:  
                if bz_gl.gl_ChangeOwnerDetail not in Values['ibugz_col']:
                    Values['ibugz_col'].append(bz_gl.gl_ChangeOwnerDetail)                    
            #env.log.error('_M_GetReqFromDB2 Values[ibugz_col]=%s',Values['ibugz_col'])  

            for a_field in bz_gl.gl_tree:  
                Values[a_field] = ''            
            tree_list = bz_utils.string2list_nosort(a_table_row['tree'])
            for idx,a_level in enumerate(tree_list):
                Values['Level'+str(idx)] = a_level 

            AdvanceFields = bz_gl.gl_advance_db_field + bz_gl.gl_advance_bz_field
            for a_field in AdvanceFields:  
                Values[a_field] = ''
            a_list = re.split(r'[#]+', a_table_row['advance_field']) 
            for u in a_list:
                    b_list = re.split(r'[:]+', u)
                    if b_list[0] != '':
                        if str(b_list[0]) == 'GroupNum':
                            Values[str(b_list[0])] = str(b_list[1])
                        else:
                            Values[str(b_list[0])] = (b_list[1]) 
        #env.log.error('_M_GetReqFromDB: Values=%s', Values)
        return Values

def _M_GetReqForDB(env, req, bugz, db_conn, table_name, a_values):  
        Current_User = req.session.sid
        if table_name == bz_gl.gl_BugzQuery:            
            SYSFields=bz_gl.gl_QuerySYSFields
            UIFields=bz_gl.gl_QueryUIFields
            MultiInputFields=bz_gl.gl_QueryUIMultiInputFields
            CheckboxFields=bz_gl.gl_QueryCheckboxFields 
        elif table_name == bz_gl.gl_BugzReminder:            
            SYSFields=bz_gl.gl_RemindSYSFields
            UIFields=bz_gl.gl_RemindUIFields
            MultiInputFields = bz_gl.gl_RemindUIMultiInputFields
            CheckboxFields=bz_gl.gl_RemindCheckboxFields        
        UIFields = UIFields + CheckboxFields + MultiInputFields
        AllFields = SYSFields + UIFields  
        
        Values={}           
        for a_field in UIFields:
            if a_field in CheckboxFields:
                Value_Str=','
                Value_List=[]
                tmp_Value_List = req.args.get(a_field, [])
                if type(tmp_Value_List)!=type(list()):
                    Value_List=[tmp_Value_List]
                else:
                    Value_List=tmp_Value_List
                    
                if len(Value_List)==0:
                    Value_Str=''
                else:
                    Value_Str=',' + ','.join(Value_List)+','
                Values[a_field] = Value_Str   
            elif a_field in MultiInputFields:
                tmp = req.args.get(a_field, '').strip()
                if tmp != '':
                    Values[a_field] = ',' + ','.join(re.split(r'[;,\s]+', tmp)) + ','
                else:
                    Values[a_field] = ''
            else:
                Values[a_field] = req.args.get(a_field, '').strip()
                        
        if table_name == bz_gl.gl_BugzQuery:
            Values['ower'] = req.session.sid 
            bz_url = bugz.BG_SearchUrl2(a_row=a_values)
            if bz_url is None:
                add_notice(req, "Please Select the correct Query Rule!") 
                return None
                
            Values['advance_field'] = _V_Query_advance_field(env, req, a_values)         
            Values['tree'] = _V_Query_tree(env, req, a_values)
            Values['treetype'] = req.args.get(bz_gl.gl_QueryNameL1, '').strip()
            
            Values['orderby'] = a_values['orderby']
            Values['csv_start_time'] = a_values['csv_start_time']
            Values['csv_end_time'] = a_values['csv_end_time']
            Values['csv_history'] = a_values['csv_history']
            if bz_gl.gl_Statics_bugtotal.decode("GBK") in Values['custom_statics']:
                if Values['product'] == '':
                    add_notice(req, "must choose one product!") 
                    return None
                else:
                    if 'product' not in Values['columnlist']:
                        Values['columnlist'] += ('product') + ','
                    if 'component' not in Values['columnlist']:
                        Values['columnlist'] += ('component') + ','
            elif bz_gl.gl_Statics_persontouch.decode("GBK") in Values['custom_statics']:
                if Values['product_ower'] == '':
                    add_notice(req, "must imput 'ProductOwer'!") 
                    return None                
                else:                    
                    if bz_gl.gl_PersonTouchCount not in Values['ibugz_col']:
                        Values['ibugz_col'] += (bz_gl.gl_PersonTouchCount) + ','
                    if bz_gl.gl_TouchDetail not in Values['ibugz_col']:
                        Values['ibugz_col'] += (bz_gl.gl_TouchDetail) + ','     
                    
        elif table_name == bz_gl.gl_BugzReminder:
            Values['SubmittedDate'] = bz_utils.curtime_string()
            Values['State'] = 'enable'
            Values['Submitter'] = Current_User
            
        return Values
            
def _ActionDB(env, req, data, db_conn, table_name, a_values):   
        Current_User = req.session.sid
        if table_name == bz_gl.gl_BugzQuery:            
            SYSFields=bz_gl.gl_QuerySYSFields
            UIFields=bz_gl.gl_QueryUIFields
            MultiInputFields=bz_gl.gl_QueryUIMultiInputFields
            CheckboxFields=bz_gl.gl_QueryCheckboxFields  
            ComposeFields = bz_gl.gl_advance_db_field + bz_gl.gl_advance_bz_field + bz_gl.gl_tree
        elif table_name == bz_gl.gl_BugzReminder:            
            SYSFields=bz_gl.gl_RemindSYSFields
            UIFields=bz_gl.gl_RemindUIFields
            MultiInputFields = bz_gl.gl_RemindUIMultiInputFields
            CheckboxFields=bz_gl.gl_RemindCheckboxFields  
            ComposeFields = []
        UIFields = UIFields + CheckboxFields + MultiInputFields
        AllFields = SYSFields + UIFields + ComposeFields
        
        CurrentRow ={} 
        ID=req.args.get('ID', '').strip() 
        
        action = req.args.get('action', '').strip()
        if table_name == bz_gl.gl_BugzQuery:
            a_table = bz_model.BugzQuery(ID, db_conn)
        elif table_name == bz_gl.gl_BugzReminder:
            a_table = bz_model.BugzReminder(ID, db_conn)    
            
        if ID!='':                     
            if action == "del":
                a_table.delete()
                if table_name == bz_gl.gl_BugzQuery:
                    bz_utils._del_path(bz_gl.gl_csv_rootPath+ID)
                    jump_url = data['SiteRoot']
                    req.redirect(jump_url)
            elif action == "disable" or action == "enable":
                if table_name == bz_gl.gl_BugzReminder: 
                    a_table['State']=action
                    a_table.save_changes()                    
            else:   #edit          
                for field in AllFields:   
                    if field in MultiInputFields:
                        CurrentRow[field]=','.join(a_values[field])
                    else:
                        CurrentRow[field]=a_values[field] 
        else:
            a_values['ID'] = ''
            #for field in UIFields:      
            for field in AllFields:      
                CurrentRow[field]=a_values[field]   
        
        data['CurrentRow']= CurrentRow
        env.log.error('_ActionDB: CurrentRow=%s', CurrentRow)


def _A_SynQuery(env, bugz, db_conn, ID, CurrentUser, cols, rows, a_values):
        #env.log.error('_P_OrinalQuery:ID= %s', ID)
        if ID!='':
            cur_user_dir = bz_gl.gl_csv_rootPath+ID
            if not os.path.exists(cur_user_dir):
                os.mkdir(cur_user_dir)            
            csv_file = ID+'.csv'
            csv_url = bz_gl.bz_csv_url(ID=ID)  
            full_csv_file = os.path.join(cur_user_dir, csv_file)
            
            a_table = bz_model.BugzQuery(ID, db_conn)   
            a_table['csv_start_time'] = bz_utils.curtime_string()
            a_table['csv_end_time'] = 'querying, plz waiting!'
            a_table.save_changes()              
        else:
            csv_file = CurrentUser+'_'+bz_utils._get_current_time_str()+'.csv'
            csv_url = bz_gl.gl_site_url+'iBugzillaTmp/'+csv_file
            full_csv_file = os.path.join(bz_gl.gl_csv_rootPath.replace('iBugzilla','iBugzillaTmp'), csv_file)

        columnlist = a_values['columnlist']  
        ibugz_col = a_values['ibugz_col']
        cols += ['bug_id']+columnlist+ibugz_col    
                
        result = [] 
        query_url = bugz.BG_SearchUrl2(a_row=a_values)  
        bugz.BG_Search(query_url, result, collist=columnlist)  
        _M_QueryResult(env, result, bugz, cols, rows, a_values)
        _A_WriteQueryResult(env, cols, rows, full_csv_file)
        if ID!='':     
            a_table['csv_end_time'] = bz_utils.curtime_string()
            curday_str = bz_utils.curday_string()
            #',' + ','.join(re.split(r'[;,\s]+', req.args.get(a_field, '').strip())) + ','
            if curday_str not in a_table['csv_history']:
                a_table['csv_history'] += curday_str+',' #bz_utils.curday_string()            
            a_table.save_changes()  
        return csv_file#csv_url
                
def _A_Submit(env, req, db_conn, table_name, a_values):   
        Current_User = req.session.sid
        if table_name == bz_gl.gl_BugzQuery:            
            SYSFields=bz_gl.gl_QuerySYSFields
            UIFields=bz_gl.gl_QueryUIFields
            MultiInputFields=bz_gl.gl_QueryUIMultiInputFields
            CheckboxFields=bz_gl.gl_QueryCheckboxFields    
        elif table_name == bz_gl.gl_BugzReminder:            
            SYSFields=bz_gl.gl_RemindSYSFields
            UIFields=bz_gl.gl_RemindUIFields
            MultiInputFields = bz_gl.gl_RemindUIMultiInputFields
            CheckboxFields=bz_gl.gl_RemindCheckboxFields        
        UIFields = UIFields + CheckboxFields + MultiInputFields
        AllFields = SYSFields + UIFields        
          
        ID=req.args.get('ID', '').strip()  
        if ID == '':             
            ID = None
        else:
            a_values['ID'] = ID
            
        if table_name == bz_gl.gl_BugzQuery:
            a_table = bz_model.BugzQuery(ID, db_conn)
        elif table_name == bz_gl.gl_BugzReminder:
            a_table = bz_model.BugzReminder(ID, db_conn) 
            
        if ID == None:
            for name in AllFields:
                if name != 'ID':
                    a_table[name] = a_values[name]
            ID = a_table.insert()            
        else:  
            for name in AllFields:
                a_table[name] = a_values[name]
            a_table.save_changes()      

        return ID
            
def _A_SendEmail(env, req, data, queryurl, ID, csv_file):   
    mail_content = bz_web.bz_queryresult(req, data['cols'], data['rows'])
    maildic = {}                
    maildic['title'] = req.args.get(bz_gl.gl_EmailTitle, '') 
    emaillist = req.args.get(bz_gl.gl_EmailList)
    maildic['decription'] = req.args.get(bz_gl.gl_EmailDescription)
    maildic['to'] = bz_utils.string2tuple(emaillist)                
    maildic['QueryLink'] = queryurl #req.args.get(bz_gl.gl_QueryLink, '') 
    maildic['content'] = bz_web.bz_queryurl(maildic['QueryLink'], ID)  #mail_content.decode('utf-8') 
    if ID!='':
        maildic['attach_file'] = os.path.join(bz_gl.gl_csv_rootPath+ID, ID+'.csv')            
    else:
        maildic['attach_file'] = os.path.join(bz_gl.gl_csv_rootPath.replace('iBugzilla','iBugzillaTmp'), csv_file)            
    bz_utils.SendHtmlMail(env, maildic) 
    add_notice(req, "Sendmail(%s) to %s", maildic['title'], maildic['to']) 
    return 

def _A_WriteQueryResult(env, cols, rows, full_csv_file):   
    #csv_file = a_values['name']+ '_'+data['CurrentUser']+'_'+bz_utils._get_current_time_str()+'.csv'
    #full_csv_file = os.path.join(data['CurrentCSVPath'], csv_file)
                
    import csv_action
    #csv_action.csv_write(full_csv_file, cols, rows)
    a_sheet = bz_utils.curday_string()
    csv_action.xls_write(env, full_csv_file, a_sheet, cols, rows)
    #env.log.error('_A_WriteCSV_QueryResult ok')
    return 

def _A_ReadQueryResult(env, cols, rows, full_csv_file, a_sheet):   
    #csv_file = a_values['name']+ '_'+data['CurrentUser']+'_'+bz_utils._get_current_time_str()+'.csv'
    #full_csv_file = os.path.join(data['CurrentCSVPath'], csv_file)
                
    import csv_action
    #env.log.error('_A_ReadQueryResult: %s',a_sheet)
    a_sheet = a_sheet.split(' ')[0]
    #env.log.error('_A_ReadQueryResult: %s',a_sheet)
    #return csv_action.csv_read(env, full_csv_file, cols, rows)
    return csv_action.xlm_read(env, full_csv_file, a_sheet, cols, rows)

def _A_StaticsQueryResult(env, YM_data_dic, Xaxis_name, csv_file):                         
    import csv_action
    #env.log.error('_A_StaticsQueryResult: %s',a_sheet)
    #return csv_action.xlm_read(env, full_csv_file, a_sheet, cols, rows)
    import pyExcelerator as xl
    #Ã·»°excelŒƒº˛÷–µƒ±Ìµ• ˝ƒø
    sheets = xl.parse_xls(csv_file)
    nsheets = len(sheets)
    #env.log.error('_A_StaticsQueryResult: %s has %s sheets',csv_file,nsheets)

    for n in range(nsheets):
        sheet = sheets[n]
        #Ã·»°±Ìµ•nµƒ√˚≥∆
        sh_name = sheet[0]
        sh_data = sheet[1]
        #env.log.error('_A_StaticsQueryResult: sh_name=%s',sh_name)
        Xaxis_name.append((sh_name))             
        ym_data = [] 
        lenth = 0
        all_data_points = len(sh_data)
        for i in range(all_data_points):
            #a_line = []
            #for j in range(all_data_points):                 
            #    if sh_data.has_key((i,j)):
            #        a_line.append(sh_data[(i,j)])
            #if len(a_line) > 0:                    
            #    lenth += 1
            #else:
            #    lenth -= 1
            #    break
            Flag = False
            for j in range(all_data_points):                 
                if sh_data.has_key((i,j)):
                    Flag = True
                    break
            if Flag:                    
                lenth += 1
            else:
                lenth -= 1
                break
        
        ym_data.append(lenth)            
        #YM_data_dic.update({sh_name:ym_data}) 
        YM_data_dic[sh_name]=ym_data
        #env.log.error('_A_StaticsQueryResult: YM_data_dic=%s',YM_data_dic)
        #dict1.setdefault('b',2) 
    
def _V_Query_tree(env, req, a_values):     
        L1 = a_values[bz_gl.gl_QueryNameL1] 
        L2 = a_values[bz_gl.gl_QueryNameL2]  #req.args.get(bz_gl.gl_QueryNameL2, '').strip().replace(',','') 
        L3 = a_values[bz_gl.gl_QueryNameL3]  #req.args.get(bz_gl.gl_QueryNameL3, '').strip().replace(',','') 
        #env.log.error('_V_Query_tree: %s: %s: %s', L1,L2,L3) 
        tree = bz_gl.gl_tree_split_tag+L1 + bz_gl.gl_tree_split_tag+L2 + bz_gl.gl_tree_split_tag+L3+bz_gl.gl_tree_split_tag            
        #env.log.error('_V_Query_tree: %s', tree) 
        return tree

def _V_Query_advance_field(env, req, a_values):
        Values={}
        advance_field = ''
        for a_field in bz_gl.gl_advance_db_field:
            Values[a_field] = a_values[a_field] #req.args.get(a_field, '').strip()
            if Values[a_field] != '':
                advance_field += a_field+bz_gl.gl_advancefield_split_stag+\
                            Values[a_field]+bz_gl.gl_advancefield_split_btag
        
        env.log.error('_V_Query_advance_field: %s', a_values['GroupNum'])   
        if a_values['GroupNum'] == '0':
            return advance_field
            
        env.log.error('_V_Query_advance_field: %s', a_values)   
        for a_field in bz_gl.gl_advance_bz_field:
            Values[a_field] = a_values[a_field] #req.args.get(a_field, '').strip()
            if Values[a_field] != '---' and Values[a_field] != '':
                advance_field += a_field+bz_gl.gl_advancefield_split_stag+\
                            Values[a_field]+bz_gl.gl_advancefield_split_btag
        env.log.error('_V_Query_advance_field: %s', advance_field)         
        return advance_field
