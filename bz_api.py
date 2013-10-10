# -*- coding: utf-8 -*-
#

import csv
import os
import re
import mimetypes
import locale
import commands

from sgmllib import SGMLParser
from cStringIO import StringIO
from urlparse import urlsplit, urljoin
from urllib import urlencode
from urllib2 import build_opener, HTTPCookieProcessor, Request
from elementtree import ElementTree
from cookielib import LWPCookieJar, CookieJar


import bz_utils
import bz_gl

#import sys
#reload(sys)  
#sys.setdefaultencoding('utf-8')

COOKIE_FILE = '.bugz_cookie'


class BugzConfig:
    urls = {
        'auth': 'index.cgi',
        'list': 'buglist.cgi',
        'show': 'show_bug.cgi',
        'show_activity': 'show_activity.cgi',
        'attach': 'attachment.cgi',
        'post': 'post_bug.cgi',        
        'modify': 'process_bug.cgi',
        'attach_post': 'attachment.cgi',
        'query': 'query.cgi',
        'browse': 'describecomponents.cgi',
    }        

    headers = {
        'Accept': '*/*',
        'User-agent': '',
    }

    params = {
        'auth': {
        "Bugzilla_login": "",
        "Bugzilla_password": "",
        "GoAheadAndLogIn": "1",
        },

        'post': {
        'product': 'Gentoo Linux',
        'version': 'unspecified',
        'rep_platform': 'All',
        'op_sys': 'Linux',
        'priority': 'P3',
        'bug_severity': 'enhancement',
        'bug_status': 'NEW',
        'assigned_to': '',
        'keywords': '',
        'dependson':'',
        'blocked':'',
        'component': 'Ebuilds',
        # needs to be filled in
        'bug_file_loc': '',
        'short_desc': '',
        'comment': '',
        },

        'attach': {
        'id':''
        },

        'attach_post': {
        'action': 'insert',
        'contenttypemethod': 'manual',
        'bugid': '',
        'description': '',
        'contenttypeentry': 'text/plain',
        'comment': '',
        },

        'show': {
        'id': '',
        'ctype': 'xml'
        },

        'list': {
        #'columnlist': '',
        #'query_format': 'advanced',
        #'short_desc_type': 'allwordssubstr',
        #'short_desc': '',
        #'long_desc_type': 'substring',
        #'long_desc' : '',
        #'bug_file_loc_type': 'allwordssubstr',
        #'bug_file_loc': '',
        #'status_whiteboard_type': 'allwordssubstr',
        #'status_whiteboard': '',
        #'bug_status': [],
        #'bug_severity': [],
        #'priority': [],
        #'emailassigned_to1':'1',        
        #'emailtype1': 'substring',
        #'email1': '',
        #'emailassigned_to2':'1',
        #'emailreporter2':'1',
        #'emailcc2':'1',
        #'emailtype2':'substring',
        #'email2':'',
        #'bugidtype':'include',
        #'bug_id':'',
        #'chfieldfrom':'',
        #'chfieldto':'',#'Now',
        #'cmdtype':'doit',
        #'order': 'Bug Number',
        #'field0-0-0':'noop',
        #'type0-0-0':'noop',
        #'value0-0-0':'',
        #'ctype':'csv',
        },

        'modify': {
        #    'delta_ts': '%Y-%m-%d %H:%M:%S',
        'longdesclength': '1',
        'id': '',
        'newcc': '',
        'removecc': '',  # remove selected cc's if set
        'cc': '',        # only if there are already cc's
        'bug_file_loc': '',
        'bug_severity': '',
        'bug_status': '',
        'op_sys': '',
        'priority': '',
        'version': '',
        'target_milestone': '',
        'rep_platform': '',
        'product':'',
        'component': '',
        'short_desc': '',
        'status_whiteboard': '',
        'keywords': '',
        'dependson': '',
        'blocked': '',
        'knob': ('none', 'assigned', 'resolve', 'duplicate', 'reassign'),
        'resolution': '', # only valid for knob=resolve
        'dup_id': '',     # only valid for knob=duplicate
        'assigned_to': '',# only valid for knob=reassign
        'form_name': 'process_bug',
        'comment':''        
        }

    }

    choices = {
        'status': {
        'unconfirmed': 'UNCONFIRMED',
        'new': 'NEW',
        'assigned': 'ASSIGNED',
        'reopened': 'REOPENED',
        'resolved': 'RESOLVED',
        'verified': 'VERIFIED',
        'closed':   'CLOSED'
        },

        'order': {
        'number' : 'Bug Number',
        'assignee': 'Assignee',
        'importance': 'Importance',
        'date': 'Last Changed'
        },

        'columns': [
        'bugid',
        'product',        
        'component',
        'bug_severity',
        'bug_status',
        'short_desc',
        'assigned_to',
        'cf_base_on_ver',
        'cf_fix_on_ver',
        'reporter',
        'cf_come_from',
        'changeddate',
        'opendate',
        'cf_assigneddate',
        'cf_rootcauseddate',
        'cf_fixeddate',
        'cf_closeddate'
        ],

        'resolution': {
        'fixed': 'FIXED',
        'invalid': 'INVALID',
        'duplicate': 'DUPLICATE',
        'lated': 'LATER',
        'needinfo': 'NEEDINFO',
        'wontfix': 'WONTFIX',
        },

        'severity': [
        'blocker',
        'critical',
        'major',
        'normal',
        'minor',
        'trivial',
        'enhancement',
        ],

        'priority': {
        1:'P1',
        2:'P2',
        3:'P3',
        4:'P4',
        5:'P5',
        }
        
    }


#
# Global configuration
#

try:
    config
except NameError:
    config = BugzConfig()



#
# Override the behaviour of elementtree and allow us to
# force the encoding to ISO-8859-1
#

class ForcedEncodingXMLTreeBuilder(ElementTree.XMLTreeBuilder):
    def __init__(self, html = 0, target = None, encoding = None):
        try:
            from xml.parsers import expat
        except ImportError:
            raise ImportError(
                "No module named expat; use SimpleXMLTreeBuilder instead"
                )
        self._parser = parser = expat.ParserCreate(encoding, "}")
        if target is None:
            target = ElementTree.TreeBuilder()
        self._target = target
        self._names = {} # name memo cache
        # callbacks
        parser.DefaultHandlerExpand = self._default
        parser.StartElementHandler = self._start
        parser.EndElementHandler = self._end
        parser.CharacterDataHandler = self._data
        # let expat do the buffering, if supported
        try:
            self._parser.buffer_text = 1
        except AttributeError:
            pass
        # use new-style attribute handling, if supported
        try:
            self._parser.ordered_attributes = 1
            self._parser.specified_attributes = 1
            parser.StartElementHandler = self._start_list
        except AttributeError:
            pass
        encoding = None
        if not parser.returns_unicode:
            encoding = "utf-8"
        # target.xml(encoding, None)
        self._doctype = None
        self.entity = {}




#
# bugzilla interface
#

class Bugz(object):
    
    def __init__(self, env, base, user = None, password = None, forget = False,
                 always_auth = False):
        self.env = env
        self.log = env.log
        self.base = base
        
        scheme, self.host, self.path, query, frag  = urlsplit(self.base)
        self.authenticated = False

        #cookie_file = os.path.join(os.environ['HOME'], COOKIE_FILE)
        cookie_file = '/home/'+COOKIE_FILE
        try:            
            self.cookiejar = LWPCookieJar(cookie_file)
            if forget:
                try:
                    self.cookiejar.load()
                    self.cookiejar.clear()
                    self.cookiejar.save()
                    os.chmod(self.cookiejar.filename, 0700)
                except IOError:
                    pass
        except KeyError:
            #self.log.error('Unable to save session cookies in %s' % cookie_file)
            self.cookiejar = CookieJar(cookie_file)

        self.opener = build_opener(HTTPCookieProcessor(self.cookiejar))
        self.user = user
        self.password = password
        self.forget = forget
        self.always_auth = always_auth

        if always_auth:
            self.auth()

        self.f1_map_table = []
        self.o1_map_table = []

        self.get_bugz_init()
    
    def get_bugz_init(self):
        req_params = 'format=advanced'
        req_url = urljoin(self.base,  config.urls['query'])        
        req_url += '?' + req_params        
        req = Request(req_url, None, config.headers)
        resp = self.opener.open(req)        
        results = []
        content = resp.read()

        from BeautifulSoup import BeautifulSoup        
        soup = BeautifulSoup(''.join(content)) 
        
        self.log.error("get_bugz_init 1")
        self.f1_map_table = self.Btag_select2('f1', soup)
        self.o1_map_table = self.Btag_select2('o1', soup)

        self.all_product = self.Btag_select3('product', soup) 
        self.all_component = self.Btag_select3('component', soup)
        self.all_status = self.Btag_select3('bug_status', soup)
        self.all_severity = self.Btag_select3('bug_severity', soup)

        self.field_s = self.Btag_select3('f1', soup)
        self.operation_s = self.Btag_select('o1', content)  
        self.log.error("get_bugz_init 2")
        
    def get_input(self, prompt):
        """Default input handler. Expected to be override by the
        UI implementing subclass.

        @param prompt: Prompt message
        @type  prompt: string
        """
        return ''

    def auth(self):
        """Authenticate a session.
        """
        # check if we need to authenticate
        if self.authenticated:
            return

        # try seeing if we really need to request login
        try:
            self.cookiejar.load()
        except IOError:
            pass
        
        #self.log.error("Auth base=%s " % self.base)
        #self.log.error("Auth %s " % config.urls['auth'])
        
        #req_url = urljoin(self.base, config.urls['auth'])
        req_url = self.base
        req_url += config.urls['auth']
        req_url += '?GoAheadAndLogIn=1'

        #self.log.error("Auth req_url=%s " % req_url)
        req = Request(req_url, None, config.headers)
        
        resp = self.opener.open(req)
        re_request_login = re.compile(r'<title>Log in to Bugzilla</title>')
        if not re_request_login.search(resp.read()):
            self.log.error('Already logged in.')
            self.authenticated = True
            return

        # prompt for username and password if we were not supplied with it
        if not self.user or not self.password:
            import getpass
            self.log.error('No username or password given.')
            self.user = self.get_input('Username: ')
            self.password = getpass.getpass()

        # perform login
        qparams = config.params['auth'].copy()
        qparams['Bugzilla_login'] = self.user
        qparams['Bugzilla_password'] = self.password

        req_url = urljoin(self.base, config.urls['auth'])
        req = Request(req_url, urlencode(qparams), config.headers)
        resp = self.opener.open(req)
        if resp.info().has_key('Set-Cookie'):
            self.authenticated = True
            #if not self.forget:
            #    self.cookiejar.save()
            #    os.chmod(self.cookiejar.filename, 0700)                
            #self.log.error("Auth succ %s " % self.user)
            return True
        else:
            self.log.error("Auth fail %s " % self.user)
            raise RuntimeError("Failed to login")

    def BG_SearchUrl2(self, a_row=None, \
                bug_status=None, component=None, \
                columnlist=None, \
                a_assigned_to = None, a_reporter = None, \
                query='', comments = False, order = 'number'):
        qparams = config.params['list'].copy()
        qparams['columnlist'] = ['bug_id']
        
        
        UIFields=bz_gl.gl_QueryUIFields
        CheckboxFields=bz_gl.gl_QueryCheckboxFields 
        MultiInputFields=bz_gl.gl_QueryUIMultiInputFields
        BugzFields = UIFields+CheckboxFields+MultiInputFields+bz_gl.gl_advance_bz_field
        
        assigned_tos = [] 
        reporters = []
        is_null_flag = True 

        #f1_map_table = self.Btag_select2('f1')
        #self.f1_map_table
        #o1_map_table = self.Btag_select2('o1')
        if a_row is not None:        
            for a_field in BugzFields:
                #self.log.error("BG_SearchUrl2 a_field=%s, %s",a_field, a_row[a_field])         
                if a_field == 'name' \
                        or a_field == 'ibugz_col' \
                        or a_field == 'custom_statics':
                    continue
                elif a_field == 'columnlist':
                    if a_row[a_field] is not None:
                        qparams[a_field] += a_row[a_field]
                elif a_field == 'f50' \
                            or a_field == 'f500' \
                            or a_field == 'f51' \
                            or a_field == 'f99' \
                            or a_field == 'f151' \
                            or a_field == 'f199':
                    qparams[a_field] = a_row[a_field]
                    is_null_flag = False                         
                elif re.match(r"[f]\d", a_field) \
                            or a_field == 'chfield':
                        is_null_flag = False  
                        for a_map in self.f1_map_table:
                            if a_row[a_field] == a_map['ui']:
                                if a_field == 'chfield':
                                    qparams['f21'] = a_map['db']
                                    qparams['f22'] = a_map['db']
                                    qparams['o21'] = 'greaterthaneq'
                                    qparams['o22'] = 'lessthaneq'
                                else:
                                    #if a_field == 'f1':
                                    #    self.log.error("BG_SearchUrl2 qparams[a_field]=%s",qparams[a_field])                       
                                                        
                                    qparams[a_field] = a_map['db']
                                    #self.log.error("BG_SearchUrl2 qparams[a_field]=%s",qparams[a_field])                       
                        
                elif re.match(r"[o]\d", a_field):                         
                    if a_row[a_field] != '---' and a_row[a_field] != '':
                        is_null_flag = False 
                        for a_map in self.o1_map_table:
                            if a_row[a_field] == a_map['ui']:
                                qparams[a_field] = a_map['db']
                elif a_field == 'chfieldfrom':
                    qparams['v21'] = a_row[a_field]
                elif a_field == 'chfieldto':                    
                    qparams['v22'] = a_row[a_field] 
                elif a_field == 'product_ower':     
                    #self.log.error("BG_SearchUrl2 [product_ower]=%s",a_row[a_field])
                    if len(a_row[a_field]) >0:
                        qparams['v30'] = ''
                        qparams['f30'] = 'commenter'
                        qparams['o30'] = 'anywords' #contains any of the words    
                        for idx,a in enumerate(a_row[a_field]):                         
                            qparams['v30'] += a+' '                            
                        qparams['v31'] = a_row['TouchStart']
                        qparams['f31'] = 'delta_ts'
                        qparams['o31'] = 'greaterthaneq'   
                        qparams['v32'] = a_row['TouchEnd']
                        qparams['f32'] = 'delta_ts'
                        qparams['o32'] = 'lessthaneq'
                        
                elif a_row[a_field] is not None \
                            and a_row[a_field] != '' \
                            and a_row[a_field] != [] \
                            and a_row[a_field] != '---':
                    qparams[a_field] = a_row[a_field]
                    is_null_flag = False                    
                #self.log.error("BG_SearchUrl2 is_null_flag1=%s, %s",is_null_flag, a_field)         
        #self.log.error("BG_SearchUrl2 is_null_flag2=%s ",is_null_flag)  
        if bug_status is not None:
            qparams['bug_status'] = bug_status or [] 
            is_null_flag = False
        if component is not None:
            qparams['component'] = component or [] 
            is_null_flag = False
        if columnlist is not None:
            qparams['columnlist'] = qparams['columnlist']+columnlist

        if a_assigned_to is not None:
            #assigned_tos = [assigned_to]
            qparams['f1'] = 'assigned_to'
            qparams['o1'] = 'equals'
            qparams['v1'] = a_assigned_to + '@spreadtrum.com'
            is_null_flag = False  
            
        #if reporter is not None:
        #    reporters = [reporter]
        #    is_null_flag = False
 
        #if comments:
        #    qparams['long_desc'] = query
        #else:
        #    qparams['short_desc'] = query
            
        #if order is None or order == '' or order == 'number':
        #    qparams['order'] = config.choices['order'].get(order, 'Bug Number')
        #else:
        #    qparams['order'] = order   
        #self.log.error("BG_SearchUrl2 is_null_flag3=%s ",is_null_flag)                         
        if is_null_flag == False:   
            qparams['columnlist'] = bz_utils.tuple2string(qparams['columnlist'], tag=',')
            qparams['ctype'] = 'csv'
        else:
            #self.log.error("BG_SearchUrl2 qparams=%s ",qparams)
            return None
        
        req_params = urlencode(qparams, True)
        req_url = urljoin(self.base, config.urls['list'])        
        req_url += '?' + req_params
        self.log.error("BG_SearchUrl2 req_url=%s " % req_url)
        return req_url

    def BG_SearchUrl(self, query, comments = False, order = 'number',
               assigned_to = None, reporter = None, cc = None,
               whiteboard = None, keywords = None,
               status = [], severity = [], priority = [], component = [],
               product =[], cf_come_from=[], cf_base_on_ver='', cf_fix_on_ver='',
               collist = None):
        qparams = config.params['list'].copy()

        if comments:
            qparams['long_desc'] = query
        else:
            qparams['short_desc'] = query
            
        if order is None or order == '' or order == 'number':
            qparams['order'] = config.choices['order'].get(order, 'Bug Number')
        else:
            qparams['order'] = order    
            
        qparams['bug_severity'] = severity or []
        qparams['product'] = product or []
        qparams['component'] = component or ''        
        qparams['priority'] = priority or []
        qparams['bug_status'] = status or []
        qparams['cf_come_from'] = cf_come_from or []        
        #qparams['status_whiteboard'] = whiteboard or ''
        #qparams['keywords'] = keywords or ''        

        # hoops to jump through for emails, since there are
        # only two fields, we have to figure out what combinations
        # to use if all three are set.
        unique = list(set([assigned_to, cc, reporter]))
        unique = [u for u in unique if u]
        if len(unique) < 3:
            for i in range(len(unique)):
                e = unique[i]
                n = i + 1
                qparams['email%d' % n] = e
                qparams['emailassigned_to%d' % n] = int(e == assigned_to)
                qparams['emailreporter%d' % n] = int(e == reporter)
                qparams['emailcc%d' % n] = int(e == cc)
        else:
            raise AssertionError('Cannot set assigned_to, cc, and '
                                 'reporter in the same query')
                      
        qparams['columnlist'] = bz_utils.tuple2string(collist, tag=',')

        req_params = urlencode(qparams, True)
        req_url = urljoin(self.base, config.urls['list'])        
        req_url += '?' + req_params
        #self.log.error("Bugz Search req_url=%s " % req_url)

        return req_url

    def BG_Search(self, req_url, results, collist=None):            
        #self.log.error("Bugz Search req_url=\n%s",req_url)
        req = Request(req_url, None, config.headers)
        resp = self.opener.open(req)
        
        #if collist is None:# or collist == []:
        #    columns = config.choices['columns']
        #else:
        #    columns = collist
        if collist is None:
            columns = ['bug_id']
        else:
            columns = ['bug_id'] + collist
        
        #results = []
        index = 0
        #self.log.error("Bugz Search collist=\n%s",collist)
        for row in csv.reader(resp):            
            fields = {}  
            for i in range(len(row)):
                #self.log.error("Bugz Search i=%s,row[i]=%s,columns[i]=%s ",i,row[i], columns[i])
                fields[columns[i]] = row[i]
            if index > 0:
                results.append(fields)
            index += 1

        #return results[1:]

    def BG_GetById(self, bugid, results):
        """Get an ElementTree representation of a bug.
        @type  bugid: int
        @rtype: ElementTree
        """
        buginfo = Bugz.BG_Get(self, bugid)
        if not buginfo:
            return None

        a_item = {}        
        FIELDS = bz_gl.gl_srch_bugzdb_id_collist 
        #FIELDS.remove('changeddate')
		#
        #FIELDS.remove('opendate')
        #FIELDS.remove('cf_assigneddate')
        #FIELDS.remove('cf_rootcauseddate')
        #FIELDS.remove('cf_fixeddate')
        #FIELDS.remove('cf_closeddate')      
        
        FIELDS_MULTI = ('blocked', 'dependson')
        
        #results = []        
        for field in FIELDS:
            try:
                a_item[field] = buginfo.find('.//%s' % field).text
            except:
                pass
        results.append(a_item)
        #return results
        

    def BG_Get(self, bugid):
        """Get an ElementTree representation of a bug.
        @type  bugid: int
        @rtype: ElementTree
        """
        qparams = config.params['show'].copy()
        qparams['id'] = bugid

        req_params = urlencode(qparams, True)
        req_url = urljoin(self.base,  config.urls['show'])
        req_url += '?' + req_params
        req = Request(req_url, None, config.headers)
        self.log.error('BG_Get req_url=%s', req_url)
        resp = self.opener.open(req)

        fd = StringIO(resp.read())
        # workaround for ill-defined XML templates in bugzilla 2.20.2
        parser = ForcedEncodingXMLTreeBuilder(encoding = 'ISO-8859-1')
        etree = ElementTree.parse(fd, parser)
        self.log.error('BG_Get etree=%s', etree)
        
        bug = etree.find('.//bug')
        if bug and bug.attrib.has_key('error'):
            return None
        else:
            return etree

    def Bugz_GetBrowse(self, a_product):
        req_params = 'product='+a_product
        req_url = urljoin(self.base,  config.urls['browse'])        
        req_url += '?' + req_params        
        req = Request(req_url, None, config.headers)
        resp = self.opener.open(req)  
        
        fd = StringIO(resp.read())
        content = fd.getvalue()      
        return content

    def Bugz_GetHistory(self, bugid):
        qparams = config.params['show'].copy()
        qparams['id'] = bugid
        req_params = urlencode(qparams, True)
        req_url = urljoin(self.base,  config.urls['show_activity'])
        req_url += '?' + req_params
        req = Request(req_url, None, config.headers)
        resp = self.opener.open(req)

        fd = StringIO(resp.read())
        content = fd.getvalue()
        return content
        # workaround for ill-defined XML templates in bugzilla 2.20.2
        #parser = ForcedEncodingXMLTreeBuilder(encoding = 'ISO-8859-1')
        #etree = ElementTree.parse(fd, parser)
        #self.log.error('BG_GetHistory etree=%s', etree)
        
        #bug = etree.find('.//bug')
        #if bug and bug.attrib.has_key('error'):
        #    return None
        #else:
        #    return etree




    def BG_Modify(self, bugid, title = None, comment = None, url = None,
               status = None, resolution = None, 
               assigned_to = None, duplicate = 0,
               priority = None, severity = None,
               add_cc = [], remove_cc = [],
               add_dependson = [], remove_dependson = [],
               add_blocked = [], remove_blocked = [],
               whiteboard = None, keywords = None):
        """Modify an existing bug

        @param bugid: bug id
        @type  bugid: int
        @keyword title: new title for bug
        @type    title: string
        @keyword comment: comment to add
        @type    comment: string
        @keyword url: new url
        @type    url: string
        @keyword status: new status (note, if you are changing it to RESOLVED, you need to set {resolution} as well.
        @type    status: string
        @keyword resolution: new resolution (if status=RESOLVED)
        @type    resolution: string
        @keyword assigned_to: email (needs to exist in bugzilla)
        @type    assigned_to: string
        @keyword duplicate: bug id to duplicate against (if resolution = DUPLICATE)
        @type    duplicate: int
        @keyword priority: new priority for bug
        @type    priority: string
        @keyword severity: new severity for bug
        @type    severity: string
        @keyword add_cc: list of emails to add to the cc list
        @type    add_cc: list of strings
        @keyword remove_cc: list of emails to remove from cc list
        @type    remove_cc: list of string.
        @keyword add_dependson: list of bug ids to add to the depend list
        @type    add_dependson: list of strings
        @keyword remove_dependson: list of bug ids to remove from depend list
        @type    remove_dependson: list of strings
        @keyword add_blocked: list of bug ids to add to the blocked list
        @type    add_blocked: list of strings
        @keyword remove_blocked: list of bug ids to remove from blocked list
        @type    remove_blocked: list of strings

        @keyword whiteboard: set status whiteboard
        @type    whiteboard: string
        @keyword keywords: set keywords
        @type    keywords: string

        @return: list of fields modified.
        @rtype: list of strings
        """
        if not self.authenticated:
            self.auth()
            
        buginfo = Bugz.BG_Get(self, bugid)
        if not buginfo:
            return False

        import time
        modified = []
        qparams = config.params['modify'].copy()
        qparams['id'] = bugid
        qparams['knob'] = 'none'
        
        # copy existing fields
        FIELDS = ('bug_file_loc', 'bug_severity', 'short_desc', 'bug_status',
                  'status_whiteboard', 'keywords', 
                  'op_sys', 'priority', 'version', 'target_milestone',
                  'assigned_to', 'rep_platform', 'product', 'component')

        FIELDS_MULTI = ('blocked', 'dependson')
        
        for field in FIELDS:
            try:
                qparams[field] = buginfo.find('.//%s' % field).text
            except:
                pass

        for field in FIELDS_MULTI:
            qparams[field] = [d.text for d in buginfo.findall('.//%s' % field)]

        # set 'knob' if we are change the status/resolution
        # or trying to reassign bug.
        if status:
            status = status.upper()
        if resolution:
            resolution = resolution.upper()
            
        if status == 'RESOLVED' and status != qparams['bug_status']:
            qparams['knob'] = 'resolve'
            if resolution:
                qparams['resolution'] = resolution
            else:
                qparams['resolution'] = 'FIXED'
                
            modified.append(('status', status))
            modified.append(('resolution', qparams['resolution']))
        elif status == 'REOPENED' and status != qparams['bug_status']:
            qparams['knob'] = 'reopen'
            modified.append(('status', status))
        elif status == 'VERIFIED' and status != qparams['bug_status']:
            qparams['knob'] = 'verified'
            modified.append(('status', status))            
        elif status == 'CLOSED' and status != qparams['bug_status']:
            qparams['knob'] = 'closed'
            modified.append(('status', status))                        
        elif duplicate:
            qparams['knob'] = 'duplicate'
            qparams['dup_id'] = duplicate
            modified.append(('status', 'RESOLVED'))
            modified.append(('resolution', 'DUPLICATE'))   
        elif assigned_to:
            qparams['knob'] = 'reassign'
            qparams['assigned_to'] = assigned_to
            modified.append(('assigned_to', assigned_to))

        # setup modification of other bits
        if comment:
            qparams['comment'] = comment
            modified.append(('comment', ellipsis(comment, 60)))
            
        if title:
            qparams['short_desc'] = title or ''
            modified.append(('title', title))
        if url != None:
            qparams['bug_file_loc'] = url
            modified.append(('url', url))
        if severity != None:
            qparams['bug_severity'] = severity
            modified.append(('severity', severity))
        if priority != None:
            qparams['priority'] = priority
            modified.append(('priority', priority))

        # cc manipulation
        if add_cc != None:
            qparams['newcc'] = ', '.join(add_cc)
            modified.append(('newcc', qparams['newcc']))
        if remove_cc != None:
            qparams['cc'] = remove_cc
            qparams['removecc'] = 'on'
            modified.append(('cc', remove_cc))

        # bug depend/blocked manipulation
        changed_dependson = False
        changed_blocked = False
        if remove_dependson:
            for bug_id in remove_dependson:
                qparams['dependson'].remove(str(bug_id))
                changed_dependson = True
        if remove_blocked:
            for bug_id in remove_blocked:
                qparams['blocked'].remove(str(bug_id))
                changed_blocked = True
        if add_dependson:
            for bug_id in add_dependson:
                qparams['dependson'].append(str(bug_id))
                changed_dependson = True                
        if add_blocked:
            for bug_id in add_blocked:
                qparams['blocked'].append(str(bug_id))
                changed_blocked = True                

        qparams['dependson'] = ','.join(qparams['dependson'])
        qparams['blocked'] = ','.join(qparams['blocked'])
        if changed_dependson:
            modified.append(('dependson', qparams['dependson']))
        if changed_blocked:
            modified.append(('blocked', qparams['blocked']))

        if whiteboard != None:
            qparams['status_whiteboard'] = whiteboard
            modified.append(('status_whiteboard', whiteboard))
        if keywords != None:
            qparams['keywords'] = keywords
            modified.append(('keywords', keywords))

        req_params = urlencode(qparams, True)
        req_url = urljoin(self.base, config.urls['modify'])
        self.log.error('modify: req_url = %s,req_params = %s,headers = %s, ', req_url, req_params, config.headers)
        req = Request(req_url, req_params, config.headers)
        self.log.error('modify: req = %s ', req)

        try:
            resp = self.opener.open(req)
            self.log.error('modify: resp = %s ', resp)
            return modified
        except:
            return []

    def Btag_select(self, search_key, content):      
        results = []
        listname = ListName(self.env, search_key)
        listname.feed(content)
        for text in listname.data:
            #if search_key == 'o1':
            if 0:
                if 'string' in text \
                        or 'equal' in text:
                    results.append(text)
                else:
                    continue                    
            else:
                results.append(text)
	                
        return results     

    def Btag_select3(self, search_key, soup):        
        results = []
        
        tag_select = soup.find('select', id=search_key) 
        options = tag_select.findAll('option')
        from HTMLParser import HTMLParser
        import urllib
        html_parser = HTMLParser()
        for a_option in options: 
            text = ''.join(a_option.find(text=True))
            text = urllib.unquote(html_parser.unescape(text))
            #self.log.error('%s', text)   
            text = "".join(text.split())
            
            if search_key == 'product':
                #if text.find('HW_') != -1:#'HW_'
                if 'HW_' in text:
                    #self.log.error('%s', text) 
                    continue
                #if item.find('SC') != -1:
                #    results.append(item)
                else:
                    results.append(text)
            elif search_key == 'f1':
                #if 'Attachment' in text \
                #        or 'Date' in text \
                #        or 'date' in text \
                #        or 'Comment' in text \
                #        or text == 'OS' \
                #        or text == '%Complete' \
                #        or text == 'Hardware':
                        #or text in bz_gl.gl_StringFilds:
                #    continue
                #else:
                    results.append(text)  
            #elif search_key == 'component':#'PS-'
            #    results.append(item)
                #if item.find('BP-PS-') != -1 \
                #        or item.find('SH-PS-') != -1 \
                #        or item.find('SP-PS-') != -1:
                #    continue                
                #if item.find('PS-') != -1:
                #    results.append(item)                   
            else:
                results.append(text)
	                
        return results     
 

    def Btag_select2(self, id, soup):
        results = []
        
        tag_select = soup.find('select', {"name" : id}) 
            
        #self.log.error('Btag_select2: tag_select= %s',tag_select)
        options = tag_select.findAll('option')
        from HTMLParser import HTMLParser
        import urllib
        html_parser = HTMLParser()
        for a_option in options: 
            a_map={}                  
            #self.log.error('Btag_select2: %s',a_option)
            text = ''.join(a_option.find(text=True))
            text = urllib.unquote(html_parser.unescape(text))
            if id == 'f1':
                text = ' '.join(text.split())             
            if text != '---':
                a_map['ui'] = text
                #self.log.error('Btag_select2: ui=%s',a_map['ui']) 
                res = re.findall(r'value=(.*?)>', str(a_option))
                a_map['db'] = res[0].replace('"','')                
                #self.log.error('Btag_select2: db=%s',a_map['db']) 
                results.append(a_map)
        return results   

    def S_ProductOwers(self, a_product):  
        html_string = Bugz.Bugz_GetBrowse(self, a_product)
        from BeautifulSoup import BeautifulSoup        
        soup = BeautifulSoup(''.join(html_string)) 
        details = {}    
        
        table = soup.find('tbody') 
        rows = table.findAll('tr')         
        for tr in rows:
          tds = tr.findAll('td')          
          len_td = len(tds)              
          if len_td == 2:
              #for td in tds:
              for idx,td in enumerate(tds):
                  #self.log.error('2text td=%s', td)                  
                  if idx == 0:
                      a_s = td.findAll('a')
                      #self.log.error('a_s=%s', a_s)  
                      if len(a_s) == 1:  
                          for a_a in a_s:
                              tmp = a_a.find(text=True)                          
                              a_comp = ''.join(tmp)
                              #a_comp = "".join(a_comp.split())
                  elif idx == 1:
                      spans = td.findAll('span')
                      len_spans = len(spans) 
                      if len_spans == 2:                      
                          for idx,a_span in enumerate(spans):
                              if idx == 1:
                                  #self.log.error('2text a_span=%s', a_span) 
                                  tmp = a_span.find(text=True)                          
                                  a_ower = ''.join(tmp)
                                  a_ower = "".join(a_ower.split())  
                                  #self.log.error('a_comp=%s,a_ower=%s', a_comp,a_ower)
                                  details[a_comp] = a_ower
                                  #self.log.error('a_ower=%s', a_ower)
          #elif len_td == 1:#a_comp
          #    a_comp = ''.join(tds[0].find(text=True))
          #    a_comp = "".join(a_comp.split())
          #    #self.log.error('a_comp %s', a_comp)
          #    details[a_comp] = a_ower
          else:
              continue
               
        #self.log.error('F_TouchDetail:bugid=%s, a_name=%s,%s', bugid, a_name, details[a_name])  
        return details
        

    def F_CrTotalNum(self, component):  
        result = []
        #query_url = self.BG_SearchUrl('', component = component)  
        query_url = self.BG_SearchUrl2(component = component)
        self.BG_Search(query_url, result) 
        return len(result)

    def F_ChangedataToNow(self, changeddate):  
        from datetime import datetime, timedelta
        
        time1 = bz_utils.timestring2seconds(changeddate)  
        Now = datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')
        time2 = bz_utils.timestring2seconds(Now)
        delta = bz_utils.deltatime_day(time2, time1)
        return delta



    def F_TouchDetail(self, bugid, product_ower,s,e): 
        html_string = Bugz.Bugz_GetHistory(self, bugid)
        from BeautifulSoup import BeautifulSoup        
        soup = BeautifulSoup(''.join(html_string)) 
        #env.log.error('_P_Debug: %s', soup.prettify())
        table = soup.find('table', cellpadding='4') 
        if table is None:
            return (0, '')
        rows = table.findAll('tr')
        
        details = {}        
        s_count = 0
        for a_name in product_ower:
            details[a_name] = 0 #html_string.count(a_name)
            #self.log.error('F_TouchDetail:bugid=%s, a_name=%s,%s', bugid, a_name, details[a_name])
            for tr in rows:
              cols = tr.findAll('td')
              if len(cols) == 5:
                  who = "".join(''.join(cols.pop(0).find(text=True)).split())
                  when = ("".join(''.join(cols.pop(0).find(text=True)).split()))[0:10]#re.findall(r".CST$", text)
                  #self.log.error('F_TouchCount:[%s,%s]', who, when)
                  if who == (a_name+'&#64;spreadtrum.com') \
                          and when>=s and when<=e:
                      details[a_name] += 1   
                      s_count += 1
                      
            #self.log.error('F_TouchDetail:bugid=%s, a_name=%s,%s', bugid, a_name, details[a_name])  
        detail_str = ''
        for (k,v) in  details.items(): 
            #self.log.error('%s: %s', k, v)
            detail_str += (k+':'+str(v)+' ')
        self.log.error('F_TouchDetail:bugid=%s,%s,%s', bugid, s_count, detail_str)
        return (s_count, detail_str)


    def F_NeedInfoCount(self, bugid):   
        html_string = Bugz.Bugz_GetHistory(self, bugid)
        #self.log.error('F_NeedInfoCount:172621 Assigned_count=%s, Assignee_count=%s, %s', Assigned_count, Assignee_count, ProcAnalysisAssignee_count)       
        s_count = html_string.count('NeedInfoDate')
        if s_count > 0:
            s_count = s_count
        else:
            s_count = 0
        return s_count
        
    def F_NeedInfoDetail(self, bugid):   
        details = {}
        owers = []
        html_string = Bugz.Bugz_GetHistory(self, bugid)
        from BeautifulSoup import BeautifulSoup        
        soup = BeautifulSoup(''.join(html_string)) 
        #env.log.error('_P_Debug: %s', soup.prettify())

        table = soup.find('table', cellpadding='4') 
        if table is None:
            return ''
        rows = table.findAll('tr')
        for tr in rows:
          cols = tr.findAll('td')
          len_col = len(cols)
          if len_col == 3:
              continue
          #for td in cols:
          ower = ''
          for idx,td in enumerate(cols):
              #self.log.error('1 %s', td)
              text = ''.join(td.find(text=True))
              #self.log.error('1 %s', text)   
              text = "".join(text.split())
              if idx == 0:
                  ower = text.replace('&#64;spreadtrum.com','')
              elif idx == 4 and text == 'Need_Info':
                  #self.log.error('%s: %s', ower, text)
                  if ower not in owers:                       
                      details[ower] = 1 
                      owers.append(ower)
                  else:
                      details[ower] += 1          
        
        detail_str = ''
        for (k,v) in  details.items(): 
            #self.log.error('%s: %s', k, v)
            detail_str += (k+':'+str(v)+' ')
        return detail_str
        

     
    def F_ChangeOwnerDetail(self, bugid): 
        html_string = Bugz.Bugz_GetHistory(self, bugid)
        from BeautifulSoup import BeautifulSoup        
        soup = BeautifulSoup(''.join(html_string)) 
        table = soup.find('table', cellpadding='4') 
        if table is None:
            return (0, '')
        rows = table.findAll('tr')
             
        s_count = 0
        detail_str = ''
        for tr in rows:
            cols = tr.findAll('td')
            #self.log.error('F_ChangeOwnerDetail:%s', cols)
            if len(cols) == 3:                
                what = "".join(''.join(cols.pop(0).find(text=True)).split())
                if what == 'Assignee':
                    Removed = ("".join(''.join(cols.pop(0).find(text=True)).split())).replace('&#64;spreadtrum.com','')
                    Added = ("".join(''.join(cols.pop(0).find(text=True)).split())).replace('&#64;spreadtrum.com','')                  
                    detail_str += Removed + '->' + Added + ' ' 
                    s_count += 1            
            elif len(cols) == 5:  
                who = "".join(''.join(cols.pop(0).find(text=True)).split())
                when = ("".join(''.join(cols.pop(0).find(text=True)).split()))[0:10]#re.findall(r".CST$", text)            
                what = "".join(''.join(cols.pop(0).find(text=True)).split())
                if what == 'Assignee':
                    Removed = ("".join(''.join(cols.pop(0).find(text=True)).split())).replace('&#64;spreadtrum.com','')
                    Added = ("".join(''.join(cols.pop(0).find(text=True)).split())).replace('&#64;spreadtrum.com','')                  
                    detail_str += Removed + '->' + Added + ' ' 
                    s_count += 1                    

        self.log.error('F_ChangeOwnerDetail:bugid=%s,%s,%s', bugid, s_count, detail_str)
        return (s_count, detail_str)


class ListName(SGMLParser):
    def __init__(self, env, srch_key):
        SGMLParser.__init__(self)
        self.product_data = []
        self.component_data = []
        self.is_select = ""
        #self.is_a = ""
        self.name = ''
        self.env = env
        self.log = env.log 
        self.srch_key = srch_key
        self.data = []
        
    def start_select(self, attrs):
        self.is_select = 1
        #self.is_a = 1
        
        #self.name = [v for k,v in attrs if k == 'name']
        for k,v in attrs:
            #self.log.error('start_select: k=%s,v=%s',k, v)  
            if k == 'name':#<select name="component" id="component" multiple="multiple" size="7">
                #v = 
                self.name = v
                #self.log.error('start_select: self.name=%s',self.name)  
            #elif k == 'id':
            #    self.name = v
            #    self.log.error('start_select,name=%s',v)
        #if self.name !:
        #    self.data.extend(href)
            
    def end_select(self):
        self.is_select = ""
        #self.is_a = ""
        
    def handle_data(self, text):
        if self.is_select:
            #self.log.error('handle_data: component name=%s,srch_key=%s',self.name, self.srch_key)  
            if self.name == self.srch_key:                
                #self.log.error('handle_data: name=%s,text=%s',self.name, text)  
                text = text.split('\n')[0]
                if text != '':
                    #self.log.error('handle_data: product name=%s,text=%s',self.name, text)
                    self.data.append(text) 
            #elif self.name == 'component':
            #    text = text.split('\n')[0]
            #    if text != '':           
            #        self.component_data.append(text)


def bz_connect(env):
        #loginer = req.session.sid
        url = bz_gl.gl_bugz_url #'http://10.0.6.58/bugzilla/' #'http://172.16.0.58/bugzilla/'
        user = 'song.shan@spreadtrum.com'
        password = '123456'
        bugid = '100402'
                
        bugz = Bugz( env, url, user = user, password = password, forget = False,
                 always_auth = True)
        return bugz
        
#
# Auxillary functions 
#

def ellipsis(text, length):
    if len(text) > length:
        return text[:length-4] + "..."
    else:
        return text        
