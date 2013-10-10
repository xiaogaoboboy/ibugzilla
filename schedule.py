# -*- coding: utf-8 -*-
#

"""Schedule implementation."""

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
from datetime import datetime

               
import bz_utils
import bz_gl

class Schedule(object):
    def __init__(self, env, req, db_conn, bugz, file_flag, cycle, event):
        self.env = env
        self.log = env.log
        self.file_flag = file_flag
        self.cycle = cycle
        self.req = req
        self.db_conn = db_conn
        self.bugz = bugz
        self.event = event

    def condition(self):   
        string = bz_utils.read_file(self.file_flag) 
        tup = time.strptime(string,"%Y-%m-%d %H:%M:%S") 
        
        if self.cycle == bz_gl.gl_day:
            cur = datetime.strftime(datetime.now(),"%d") 
            record = tup[2] 
        elif self.cycle == bz_gl.gl_hour:
            cur = datetime.strftime(datetime.now(),"%H") 
            record = tup[3] 
        elif self.cycle == bz_gl.gl_min:
            cur = datetime.strftime(datetime.now(),"%M") 
            record = tup[4]  
        else:
            return False
                  
        #±È½Ï
        #self.log.error('condition cur=%s,record=%s', cur, record) 
        if int(record) != int(cur):
            self.log.error('condition ok cur=%s,record=%s', cur, record)  
            ret = True
        else:
            ret = False
        cur_time = datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S") 
        bz_utils.write_file(self.file_flag, cur_time)                

        return ret


    def trigger(self):
        #self.log.error('condition trigger in')
        #all_units= [u'wei.fan', u'xi.han', u'kevin.chen', u'talent.sun', u'yutai.hao', u'yitong.lin', u'kaihua.zhu', u'chun.zhang', u'rickey.zhang', u'chuan.feng', u'yongbiao.xiang', u'george.yuan', u'pizer.fan', u'song.shan', u'wei.han', u'sam.gu', u'justin.jiang', u'lei.xu', u'junbo.han', u'mingjian.liu', u'estrella.chen', u'hao.xu', u'qinghua.zhou', u'tommy.tang', u'cathy.wang', u'cuilian.yang', u'hailang.zhou', u'chong.liu', u'zhaozeng.wang', u'hua.li', u'changyou.peng', u'haibin.yu', u'bruce.jiang', u'eddie.wang', u'chun.jiang', u'maddie.lai', u'doris.wang', u'huawei.zhang', u'baoning.shan', u'long.sun', u'mengping.xu', u'xia.wei', u'minqian.qian', u'jinqiu.zhu', u'jimmy.yan', u'erling.wei', u'lawrence.chen', u'fengchun.pan', u'yi.jin', u'christina.yun', u'joe.ni', u'xiang.sun', u'hui.ding', u'jason.gao']
        #all_units = bz_gl.bz_sprd_all_usr(self.env)
        #self.log.error('condition all_units=%s',all_units)
        if self.condition() == True:  
            self.log.error('condition True++')
            thread.start_new_thread(self.event, (self.env, self.req, self.db_conn, self.bugz, 'haha'))
            self.log.error('condition True--')
