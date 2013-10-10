
# -*- coding: utf-8 -*-
#

import shutil
import calendar
import time
import struct
import posixpath
import os, sys, re, string 

from StringIO import StringIO
from datetime import datetime
from trac.util import format_datetime

smtpserver = '10.0.0.100' 

def SendPicMail(env, maildic):         
    msgRoot = MIMEMultipart('related')  
    msgRoot['Subject'] = 'test message'  
      
    msgText = MIMEText('<b>Some <i>HTML</i> text</b> and an image.<br><img src="cid:image1"><br>good!','html','utf-8')  
    msgRoot.attach(msgText)  
      
    fp = open('h:\\python\\1.jpg', 'rb')  
    msgImage = MIMEImage(fp.read())  
    fp.close()        
    msgImage.add_header('Content-ID', '<image1>')  
    msgRoot.attach(msgImage)  
      
    smtp.sendmail(sender, receiver, msgRoot.as_string())  


#HTML形式的邮件
def SendHtmlMail(env, maildic): 
    env.log.error('sendmail in') 
    
    import smtplib  
    from email.MIMEText import MIMEText  
    #from email.header import Header
    from email.mime.multipart import MIMEMultipart
    from email.mime.image import MIMEImage     
     
    title = maildic['title']
    decription = maildic['decription']
    if title is None or title == '':
        title = 'No Title From iBugzilla'
    
    to_s = maildic['to'] 
    cc_s = maildic['cc']# or None
    html_body = maildic['content']
    attach_file = maildic['attach_file']

    env.log.error('sendmail attach_file= %s', attach_file) 
    msg = MIMEMultipart('alternatvie')
    
    text = decription #'Hi:\n    '+''+'\n\n'   
    part1 = MIMEText(text.encode('utf-8'), 'plain', "utf-8")     
    env.log.error('sendmail part1 in')  
    html = """ 
        <html> 
          <head><style type="text/css">*{font-size:15px;}</style></head> 
          <body> 
                __html_body__
          
          <br /><br /><br />
          <img src="cid:image1">
          </body> 
        </html> 
    """
    html = html.replace('__html_body__', html_body)
    part2 = MIMEText(html.encode('utf-8'), "html", "utf-8")     
    env.log.error('sendmail part2 in') 
    # According to RFC 2046, the last part of a multipart message, in this case  
    # the HTML message, is best and preferred.  
    msg.attach(part1)  
    msg.attach(part2) 
    
    #发送图片
    import bz_gl
    email_logo = os.path.join(bz_gl.gl_srv_htdocs, 'email_logo.bmp')
    #env.log.error('sendmail email_logo=%s',email_logo)     
    fp = open(email_logo, 'rb')  
    msgImage = MIMEImage(fp.read())  
    fp.close()     
    msgImage.add_header('Content-ID', '<image1>')  
    msg.attach(msgImage)  

    #构造附件  
    if os.path.exists(attach_file):
        att = MIMEText(open(attach_file, 'rb').read(), 'base64', 'utf-8')  
        att["Content-Type"] = 'application/octet-stream'  
        att["Content-Disposition"] = 'attachment; filename="query_result.csv"'  
        msg.attach(att)           
    try:
            s = smtplib.SMTP(smtpserver) #登录SMTP服务器,发信#            
            fromclause = "iManage@spreadtrum.com"
            
            toclause_s = []
            to_s_list = string.splitfields(to_s, ",")
            for a_to in to_s_list:
                if a_to != '':
                    toclause_s.append(a_to+"@spreadtrum.com")
            msg['To'] = ','.join(toclause_s)

            ccclause_s = []
            cc_s_list = string.splitfields(cc_s, ",")
            for a_cc in cc_s_list:
                if a_cc != '':
                    ccclause_s.append(a_cc+"@spreadtrum.com")
            msg['CC'] = ','.join(ccclause_s)
            msg['Subject'] = title
            msg['From'] = fromclause  
            
            env.log.error('sendmail ccclause_s = %s',ccclause_s)
            env.log.error('sendmail toclause_s = %s',toclause_s)
            s.sendmail(fromclause,toclause_s+ccclause_s,msg.as_string())
    except Exception,e:
            env.log.exception("Failure sending notification "
                               "%s", e) 
                




    


def fmt_timestamp(seconds):
    millis = int(seconds * 1000) % 1000
    localtime = time.localtime(seconds)
    text = []
    text.append(time.strftime('%m/%d/%y  %H:%M:%S', localtime))
    text.append('.%03d' % millis)
    return "".join(text)


#def dayfiled2weeks(env, s, e):
def dayfiled2weeks(s, e):
    result = []


    #import datetime
    
    t_s = time.strptime(s,"%Y-%m-%d")
    dt_s = datetime(*t_s[:6])
    week_s = int(dt_s.strftime('%U'))+1
    #env.log.error('dayfiled2weeks: s weeks=%s', week_s)
        
    t_e = time.strptime(e,"%Y-%m-%d")
    dt_e = datetime(*t_e[:6])
    week_e = int(dt_e.strftime('%U'))+1
    #env.log.error('dayfiled2weeks: e weeks=%s', week_e) 

    y_s = int(s.split('-',s.count('-'))[0].replace('20',''))
    y_e = int(e.split('-',e.count('-'))[0].replace('20',''))

    #env.log.error('dayfiled2weeks: y_s=%s, y_e=%s', y_s,y_e) 
    while y_s <= y_e:    
        if y_s == y_e:
            while week_s<=week_e:
                if week_s<10:
                    result.append(str(y_e) + '.0' + str(week_s))
                else:
                    result.append(str(y_e) + '.' + str(week_s))
                week_s += 1                  
        elif y_s < y_e:
            while week_s<=54:
                if week_s<10:
                    result.append(str(y_s) + '.0' + str(week_s))
                else:
                    result.append(str(y_s) + '.' + str(week_s))
                week_s += 1 
            week_s = 1
        y_s += 1
        
    #env.log.error('dayfiled2weeks: result=%s', result)
    return result

def curtime_string():
        from datetime import datetime
        
        Now = datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')
        return Now

def curday_string():
        from datetime import datetime
        
        day = datetime.strftime(datetime.now(),'%Y-%m-%d')
        return day        

def deltatime_sec(time2, time1):#sec       
    delta = 0
    if time2 > time1:
        delta = time2 - time1                   
    return int(delta)

def deltatime_day(time2, time1):#day
    if time2 == 0 or time1 == 0:
        return 999
        
    delta = 0
    if time2 < time1:
        timeStr = 999
    elif time2 == time1:
        #timeStr = '%d:%d:%d' % (0,0,0)
        #timeStr = '%d' % (0)
        timeStr = 999
    else:
        delta = time2 - time1
        fmt_s = (delta%60)
        m = delta/60
        
        fmt_m = m%60
        h = m/60
        
        fmt_h = h%24 
        d = h/24
        if d > 1 or d == 1:          
            #timeStr = 'Days(%d) %d:%d:%d' % (d,fmt_h,fmt_m,fmt_s)
            timeStr = '%d' % (d+1)
        elif h > 0:
            #timeStr = '%d:%d:%d' % (h,fmt_m,fmt_s)
            timeStr = '%d' % (0+1)
        elif m > 0:  
            #timeStr = '%d:%d:%d' % (0,m,fmt_s)
            timeStr = '%d' % (0+1)
        elif fmt_s > 0: 
            #timeStr = '%d:%d:%d' % (0,0,fmt_s)
            timeStr = '%d' % (0+1)
        else:
            timeStr = '999'
            
        #fmt_d = d%365
        #y = d/365  
        #timeStr = '%d-%d %d:%d:%d' % (y,fmt_d,fmt_h,fmt_m,fmt_s)
        
        #seconds -> tuple->  string ->int          
    return int(timeStr)

def timestring2seconds(string):   
    time1 = 0
    if string is None or string == '':
        return time1
    #string->tuple->seconds    
    #2011-08-26 10:35:38
    tup = time.strptime(string,"%Y-%m-%d %H:%M:%S")
    time_length = time.mktime(tup)     
    return time_length

def timestring2week(env, s): 
    if s is None or s == '':
        return 'NULL'
    #string->tuple  
    #2011-08-26 10:35:38
    #env.log.error('timestring2week: s =%s', s)
    tup = time.strptime(s,"%Y-%m-%d %H:%M:%S")
    dt_s = datetime(*tup[:6])
    week_s = int(dt_s.strftime('%U'))+1
    #env.log.error('timestring2week: week_s =%s', week_s)

    y_s = s.split('-',s.count('-'))[0].replace('20','')  
    #y_s = tup[0].replace('20','')  
    #env.log.error('timestring2week: y_s =%s', y_s)
    if week_s<10:
        week = y_s + '.0' + str(week_s)
    else:                    
        week = y_s + '.' + str(week_s)
    #week = y_s + '.' + week_s
    #env.log.error('timestring2week: week=%s', week)
      
    return week
    
def tuple2string(tuples, tag=None):  
    if tag is None:
        tag = ';'
        
    string = ''
    if tuples is None or tuples == []:
        return '' #'---'

    if isinstance(tuples, list) == True:
        pass
    else:
        return tuples
        
    #if len(tuples) == 1:
    #    return tuples
    for s in tuples:
        string += s+tag
        
    return string

def string2tuple(string, tag=None):   
    if tag is None:
        tag = ';'
        
    tuples = []
    if string is None or string == '':
        return tuples
    
    flag = string.count(tag)
    if flag == 0:
        if string != '':
            tuples.append(string)
    else:  
        modules = string.split(tag,flag) 
        for sub_mod in modules:
            if sub_mod != '':
                tuples.append(sub_mod)
        
    return tuples

def string2list(env, string):
    a_list = re.split(r'[;,\s]+', string) 
    #env.log.error('string2list: %s', a_list)
    a_list = list(set(a_list))  
    a_list = [u for u in a_list if u]
    #a_list.reverse()
    return a_list

def string2list_nosort(string):
    a_list = re.split(r'[;,\s]+', string) 
    a_new_list = []
    for u in a_list:
        if u != '':
            a_new_list.append(u)
    #a_list = list(set(a_list))  
    #a_list = [u for u in a_list if u]
    #a_list.reverse()
    return a_new_list

def _show_current_time():
    current = datetime.utcnow()
    current = current.isoformat()
    current_int = int(_format_datetime(current))  
    current = format_datetime(current_int)  
    return current

def _get_current_time_str():
    import time
    from datetime import datetime, timedelta
    Timestr=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())    
    Timestr=Timestr.replace(":", "")
    Timestr=Timestr.replace("-", "")
    Timestr=Timestr.replace(" ", "")
    return Timestr



def _get_current_int_time():
    current = datetime.utcnow()
    current = current.isoformat()
    current_int = int(_format_datetime(current))  
    return current_int    

def _format_datetime(string):
    """Minimal parser for ISO date-time strings.
    
    Return the time as floating point number. Only handles UTC timestamps
    without time zone information."""
    try:
        string = string.split('.', 1)[0] # strip out microseconds
        return calendar.timegm(time.strptime(string, '%Y-%m-%dT%H:%M:%S'))
    except ValueError, e:
        raise ValueError('Invalid ISO date/time %r' % string)    

def _del_path(root): 
    if os.path.exists(root):
        shutil.rmtree(root) 
    #else:
     #   return


def read_file(file_name, mode='r'):
    """Read a file and return its content."""

    f = open(file_name, mode)
    try:
        return f.read()
    finally:
        f.close()

def write_file(file_name, data, mode='w'):
    f = open(file_name, mode)
    try:
        if data:
            f.write(data)
    finally:
        f.close()

def copy_file(src_file, dest_file):    
    if os.path.exists(dest_file):         
        os.unlink(dest_file)        
    #shutil.copy2(src_file, dest_file) 
    shutil.copy(src_file, dest_file)

def check_file(file_path):     
    #if os.path.isfile(file_path)
    if os.path.exists(file_path):   
        ret = True
    else:
        ret = False
    #log.info('ret=%s',ret)  
    return ret


def check_string(string, key):     
    flag = string.count(key)
    if flag == 0:
        ret = False
    else: 
        ret = True
        
    return ret        
