# -*- coding: utf-8 -*-
#
import sys
reload(sys)  
sys.setdefaultencoding('utf-8')

import bz_gl
import bz_utils
import bz_model


def bz_nav(req):
    js = ''
    js += "<a href=\""+req.href('/idata/Bugzilla/query/Bz_QueryTree')+"\">"+bz_gl.gl_QueryTree.decode("GBK")+"</a><code>  |  </code>"        
    #js += "<a href=\""+req.href('/idata/Bugzilla/query/Bz_QueryTreeManager')+"\">"+bz_gl.gl_QueryTreeManager.decode("GBK")+"</a><code>  |  </code>"
    js += "<a href=\""+req.href('/idata/Bugzilla/query/Bz_QueryManager')+"\">"+bz_gl.gl_OriginalFieldQuery.decode("GBK")+"</a><code>  |  </code>"     
    js += "<a href=\""+req.href('/idata/Bugzilla/query/Bz_EmailManager')+"\">"+bz_gl.gl_RemindManager.decode("GBK")+"</a><code>  |  </code>"
    js += "<a href=\""+req.href('/idata/Bugzilla/query/Bz_Help')+"\">"+bz_gl.gl_Help.decode("GBK")+"</a><code>  |  </code>"    
    
    if req.session.sid == 'song.shan':    
        #js += "<a href=\""+req.href('/idata/Bugzilla/query/Bz_RemindManager')+"\">"+bz_gl.gl_RemindManager.decode("GBK")+"</a><code>  |  </code>"
        #js += "<a href=\""+req.href('/idata/Bugzilla/query/Bz_EmailManager')+"\">"+bz_gl.gl_EmailManager.decode("GBK")+"</a><code>  |  </code>"
        js += "<a href=\""+req.href('/idata/Bugzilla/query/Bz_Debug')+"\">"+'Debug'.decode("GBK")+"</a><code>  |  </code>"
        #js += "<a href=\""+req.href('/idata/Bugzilla/query/Bz_SpecailField')+"\">"+bz_gl.gl_SpecialFieldQuery.decode("GBK")+"</a><code>  |  </code>"
        #js += "<a href=\""+req.href('/idata/Bugzilla/query/Bz_QueryStatics')+"\">QueryStatics</a><code>  |  </code>" 
        #js += "<a href=\""+req.href('/idata/Bugzilla/query/Bz_Setting')+"\">Setting</a><code> </code>  |  </code>"
        #js += "<a href=\""+req.href('/idata/Bugzilla/query/Bz_Debug')+"\">Debug</a><code>  </code>"         
    js += "<br /><br />"         
    return js

def bz_statics_nav(req):
        js = u''
        #js += u"<a href=\""+req.href('/idata/setting/Bugzilla/Bz_QueryStatics')+u"\">BUG工作量</a><code>  |  </code>"      
        js += u"<a href=\""+req.href('/idata/setting/Bugzilla/Bz_QueryStatics')+u"\">WorkStatics</a><code>  |  </code>"      
        #js += u"<a href=\""+req.href('/idata/setting/Bugzilla/Bz_QueryStatics2')+u"\">BUG处理进度</a><code> </code>" 
        js += u"<a href=\""+req.href('/idata/setting/Bugzilla/Bz_QueryStatics2')+u"\">ProgressStatics</a><code> </code>" 
        
        js += u"<br /><br />"         
        #return js.encode('utf-8')
        return js.encode('utf-8')

def bz_querytree_name(req):
    js = ''      
    js += web_single_sel(bz_gl.gl_QueryL1_Names, bz_gl.gl_QueryNameL1,)

    js += web_b(bz_gl.gl_QueryNameL2)
    js += web_input(req,  bz_gl.gl_QueryNameL2, '', size='20') 
    #if req.session.sid == 'song.shan':
    #js += web_input(bz_gl.gl_QueryNameL3, bz_gl.gl_QueryNameL3, '', size='20') 
    return js

def bz_depart_tree(req, a_Bugz_table):
        js = "d = new dTree('d');"        
        
        index = 0
        father_id = -1
        js += tree_add_node(str(index), str(father_id), 'Spreadtrum', '0', is_null=True)
        father_id = index

        QF = {}  
        QF['field_level_type'] = 'level1'
        Bugz_tables = a_Bugz_table.select(QF)
        for a_table in Bugz_tables:
            l1_name = a_table['name']
            index = index + 1            
            js += tree_add_node(str(index), str(father_id), l1_name, '0', is_null=True) #L1
            sec_father_id = index

            QF['field_level_type'] = 'level2'
            QF['field_up_name'] = l1_name
            Bugz_tables = a_Bugz_table.select(QF) 
            for a_table in Bugz_tables: 
                l2_name = a_table['name']              
                index = index + 1
                js += tree_add_node(str(index), str(sec_father_id), l2_name, '0', is_null=True) #L2   
                third_father_id = index

                QF['field_level_type'] = 'level3'
                QF['field_up_name'] = l2_name
                Bugz_tables = a_Bugz_table.select(QF) 
                for a_table in Bugz_tables: 
                    l3_name = a_table['name']    
                    index = index + 1
                    js += tree_add_node(str(index), str(third_father_id), l3_name, '0', is_null=True) #L3   
                    fourth_father_id = index

                    QF['field_level_type'] = 'level4'
                    QF['field_up_name'] = l3_name
                    Bugz_tables = a_Bugz_table.select(QF) 
                    for a_table in Bugz_tables: 
                        l4_name = a_table['name']    
                        index = index + 1
                        js += tree_add_node(str(index), str(fourth_father_id), l4_name, '0', is_null=True) #L4  
                       
        js += "\r\n" + "document.write(d);"  
        
        return js 
        
def bz_query_tree(env, req, treelist):
        js = "d = new dTree('d');"        
        all_roots = []
        all_root_indexs = {}
        a_node = {}
        a_node['index'] = 0
        father_id = -1
        a_node['name'] = 'WorkSpace'
        a_node['is_leaf'] = False
        a_root = 'WorkSpace'
        js += tree_add_node(a_node, father_id, all_root_indexs, all_roots, a_root) #L0 root   
        
        for id,name,tree in treelist:             
            a_levels = {}
            tree_list = bz_utils.string2list_nosort(tree)
            for idx,a_level in enumerate(tree_list):
                a_levels['L'+str(idx+1)] = a_level 
            tree_roots = (idx+1)
            #env.log.error('bz_query_tree: %s,%s', a_levels, tree_roots)
            
            if a_levels['L1'] is not None and a_levels['L1'] != '':
                a_root = ','+a_levels['L1']+','
                if a_root not in all_roots:
                    a_node['name'] = a_levels['L1']
                    a_node['is_leaf'] = False            
                    js += tree_add_node(a_node, all_root_indexs['WorkSpace'], all_root_indexs, all_roots, a_root) #L1 root                      
                if tree_roots == 1:                        
                    a_node['name'] = name
                    a_node['name_id'] = id
                    a_node['is_leaf'] = True            
                    js += tree_add_node(a_node, all_root_indexs[a_root], all_root_indexs, all_roots, a_root)  #L2 leaf
                    continue
                    
                if a_levels['L2'] is not None and a_levels['L2'] != '':
                    a_root = ','+a_levels['L1']+','+a_levels['L2']+','                    
                    if a_root not in all_roots:                                        
                        a_node['name'] = a_levels['L2']
                        a_node['is_leaf'] = False    
                        js += tree_add_node(a_node, all_root_indexs[','+a_levels['L1']+','], all_root_indexs, all_roots, a_root)  #L2 root
                    if tree_roots == 2:
                        a_node['name'] = name
                        a_node['name_id'] = id
                        a_node['is_leaf'] = True 
                        js += tree_add_node(a_node, all_root_indexs[a_root], all_root_indexs, all_roots, a_root) #L3 leaf
                        continue

                    if a_levels['L3'] is not None and a_levels['L3'] != '':
                        a_root = ','+a_levels['L1']+','+a_levels['L2']+','+a_levels['L3']+','
                        if a_root not in all_roots:                             
                            a_node['name'] = a_levels['L3']
                            a_node['is_leaf'] = False            
                            js += tree_add_node(a_node, all_root_indexs[','+a_levels['L1']+','+a_levels['L2']+','], all_root_indexs, all_roots, a_root)  #L3 root
                        if tree_roots == 3:
                            a_node['name'] = name
                            a_node['name_id'] = id
                            a_node['is_leaf'] = True 
                            js += tree_add_node(a_node, all_root_indexs[a_root], all_root_indexs, all_roots, a_root)  #L4 leaf 
                            continue
                
        js += "\r\n" + "document.write(d);"  
        
        return js     

def bz_mailcollist(req):
        columns = []   
        if 1:
            query_url = req.args.get(bz_gl.gl_EmailURL, '')
            if query_url is not None and query_url != '':                
                #columns.insert(0,"bug_id")
                #columns.insert(1,"short_desc")                
                
                modules = query_url.split('&',query_url.count('&')) 
                #self.log.error("_get_collist modules=%s",modules)  
                for sub_mod in modules:     
                    if sub_mod.find('columnlist') != -1:                
                        modules2 = sub_mod.split('%2C',sub_mod.count('%2C')) #%2C ,
                        #self.log.error("_get_collist modules2=%s",modules2)  
                        for sub_mod2 in modules2:
                            if sub_mod2 != '':
                                columns.append(sub_mod2.replace('columnlist=',''))   
                                
        #self.log.error("_get_mailcollist columns=%s",columns)                        
        return columns   #list


def bz_old_collist(req):
    return bz_gl.gl_srch_bugzdb_collist 
    
def bz_bugzilla_collist(req, show_collist):
        columns = [] 
        all_fileds = bz_gl.bz_bugzillafileds(req)
        if len(all_fileds) > 0:
            for a_unit in all_fileds:                
                value = a_unit['value']
                fname = a_unit['fname'] 
                columns.append(value)
                show_collist.append(value)
        columns.insert(0,"bug_id")
        columns.insert(1,"short_desc")     
        show_collist.insert(0,"bug_id")
        show_collist.insert(1,"short_desc") 
        
        return columns

def bz_specail_collist(req, show_collist, bugzilla_collist):
        columns = []
        all_fileds = bz_gl.bz_specialfileds(req)
        if len(all_fileds) > 0:
            for a_unit in all_fileds:                
                value = a_unit['value']
                fname = a_unit['fname'] 
                if value == bz_gl.gl_ChangedataToNow:
                    if 'changeddate' in bugzilla_collist:
                        pass
                    else:
                        bugzilla_collist.append('changeddate')
                        show_collist.append('changeddate')
                columns.append(value)
                show_collist.append(value)          
        return columns

def bz_statics_collist(req):
        columns = []
        all_fileds = bz_gl.bz_specialfileds(req)
        if len(all_fileds) > 0:
            for a_unit in all_fileds:                
                value = a_unit['value']
                fname = a_unit['fname'] 
                if value == bz_gl.gl_ChangedataToNow:
                    if 'changeddate' in bugzilla_collist:
                        pass
                    else:
                        bugzilla_collist.append('changeddate')
                        show_collist.append('changeddate')
                columns.append(value)
                show_collist.append(value)          
        return columns
        

def bz_queryurl(queryurl, ID):
        #queryname = ("Link To Bugzilla".decode('GBK'))
        #js = '<legend>'+("Email".decode('GBK'))+'</legend>'
        js = "<div style=\"background: #ffd;border: 1px solid gray;width:1300px;\">"        
        js += "<br />"        
        js += "<br />" 
        js += web_b("BUG统计输出结果".decode('GBK'))
        #js += u"<a href=\""+queryurl+"\"  target=\"_blank\">"+queryname+"</a>" 

        js += u"<a href=\""+queryurl+"\"  target='_blank'>BugzillaResult</a>&nbsp;&nbsp;&nbsp;" 
        if ID is not None and ID!='':
            CSV_url = bz_gl.bz_csv_url(ID=ID)
            js += u"<a href=\""+CSV_url+"\">CSV</a>&nbsp;&nbsp;&nbsp;" 
            iBugzillaResult_url = bz_gl.bz_SiteRoot('Bz_QueryManager')+'?ID='+ID
            js += u"<a href=\""+iBugzillaResult_url+"\" target='_blank' >iBugzillaResult</a>&nbsp;&nbsp;&nbsp; "                       
            js += "<br />"  

            js += web_b("周期变化趋势图表".decode('GBK'))
            iBugzillaResultTrend_url = bz_gl.bz_SiteRoot('Bz_TrendPic')+'?ID='+ID
            js += u"<a href=\""+iBugzillaResultTrend_url+"\" target='_blank' >iBugzillaResultTrend</a>&nbsp;&nbsp;&nbsp; "                       
        js += "<br />"  
        js += "</div>"              
                    
        return js
                
def bz_queryresult(req, cols, rows):
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')

    if 1:
        js = ""  
        js += u"<table id=\"large\" name=\"large\" class=\"listing\">"
        js += u"<thead>"
        js += u"<tr>"
        for col in cols: 
            js += u"<th width=\"75\">"
            js += col
            js += u"</th>"
        js += u"</tr>"
        js += u"</thead>"
		
        js += u"<tbody>"
        for row in rows:   
            js += u"<tr>"
            for idx,col in enumerate(row):   
                js += u"<td>"
                if idx == 0:
                    href = u'http://10.0.6.58/bugzilla/show_bug.cgi?id='+str(col)
                    js += u"<a href=\""+href+"\"  target=\"_blank\">"+str(col)+"</a>"
                else:
                    js = u' '.join((js, str(col))).encode('utf-8')
                    #js += (str(col)).decode('GBK')
                js += u"</td> " 
            js += u"</tr>"
        js += u"</tbody>"		
        js += u"</table>"
        
    return js
        

def bz_setting(env, req, bugz):
        import time
        from datetime import datetime 
        
        string = bz_utils.read_file(bz_gl.gl_schdule_pollingtime) 
        tup = time.strptime(string,"%Y-%m-%d %H:%M:%S") 
        
        curday = int(datetime.strftime(datetime.now(),"%d"))
        curhour = int(datetime.strftime(datetime.now(),"%H")) 
        curmin = int(datetime.strftime(datetime.now(),"%M")) 
        
        js = '' 
        sid = req.session.sid

        js += "<div style=\"background: #ffd;border: 1px solid gray;width:1200px;position: relative;margin-left:auto;margin-right:auto;\">"
        js += "<br />"

        #env.log.error('bz_setting: %s,%s,%s', curday, curhour, (curmin - int(tup[4])))
        #env.log.error('bz_setting: %s', tup)
        if curday != int(tup[2]) \
                    or curhour != int(tup[3]) \
                    or (curmin - int(tup[4])) > 1:
            js += web_button(bz_gl.gl_SchduleTrigger, "启动同步触发器".decode('GBK'))
            
        if req.session.sid == 'song.shan':
            #js += web_button(bz_gl.gl_SynchronizeOwer_3levels, "同步三级个人部门信息".decode('GBK'))
            #js += web_button(bz_gl.gl_SynchronizeDepart_3levels, "同步三级部门信息".decode('GBK')) 
            #js += web_button(bz_gl.gl_SynchronizeDepart_leader, "同步前三级部门领导信息".decode('GBK')) 
            js += web_button(bz_gl.gl_SynchronizeBugzData, "同步BugList信息".decode('GBK'))
            js += web_button(bz_gl.gl_SynchronizeOwerDepart, "同步BugList部门信息".decode('GBK'))
            
        #js += web_b("工号".decode('GBK'))
        #js += web_input(bz_gl.gl_User_SN, '')        
        js += "<br /><br />"  

        js += web_b("Ower".decode('GBK'))
        js += web_input(req,  bz_gl.gl_Assignee, '', size='10') 
        js += web_button(bz_gl.gl_SearchOwerDepart, "查询个人部门信息".decode('GBK'))  
        js += web_button(bz_gl.gl_SynchronizeOwer, "修改个人部门信息".decode('GBK'))
        js += "<br /><br />"  
        
        js += web_b("部门名称".decode('GBK')) 
        js += web_input(req,  bz_gl.gl_DepartmentName, '', size='10') 
        js += web_single_sel(bz_gl.gl_DepartmentLevels, bz_gl.gl_DepartmentLevel) 
        js += web_b("部门领导".decode('GBK')) 
        js += web_input(req,  bz_gl.gl_DepartmentLeader, '', size='10') 
        js += web_b("上级部门名称".decode('GBK')) 
        js += web_input(req,  bz_gl.gl_DepartmentUpName, '', size='10') 
        js += web_button(bz_gl.gl_SearchDepart, "查询部门信息".decode('GBK'))
        js += web_button(bz_gl.gl_SynchronizeDepart, "修改部门信息".decode('GBK'))
        js += "<br /><br />"
        
                    
              
        js += "<br /><br />"   
     
            
        js += "</div>" 
        
        js += "<br /><br />"      
         
        return js


def bz_dep(env, req, a_Bugz_table, level_type, level_name):   
        QF = {}          
        QF['field_level_type'] = level_type  
        Bugz_tables = a_Bugz_table.select(QF) 

        return web_checkboxs(env, req, level_type, level_name, Bugz_tables)

def bz_fields(env, req, checkbox_id, name, checkbox_list):  
        if checkbox_id == bz_gl.gl_StaticsField:
            checkboxs = []   
            tmp={}
            tmp['name'] = bz_gl.gl_Statics_bugtotal.decode('GBK')            
            checkboxs.append(tmp)
            js = web_checkboxs(env, req, checkbox_id, name, checkboxs)
            js += "<br />"        
        else:
            checkboxs = []   
            for a_field in checkbox_list:
                tmp={}
                tmp['name'] = a_field.decode('GBK')            
                checkboxs.append(tmp)            
            js = web_checkboxs(env, req, checkbox_id, name, checkboxs)
            js += "<br />"
        return js
     
def bz_statics(env, req, bugz, db_conn): 
        js = '' 

        sid = req.session.sid

        js += "<div style=\"background: #ffd;border: 1px solid gray;width:1200px;position: relative;margin-left:auto;margin-right:auto;\">"
        js += "<br />"

        js += web_b("Ower".decode('GBK'))
        js += web_input(req,  bz_gl.gl_Assignee, '')  
        js += web_button(bz_gl.gl_SynchronizeBugzDB, "同步BugzDB".decode('GBK'))
        js += "<br /><br />"            

        js += web_b("开始日期".decode('GBK'))
        js += web_input(req,  bz_gl.gl_BugStaticsStart, '',size='10')
        js += web_b("结束日期".decode('GBK'))
        js += web_input(req,  bz_gl.gl_BugStaticsEnd, '',size='10')
        js += "<br />" 
        #js += web_b("分支类型".decode('GBK'))
        #js += web_radio(bz_gl.gl_BranchType, bz_gl.gl_DM_BASE, True)
        js += "<br /><br />" 

        #js += web_b(bz_gl.gl_Department.decode('GBK')) 
        #js += web_single_sel(bz_gl.gl_Level1_departments, bz_gl.gl_Level1)
        #js += web_single_sel(bz_gl.gl_Level2_departments, bz_gl.gl_Level2)
        #js += web_single_sel(bz_gl.gl_Level3_departments, bz_gl.gl_Level3)        
        #js += web_single_sel(bz_gl.gl_Level4_departments, bz_gl.gl_Level4)
        #js += "<br />" 
        #js += web_b("部门等级".decode('GBK'))
        #js += web_radio(bz_gl.gl_DepartmentLevelID, bz_gl.gl_Level1.decode('GBK'), False)
        #js += web_radio(bz_gl.gl_DepartmentLevelID, bz_gl.gl_Level2.decode('GBK'), False)
        #js += web_radio(bz_gl.gl_DepartmentLevelID, bz_gl.gl_Level3.decode('GBK'), False)
        #js += web_radio(bz_gl.gl_DepartmentLevelID, bz_gl.gl_Level4.decode('GBK'), False) 
        #js += "<br />"

        a_Bugz_table = bz_model.Bugz_Depart(None, db_conn)
        #js += bz_dep(env, req, a_Bugz_table, bz_gl.gl_Level1, "一级部门".decode('GBK'))
        js += bz_dep(env, req, a_Bugz_table, bz_gl.gl_Level2, "二级部门".decode('GBK'))
        js += bz_dep(env, req, a_Bugz_table, bz_gl.gl_Level3, "三级部门".decode('GBK'))
        js += bz_dep(env, req, a_Bugz_table, bz_gl.gl_Level4, "四级部门".decode('GBK'))
        js += "<br /><br />" 
        
        js += web_b(bz_gl.gl_Unit.decode('GBK'))  
        js += web_radio(bz_gl.gl_UnitID, bz_gl.gl_Department.decode('GBK'), True)         
        js += web_radio(bz_gl.gl_UnitID, bz_gl.gl_Person, False)
       
        js += "<br />"
        js += web_b(bz_gl.gl_StaticsType.decode('GBK'))        
        js += web_radio(bz_gl.gl_StaticsTypeID, bz_gl.gl_BugNow.decode('GBK'), True)
        js += web_radio(bz_gl.gl_StaticsTypeID, bz_gl.gl_BugInTime.decode('GBK'), False)
        js += web_radio(bz_gl.gl_StaticsTypeID, bz_gl.gl_BugClass.decode('GBK'), False)        
        js += web_radio(bz_gl.gl_StaticsTypeID, bz_gl.gl_BugOrigin.decode('GBK'), False)
        js += web_radio(bz_gl.gl_StaticsTypeID, bz_gl.gl_BugTrend.decode('GBK'), False)
        js += web_radio(bz_gl.gl_StaticsTypeID, bz_gl.gl_BugTrendNew.decode('GBK'), False)  
        js += web_radio(bz_gl.gl_StaticsTypeID, bz_gl.gl_BugOriginalData.decode('GBK'), False)  
        
        js += "<br /><br />"        
        
        js += web_button(bz_gl.gl_Submit_Query, 'Query')          
        js += "<br /><br />"            


        #if req.session.sid == 'song.shan':
            #js += web_input(bz_gl.gl_From, bz_gl.gl_From, '')
            #js += web_input(bz_gl.gl_To, bz_gl.gl_To, '')  
            #js += "<br />"        
            
        js += "</div>" 
        
        js += "<br /><br />"      
         
        return js



        
def bz_querytreemanager(req, a_Bugz_Query, title=''):  
        js = '<legend>'+("查询树管理".decode('GBK'))+'</legend>'
        js += web_b(bz_gl.gl_QueryName)
        js += web_input(req,  bz_gl.gl_QueryName,title) 
        js += bz_querytree_name(req)   
        js += web_button(bz_gl.gl_Save_Query, 'Save') 
        js += "<br />"  
                
        return js             
            
def bz_query_disp(req, comments = False, order = 'number',
               assigned_to = None, reporter = None, cc = None,
               whiteboard = None, keywords = None,
               status = [], severity = [], priority = [], component = [],
               product =[], cf_come_from=[], cf_base_on_ver='', cf_fix_on_ver='', 
               orderby=''):
        
        if assigned_to is not None:
            assignee = assigned_to
        else:
            assignee = req.args.get(bz_gl.gl_Assignee)
            
        if status != []:
            status = status
        else:
            status = req.args.get(bz_gl.gl_Status) 

        if product != []:
            product = product
        else:
            product = req.args.get(bz_gl.gl_Product)

        if component != []:
            component = component
        else:            
            component = req.args.get(bz_gl.gl_Component)

        if severity != []:
            severity = severity
        else:            
            severity = req.args.get(bz_gl.gl_Severity)

        if priority != []:
            priority = priority
        else:                        
            priority = req.args.get('priority')

        if reporter != []:
            reporter = reporter
        else:  
            reporter = req.args.get(bz_gl.gl_Reporter) 

        if cf_come_from != []:
            cf_come_from = cf_come_from
        else:  
            cf_come_from = req.args.get(bz_gl.gl_ComeFrom) 
            
        if cf_base_on_ver != '':
            cf_base_on_ver = cf_base_on_ver
        else:              
            cf_base_on_ver = req.args.get(bz_gl.gl_BaseOnVersion) 

        if cf_fix_on_ver != '':
            cf_fix_on_ver = cf_fix_on_ver
        else:                       
            cf_fix_on_ver = req.args.get(bz_gl.gl_FixOnVersion)   

        if orderby != '':
            orderby = orderby
        else:                       
            orderby = req.args.get(bz_gl.gl_OrderBy)   
        if orderby is None or orderby == '':
            orderby = 'bug_id'
            
        js = ''
        js += "	<b>"+"Query Condition"+":</b>"
        js += "<br />"   
        js += web_li('Product', bz_utils.tuple2string(product))
        js += web_li('Component', bz_utils.tuple2string(component))
        js += web_li(bz_gl.gl_OrderBy, orderby)
        js += "<br />"
        
        js += web_li('Status', bz_utils.tuple2string(status))        
        js += web_li('Severity', bz_utils.tuple2string(severity))          
        js += "<br />"
        #js += web_li('Base_On_Version', cf_base_on_ver)
        #js += web_li('Fix_On_Version', cf_fix_on_ver)
        #js += "<br />"
        js += web_li(bz_gl.gl_Assignee, assignee)
        js += web_li('Reporter', reporter)
        js += web_li('ComeFrom', bz_utils.tuple2string(cf_come_from))           
        js += "<br />"

        js += "<br />" 
        return js

def bz_query_url(req, query_url):                
        js = ''
        js += "	<b>"+"Query URL"+":</b>"        
        js += "	<a href='" + query_url +  "' target='_blank'>" + query_url + u"</a>"
        js += "<br /><br />"

        #js += "<br /><br />"            
        return js


def bz_small_email_box(req, QueryRows):
                
        js = ''
        #js += '<legend>'+("Email".decode('GBK'))+'</legend>'
        #js += "<div style=\"width:800px;\">"        
        
        #js += web_b("邮件内容".decode('GBK'))
        #js += web_textarea(req,  bz_gl.gl_EmailDescription, '')
        #js += "<br />"
        
        QueryIDs = []
        for row in QueryRows:    
                #tmp_row['QueryID'] = row['ID']
                #tmp_row['QueryName'] = row['name']#.decode('GBK')
            QueryIDs.append(row['QueryID'])
                        
        js += web_single_sel(QueryIDs, bz_gl.gl_QueryID,)
        
        #js += "</div>" 
        return js
        
def bz_email_box(req, query_url, csv_url):   
#def bz_email_box(req, query_url): 
        js = ''
        js += '<legend>'+("Email".decode('GBK'))+'</legend>'
        js += "<div style=\"background: #ffd;border: 1px solid gray;width:800px;\">"        
        js += "<br />"
        
        js += web_b("邮件标题".decode('GBK'))
        js += web_input(req,  bz_gl.gl_EmailTitle, '', size='70')  
        js += "<br />" 
        js += web_b("接收人员".decode('GBK'))
        js += web_input(req,  bz_gl.gl_EmailList, req.session.sid+';', size='70')  
        js += "<br />" 
        js += web_b("邮件内容".decode('GBK'))
        js += web_textarea(req,  bz_gl.gl_EmailDescription, '')
        js += "<br />" 
        js += web_b("结果链接".decode('GBK'))
        #js += web_input(req,  bz_gl.gl_QueryLink, query_url, size='70', readonly=True) 
        js += "<a href='" + query_url +  "' target='_blank'>" + "Link To Bugzilla(不包括iBugzilla Field)".decode('GBK') + u"</a> &nbsp;&nbsp;&nbsp;&nbsp;"
        if csv_url != '':
            js += "<a href='" + csv_url +  "' target='_blank'>" + "Save To .csv File" + u"</a> &nbsp;&nbsp;&nbsp;&nbsp;"
        js += "<br />" 
        js += web_button(bz_gl.gl_Send_Email, 'SendEmail') 
        
        #js += web_b(bz_gl.gl_EmailURL)
        #js += web_input(req,  bz_gl.gl_EmailURL, query_url)
        js += "<br />"  
        js += "</div>" 
        return js

def bz_Heart(env, req): 
    import watch_dog
    
    js = watch_dog.WatchDogUI(env, bz_gl.gl_srv_heart)
    return js 



def web_textarea( req,  name, default, size='40'):
    #<textarea id=".." name=".." class="wikitext trac-resizable" rows="10" cols="70"></textarea>
        if default is None or default == '':
            #default = ''
            #old_sels = []
            for k, v in req.args.iteritems():
                if k==name and v:
                    #if type(v)==type(list()):
                    #    old_sels=v
                    #else:
                    #    old_sels=[v]
                    default = v
        js = "<textarea id=\""+name+"\" name=\""+name+"\" class=\"wikitext trac-resizable\" rows=\"10\" cols=\"70\" >"+default+"</textarea>"
        return js   
        
def web_input( req,  name, default, size='40', readonly=False):
        if default is None or default == '':
            #default = ''
            #old_sels = []
            for k, v in req.args.iteritems():
                if k==name and v:
                    #if type(v)==type(list()):
                    #    old_sels=v
                    #else:
                    #    old_sels=[v]
                    default = v
        js = ''    
        input_type = 'text'
        if readonly == False:
            js += "	<input id=\""+name+"\" type=\""+input_type+"\" name=\""+name+"\" size=\""+size+"\" value=\""+default+"\" />"
        else:
            js += "	<input id=\""+name+"\" type=\""+input_type+"\" name=\""+name+"\" size=\""+size+"\" value=\""+default+"\" readonly=\"1\"/></td>"

        
        #js += "	<input id=\""+name+"\" type=\"text\" name=\""+name+"\" size=\""+size+"\" value=\""+default+"\" />"
        return js   


def web_b(name):
        js = ''    
        js += "	<b style=\"background: #eee\">"+name+":</b>"
        return js 

        
def web_radio(name, value, checked):
        js = ''  

        #<input type="radio" id="Data_Type" name="Data_Type" value="Percent" checked="checked" />Percent    
        #<input type="radio" id="Data_Type" name="Data_Type" value="Hours" />Hours
        
        if checked == True:
            js += "	<input id=\""+name+"\" type=\"radio\" name=\""+name+"\" value=\""+value+"\" checked=\"checked\" />"+value
        else:
            js += "	<input id=\""+name+"\" type=\"radio\" name=\""+name+"\" value=\""+value+"\" />"+value
                        
        return js 

def web_checkbox(name, value, checked):
        js = ''  
        #<input type="checkbox" id="field_DepID2" name="field_DepID2" value="PHY" />PHY

        #<input type="checkbox" id="field_Project_Name" name="field_Project_Name" value="部门事务" checked="checked" />部门事务
        #<input type="checkbox" id="field_Project_Name" name="field_Project_Name" value="SC6530" />SC6530
        if checked == True:
            js += "	<input id=\""+name+"\" type=\"checkbox\" name=\""+name+"\" value=\""+value+"\" checked=\"checked\" />"+value
        else:
            js += "	<input id=\""+name+"\" type=\"checkbox\" name=\""+name+"\" value=\""+value+"\" />"+value
                        
        return js 

def web_checkboxs(env, req, checkbox_id, name, checkboxs): 
        js =''
        old_checkboxs = []
        for k, v in req.args.iteritems():
            if k==checkbox_id and v:
                if type(v)==type(list()):
                    old_checkboxs=v
                else:
                    old_checkboxs=[v]
        
        QF = {} 
        js += web_b(name)
        for a_checkbox in checkboxs:
            value = a_checkbox['name']
            js += web_checkbox(checkbox_id, value.decode('GBK'), value in old_checkboxs)  
            
        js += "<br />" 
        return js   

def web_button(id, name):
        js = ''
        js += "<input type=\"submit\" name=\""+id+"\" value=\""+name+"\" />"   

        return js   

def web_mutls_sel(req, mutls_sel, name):
        old_sels = []
        for k, v in req.args.iteritems():
            if k==name and v:
                if type(v)==type(list()):
                    old_sels=v
                else:
                    old_sels=[v]
                    
        js = ''  
        js += "<span class=\"field_label  required\"    id=\""+name+"\">"
        js += "<b style=\"background: #eee\">"+name+":</b>"
        js += "</span>"
        js += "      <select name=\""+name+"\" id=\""+name+"\"  multiple=\"multiple\" size=\"7\">"
        nums = 0
        while len(mutls_sel) > nums:
            x = mutls_sel[nums].decode('utf-8')            
            nums += 1  
            if x  in old_sels:
                js += "                        <option value=\""+x+"\" selected=\"selected\">"+x+"</option>"  
            else:                 
                js += "                        <option value=\""+x+"\" >"+x+"</option>"  
        js += "      </select>"
        return js    

def web_single_sel(sels, name):
        js = ''
        #js += "<b style=\"background: #eee\">"+name+":</b>"
        js += "<b>"+name+":</b>"
        js += "      <select name=\""+name+"\" id=\""+name+"\"  >"
        nums = 0
        while len(sels) > nums:
            x = sels[nums].decode('utf-8')            
            nums += 1  
            js += "                        <option value=\""+x+"\">"+x+"</option>"            
        js += "      </select>"
        return js  

def web_li(id, infos):  
        if infos is None or infos == '':
            infos = '---' 
        js = ''    
        #js += "<li>"        
        js += "<strong>"+id+":</strong>"+infos+"      "
        #js += "</li>"
        return js      

def web_get_checkbox(req, field_id, units): 
    field_value = req.args.get(field_id)    
    if field_value is not None:
        if isinstance(field_value, list) == True:
            for a_item in field_value:
                a_list = {}
                a_list['fname'] = field_id
                a_list['value'] = a_item
                units.append(a_list)
        else:
            a_list = {}
            a_list['fname'] = field_id
            a_list['value'] = field_value
            units.append(a_list)

def web_table(req, cols, rows): 
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')

    if 1:
        js = ''

        js += ""  

        js += u"<table id=\"large2\" name=\"large\" class=\"listing\">"
        js += u"<thead>"
        js += u"<tr>"
        for col in cols: 
            js += u"<th width=\"75\">"
            js += col
            js += u"</th>"
        js += u"</tr>"
        js += u"</thead>"
		
        js += u"<tbody>"
        for row in rows:   
            js += u"<tr>"
            for idx,col in enumerate(row):   
                js += u"<td>"
                js = u' '.join((js, str(col))).encode('utf-8')
                js += u"</td> " 
            js += u"</tr>"
        js += u"</tbody>"		
        js += u"</table>"
        
    return js
        


def tree_add_node(tree, father_id, all_root_indexs, all_roots, a_root): 
        index = tree['index'] 
        name = tree['name']        
        is_leaf = tree['is_leaf']
        js = ''
        js += '\r\nd.add('
        js += '\''+str(index)+'\''
        js += ',\''+str(father_id)+'\''
        if is_leaf == False:
            js += ',\''+name+'\',\"javascript:test();\");'   
            all_root_indexs[a_root] = index
            all_roots.append(a_root)
        else:
            name_id = tree['name_id']
            js += ',\''+name+'\',\"javascript:Bz_QueryTree(\''+name_id+'\',\''+name+'\');\");'      
        tree['index'] = index+1    
        return js
