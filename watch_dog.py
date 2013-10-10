# -*- coding: utf-8 -*-
#
import os
import struct
import posixpath
import calendar
import re
import time
import socket
import thread
import urllib2

from StringIO import StringIO
from datetime import datetime, timedelta

from trac.util.translation import _, ngettext, tag_
from trac.util import escape, pretty_timedelta, format_datetime, shorten_line, \
                      Markup
from trac.attachment import Attachment
from trac.config import BoolOption, IntOption, Option
from trac.core import *
from trac.resource import ResourceNotFound
from trac.web import IRequestHandler, RequestDone
          
import bz_utils
import bz_event
import bz_gl

gl_Server_Error = 'Server Error!'
gl_srv_heart_polling_time = 'srv_heart'
def WatchDog(env, req, heart_file):  
        if not os.path.isfile(heart_file):
            polling_time = gl_Server_Error
        else:
            polling_time = bz_utils.read_file(heart_file) 

        
        Now = datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')
        if polling_time == gl_Server_Error: 
            bz_utils.write_file(heart_file, Now)  
        else:            
            time1 = bz_utils.timestring2seconds(polling_time)              
            time2 = bz_utils.timestring2seconds(Now)
            delta = bz_utils.deltatime_sec(time2, time1) 
            if delta > 60:
                env.log.error('WatchDog: polling_time=%s, cur_time=%s, %s',time1, time2, delta)
                thread.start_new_thread(FeedDog, (env, req, heart_file, 'haha'))
            else:
                bz_utils.write_file(heart_file, Now)


def WatchDogUI(env, heart_file):
    if not os.path.isfile(heart_file):
        polling_time = gl_Server_Error
    else:
        polling_time = bz_utils.read_file(heart_file)     

    js = ''    
    js += "	<b style=\"background: #eee\">"+("Polling Time".decode('GBK'))+":</b>"
    js += "	<input id=\""+gl_srv_heart_polling_time+"\" type=\"text\" name=\""+gl_srv_heart_polling_time+"\" size=\"20\" value=\""+polling_time+"\" readonly=\"1\"/></td>"
    #js += web_input(bz_gl.gl_srv_heart_polling_time, 'text', polling_time, size='50', readonly=True)       
    #js += web_button(gl.gl_server_monitor, 'iTestHeartBeat')  
    js += "<br /><br /><br />"  
    env.log.error('WatchDogUI: %s', polling_time)
    return js 
     


def FeedDog(env, req, heart_file, cc):    
    schedule_event = Schedule(env, heart_file)
    env.log.error('Feed_Dog: ++')

    #rpc_server.iTestRPCMain(env,'haha')
    #thread.start_new_thread(rpc_server.iTestRPCMain, (env,'haha'))
        
    while 1:        
        #env.log.error('_monitor_tmanager: ++while')        
        #rpc_server.iTestHeartBeat(env,req)        
        schedule_event.trigger()
        #env.log.error('_monitor_tmanager: --while')
        time.sleep(bz_gl.gl_Run_Interval)

    env.log.error('Feed_Dog: --')    


class Schedule(object):
    def __init__(self, env, heart_file):
        self.env = env
        self.log = env.log
        self.heart_file = heart_file
        
        #self.mskernel_flag = True
        #self.arm_flag = True
        #self.svr_env = bz_utils.get_file_dir(self.env, bz_utils.get_itest_log_dir(self.env), gl.gl_init_env) 
        #self.t_dailybuild_flag = bz_utils.get_file_dir(self.env, self.svr_env, gl.gl_auto_dailybuild_file_name)

    def condition(self):
        Now = datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')
        #elf.log.error('Watchdog: condition Now=%s', Now)  
        #elf.log.error('Watchdog: condition heart_file=%s', self.heart_file) 
        bz_utils.write_file(self.heart_file, Now)
        
        #polling_time = bz_utils._show_current_time()       
        #polling_times1 = polling_time.split(' ',polling_time.count(' '))
        #polling_times2 = polling_times1[0].split('/',polling_times1[0].count('/'))     
        #08/04/11 08:16:21
        #polling_times2[2] = 11        
        #cur_day = polling_times2[1]  
        
        return True
        #if os.path.isfile(self.t_dailybuild_flag):            
        #    #比较是否过了一天            
        #    record_day = bz_utils.read_file(self.t_dailybuild_flag)            
        #    self.log.debug('condition %s,%s', record_day, cur_day) 
        #    if record_day != cur_day:
        #        bz_utils.write_file(self.t_dailybuild_flag,cur_day)
        #        ret = True
        #    else:
        #        ret = False
        #else:
        #    #第一次创建文件
        #    bz_utils.write_file(self.t_dailybuild_flag,cur_day)
        #    ret = True
        #self.log.debug('condition - %s', ret) 
        #return ret


    def trigger(self):
        if self.condition() == True:  
            #self.log.error('Watchdog: trigger S_Remind++')    
            self.S_Remind()
            #self.log.error('Watchdog: trigger S_Remind--')    
            
            #thread.start_new_thread(db_backup, (self.env, 'haha'))
            #thread.start_new_thread(clearup_logins, (self.env, 'haha'))
            #thread.start_new_thread(dailybuild, (self.env, 'haha')) 

    def S_Remind(self): 
        #self.log.error('S_Remind ++')
        
        bz_event.bz_event_main(self.env)  
        #self.log.error('S_Remind --') 
        