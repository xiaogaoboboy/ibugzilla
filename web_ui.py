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
import bz_web_ui
import schedule

db_conn=None
Current_User= ''
Host_Server=1


if Host_Server==0:
    SiteRoot='/trac/idata'
else:
    SiteRoot='/idata'
            
class AdminModule(Component):
    """Web administration interface provider and panel manager."""

    implements(INavigationContributor, IRequestHandler, ITemplateProvider)

    module_providers = ExtensionPoint(IModuleProvider)

    # INavigationContributor methods

    def get_active_navigation_item(self, req):
        return 'idata'

    def get_navigation_items(self, req):
        # The 'Admin' navigation item is only visible if at least one
        #yield 'mainnav', 'idata', tag.a(_('iData'), href=req.href('/idata/itask/home'), title=_('report'))
        yield 'mainnav', 'idata', tag.a(_('iData'), href=req.href('/idata/Bugzilla/query'), title=_('report'))
        
    # IRequestHandler methods

    def match_request(self, req):
        #self.log.error('match_request: %s',req.path_info)
        match = re.match('/idata(?:/([^/]+)(?:/([^/]+)(?:/(.+))?)?)?$', req.path_info)        
        if match:
            req.args['cat_id'] = match.group(1)
            req.args['panel_id'] = match.group(2)
            req.args['path_info'] = match.group(3)
            return True

    def process_request(self, req):
        global db_conn
        global Current_User
        
        add_ctxtnav(req, _('iTask'), href='http://imanage.spreadtrum.com/idata/itask/home')#req.href('/idata/itask/home'))
        
        Current_User = req.authname.lower()
        if req.authname.lower()=='anonymous':
            add_warning(req, 'Please login first!')
            
        database_host= self.env.config.get('iManage', 'database_host').strip()
        database_port= self.env.config.getint('iManage', 'database_port')
        database_user= self.env.config.get('iManage', 'database_user').strip()
        database_passwd= self.env.config.get('iManage', 'database_passwd').strip()
        database_db= self.env.config.get('iManage', 'database_db').strip()
        database_charset= self.env.config.get('iManage', 'database_charset').strip()
        
        #db_conn=MySQLdb.connect(host=database_host,port=database_port,user=database_user, passwd=database_passwd, db=database_db,charset=database_charset)
        #db_conn=MySQLdb.connect(host='10.0.0.175',port=3306,user='iadmin', passwd='itask@ADMIN89', db='imanage',charset='utf8')

        db_conn=MySQLdb.connect(host='10.0.0.175',port=3306,user='ilogadmin', passwd='SPD@ilogservice99', db='ilog',charset='utf8')
        
        providers = self._get_providers(req)
        cat_id = req.args.get('cat_id') 
        panel_id = req.args.get('panel_id')
        path_info = req.args.get('path_info')
        provider = providers.get((cat_id, panel_id), None)
        #self.log.error("AdminModule:%s,%s,%s",cat_id,panel_id,path_info)
        
        if not provider:
            raise HTTPNotFound(_('Unknown administration module'))

        template, data = provider.render_module(req, cat_id, panel_id, path_info)

        data.update({
                'active_cat': cat_id, 
                'active_panel': panel_id,
                #'SiteRoot':SiteRoot, 
                'CurrentUser':Current_User, 
            })

        return template, data, None

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        """Return a list of directories with static resources (such as style
        sheets, images, etc.)

        Each item in the list must be a `(prefix, abspath)` tuple. The
        `prefix` part defines the path in the URL that requests to these
        resources are prefixed with.

        The `abspath` is the absolute path to the directory containing the
        resources on the local file system.
        """
        from pkg_resources import resource_filename
        return [('hw', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        from pkg_resources import resource_filename
        return [resource_filename(__name__, 'templates')]

    def _get_providers(self, req):
        """Return a list of available admin panels."""
        providers = {}

        for provider in self.module_providers:
            p = list(provider.get_module(req) or [])
            for panel in p:
                providers[(panel[0], panel[1])] = provider
                
        return providers

class Worklog_home_Module(Component):

    implements(IModuleProvider)

    def get_module(self, req):
        
        yield ('itask','home')

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

                
    def render_module(self, req, cat, page, path_info):
        import os
        from genshi import HTML
        import sprd_user_model
        import task_model
        import worklog_model
        import column_chart_model
        import pie_chart_model

        add_stylesheet(req, 'hw/css/datetime.css')
        if Host_Server == 0:
            add_stylesheet(req, 'hw/css/jquery-ui_itask_dev.css')
        else:
            add_stylesheet(req, 'hw/css/jquery-ui_itask.css')

        add_script(req, 'hw/js/jquery-ui.min.js')
        add_script(req, 'hw/js/jquery-ui-timepicker-addon.js')
        add_script(req, 'hw/js/highcharts.js')
        
        data = {}

        Submit_Query=req.args.get('Submit_Query', '').strip()
        Submit_Query_Team=req.args.get('Submit_Query_Team', '').strip()
        
        import sprd_product_model

        a_sprd_product =sprd_product_model.SPRD_Product(None)
        myUser = Current_User 

        ym_current_user = []
        all_project = []
        if req.authname.lower()!='anonymous':
            YearMonth_Start = req.args.get('field_YearMonth_Start', '').strip()
            YearMonth_End = req.args.get('field_YearMonth_End', '').strip()
            if not YearMonth_End:
                YearMonth_End = datetime.strftime(datetime.now(),"%Y-%m")
            if not YearMonth_Start:
                start_m_tmp = datetime.strftime(datetime.now(),"%m")
                if start_m_tmp in ['01', '02']:
                    start_m_tmp = str(int(start_m_tmp) + 10 )
                    YearMonth_Start = str(int(datetime.strftime(datetime.now(),"%Y"))-1) + "-" + start_m_tmp
                else:
                    start_m_tmp = str(int(start_m_tmp)-2)
                    if len(start_m_tmp)==1:
                        start_m_tmp = "0" + start_m_tmp
                    YearMonth_Start = datetime.strftime(datetime.now(),"%Y") + "-" + start_m_tmp
            all_ym = self.Year_Month_Process([YearMonth_Start,YearMonth_End ])

            for a_ym in all_ym:
                tmp =a_ym.split('-')
                tmp_y = tmp[0]
                tmp_m = tmp[1]
                All_Percent = a_sprd_product.Get_Prj_Percent(myUser,tmp_y+'-' +tmp_m, 'Percent')
                if  All_Percent:
                    tmp_data = All_Percent
                    ym_current_user.append({'ym':(tmp_y+'-' +tmp_m), 'data':tmp_data})
                    for a_key in tmp_data.keys():
                        if a_key:
                            if a_key not in all_project:
                                all_project.append(a_key)
                else:
                    ym_current_user.append({'ym':(tmp_y+'-' +tmp_m), 'data':{}})

            ym_current_user_dic={}
            for a_prj in all_project:
                tmp_data=[]
                for a_row in ym_current_user:
                    if a_prj in a_row['data'].keys():
                        tmp_data.append(a_row['data'][a_prj]*100)
                    else:
                        tmp_data.append(0)
                ym_current_user_dic.update({a_prj:tmp_data})
            Column_data_str = column_chart_model.Column_Chart.get_column_Xaxis(ym_current_user_dic)
            column_Xaxis_name_str = column_chart_model.Column_Chart.get_column_Xaxis_name(all_ym)
            data.update({'column':HTML(column_chart_model.Column_Chart.get_column_chart_javascript('column' ,  'container_column','my Products map', column_Xaxis_name_str ,'Man-Month',  Column_data_str, ''))}) 
        data.update({'ym_current_user':ym_current_user})

        data.update({'ym_current_user_prj':all_project})

        ym_myteam = []
        all_project = []
        if Current_User!='anonymous':
            a_SPRD_User = sprd_user_model.SPRD_User(None)
            all_user = a_SPRD_User.Get_Direct_Member(Current_User)
            all_user = [a_user['EName'].replace(' ', '.').lower() for a_user in all_user]
            
            tmp =datetime.strftime(datetime.now(),"%Y-%m")
            YearMonth_Team = req.args.get('field_YearMonth_Team', '').strip()
            if YearMonth_Team:
                tmp = YearMonth_Team
            for a_User in all_user:
                All_Percent = a_sprd_product.Get_Prj_Percent(a_User,tmp, 'Percent')
                ym_myteam.append({'username':a_User, 'data':All_Percent})
                for a_prj_key in All_Percent.keys():
                    if a_prj_key not in all_project:
                        all_project.append(a_prj_key)
            data.update({'ym_myteam_date':tmp})

            ym_myteam_dic={}
            x_username=[]
            for a_prj in all_project:
                tmp_data=[]
                for a_row in ym_myteam:
                    if a_prj in a_row['data'].keys():
                        tmp_data.append(a_row['data'][a_prj]*100)
                    else:
                        tmp_data.append(0)
                for a_row in ym_myteam:
                    x_username.append(a_row['username'])
                ym_myteam_dic.update({a_prj:tmp_data})
            Column_data_str_team = column_chart_model.Column_Chart.get_column_Xaxis(ym_myteam_dic)
            column_Xaxis_name_str_team = column_chart_model.Column_Chart.get_column_Xaxis_name(x_username)
            data.update({'column_team':HTML(column_chart_model.Column_Chart.get_column_chart_javascript('column' ,  'container_column_team','my Team Map', column_Xaxis_name_str_team ,'Man-Month',  Column_data_str_team, 'junbo.han'))}) 
            
        data.update({'ym_myteam':ym_myteam})
        data.update({'ym_myteam_prj':all_project})


        templates='worklog_home.html'

        return templates, {'worklog_report': data}



class Worklog_Query_Module(Component):

    implements(IModuleProvider)

    def get_module(self, req):
        yield ('itask','report')

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
        
    def render_module(self, req, cat, page, path_info):
        import os
        from genshi import HTML
        import sprd_product_model
        import sprd_user_model
        import task_model
        import worklog_model
        import column_chart_model
        import pie_chart_model

        if Host_Server==0:
            add_script(req, 'hw/js/worklog_check_dev.js')
        else:
            add_script(req, 'hw/js/worklog_check.js')
            
        add_stylesheet(req, 'hw/css/datetime.css')
        if Host_Server == 0:
            add_stylesheet(req, 'hw/css/jquery-ui_itask_dev.css')
        else:
            add_stylesheet(req, 'hw/css/jquery-ui_itask.css')

        add_script(req, 'hw/js/jquery-ui.min.js')
        add_script(req, 'hw/js/jquery-ui-timepicker-addon.js')
        add_script(req, 'hw/js/highcharts.src.js')
        
        Data_Type = req.args.get('Data_Type', 'Percent').strip()
        Show_Style_Product = req.args.get('Show_Style_Product', '').strip()
        Show_Style_Department = req.args.get('Show_Style_Department', '').strip()
        
        Validate = req.args.get('Validate', '').strip()
        
        if not Show_Style_Product and not Show_Style_Department:
            Show_Style_Product='Product'
        data = {}
        QF={}
        all_Users_SN=[]
        javascript_str_MD="{"
        Select_Projects = []
        myDepartment = []
        for k, v in req.args.iteritems():
            if k=='field_DepID2' and v:
                if type(v)==type(list()):
                    myDepartment=v
                else:
                    myDepartment=[v]
            if k=='field_Project_Name' and v:
                if type(v)==type(list()):
                    Select_Projects=v
                else:
                    Select_Projects=[v]

        a_user_obj = sprd_user_model.SPRD_User(None)
        all_department = a_user_obj.Get_DEV_Dep_Level_2()
            
        data.update({'myDepartment':myDepartment})
        data.update({'all_department':all_department})

        #Current_User_DIC= a_user_obj.Get_User(Current_User)

        a_SPRD_Product =sprd_product_model.SPRD_Product(None)       
        myProjects = a_SPRD_Product.Get_myProject(Current_User)
        all_Projects = a_SPRD_Product.Get_Product()
        data.update({'myProjects':myProjects})
        data.update({'all_Projects':all_Projects})
        data.update({'Select_Projects':Select_Projects})
        
        if (req.method == "POST"):
            if len(myDepartment)==0:
                myDepartment = all_department
            
            # validate user fill
            if Validate:
                all_nofill = []
                YearMonth_Start = req.args.get('field_YearMonth_Start', '').strip()
                YearMonth_End = req.args.get('field_YearMonth_End', '').strip()
                if not YearMonth_End:
                    YearMonth_End = datetime.strftime(datetime.now(),"%Y-%m")
                if not YearMonth_Start:
                    start_m_tmp = datetime.strftime(datetime.now(),"%m")
                    if start_m_tmp in ['01', '02']:
                        start_m_tmp = str(int(start_m_tmp) + 10 )
                        YearMonth_Start = str(int(datetime.strftime(datetime.now(),"%Y"))-1) + "-" + start_m_tmp
                    else:
                        start_m_tmp = str(int(start_m_tmp)-2)
                        if len(start_m_tmp)==1:
                            start_m_tmp = "0" + start_m_tmp
                        YearMonth_Start = datetime.strftime(datetime.now(),"%Y") + "-" + start_m_tmp
                all_ym = self.Year_Month_Process([YearMonth_Start,YearMonth_End ])
                for a_dept in myDepartment:
                    all_user = a_user_obj.Get_DepUsers('', a_dept, '')
                    for a_user in all_user:
                        for a_ym in all_ym:
                            result=a_SPRD_Product.Get_Fill_Worklog(a_user['EName'].replace(' ', '.').lower(),a_ym)
                            if result==0:
                                all_nofill.append({'User':a_user, 'YM':a_ym})
                            #time.sleep(0.2)
                data['all_nofill'] = all_nofill
                templates='worklog_validate.html'                
                return templates, {'worklog_report': data}
                
            a_worklog_obj = worklog_model.Worklog(None, db_conn)
            
            fill_worklog = a_worklog_obj.select(req.args)
            fill_worklog_show = a_worklog_obj.show(req.args)
            
            for a_fill in fill_worklog:
                if a_fill['Hours']=='0' or a_fill['Hours']=='':
                    fill_worklog.remove(a_fill)
                    
            data.update({'fill_worklog_show':fill_worklog_show})

            all_year_month=[]
            fill_worklog_project_show={}
            fill_Projects = []
            fill_Projects_excel = []
            for a_fill_worklog in fill_worklog:
                    tmp = a_fill_worklog['Project_Name']
                    if tmp:
                        if tmp not in fill_Projects :
                            fill_Projects.append(tmp)
                    a_key = a_fill_worklog['User_SN'] + u'_' + a_fill_worklog['Year_Months'] + u'_' + tmp
                    if Data_Type=='Percent':
                        if a_fill_worklog[Data_Type]:
                            fill_worklog_project_show.update({a_key:a_fill_worklog[Data_Type] + '%'})
                        else:
                            fill_worklog_project_show.update({a_key:a_fill_worklog[Data_Type]})
                    else:
                        fill_worklog_project_show.update({a_key:a_fill_worklog[Data_Type]})
                        
                    if a_fill_worklog['Year_Months'] not in all_year_month:
                        if a_fill_worklog['Year_Months']:
                            all_year_month.append(a_fill_worklog['Year_Months'])
            fill_Projects.sort()
            if len(Select_Projects)==0:
                data.update({'fill_Projects':fill_Projects})
                fill_Projects_excel = fill_Projects
            else:
                data.update({'fill_Projects':Select_Projects})
                fill_Projects_excel = Select_Projects
            # >100.00 processing
            if Data_Type=='Percent':
                fill_worklog_project_show = self.fill_worklog_process(fill_worklog_project_show)
            
            Create_Excel = req.args.get('Create_Excel', '').strip()
            if Create_Excel:
                import excel_model
                excel_model=excel_model.Excel()
                full_path = excel_model.Create('iData', fill_Projects_excel,fill_worklog_show, fill_worklog_project_show)
                full_path = full_path.replace('\\', '/')
                req.send_file(full_path)
                
            all_year_month = self.Year_Month_Process(all_year_month)
            
            data.update({'fill_worklog_project_show':fill_worklog_project_show})

            Project_YM = a_worklog_obj.Project_YM(req.args, Data_Type)
            
            Column_Project_YM_data_dic = {}
            for a_project in fill_Projects_excel:
                ym_data = []
                for a_year_month in all_year_month:
                    int_tag = 0
                    for a_row in Project_YM:
                        if a_row['Project_Name'] == a_project and a_row['Year_Months'] == a_year_month:
                            if a_row[Data_Type]:
                                if Data_Type=='Percent':
                                    ym_data.append(float(a_row[Data_Type])/100.00)
                                else:
                                    ym_data.append(float(a_row[Data_Type]))
                                int_tag = 1
                    if int_tag == 0:
                        ym_data.append(0)
                Column_Project_YM_data_dic.update({a_project:ym_data})

            Pie_Project_YM_data_dic = {}
            for a_project in fill_Projects_excel:
                int_tag = 0
                for a_row in Project_YM:
                    if a_row['Project_Name'] == a_project :
                        if a_row[Data_Type]:
                            int_tag = 1
                            if a_row['Project_Name'] in Pie_Project_YM_data_dic.keys():
                                if Data_Type=='Percent':
                                    Pie_Project_YM_data_dic[a_row['Project_Name']] = Pie_Project_YM_data_dic[a_row['Project_Name']] + float(a_row[Data_Type])/100.00
                                else:
                                    Pie_Project_YM_data_dic[a_row['Project_Name']] = Pie_Project_YM_data_dic[a_row['Project_Name']] + float(a_row[Data_Type])
                            else:
                                if Data_Type=='Percent':
                                    Pie_Project_YM_data_dic[a_row['Project_Name']]  = float(a_row[Data_Type])/100.00
                                else:
                                    Pie_Project_YM_data_dic[a_row['Project_Name']]  = float(a_row[Data_Type])
                if  int_tag== 0:
                    Pie_Project_YM_data_dic[a_project]  = 0
            
            Dept_Column_data_dic = {}
            Dept_YM = a_worklog_obj.Department_YM(req.args, Data_Type)

            for a_dept in myDepartment:
                ym_data = []
                for a_year_month in all_year_month:
                    int_tag = 0
                    for a_row in Dept_YM:
                        if a_row['DepID2'] == a_dept and a_row['Year_Months'] == a_year_month:
                            if a_row[Data_Type]:
                                if Data_Type=='Percent':
                                    ym_data.append(float(a_row[Data_Type])/100.00)
                                else:
                                    ym_data.append((a_row[Data_Type]))
                                int_tag = 1
                    if int_tag == 0:
                        ym_data.append(0)
                Dept_Column_data_dic.update({a_dept:ym_data})

            Pie_Dept_YM_data_dic = {}
            for a_dept in myDepartment:
                int_tag = 0
                for a_row in Dept_YM:
                    if a_row['DepID2'] == a_dept:
                        if a_row[Data_Type]:
                            int_tag = 1
                            if a_row['DepID2'] in Pie_Dept_YM_data_dic.keys():
                                if Data_Type=='Percent':
                                    Pie_Dept_YM_data_dic[a_row['DepID2']] = Pie_Dept_YM_data_dic[a_row['DepID2']] + float(a_row[Data_Type])/100.00
                                else:
                                    Pie_Dept_YM_data_dic[a_row['DepID2']] = Pie_Dept_YM_data_dic[a_row['DepID2']] + float(a_row[Data_Type])
                            else:
                                if Data_Type=='Percent':
                                    Pie_Dept_YM_data_dic[a_row['DepID2']]  = float(a_row[Data_Type])/100.00
                                else:
                                    Pie_Dept_YM_data_dic[a_row['DepID2']]  = float(a_row[Data_Type])
                if  int_tag== 0:
                    Pie_Dept_YM_data_dic[a_dept]  = 0
                    
            column_Xaxis_name = all_year_month
            
            Column_data_str = column_chart_model.Column_Chart.get_column_Xaxis(Column_Project_YM_data_dic)
            column_Xaxis_name_str = column_chart_model.Column_Chart.get_column_Xaxis_name(column_Xaxis_name)
            
            if Show_Style_Product:
                if Data_Type=='Percent':
                    data.update({'column':HTML(column_chart_model.Column_Chart.get_column_chart_javascript('column' ,  'container_column','Products map', column_Xaxis_name_str ,'Man-Month',  Column_data_str, ''))}) 
                else:
                    data.update({'column':HTML(column_chart_model.Column_Chart.get_column_chart_javascript('column' ,  'container_column','Products map', column_Xaxis_name_str ,'Man-Hour',  Column_data_str, ''))}) 
            column_table_str = column_chart_model.Column_Chart.get_table_str(column_Xaxis_name,Column_Project_YM_data_dic)
            data.update({'column_table':HTML(column_table_str)})
            data.update({'pie_table':HTML(pie_chart_model.Column_Chart.get_table_str(Pie_Project_YM_data_dic))})

            Dep_Column_data_str = column_chart_model.Column_Chart.get_column_Xaxis(Dept_Column_data_dic)
            if Data_Type=='Percent':
                data.update({'dep_column':HTML(column_chart_model.Column_Chart.get_column_chart_javascript('column' ,  'dep_container_column','Departments map', column_Xaxis_name_str ,'Man-Month',  Dep_Column_data_str, ''))}) 
            else:
                data.update({'dep_column':HTML(column_chart_model.Column_Chart.get_column_chart_javascript('column' ,  'dep_container_column','Departments map', column_Xaxis_name_str ,'Man-Hour',  Dep_Column_data_str, ''))}) 
            column_table_dep_str = column_chart_model.Column_Chart.get_table_str(column_Xaxis_name,Dept_Column_data_dic)
            data.update({'column_table_dep':HTML(column_table_dep_str)})
            data.update({'pie_table_dep':HTML(pie_chart_model.Column_Chart.get_table_str(Pie_Dept_YM_data_dic))})
            if Show_Style_Product:
                data.update({'pie':HTML(pie_chart_model.Column_Chart.get_pie_chart_javascript('pie' ,  'container_pie','Products map', pie_chart_model.Column_Chart.get_str(Pie_Project_YM_data_dic)))})  
            data.update({'dep_pie':HTML(pie_chart_model.Column_Chart.get_pie_chart_javascript('pie' ,  'dep_container_pie','Departments map', pie_chart_model.Column_Chart.get_str(Pie_Dept_YM_data_dic)))})                     
                                              
            data.update({'Height':300})
            
        else:
            data.update({'Height':0})

        data.update({'req':req.args})
        
        templates='worklog_query.html'
        
        data.update({'Show_Style_Product': Show_Style_Product })
        data.update({'Show_Style_Department': Show_Style_Department })
        data.update({'Data_Type': Data_Type})
        
        return templates, {'worklog_report': data}

    def Year_Month_Process(self, ym):
        result = []
        ym.sort()
        if len(ym)<2:
            return ym

        if ym[0]==ym[1]:
            return [ym[0]]
            
        a_ym = ym[0]
        if a_ym not in result:
            result.append(a_ym)

        next_ym = ''
        while next_ym!=ym[-1]:
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
        
    def Year_Month_Process_bak(self, ym):
        result = []
        ym.sort()
        for a_ym in ym:
            if a_ym not in result:
                result.append(a_ym)
            if a_ym==ym[-1]:
                break
            next_ym = ''
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
        return result

    def fill_worklog_process(self, myworklog):
        
        #累加每个人某月份所有项目工时百分比
        data_tmp={}
        #记录有值的那个Key
        data_prj={}
        
        for a_key in myworklog:
            data = myworklog[a_key]
            if data:
                if '%' in data:
                    pattern=re.compile(ur'^(\d+_\d+-\d+)_(.*)$')
                    m=pattern.match(a_key)
                    if m:
                        key_tmp = m.group(1)
                        if key_tmp in data_tmp:
                            data_tmp[key_tmp] = data_tmp[key_tmp] + float(data[0:-1])
                        else:
                            data_tmp[key_tmp] = float(data[0:-1])
                        data_prj[key_tmp] = a_key

        for a_key in data_tmp:
            if data_tmp[a_key]!=100:
                if '%' in myworklog[data_prj[a_key]]:
                    new_value = float(myworklog[data_prj[a_key]].replace('%', '')) +  100.00 - data_tmp[a_key] 
                    myworklog.update({data_prj[a_key]: new_value})
                
        return myworklog
                
        
class Worklog_myProjects_Module(Component):

    implements(IModuleProvider)

    def get_module(self, req):
        yield ('itask','myproject')

    def render_module(self, req, cat, page, path_info):
        
        import sprd_product_model
        
        data = {}

        a_SPRD_Product = sprd_product_model.SPRD_Product(None)       
        ALLProjects = a_SPRD_Product.Get_Product()
        data['ALLProjects'] = ALLProjects

        Projects = a_SPRD_Product.Get_myProject(Current_User)
        data['Projects'] = Projects

        if (req.method == "POST"):
            cursor = db_conn.cursor()
            add_to_my_Project= req.args.get('add_to_my_Project', '').strip()
            if add_to_my_Project:
                SelectProject = req.args.get('SelectProject', [])
                AllProjectName=[]
                if len(SelectProject)>0:
                    if type(SelectProject)==type(list()):
                        AllProjectName=SelectProject
                    else :
                        AllProjectName=[SelectProject]
                        
                sql="DELETE FROM myProject where Submitter=%s"
                values = (Current_User,)
                cursor.execute(sql, values)
                db_conn.commit() 
                for aPt in AllProjectName :
                    sql="""INSERT INTO myProject
                        (ID,Project_Name,Submitter) 
                        values (%s,%s,%s)"""
                    values = (None,aPt, Current_User)
                    cursor.execute(sql, values)
                    db_conn.commit() 
                req.redirect(SiteRoot + "/itask/myproject")
                
        templates='idata_myproject_setting.html'
        
        return templates, {'idata_mysetting': data}


class Worklog_Submit_Rate_Module(Component):

    implements(IModuleProvider)

    def get_module(self, req):
        yield ('itask','submitrate')

    def render_module(self, req, cat, page, path_info):
        
        import time
        import re
        from datetime import datetime, timedelta
        import MySQLdb

        add_stylesheet(req, 'hw/css/datetime.css')
        if Host_Server == 0:
            add_stylesheet(req, 'hw/css/jquery-ui_itask_dev.css')
        else:
            add_stylesheet(req, 'hw/css/jquery-ui_itask.css')

        add_script(req, 'hw/js/jquery-ui.min.js')
        add_script(req, 'hw/js/jquery-ui-timepicker-addon.js')
        
        data={}
            
        if (req.method == "POST"):
            Start_Date = req.args.get('field_Start_Date', '').strip()
            End_Date = req.args.get('field_End_Date', '').strip()
            if not Start_Date:
                myWeek= int(datetime.strftime(datetime.now(),"%w"))
                if myWeek==0:
                    myWeek=7
                Start_Date  = datetime.strftime(datetime.now() - timedelta(days =(myWeek-1) ),"%Y-%m-%d") 
            if not End_Date:
                End_Date = datetime.strftime(datetime.now(),"%Y-%m-%d") 
            
            data['field_Start_Date'] = Start_Date
            data['field_End_Date'] = End_Date
            
            Days = ['2013-05-01','2013-06-10','2013-06-11','2013-06-12', '2013-09-19','2013-09-20','2013-10-01','2013-10-02','2013-10-03','2013-10-04','2013-10-07']
            Work_Days=['2013-06-08','2013-06-09', '2013-09-22','2013-09-29', '2013-10-12']
            
            task_db = None
            user_db = None
            if Host_Server==0:
                user_db=MySQLdb.connect(host='172.16.14.60',port=3306,user='root', passwd='root', db='imanage',charset='utf8')
                task_db=MySQLdb.connect(host='172.16.14.60',port=3306,user='root', passwd='root', db='itask',charset='utf8')
            else:
                user_db=MySQLdb.connect(host='10.0.0.175',port=3306,user='iadmin', passwd='itask#ADMIN89', db='imanage',charset='utf8')
                task_db=MySQLdb.connect(host='10.0.0.175',port=3306,user='iadmin', passwd='itask#ADMIN89', db='itask',charset='utf8')
                
            task_cursor = task_db.cursor()
            user_cursor = user_db.cursor()

            Work_Day = []
            All_Day = []
            All_Dep = {}


            Date_tmp = datetime(int(Start_Date[0:4]), int(Start_Date[5:7]),int(Start_Date[8:10]),8,0,0)
            Date_tmp_STR = datetime.strftime(Date_tmp,"%Y-%m-%d") 
            while Date_tmp_STR <= End_Date:
                All_Day.append(Date_tmp_STR)
                myWeek= int(datetime.strftime(Date_tmp,"%w"))
                if myWeek==0:
                    myWeek=7
                if myWeek in [6,7] and Date_tmp_STR in Work_Days:
                    Work_Day.append(Date_tmp_STR)
                if myWeek in [1,2,3,4,5] and Date_tmp_STR not in Days:
                    Work_Day.append(Date_tmp_STR)
                Date_tmp = Date_tmp + timedelta(days =1)
                Date_tmp_STR = datetime.strftime(Date_tmp,"%Y-%m-%d") 

            #assert  All_Day is None,All_Day


            DEP_1_Content = {}
            DEP_2_Content = {}
            DEP_3_Content = {}
            
            DEP_Counter_all_user  = {}
            DEP_Counter_all_fill  = {}
            DEP_Counter_per_fill  = {}
            
            all_user =[]
            user_sql = ''
            if 'PERMISSION_ADMIN'  in req.perm : 
                user_sql = "select Badge,EName,DepID1,DepID2,DepID3 from User_List where Status='" + u"在职" + "' "
            else:
                user_sql = "select Badge,EName,DepID1,DepID2,DepID3 from User_List where 3=4"
            user_cursor.execute(user_sql)
            for  Badge,EName,DepID1,DepID2,DepID3   in user_cursor:
                all_user.append([Badge,EName,DepID1,DepID2,DepID3])
            for a_user in all_user:
                    Badge,EName,DepID1,DepID2,DepID3 = a_user
                    if len(Badge)==5 and Badge[0:1]=='9':
                        continue
                    fill_count = 0
                    
                    dep1_Key = DepID1
                    dep2_Key = DepID1 + '/' + DepID2 
                    dep3_Key = DepID1 + '/' + DepID2  + '/' + DepID3
                    
                    
                    if dep1_Key  in DEP_Counter_all_user:
                        DEP_Counter_all_user[dep1_Key] = DEP_Counter_all_user[dep1_Key] +1
                    else:
                        DEP_Counter_all_user[dep1_Key] =1
                        
                    if dep2_Key  in DEP_Counter_all_user:
                        DEP_Counter_all_user[dep2_Key] = DEP_Counter_all_user[dep2_Key] +1
                    else:
                        DEP_Counter_all_user[dep2_Key] =1
                        
                    if dep3_Key  in DEP_Counter_all_user:
                        DEP_Counter_all_user[dep3_Key] = DEP_Counter_all_user[dep3_Key] +1
                    else:
                        DEP_Counter_all_user[dep3_Key] =1
                        
                    #all_user = all_user + 1
                    for a_day in All_Day:
                        USER_NAME = EName.replace(' ','.').lower()
                        task_sql_1 = "select count(*) FROM itask.TaskComment t2 where t2.Submitter='" + USER_NAME + "'  and t2.SubmittedDate>='" + a_day + " 00:00:00' and t2.SubmittedDate<='" + a_day + " 23:59:59' "
                        task_sql_2 = "select count(*) FROM itask.Task t3 where t3.Submitter='" + USER_NAME + "' and t3.SubmittedDate>='" + a_day + " 00:00:00' and t3.SubmittedDate<='" + a_day + " 23:59:59'"
                        a_day = datetime(int(a_day[0:4]), int(a_day[5:7]),int(a_day[8:10]),8,0,0)
                        myWeek= int(datetime.strftime(a_day,"%w"))
                        if myWeek==0:
                            myWeek=7
                        if (DepID1=='Product' and DepID2=='PM' or DepID1=='General Supporting') and myWeek!=6 and myWeek!=7:
                                Week_Start_DB = datetime.strftime(a_day - timedelta(days =(myWeek-1)),"%Y-%m-%d")  + ' 00:00:00'
                                Week_END_DB = datetime.strftime(a_day + timedelta(days =(5-myWeek)),"%Y-%m-%d")   + ' 23:59:59'
                                task_sql_1 = "select count(*) FROM itask.TaskComment t2 where t2.Submitter='" + USER_NAME + "'  and t2.SubmittedDate>='" + Week_Start_DB + "' and t2.SubmittedDate<='" + Week_END_DB + "' "
                                task_sql_2 = "select count(*) FROM itask.Task t3 where t3.Submitter='" + USER_NAME + "' and t3.SubmittedDate>='" + Week_Start_DB + "' and t3.SubmittedDate<='" + Week_END_DB + "' "            
                        task_cursor.execute(task_sql_1)
                        if task_cursor.fetchone()[0]>0:
                            fill_count = fill_count + 1
                        else:
                            task_cursor.execute(task_sql_2)
                            if task_cursor.fetchone()[0]>0:
                                fill_count = fill_count + 1
                    if fill_count>0:
                        if dep1_Key  in DEP_Counter_all_fill:
                            DEP_Counter_all_fill[dep1_Key] = DEP_Counter_all_fill[dep1_Key] +1.00
                        else:
                            DEP_Counter_all_fill[dep1_Key] =1.00
                            
                        if dep2_Key  in DEP_Counter_all_fill:
                            DEP_Counter_all_fill[dep2_Key] = DEP_Counter_all_fill[dep2_Key] +1.00
                        else:
                            DEP_Counter_all_fill[dep2_Key] =1.00
                            
                        if dep3_Key  in DEP_Counter_all_fill:
                            DEP_Counter_all_fill[dep3_Key] = DEP_Counter_all_fill[dep3_Key] +1.00
                        else:
                            DEP_Counter_all_fill[dep3_Key] =1.00
                            
                        if dep1_Key in DEP_Counter_per_fill:
                            DEP_Counter_per_fill[dep1_Key] = DEP_Counter_per_fill[dep1_Key] + (fill_count+ 0.00)/(len(Work_Day) or 1)
                        else:
                            DEP_Counter_per_fill[dep1_Key] =(fill_count+ 0.00)/(len(Work_Day) or 1)
                            
                        if dep2_Key in DEP_Counter_per_fill:
                            DEP_Counter_per_fill[dep2_Key] = DEP_Counter_per_fill[dep2_Key] + (fill_count+ 0.00)/(len(Work_Day) or 1)
                        else:
                            DEP_Counter_per_fill[dep2_Key] =(fill_count+ 0.00)/(len(Work_Day) or 1)
                            
                        if dep3_Key in DEP_Counter_per_fill:
                            DEP_Counter_per_fill[dep3_Key] = DEP_Counter_per_fill[dep3_Key] + (fill_count+ 0.00)/(len(Work_Day) or 1)
                        else:
                            DEP_Counter_per_fill[dep3_Key] =(fill_count+ 0.00)/(len(Work_Day) or 1)
                    
            Department_top_1=[]
            Department_top_2=[]
            Department_top_3=[]
            
            for a_key in DEP_Counter_all_user:

                if a_key  not in DEP_Counter_all_fill:
                    DEP_Counter_all_fill[a_key]=0.00
                if a_key  not in DEP_Counter_per_fill:
                    DEP_Counter_per_fill[a_key] = 0.00
                            
                match= a_key.count('/')
                if match==0:
                        Department_top_1.append(
                            {
                                'DEP_Name':a_key,
                                'UserCount':DEP_Counter_all_user[a_key],
                                'UserRate':round(DEP_Counter_all_fill[a_key]/DEP_Counter_all_user[a_key],4)*100,
                                'Submitted_Rate':round(DEP_Counter_per_fill[a_key]/DEP_Counter_all_user[a_key],4)*100
                            }
                        )

                if match==1:
                        Department_top_2.append(
                            {
                                'DEP_Name':a_key,
                                'UserCount':DEP_Counter_all_user[a_key],
                                'UserRate':round(DEP_Counter_all_fill[a_key]/DEP_Counter_all_user[a_key],4)*100,
                                'Submitted_Rate':round(DEP_Counter_per_fill[a_key]/DEP_Counter_all_user[a_key],4)*100
                            }
                        )

                if match==2:
                        Department_top_3.append(
                            {
                                'DEP_Name':a_key,
                                'UserCount':DEP_Counter_all_user[a_key],
                                'UserRate':round(DEP_Counter_all_fill[a_key]/DEP_Counter_all_user[a_key],4)*100,
                                'Submitted_Rate':round(DEP_Counter_per_fill[a_key]/DEP_Counter_all_user[a_key],4)*100
                            }
                        )
                    
            Department_top_1.sort(key=lambda s: s['Submitted_Rate'])
            Department_top_1.reverse()

            Department_top_2.sort(key=lambda s: s['Submitted_Rate'])
            Department_top_2.reverse()
            
            Department_top_3.sort(key=lambda s: s['Submitted_Rate'])
            Department_top_3.reverse()
            
            data['DEP_LEVEL_1_Data'] = Department_top_1
            data['DEP_LEVEL_2_Data'] = Department_top_2
            data['DEP_LEVEL_3_Data'] = Department_top_3

        else:
            data['DEP_LEVEL_1_Data']=[]
            data['DEP_LEVEL_2_Data']=[]
            data['DEP_LEVEL_3_Data']=[]
            
        templates='worklog_submitrate.html'
        
        return templates, {'worklog_report': data}
        
class Bugzilla_Module(Component):

    implements(IModuleProvider)
        
    def get_module(self, req):
        #idata/setting/myagent#
        #add_ctxtnav(req, _('Bugzilla'), href=req.href('/idata/setting/Bugzilla'))        
        #yield ('setting','Bugzilla')

        add_ctxtnav(req, _('iBugzilla'), href=req.href('/idata/Bugzilla/query'))
        yield ('Bugzilla','query')
        
    def render_module(self, req, cat, page, path_info):
        data = {}      
        add_script(req, 'hw/js/Bz_Ajax.js')     
        
        #tablequery  
        #add_script(req, 'hw/js/bz_jquery.dataTables.min.js')  
        #add_script(req, 'hw/js/bz_jquery.js') 
        
        #bz_jquery.dataTables.js  
        #add_script(req, 'hw/js/jquery.dataTables.min.js')   
        #add_stylesheet(req, 'hw/css/demo_table.css')    
        
        bugz = bz_api.bz_connect(self.env)  
        
        import watch_dog
        watch_dog.WatchDog(self.env, req, bz_gl.gl_srv_heart)        
        
        if path_info is None:
            path_info = 'Bz_QueryManager'
        js  = bz_web.bz_nav(req)
        data.update({'bz_nav':HTML(js)})              
        data['CurrentUser']=req.session.sid    
        data['path_info']=path_info
        data['SiteRoot']='http://tracsrv/idata/Bugzilla/query/'+path_info

        if path_info == 'Bz_QueryManager':
            bz_web_ui._P_QueryManager(self.env, req, data, bugz, db_conn) 
            templates='Bz_QueryManager.html' 
            
        elif path_info == 'Bz_AQuery':        
            bz_web_ui._P_AQuery(self.env, req, data, bugz, db_conn)
            templates='Bz_QueryManager.html' 
            
        elif path_info == 'Bz_TrendPic':        
            bz_web_ui._P_TrendPic(self.env, req, data, bugz, db_conn)
            templates='Bz_QueryTrendPic.html' 
            
        elif path_info == 'Bz_QueryStatics':        
            data = self._P_Statics(req, data, bugz)
            templates='Bz_QueryStatics.html'  

        elif path_info == 'Bz_Setting':        
            data = self._P_Setting(req, data, bugz)
            templates='Bz_Setting.html'

        elif path_info == 'Bz_QueryTree':        
            data = bz_web_ui._P_QueryTree(self.env, req, data, bugz, db_conn)
            templates='Bz_QueryTree.html' 

        elif path_info == 'Bz_Ajax_QueryTree':
            bz_web_ui._P_Ajax_QueryTree(self.env, req, data, bugz, db_conn)        
            
        elif path_info == 'Bz_Debug':
            bz_web_ui._P_Debug(self.env, req, bugz)            
            templates='Bz_QueryBlank.html'

        elif path_info == 'Bz_EmailManager':
            bz_web_ui._P_EmailManager(self.env, req, data, bugz, db_conn)        
            templates='Bz_EmailManager.html'

        elif path_info == 'Bz_Help':   
            templates='Bz_Help.html'          
            
        else:               
            bz_web_ui._P_QueryManager(self.env, req, data, bugz, db_conn) 
            templates='Bz_QueryManager.html'
      
            
        #return templates, {'worklog_report': data}  
        return templates, data


    def _P_Schdule(self, req, db_conn, bugz, cc):        
        file_flag = bz_gl.gl_schdule_pollingtime          
        cur_time = datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S")  
        bz_utils.write_file(file_flag, cur_time)          
        #schedule_event = schedule.Schedule(self.env, req, db_conn, bugz, file_flag, bz_gl.gl_day, bz_model.Syn_Bugz_BugList)        
        #schedule_event = schedule.Schedule(self.env, req, db_conn, bugz, file_flag, bz_gl.gl_hour, bz_model.Syn_Bugz_BugList)   
        schedule_event = schedule.Schedule(self.env, req, db_conn, bugz, file_flag, \
                        bz_gl.gl_hour, bz_model.Schedule_SynBugList)   
        
        while 1:            
            schedule_event.trigger()
            time.sleep(30*1)
            
        self.log.error('_P_Schdule: --')  

    def _P_SearchDepart(self, req, all_units, data):   
        exrows = []       

        level = req.args.get(bz_gl.gl_DepartmentLevel) 
        a_Bugz_table = bz_model.Bugz_Depart(None, db_conn)

        self.log.error('_P_SearchDepart level= %s', level) 
        QF = {}  
        QF['field_level_type'] = level  
        Bugz_tables = a_Bugz_table.select(QF)
       
        for a_table in Bugz_tables:            
            alist = []                       
            for col in bz_gl.gl_DepartmentNames: 
                alist.append(a_table[col])  
            exrows.append(tuple(alist))

        data['exrows'] = exrows 
        data['excols'] = bz_gl.gl_DepartmentMMINames 

    def _P_SearchOwerDepart(self, req, all_units, data): 
        cols = bz_gl.gl_DepartmentLevels     
        exrows = []
        excols = []        
        excols.insert(0,"Ower")
        for a_label in cols:
            excols.append(a_label)
            
        a_Bugz_table = bz_model.Bugz_Ower(None, db_conn)  
        QF = {}  
        for a_unit in all_units:  
            QF['field_ower'] = a_unit  
            
            alist = []            
            alist.append(a_unit)
            Bugz_tables = a_Bugz_table.select(QF)
            length = len(Bugz_tables) 
            if length == 1: 
                for row_Bugz_table in Bugz_tables:                    
                    break
                for col in cols:   
                    #self.log.error('_P_SearchOwerDepart col= %s, a_Bugz_table[col]= %s', col, a_Bugz_table[col]) 
                    alist.append(row_Bugz_table[col])  
            exrows.append(tuple(alist))
      
        data['exrows'] = exrows 
        data['excols'] = excols                                      

    def _P_Setting(self, req, data, bugz):  
        
                     
        js = bz_web.bz_setting(self.env, req, bugz)     
        data.update({'setting':HTML(js)}) 
        
        a_Bugz_table = bz_model.Bugz_Depart(None, db_conn)     
        b_Bugz_table = bz_model.Bugz_Ower(None, db_conn)  
        all_units = bz_gl.bz_owers(self.env, req, a_Bugz_table)  
        #all_units = bz_gl.bz_new_owers(self.env, req, b_Bugz_table) 
        
        if bz_gl.gl_SynchronizeBugzData in req.args:             
            thread.start_new_thread(bz_model.Syn_Bugz_BugList, (self.env, req, db_conn, bugz, all_units, 'haha'))
        elif bz_gl.gl_SearchOwerDepart in req.args:             
            self._P_SearchOwerDepart(req, all_units, data)   
        elif bz_gl.gl_SearchDepart in req.args:             
            self._P_SearchDepart(req, all_units, data)    
        elif bz_gl.gl_SchduleTrigger in req.args:             
            thread.start_new_thread(self._P_Schdule, (req, db_conn, bugz, 'haha'))                     
        elif bz_gl.gl_SynchronizeOwer_3levels in req.args:             
            thread.start_new_thread(bz_model.Syn_Bugz_Ower_3levels, (self.env, req, db_conn, all_units, 'haha'))
        elif bz_gl.gl_SynchronizeDepart_3levels in req.args:             
            thread.start_new_thread(bz_model.Syn_Bugz_Depart_3levels, (self.env, req, db_conn, all_units, 'haha'))         
        elif bz_gl.gl_SynchronizeDepart_leader in req.args:             
            thread.start_new_thread(bz_model.Syn_Bugz_Depart_leader, (self.env, req, db_conn, all_units, 'haha'))        
        elif bz_gl.gl_SynchronizeOwer in req.args:             
            thread.start_new_thread(bz_model.Syn_Bugz_Ower, (self.env, req, db_conn, all_units, 'haha'))
        elif bz_gl.gl_SynchronizeDepart in req.args:   
            thread.start_new_thread(bz_model.Syn_Bugz_Depart, (self.env, req, db_conn, all_units, 'haha'))          
        elif bz_gl.gl_SynchronizeOwerDepart in req.args:             
            thread.start_new_thread(bz_model.Syn_Bugz_BugList_Depart, (self.env, req, db_conn, all_units, 'haha'))
        #elif bz_gl.gl_SynchronizeOwerTime in req.args:             
        #    thread.start_new_thread(bz_model.Syn_Bugz_BugList_Time, (self.env, req, db_conn, all_units, 'haha'))
                    
        #if req.session.sid == 'song.shan':
        #self._P_DepartTree(req, bugz, data)     
        return data 
        




    def _P_Statics_Pic(self, data, Title_name, SubTitle_name, Xaxis_name, Yaxis_Title_name, YM_data_dic, pic_type): 
        import line_chart_model
        import column_chart_model
        from genshi import HTML 

        import sys
        reload(sys)
        sys.setdefaultencoding('gb2312')

        Xaxis_name_str = line_chart_model.Line_Chart.get_line_Xaxis_name(Xaxis_name)
        data_str = line_chart_model.Line_Chart.get_line_Xaxis(YM_data_dic)
        
        Title_name = Title_name.encode('utf-8') 
        Xaxis_name_str = Xaxis_name_str.encode('utf-8') 
        Yaxis_Title_name = Yaxis_Title_name.encode('utf-8')
        data_str = data_str.encode('utf-8')

        if pic_type == bz_gl.gl_BugTrend.decode("GBK") \
                or pic_type == bz_gl.gl_BugTrendNew.decode("GBK"):          
            line_str = line_chart_model.Line_Chart.get_line_chart_javascript('line', 'container_line', \
                Title_name, SubTitle_name, Xaxis_name_str , \
                Yaxis_Title_name,  data_str)
        else: 
            line_str = column_chart_model.Column_Chart.get_column_chart_javascript('line', 'container_line', \
                Title_name, Xaxis_name_str , \
                Yaxis_Title_name,  data_str, SubTitle=SubTitle_name)
        
        data.update({'line':HTML(line_str)})


    def _P_Original_Data(self, req, statics_type, all_units, unit_type, data):         
        a_Bugz_table = bz_model.Bugz_BugList(None, db_conn)   
        cols = bz_gl.gl_BugOriginalData_cols
        weeks_cols = bz_gl.bz_weeks(req)
        
        exrows = []         
        for a_unit in all_units:                
            QF = {}             
            if unit_type == bz_gl.gl_Department.decode('GBK'):
                ower = a_unit['value']
                QF['field_'+a_unit['fname']] = ower 
                    
            for a_week in weeks_cols:                    
                QF['field_start_time'] = a_week  
                
                row_Bugz_table = a_Bugz_table.select(QF)
                for row in row_Bugz_table:
                    alist = []
                    for fname in cols:
                        alist.append(row[fname])  
                    exrows.append(tuple(alist)) 
              
        data['rows'] = exrows 
        data['cols'] = cols  

    def _P_Append_Row(self, req, result, cols, rows):         
        for row in result:
            alist = []
            for fname in cols:
                alist.append(row[fname])  
            rows.append(tuple(alist)) 
       
    def _P_Statics_Data(self, req, statics_type, all_units, unit_type, data): 
        import line_chart_model
        
        a_Bugz_table = bz_model.Bugz_BugList(None, db_conn) 
        weeks_cols = bz_gl.bz_weeks(req)
        statics_cols = bz_gl.bz_statics_cols(req, statics_type)
        
        cols = bz_gl.gl_BugOriginalData_cols
        rows = []    
        exrows = []   
        excols = []
        excols.insert(0,"Ower")

        Xaxis_name = [] 
        for a_Xaxis in statics_cols:
            Xaxis_name.append((a_Xaxis))            
            excols.append((a_Xaxis))            
        YM_data_dic = {} 
        
        for a_unit in all_units:                
            QF = {}   
            if unit_type == bz_gl.gl_Department.decode('GBK'):
                ower = a_unit['value']
                QF['field_'+a_unit['fname']] = ower              
            elif unit_type == bz_gl.gl_Person:            
                QF['field_assigned_to'] =  a_unit + '@spreadtrum.com' 
                ower = a_unit
                
            Total = 0
            ym_data = [] 
            alist = []            
            alist.append(ower)

            for col in statics_cols:
                lenth = 0
                a_num_data = {}
                a_deltaday_data = {}
                a_num_data[col] = 0 
                a_deltaday_data[col] = 0 
                for a_week in weeks_cols:                    
                    QF['field_start_time'] = a_week                     
                    if statics_type == bz_gl.gl_BugTrend.decode("GBK"):
                        QF['field_end_time'] = col  
                    elif statics_type == bz_gl.gl_BugOrigin.decode("GBK"):            
                        QF['field_cf_come_from'] = col
                    elif statics_type == bz_gl.gl_BugClass.decode("GBK"):            
                        QF['field_bug_severity'] = col  

                    if statics_type == bz_gl.gl_BugNow.decode("GBK"):          
                        QF['field_bug_severity'] = col
                        
                        QF['field_bug_status'] = "NEW"
                        result = a_Bugz_table.select(QF)                        
                        self._P_Append_Row(req, result, cols, rows)
                        lenth += len(result)  
                        
                        QF['field_bug_status'] = "Assigned"
                        result = a_Bugz_table.select(QF)                        
                        self._P_Append_Row(req, result, cols, rows)
                        lenth += len(result)  
                        
                        QF['field_bug_status'] = "ROOT-Caused"
                        result = a_Bugz_table.select(QF)                        
                        self._P_Append_Row(req, result, cols, rows)
                        lenth += len(result)  
                    elif statics_type == bz_gl.gl_BugTrendNew.decode("GBK"):   
                        if col == a_week:
                            result = a_Bugz_table.select(QF)                        
                            self._P_Append_Row(req, result, cols, rows)
                            lenth = len(result) 
                    elif statics_type == bz_gl.gl_BugInTime.decode("GBK"): 
                        result = a_Bugz_table.select(QF)                        
                        self._P_Append_Row(req, result, cols, rows)                   
                        for row in result:  
                            OpenedDate=row['opendate'] #1 
                            time1 = bz_utils.timestring2seconds(OpenedDate)                        
                            AssignedDate=row['cf_assigneddate'] #2  
                            time2 = bz_utils.timestring2seconds(AssignedDate)
                            RootCausedDate=row['cf_rootcauseddate'] #3
                            time3 = bz_utils.timestring2seconds(RootCausedDate)
                            FixedDate=row['cf_fixeddate']          #4
                            time4 = bz_utils.timestring2seconds(FixedDate)                            
                            ClosedDate=row['cf_closeddate']        #5
                            time5 = bz_utils.timestring2seconds(ClosedDate)
                            
                            if col == 'open2assign(Days)':
                                delta = bz_utils.deltatime_day(time2, time1)
                            elif col == 'assign2root_cause(Days)':
                                delta = bz_utils.deltatime_day(time3, time2)
                            elif col == 'root_cause2fix(Days)':
                                delta = bz_utils.deltatime_day(time4, time3)
                            elif col == 'fix2close(Days)': 
                                delta = bz_utils.deltatime_day(time5, time4)
                                
                            if delta != 999:  
                                a_deltaday_data[col] +=  delta   
                                a_num_data[col] += 1       
                                 
                    else:
                        result = a_Bugz_table.select(QF)                        
                        self._P_Append_Row(req, result, cols, rows)
                        lenth += len(result) 
                        
                if statics_type == bz_gl.gl_BugInTime.decode("GBK"):   
                    if a_num_data[col] != 0:
                        lenth = int('%d' % (a_deltaday_data[col]/a_num_data[col])) 
                    else:
                        lenth = 999
                Total += lenth 
                alist.append(lenth)  #a col
                ym_data.append(lenth)            
                YM_data_dic.update({ower:ym_data})
            alist.append(Total)
            exrows.append(tuple(alist))         
        excols.append("Total")        
        data['exrows'] = exrows 
        data['excols'] = excols 
        
        data['rows'] = rows 
        data['cols'] = cols          

        Title_name = statics_type 
        lenth_week = len(weeks_cols)
        SubTitle_name = 'week period: '+weeks_cols[0]+'-->'+weeks_cols[lenth_week-1]
        Yaxis_Title_name = bz_gl.bz_statics_Yaxis_Title(statics_type)
        self._P_Statics_Pic(data, Title_name, SubTitle_name, Xaxis_name, Yaxis_Title_name, YM_data_dic, statics_type)
    
    def _P_Statics(self, req, data, bugz):                     
        js = bz_web.bz_statics(self.env, req, bugz, db_conn)     
        data.update({'ex_basic_query':HTML(js)}) 
        
        b_Bugz_table = bz_model.Bugz_Ower(None, db_conn) 
        statics_type = req.args.get(bz_gl.gl_StaticsTypeID)        
        unit_type = req.args.get(bz_gl.gl_UnitID)
        if unit_type == bz_gl.gl_Department.decode('GBK'):
            all_units = bz_gl.bz_departments(req)
        elif unit_type == bz_gl.gl_Person:
            all_units = bz_gl.bz_new_owers(self.env, req, b_Bugz_table) 
            self.log.error('_P_Statics: all_units=%s', all_units)
        
        if bz_gl.gl_Submit_Query in req.args:    
            if statics_type == bz_gl.gl_BugOriginalData.decode("GBK"): 
                self._P_Original_Data(req, statics_type, all_units, unit_type, data)
            else:
                self._P_Statics_Data(req, statics_type, all_units, unit_type, data)
        elif bz_gl.gl_SynchronizeBugzDB in req.args: 
            a_Bugz_table = bz_model.Bugz_Depart(None, db_conn)
            all_users = bz_gl.bz_owers(self.env, req, a_Bugz_table)          
            bz_model.Syn_Bugz_BugList(self.env, req, db_conn, bugz, all_users, bz_gl.gl_SynchronizeBugzDB)   
            bz_model.Syn_Bugz_BugList_Depart(self.env, req, db_conn, all_users, bz_gl.gl_SynchronizeBugzDB)
      
    
        
        return data 


    def _P_DepartTree(self, req, bugz, data):  
        a_Bugz_table = bz_model.Bugz_Depart(None, db_conn)
        js = bz_web.bz_depart_tree(req, a_Bugz_table) 
        
        data.update({'dtree_js':HTML(js)})

        
  

class Worklog_Help_Module(Component):

    implements(IModuleProvider)

    def get_module(self, req):
        add_ctxtnav(req, _('Help'), href=req.href('/idata/help/help'))
        yield ('help','help')

    def render_module(self, req, cat, page, path_info):
        import os
        from genshi import HTML

        data = {}
        
        templates='worklog_help.html'
        
        return templates, {'worklog_report': data}
 
