# -*- coding: utf-8 -*-
#
from htmlentitydefs import entitydefs
from HTMLParser import HTMLParser
import sys,urllib2

from htmlentitydefs import name2codepoint

class DataParser(HTMLParser):
    def __init__(self, env, srch_tag, product=''):
        self.env = env
        self.log = env.log    
        self.onedata = None
        self.data = []      
        self.isTag = 0
        self.name = ''
        self.email = []
        self.component = []
        self.srch_tag = srch_tag
        self.product = product
        HTMLParser.__init__(self)

    def handle_starttag(self,tag,attrs):
        self.log.error('Start tag:', tag)
        for attr in attrs:
            self.log.error('     attr:', attr)
            
        if tag == self.srch_tag:
            self.isTag = 1
            #self.log.error('DataParser: +++++ data=%s', self.data)
            #self.name = [v for k,v in attrs if k == 'name']
            for k,v in attrs:
                self.log.error('handle_starttag k=%s,v=%s',k, v)  
                if k == 'class':
                    self.name = v
                elif k == 'href': 
                    #<a class="email" href="mailto:elly.zhou&#64;spreadtrum.com" title="Zhou Elly(周莹莉）588-1089 &lt;elly.zhou&#64;spreadtrum.com&gt;"> <span class="fn">Zhou Elly(周莹莉）588-1089</span></a>
                    if 'mailto:' in v:
                        email = v.replace('mailto:','')#href="mailto:icsccb@spreadtrum.com"
                        self.email.append(email)
                    
                    #buglist.cgi?product=SC8825_4.0.3&component=Trout_WIFI&resolution=---
                    #<a href="buglist.cgi?product=SC8825_4.0.3&amp;component=8825_4.0_PM_CCB&amp;resolution=---">8825_4.0_PM_CCB</a>
                    if '&resolution=---' in v:
                        component = v.replace('buglist.cgi?product='+self.product+'&component=','')
                        component = component.replace('&resolution=---','')
                        self.component.append(component)
                
            

    def handle_data(self,text):           
        if self.isTag:
            self.log.error('Data     :', text) 
            #self.log.error('DataParser: handle_data %s, data=%s', self.isTag, text)
            self.onedata = text
            if self.name == 'email':                
                self.log.error('handle_data: name=%s,text=%s',self.name, text)  
                #text = text.split('\n')[0]
                if text != '' or text != ' ':                    
                    self.data.append(text)             

    def handle_endtag(self,tag): 
        self.log.error('End tag  :', tag) 
        if tag == self.srch_tag:            
            self.log.error('handle_endtag: ------ data=%s', self.data)
            self.isTag = 0

    def get_onedata(self):
        return self.onedata

    def get_data(self):
        return self.data

    def get_email(self):
        return self.email        

    def get_component(self):
        return self.component   

    def get_comp_ower(self):
        html_parser = HTMLParser()
        comp_ower = []
        self.log.error('get_comp_ower: self.email=%s', self.email)
        self.log.error('get_comp_ower: self.component=%s', self.component)
        if len(self.email) == len(self.component):
            index = 0
            for a_email in self.email:
                a_comp_ower = {}
                import urllib
                a_comp = self.component[index]
                a_comp_ower['Component'] = urllib.unquote(html_parser.unescape(a_comp))
                
#比方说一个从网页中抓到的字符串
#s = '&lt;abc&gt;'

#用Python可以这样处理：
#import HTMLParser
#html_parser = HTMLParser.HTMLParser()
#s = html_parser.unescape(s) #这样就得到了s = '<abc>'
                a_ower = a_email.replace('@spreadtrum.com','')
                a_ower = a_ower.replace('@Spreadtrum.com','')
                a_comp_ower['Ower'] = html_parser.unescape(a_ower).replace('&#64;','@')
                
                comp_ower.append(a_comp_ower) 
                index += 1
        self.log.error('get_comp_ower: comp_ower=%s', comp_ower)
        return comp_ower   


class MutilHTMLParser(HTMLParser): 
    def __init__(self, env, tags, select_name):
        self.env = env
        self.log = env.log    
        self.taglevels=[] 
        self.handledtags=tags #['select'] #['body'] #['title','body'] #提出标签 
        self.processing=None
        self.select_name=select_name
        self.a_map={}
        self.a_map['ui'] = ''
        self.a_map['db'] = '' 
        self.map_table=[]
        HTMLParser.__init__(self) 
    def handle_starttag(self,tag,attrs): 
        if tag in self.handledtags: 
            self.data=''             
            self.values=[]            
        if tag =='select': 
            for name,value in attrs:                
                if name=='name':
                    if value==self.select_name:
                        self.processing=tag 
                        #self.log.error('=== in value=%s ', value) 
                    else:
                        self.processing=None 
                        #self.log.error('=== out value=%s ', value) 
        if self.processing:  
            if tag =='option': 
                for name,value in attrs:                
                    if name=='value':
                        #self.log.error('1  value=%s', value)
                        self.a_map['db'] = value
                        #self.log.error('1  a_map=%s', self.a_map)
    def handle_data(self,data): 
        if self.processing: 
            #self.log.error('2  data=%s', self.data)
            self.data +=data
            data = data.replace('\n    ','')  
            data = data.replace('      ','') 
            if data != '' and self.a_map['db'] != '':
                self.a_map['ui'] = data
                a_map={}
                a_map['ui']=self.a_map['ui']
                a_map['db']=self.a_map['db']
                self.map_table.append(a_map)
                #self.log.error('2  a_map=%s', self.a_map)
                #self.log.error('2  map_table=%s', self.map_table)
                self.a_map['ui'] = ''
                self.a_map['db'] = ''
            #else:
            #    self.log.error('2  data=%s', data)
                
    def handle_endtag(self,tag): 
        if tag==self.processing:  
            #self.log.error('3  %s', str(tag)+':'+str(self.getdata()))
            #self.log.error('3  map_table=%s', self.map_table)
            self.processing=None 
    def getdata(self): 
        return self.map_table
        

class MyHTMLParser(HTMLParser):
    def __init__(self, env):
        self.env = env
        self.log = env.log
        self.data = []   
        
        self.taglevels=[] 
        self.handledtags=['select','option'] 
        self.processing=None 
        
        self.name = ''        
        HTMLParser.__init__(self)
        self.log.error('MyHTMLParser --')
        
    def handle_starttag(self, tag, attrs):
        self.log.error('Start tag:', tag)
        for attr in attrs:
            self.log.error('     attr:', attr)
            
    def handle_endtag(self, tag):
        self.log.error('End tag  :', tag)

    def handle_data(self, data):
        self.log.error('Data     :', data)
        
    def handle_comment(self, data):
        #print "Comment  :", data
        self.log.error('Comment  :', data)
        
    def handle_entityref(self, name):
        c = unichr(name2codepoint[name])
        #print "Named ent:", c
        self.log.error('Named ent:', c)
        
    def handle_charref(self, name):
        if name.startswith('x'):
            c = unichr(int(name[1:], 16))
        else:
            c = unichr(int(name))
        #print "Num ent  :", c
        self.log.error('Num ent  :', c)
        
    def handle_decl(self, data):
        #print "Decl     :", data
        self.log.error('Decl     :', data)
        

