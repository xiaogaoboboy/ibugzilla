# -*- coding: utf-8 -*-

import re
import os
from xlwt import *
from datetime import datetime, timedelta

class Excel(object):
    
    def __init__(self, ):
        self.style_init = easyxf("""
            align: 
                wrap on, 
                horiz left;
            pattern: 
                pattern solid, 
                fore-colour white;
            borders:
                left medium,
                right medium,
                top medium,
                bottom medium
            """)
        self.style_lab = easyxf("""
            font: 
                colour_index white,
                name Arial, 
                height 0xFF,
                bold on;
            align: 
                wrap off, 
                horiz left;
            pattern: 
                pattern solid, 
                fore-colour light_blue;
            borders:
                left medium,
                right medium,
                top medium,
                bottom medium
            """)
        self.style_lab_big = easyxf("""
            font: 
                colour_index white,
                name Arial, 
                height 0x150,
                bold on;
            align: 
                wrap off, 
                horiz left;
            pattern: 
                pattern solid, 
                fore-colour light_blue;
            borders:
                left medium,
                right medium,
                top medium,
                bottom medium
            """)
        self.style_lab_right = easyxf("""
            font: 
                colour_index white,
                name Arial, 
                bold on;
            align: 
                wrap off, 
                horiz right;
            pattern: 
                pattern solid, 
                fore-colour light_blue;
            borders:
                left medium,
                right medium,
                top medium,
                bottom medium
            """)
        self.style_Title = easyxf("""
            font: 
                height 0x250,
                colour_index white,
                bold on;
            align: 
                wrap off, 
                vert center, 
                horiz center;
            pattern: 
                pattern solid, 
                fore-colour gray_ega;
            borders:
                left thin,
                right thin,
                top thin,
                bottom thin
            """)
        self.style_heading = easyxf("""
            font: 
                height 0xFF,
                colour_index white,
                bold on;
            align: 
                wrap off, 
                vert center, 
                horiz center;
            pattern: 
                pattern solid, 
                fore-colour gray_ega;
            borders:
                left thin,
                right thin,
                top thin,
                bottom thin
            """)
        self.style_body = easyxf("""
            align: 
                wrap on, 
                vert center, 
                horiz left;
            pattern: 
                pattern solid, 
                fore-colour light_yellow;
            borders:
                left thin,
                right thin,
                top thin,
                bottom thin
            """)

    
    def Create(self, Label_Name, fill_Projects, fill_worklog_show, fill_worklog_project_show):

        if Label_Name:
            w = Workbook()
            ws = w.add_sheet(Label_Name, cell_overwrite_ok=True)
            for a_col in range(0, 100):
                ws.col(a_col).width=5000

            row_index =0
            col_index = 0
            ws.write(row_index, col_index, u'ID',self.style_heading)
            ws.write(row_index, col_index + 1, u'Chinese Name',self.style_heading)
            ws.write(row_index, col_index + 2, u'English Name',self.style_heading)
            ws.write(row_index, col_index + 3, u'Dep1',self.style_heading)
            ws.write(row_index, col_index + 4, u'Dep2',self.style_heading)
            ws.write(row_index, col_index + 5, u'Dep3',self.style_heading)
            ws.write(row_index, col_index + 6, u'Year-Month',self.style_heading)
            col_index = col_index +7
            for a_project in fill_Projects:
                 ws.write(row_index, col_index, a_project,self.style_heading)
                 col_index +=1
            
            row_index = row_index +1
            col_index = 0
            for a_worklog in fill_worklog_show:
                ws.write(row_index, col_index ,a_worklog['User_SN'],self.style_body)
                ws.write(row_index, col_index + 1 ,a_worklog['UserName_CN'],self.style_body)
                ws.write(row_index, col_index + 2 ,a_worklog['UserName'],self.style_body)
                ws.write(row_index, col_index + 3 ,a_worklog['DepID1'],self.style_body)
                ws.write(row_index, col_index + 4 ,a_worklog['DepID2'],self.style_body)
                ws.write(row_index, col_index + 5 ,a_worklog['DepID3'],self.style_body)
                ws.write(row_index, col_index + 6 ,a_worklog['Year_Months'],self.style_body)
                col_index = col_index +7
                for a_project in fill_Projects:
                    tmp_key = a_worklog['User_SN'] + '_' + a_worklog['Year_Months'] + '_'   +  a_project
                    if tmp_key in fill_worklog_project_show.keys():
                        ws.write(row_index, col_index,fill_worklog_project_show[tmp_key],self.style_body)
                    else:
                        ws.write(row_index, col_index,'',self.style_body)
                    col_index +=1
                col_index = 0
                row_index = row_index +1

            savefile = "iTada_" + Label_Name + "_" + datetime.strftime(datetime.now(),"%Y-%m-%d-%H-%M-%S") + ".xls"
            if os.name=='posix':
                savefile = '/tmp/' + savefile
            else:
                savefile = os.environ['TEMP'] + '/' + savefile
            w.save(savefile)
            return savefile
