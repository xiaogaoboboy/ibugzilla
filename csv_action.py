# -*- coding: utf-8 -*-
#
import os
import sys  
import csv  
from pyExcelerator import *
import pyExcelerator as xl

reload(sys)  
sys.setdefaultencoding('utf-8')  
  
def csv_action_read(csv_file):   
    result = []
    file_csv = os.path.join(csv_file) 
    csvFile = csv.reader(open(file_csv))  
    for line in csvFile: 
        line_str = ''
        data_len = len(line)
        data_no = 0
        for data in line:  
            data_no += 1
            if data_no < data_len:
                line_str += data.encode('GBK')+','            
            else:
                line_str += data.encode('GBK')

        result.append(line_str)
    return  result

def xls_write(env, csv_file, a_sheet, cols, rows): 
    w = Workbook()
    
    if os.path.exists(csv_file):
        sheets = xl.parse_xls(csv_file)
        nsheets = len(sheets)
#>>> nsheets
#[(u'testExcelReport_hr',
#  {(0, 0): u'Deletetime',
#   (0, 1): u'Food',
#   (0, 2): u'Peak Rate',
#   (0, 3): u'Total Bytes',
#   (0, 4): u'Total Msg No'})]
     #This keeps all sheets except for the one named a_sheet, in effect removing a_sheet.
     #sheets = [(sheet_name, sheet_data) for (sheet_name, sheet_data) in sheets if sheet_name != a_sheet]
        for n in range(nsheets):
            #提取excel文件中的第n个表单
            sheet = sheets[n]
            #提取表单n的名称
            sh_name = sheet[0]
            if sh_name == a_sheet:
                env.log.error('xls_write: %s exist',a_sheet)
                continue
            ws = w.add_sheet(sh_name)
            sh_data = sheet[1]                    
            all_data_points = len(sh_data)
            for i in range(all_data_points):
                a_line = []
                for j in range(all_data_points):                 
                    if sh_data.has_key((i,j)):
                        #env.log.error('xlm_read: %s %s, %s',i,j,sh_data[(i,j)])
                        if isinstance(sh_data[(i,j)],float):
                            a_line.append(int(sh_data[(i,j)]))
                        else:
                            a_line.append(sh_data[(i,j)])
                #env.log.error('csv_read: a_line=%s',a_line)
                if i == 0:
                    for j in range(0, len(a_line)):
                        ws.write(i, j, a_line[j])
                else:
                    if len(a_line) > 0:             
                        for j,col in enumerate(a_line):  
                            ws.write(i, j, col)                         
                    else:
                        continue 

         
    #create a work book
    ws = w.add_sheet(a_sheet)
    #create xls header
    for index in range(0, len(cols)):
        ws.write(0, index, cols[index])

    #write content前三个参数分别是行、列、值
    for i,row in enumerate(rows):   
        for j,col in enumerate(row):  
            ws.write(i+1, j, col) 
    #env.log.error('xls_write: get_width=%s',w.get_width())  
    w.save(csv_file)     
    

def csv_write(csv_file,cols, rows): 
    #wb中的w表示写入模式，b是文件模式
    #写入一行用writerow
    #多行用writerows
    if 0:
        csvfile = file(csv_file, 'wb')
        writer = csv.writer(csvfile)    
        writer.writerow(cols)
        writer.writerows(rows)
    else:
        import codecs 
        
        fobj = open(csv_file,'wb')
        fobj.write(codecs.BOM_UTF8)  
        w = csv.writer(fobj)  
        w.writerow(cols) 
        w.writerows(rows)   
        fobj.close()    

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
#名字：ParseXlsUerator
#摘要：实现应用pyExcelerator产品读取excel文件的功能
#变量：upload —— 用户上传的excel文件
#返回：返回一个列表，每一项就是一个表单(sheet)；
#      其中表单是一个二元组(表单名称,表单数据)；
#      其中表单数据是一个字典，
#          key为单元格索引(i,j)，valuse为单元格的数据；
#      如果某个单元格无数据，那么就不存在这个值。
#      假设返回值为 sheets
#      则范例excel文件中的表单数为 len(sheets)
#        表单n的名称为 sheets[ n ][0]
#        表单n的数据为 sheets[ n ][1]
#        表单n的i行j列的单元格数据为 sheets[ n ][1][(i,j)]
#建立：lindalee@RunTo建立于2006年5月1日
#备注：应用pyExcelerator产品分析excel文件必须已知文件结构，
#      才能提取出某一位置的数据并根据变量类型对该数据进行处理。
#      同时还缺少对于上传文件不是excel格式这种异常情况的处理。
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
def ParseXlsUerator(upload):
  if not upload:
    return 0
  else:
    upload_data = upload.read()
    if len(upload_data)==0:
      return 0

  import pyExcelerator
  tmpfile = '/website/zopeinst/Extensions/upload.xls'
  f = open(tmpfile, 'wb')
  f.write(upload_data)
  f.close()

  sheets = pyExcelerator.parse_xls(tmpfile)
  return sheets

  
def xlm_read(env, csv_file, a_sheet, cols, rows): 
    #request = container.REQUEST
    #response =  request.RESPONSE

    #response.setHeader("Content-type","text/html;charset=utf-8")

    #读取用户上传的excel文件中的数据
    #sheets = context.ParseXlsUerator(upload)
    #return sheets

    #判断读取是否是否成功
    #if sheets==0:
    #  ErrStr = context.UrlEnCode("选择了无效文件或空文件，请重新上传！")
    #  response.redirect(context.absolute_url()+ \
    #                '/testerator_UploadXls?portal_status_message=' + ErrStr)
    #  return 0
    if not os.path.exists(csv_file):
        return False
        
    #提取excel文件中的表单数目
    sheets = xl.parse_xls(csv_file)
    nsheets = len(sheets)
    env.log.error('xlm_read: %s has %s sheets',csv_file,nsheets)

    for n in range(nsheets):
        #提取excel文件中的第n个表单
        sheet = sheets[n]
        #提取表单n的名称
        sh_name = sheet[0]
        if sh_name != a_sheet:
            continue
        #提取表单n的数据
        sh_data = sheet[1]
        #env.log.error('xlm_read: %s %s',n+1,context.ShowXlsCell(1,sheet[0]))
        #env.log.error('xlm_read: %s %s',n+1,sh_name)
        #
        #env.log.error('xlm_read: sheet=%s ',sheet)
        #env.log.error('xlm_read: sh_data=%s, \n %s',sh_data, len(sh_data))
          
        
        #判断表单n是否为空
        #if len(sh_data)!=0:
        #env.log.error('xlm_read: %s',sh_data)
        #for i,row in range(len(sh_data)):
        #for i,row in enumerate(sh_data):  
            # env.log.error('xlm_read: %s,  %s',i,row)
            #for j in range(len(row)):
            #for j,row in enumerate(sh_data):  
                    
        #for idx,line in enumerate(sh_data):
        all_data_points = len(sh_data)
        for i in range(all_data_points):
            #env.log.error('xlm_read: %s',i)
            a_line = []
            for j in range(all_data_points):                 
                if sh_data.has_key((i,j)):
                    #env.log.error('xlm_read: %s %s, %s',i,j,sh_data[(i,j)])
                    if isinstance(sh_data[(i,j)],float):
                        a_line.append(int(sh_data[(i,j)]))
                    else:
                        a_line.append(sh_data[(i,j)])
            #env.log.error('csv_read: a_line=%s',a_line)
            if i == 0:
                cols += a_line                       
            else:
                if len(a_line) > 0:                    
                    rows.append(a_line)
                else:
                    return True
    return True

def csv_read(env, csv_file, cols, rows): 
    if not os.path.exists(csv_file):
        return False
    fobj = file(csv_file, 'rb')
    content = csv.reader(fobj)

    for idx,line in enumerate(content):
    #for idx,a_level in enumerate(tree_list)
        if idx == 0:
            #
            #cols = line
            #cols.append(line)
            cols += line
        else:
            #env.log.error('csv_read: line=%s',line)
            rows.append(line)

    fobj.close()  
    return True
