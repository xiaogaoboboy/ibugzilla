# -*- coding: utf-8 -*-
#

####################window
gl_srv_heart = 'D:\\site\\trac\\log\\bz_srv_heart.txt'
gl_srv_htdocs = 'D:\\site\\trac\\htdocs\\'
gl_csv_rootPath = 'D:\\site\\trac\\htdocs\\iBugzilla\\'
gl_bugz_url = 'http://10.0.6.58/bugzilla/'
gl_internal_bugz_url = 'http://172.16.0.58/bugzilla/'
gl_base_url = 'http://tracsrv/idata/Bugzilla/query/QueryManager'
gl_site_url = 'http://tracsrv/chrome/site/'
###################
#gl_srv_heart = '/srv/trac/Projects/imanage/log/bz_srv_heart.txt'
#gl_bugz_url = 'http://172.16.0.58/bugzilla/'
#gl_base_url = 'http://imanage.sprd.com/idata/Bugzilla/query/QueryManager'

gl_Run_Interval = 60  

gl_prj_log_root = '/srv/trac/Projects/imanage/log'
gl_srv_heart_polling_time = 'srv_heart_polling_time'
gl_guardprocess_flag = 'Server Error!'


gl_schdule_pollingtime = '/srv/trac/Projects/imanage/log/schdule_pollingtime.txt'

gl_QueryCheckboxFields = ['columnlist','ibugz_col', 'custom_statics', \
                            'product','component','bug_status',\
                            'bug_severity', 'cf_come_from']
gl_QueryUIMultiInputFields = ['product_ower'] 
gl_QueryUIFields = ['name', 'f1', 'v1', 'o1', 'f2', 'v2', 'o2', \
                        'f3', 'v3', 'o3', \
                        'chfield', 'chfieldfrom', 'chfieldto']                       
gl_QuerySYSFields = ['ID', 'advance_field', 'tree', 'treetype', 'ower', \
                        'orderby', 'csv_start_time', 'csv_end_time', 'csv_history']
gl_tree = ['Level0', 'Level1', 'Level2']                        
gl_advance_bz_field = ['j_top', 'j50', 'j51', 'j151', \
                        'f51', 'f151', 'f99','f199', 'f50','f500',\
                        'f52', 'o52', 'v52', \
                        'f53', 'o53', 'v53', \
                        'f54', 'o54', 'v54', \
                        'f55', 'o55', 'v55', \
                        'f56', 'o56', 'v56', \
                        'f57', 'o57', 'v57', \
                        'f58', 'o58', 'v58', \
                        'f59', 'o59', 'v59', \
                        'f60', 'o60', 'v60', \
                        'f61', 'o61', 'v61', \
                        'f152', 'o152', 'v152', \
                        'f153', 'o153', 'v153', \
                        'f154', 'o154', 'v154', \
                        'f155', 'o155', 'v155', \
                        'f156', 'o156', 'v156', \
                        'f157', 'o157', 'v157', \
                        'f158', 'o158', 'v158', \
                        'f159', 'o159', 'v159', \
                        'f160', 'o160', 'v160', \
                        'f161', 'o161', 'v161']
gl_advance_db_field =  ['GroupNum', 'TouchStart', 'TouchEnd'] 
                        
gl_StringFilds = ["Bug ID", "Summary", "Assignee","Reporter",  \
                        "CC","Commenter",  \
                        "Base_On_Version", \
                        "Fix_On_Version", 
                        "ChangeType",\
                        "Comment"]
gl_StringOperations = ["is equal to", \
                        "is not equal to", \
                        "is equal to any of the strings", \
                        "contains the string",  \
                        "does not contain the string", \
                        "contains any of the strings", \
                        "contains all of the strings", \
                        "contains none of the strings"]

#gl_TimeFields = ["delta_ts","[Bug creation]","cf_closeddate", "cf_fixeddate",  \
#                        "cf_assigneddate","cf_rootcauseddate", \
#                        "cf_postponedate","cf_needinfodate", \
#                        "cf_invaliddate", "cf_duplicatedate",\
#                        "cf_reopendate"]
gl_TimeFields = ["Changed", "Creation date","ClosedDate", "FixedDate",  \
                        "AssignedDate","RootCausedDate", \
                        "PostponeDate","NeedInfoDate", \
                        "InValidDate", "DuplicateDate",\
                        "ReOpenDate"]
                        
gl_RemindCheckboxFields = ['RemindWeek', 'RemindMonth']   
gl_RemindUIMultiInputFields = ['EmailTo','EmailCc'] 
gl_RemindUIFields = ['Headline', 'RemindType','RemindAction','RemindInterval',\
                            'RemindTime', 'RemindCounter', 'RemindStartDate', 'RemindEndDate', \
                            'BugzQueryID', 'EmailContent'] 
gl_RemindSYSFields = ['ID','Submitter','SubmittedDate','State']


gl_BugzQuery = 'BugzQuery'
gl_BugzReminder = 'BugzReminder'
        
gl_QueryTree = '查询树'
gl_QueryTreeManager = '查询树管理'
gl_EmailManager = '事件管理'
gl_RemindManager = '邮件管理' 
gl_Help = '帮助'
#gl_OriginalFieldQuery = '原始字段查询'
gl_OriginalFieldQuery = '查询管理'

gl_BugzillaField = 'BugzillaField'
gl_BugzillaFields = ['short_desc',\
                    'assigned_to',\
                    'reporter',\
                    'product',\
                    'component',\
                    'bug_severity',\
                    'bug_status',\
                    'cf_come_from',\
                    'changeddate',\
                    'opendate',\
                    'cf_base_on_ver',\
                    'cf_fix_on_ver',\
                    'cf_assigneddate',\
                    'cf_rootcauseddate',\
                    'cf_fixeddate',\
                    'cf_closeddate', \
                    'resolution']
gl_iBugzillaFields = ['ChangeOwnerCount', \
                    'ChangedataToNow', \
                    'NeedInfoCount', \
                    'PersonTouchCount']
gl_ChangeOwnerCount = 'ChangeOwnerCount'
gl_ChangeOwnerDetail = 'ChangeOwnerDetail'
gl_ChangedataToNow = 'ChangedataToNow'
gl_NeedInfoCount = 'NeedInfoCount'
gl_NeedInfoDetail = 'NeedInfoDetail'
gl_PersonTouchCount = 'PersonTouchCount'
gl_TouchDetail = 'TouchDetail'
gl_iBugzillaStatics = ['各模块CR总数及模块责任人(By Product)']
                    
gl_StaticsField = 'StaticsField'
gl_StaticsFields = ["各模块CR总数及模块责任人(By Product)", \
                    "Test2"]
gl_Statics_bugtotal = '各模块CR总数及模块责任人(By_Product)'
gl_Statics_persontouch = '个人活跃度(By_ProductOwer)'
gl_Statics_bugtotal_cols = ['Component', 'Ower', 'CR TotalNum']
gl_Statics_persontouch_cols = ['ProductOwer', 'Total-PersonTouch']

gl_SpecialFieldQuery = '统计字段查询'
gl_SpecialField = 'SpecialField'
gl_SpecialFields = ['ChangeOwnerCount', 'ChangedataToNow']


gl_day = 'day'
gl_hour = 'hour'
gl_min = 'min'

gl_BaseOnVersion = 'BaseOnVersion'
gl_FixOnVersion = 'FixOnVersion'

gl_From = 'From'
gl_To = 'To'

gl_SearchOwerDepart = 'SearchOwerDepart'
gl_SynchronizeOwer = 'SynchronizeOwer'

gl_SearchDepart = 'SearchDepart'
gl_SynchronizeDepart = 'SynchronizeDepart'

gl_SynchronizeOwer_3levels = 'SynchronizeOwer_3levels' 
gl_SynchronizeDepart_3levels = 'SynchronizeDepart_3levels' 
gl_SynchronizeDepart_leader = 'SynchronizeDepart_leader'
gl_SynchronizeBugzDB = 'SynchronizeBugzDB'
gl_SynchronizeBugzData = 'SynchronizeBugzData'
gl_SynchronizeOwerDepart = 'SynchronizeOwerDepart'
gl_SynchronizeOwerTime = 'SynchronizeOwerTime'
gl_SchduleTrigger = 'SchduleTrigger' 

gl_TimeField = 'TimeField'
gl_AllField = 'AllField'
gl_FieldValue = 'FieldValue'
gl_Status = 'Status'
gl_Component = 'Component'
gl_Product = 'Product'
gl_Severity = 'Severity'
gl_Reporter = 'Reporter'
gl_Assignee = 'Assignee'
gl_BugID = 'BugID' 
gl_User_SN = 'User_SN'
gl_EmailList = 'EmailList'
gl_QueryLink = 'QueryLink'
gl_EmailDescription = 'EmailDescription'
gl_QueryID = 'QueryID'
gl_EmailURL = 'EmailURL'
gl_EmailTitle = 'EmailTitle'
gl_Debug = 'gl_Debug'

gl_BugNow = 'CR现状统计'

gl_BugTrendNew = 'CR新增趋势分析'
gl_BugTrend = 'CR解决趋势分析'
gl_BugTrend_cols = [] 

gl_BugOriginalData = '原始数据'  
gl_BugOriginalData_cols = ["bug_id", "short_desc", "assigned_to", "bug_status", \
                        "bug_severity", "cf_come_from", "opendate", \
                        "level4", "level3", \
                        "level2", "level1", \
                        "start_time", "end_time", "resolution"] 

gl_collist = ["product", "component", "bug_status", \
                        "bug_severity", "reporter", "assigned_to",\
                        "cf_come_from", "cf_base_on_ver", "cf_fix_on_ver", "changeddate"] 

gl_srch_bugzdb_collist = ['short_desc', \
                    'assigned_to',\
                    'product',\
                    'component',\
                    'bug_severity',\
                    'bug_status',\
                    'cf_base_on_ver',\
                    'cf_fix_on_ver',\
                    'reporter',\
                    'cf_come_from',\
                    'changeddate',\
                    'opendate',\
                    'cf_assigneddate',\
                    'cf_rootcauseddate',\
                    'cf_fixeddate',\
                    'cf_closeddate', \
                    'resolution']
#                    'creation']
#                    'creation_ts', \
#                    'delta_ts']

gl_srch_bugzdb_id_collist = ['bug_id', 'short_desc', 'assigned_to',\
                    'product',\
                    'component',\
                    'bug_severity',\
                    'bug_status',\
                    'cf_base_on_ver',\
                    'cf_fix_on_ver',\
                    'reporter',\
                    'cf_come_from',\
                    'resolution']
                    
                        
gl_BugInTime = 'CR处理及时率'  
gl_BugInTime_cols = ["open2assign(Days)", "assign2root_cause(Days)", \
                        "root_cause2fix(Days)", "fix2close(Days)"]   


gl_BugClass = 'CR等级分布' 
gl_BugClass_cols = ["1-Critical", "2-Major", "3-Average", "4-Minor", \
                        "5-Improved"] 
                        
gl_BugOrigin = 'CR来源' 
gl_BugOrigin_cols = ["Customer", "Development_Area", "FAE", "FT", \
                        "Internal_Customer", "PLDSQA", "Test_Area", "TR_TEST", \
                        "UEIT"] 
                 
gl_ComeFrom = 'ComeFrom'
gl_QueryName = 'QueryTreeName'
gl_QueryNameL1 = 'Level0'
gl_QueryNameL2 = 'Level1'
gl_QueryNameL3 = 'Level2'
gl_tree_split_tag = ','
gl_advancefield_split_btag = '#'
gl_advancefield_split_stag = ':'

gl_QueryL1_Names = ['PersonnalQuery','CommonQuery']
gl_PersonnalQuery = 'PersonnalQuery'
gl_CommonQuery = 'CommonQuery'
                        
gl_OrderBy = 'OrderBy'
gl_ColumnList = 'ColumnList'
gl_ExColumnList = 'ExColumnList'

gl_Myall = 'My All'
gl_MyToDo = 'My To Do'
gl_NewQuery = 'My Query'
gl_NewCommonQuery = 'Query Manager'
gl_DelQuery = 'DelQuery'

gl_Submit_Query = 'Query'
gl_Save_Query = 'Save'

gl_Submit_ExQuery = 'Submit_ExQuery'
gl_Query_Email = 'Query_Email'
gl_Send_Email = 'Send_Email'


gl_Department = "部门"
gl_DepartmentName = "DepartmentName"
gl_DepartmentUpName = "DepartmentUpName"
gl_DepartmentLeader = "DepartmentLeader"
gl_DepartmentNames = ["name", "level_type", "leader", "up_name"]
gl_DepartmentMMINames = ["name", "level_type", "leader", "up_name"]
gl_DepartmentLevel = "DepartmentLevel"
gl_DepartmentLevels = ["level1", "level2", "level3", "level4"]

gl_DepartmentLevelID = 'DepartmentLevelID'
gl_Level1 = 'level1'
gl_Level2 = 'level2'
gl_Level3 = 'level3'
gl_Level4 = 'level4'

gl_Unit = "统计粒度"
gl_UnitID = "Unit"
gl_Person = "Ower"


gl_StaticsType = "统计类型"
gl_StaticsTypeID = 'StaticsType'

gl_BugStaticsStart = 'BugStaticsStart'
gl_BugStaticsEnd = 'BugStaticsEnd'

gl_BranchType = "BranchType"
gl_DM_BASE = "DM_BASE"

def bz_csv_url(ID=None, csv_file=None):
    if ID is not None:             
        csv_file = ID+'.csv'
        csv_url = 'http://tracsrv/chrome/site/iBugzilla/'+ID+'/'+csv_file  
    elif csv_file is not None:
        csv_url = gl_site_url+'iBugzillaTmp/'+csv_file        
    return csv_url

def bz_SiteRoot(path_info):
    return 'http://tracsrv/idata/Bugzilla/query/'+path_info
 


def bz_bugz_url(req_url):  
        req_url = req_url.replace('&ctype=csv','')
        return req_url

def bz_bugz_url_csv(req_url):  
        req_url += "&ctype=csv"
        return req_url

def bz_startday(req):        
        import bz_utils
        from datetime import datetime, timedelta
        
        YearMonth_Start = req.args.get(gl_BugStaticsStart, '').strip()
        if not YearMonth_Start:
            YearMonth_Start = '2012-01-01'          
        return YearMonth_Start

def bz_endday(req):        
        import bz_utils
        from datetime import datetime, timedelta
        
        YearMonth_End = req.args.get(gl_BugStaticsEnd, '').strip()        
        if not YearMonth_End:
            YearMonth_End = datetime.strftime(datetime.now(),"%Y-%m-%d")  
        
        return YearMonth_End

def bz_chfield(req):        
        import bz_utils
        from datetime import datetime, timedelta
        
        YearMonth_End = req.args.get(gl_BugStaticsEnd, '').strip()        
        if not YearMonth_End:
            YearMonth_End = datetime.strftime(datetime.now(),"%Y-%m-%d")  
        
        return '[Bug creation]'

def bz_weeks(req):        
        import bz_utils
        from datetime import datetime, timedelta
        
        YearMonth_Start = req.args.get(gl_BugStaticsStart, '').strip()
        YearMonth_End = req.args.get(gl_BugStaticsEnd, '').strip()        
        if not YearMonth_End:
            YearMonth_End = datetime.strftime(datetime.now(),"%Y-%m-%d")
        if not YearMonth_Start:
            YearMonth_Start = '2012-01-01' 
        cols = bz_utils.dayfiled2weeks(YearMonth_Start,YearMonth_End)    
        
        return cols

def bz_statics_cols(req, statics_type):     
    if statics_type == gl_BugInTime.decode("GBK"):
        cols = gl_BugInTime_cols
    elif statics_type == gl_BugNow.decode("GBK"):
        cols = gl_BugClass_cols
    elif statics_type == gl_BugClass.decode("GBK"):
        cols = gl_BugClass_cols        
    elif statics_type == gl_BugOrigin.decode("GBK"):
        cols = gl_BugOrigin_cols   
    elif statics_type == gl_BugTrend.decode("GBK") \
            or statics_type == gl_BugTrendNew.decode("GBK"): 
        return bz_weeks(req)  
    else:
        cols = []  
    
    return cols


def bz_statics_Yaxis_Title(statics_type):     
    if statics_type == gl_BugInTime.decode("GBK"):
        Yaxis_Title_name = 'CR处理天数'
    elif statics_type == gl_BugClass.decode("GBK"):
        Yaxis_Title_name = 'CR数'
    elif statics_type == gl_BugNow.decode("GBK"):
        Yaxis_Title_name = '未解决CR数量'        
    elif statics_type == gl_BugOrigin.decode("GBK"):
        Yaxis_Title_name = 'CR数'
    elif statics_type == gl_BugTrend.decode("GBK"):
        Yaxis_Title_name = '解决CR数量'
    elif statics_type == gl_BugTrendNew.decode("GBK"):
        Yaxis_Title_name = '新增CR数量'
    else:
        Yaxis_Title_name = 'Todo'

    
    return Yaxis_Title_name

def bz_new_usr(env, req, a_Bugz_table): 
    user = []
    assigned_to = req.args.get(gl_Assignee)
    #env.log.error('bz_new_usr: assigned_to=%s', assigned_to)

    if assigned_to is not None and assigned_to !='':
        user.append(assigned_to.strip())
    else:  
        deps = bz_departments(req)
        env.log.error('bz_usr: deps=%s', deps)
        for a_dep in deps:
            QF = {}   
            QF['field_'+a_dep['fname']] = a_dep['value']            
            Bugz_tables = a_Bugz_table.select(QF)            
            for a_table in Bugz_tables:
                leader = a_table['ower']
                user.append(leader)
    
    return user
  

def bz_usr(env, req, a_Bugz_table): 
    user = []
    assigned_to = req.args.get(gl_Assignee)
    #env.log.error('bz_usr: assigned_to=%s', assigned_to)

    if assigned_to is not None and assigned_to !='':
        user.append(assigned_to.strip())
    else:  
        deps = bz_departments(req)
        #env.log.error('bz_usr: deps=%s', deps)
        for a_dep in deps:
            QF = {}                  
            QF['field_name'] = a_dep['value']
            QF['field_level_type'] = a_dep['fname']
            Bugz_tables = a_Bugz_table.select(QF)            
            for a_table in Bugz_tables:
                #env.log.error('bz_usr: leader=%s', leader)
                leader = a_table['leader']
                user.append(leader)
        
    #for k, v in req.args.iteritems():
    #    if k==gl_Assignee and v:
    #        if type(v)==type(list()):
    #            myDepartment=v
    #        else:
    #            myDepartment=[v] 
    
    return user


def bz_new_owers(env, req, a_Bugz_table): 
    all_users = []          
    users = bz_new_usr(env, req, a_Bugz_table)
    env.log.error('bz_new_owers: users=%s', users)
    for a_User in users:                  
        all_users.append((a_User)) 

    return all_users

def bz_sprd_all_usr(env): 
    import sprd_user_model

    a_user_obj = sprd_user_model.SPRD_User(None)
    all_Users = []
    all_mem = a_user_obj.Get_All_Member('leo.li')             
    if all_mem is not None:
        all_users = [ a_user['EName'].lower().replace(' ', '.') for a_user in all_mem]             
    all_users.append(('leo.li'))     
    env.log.error('bz_sprd_all_usr: %s', all_users)
    return all_Users

def bz_owers(env, req, a_Bugz_table): 
    import sprd_user_model

    a_user_obj = sprd_user_model.SPRD_User(None)
    all_users = []   
    #all_department = a_user_obj.Get_DEV_Dep_Level_2()         
    users = bz_usr(env, req, a_Bugz_table)
    #env.log.error('bz_owers: users=%s', users)
    for Current_User in users:        
        #all_Direct_user = a_user_obj.Get_Direct_Member(Current_User)       
        all_mem = a_user_obj.Get_All_Member(Current_User)             
        if all_mem is not None:
            all_users = [ a_user['EName'].lower().replace(' ', '.') for a_user in all_mem]             
        all_users.append((Current_User)) 

    return all_users


            
def bz_departments(req):   
    import bz_web
    dep = [] 
    bz_web.web_get_checkbox(req, gl_Level1, dep)
    bz_web.web_get_checkbox(req, gl_Level2, dep)
    bz_web.web_get_checkbox(req, gl_Level3, dep)
    bz_web.web_get_checkbox(req, gl_Level4, dep)  

    #level = req.args.get(gl_DepartmentLevelID)
    #if level == gl_Level1:
    #    dep = gl_Level1_departments
    #elif level == gl_Level2:
    #    dep = gl_Level2_departments
    #elif level == gl_Level3:
    #    dep = gl_Level3_departments
    #elif level == gl_Level4:
    #    dep = gl_Level4_departments
    #env.log.error('bz_departments: dep = %s', dep)
    
    return dep

def bz_specialfileds(req):   
    import bz_web
    units = [] 
    bz_web.web_get_checkbox(req, gl_SpecialField, units)    
    return units    

def bz_bugzillafileds(req):   
    import bz_web
    units = [] 
    bz_web.web_get_checkbox(req, gl_BugzillaField, units)    
    return units     
    
