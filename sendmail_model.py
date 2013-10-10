# -*- coding: utf-8 -*-

import smtplib
from email.MIMEText import MIMEText

class SendMail(object):

    def __init__(self):
        self.smtp_server = ''
        self.mail_postfix = '@spreadtrum.com'
        self.Task_URL = ''
        self.From = ''
        self.CCList = []
        self.ToList = []
        self.Subject = ''
        self.Content = ''

    def Send_Mail(self):
        try:
            #self.ToList = ['mingjian.liu']
            self.Content = '<html><head><style type="text/css">*{font-size:15px;}</style></head><body>' + self.Content + '</body></html>'
            msg = MIMEText(self.Content.encode('utf-8'), _subtype='html', _charset='utf-8')     

            All_LIST = []
                        
            if self.From  not in self.CCList:
                if '.' in self.From:
                    self.CCList.append(self.From)
            
            for aa in self.CCList:
                if aa not in All_LIST :
                    All_LIST.append(aa)
            for aa in self.ToList:
                if aa not in All_LIST :
                    All_LIST.append(aa)

            self.CCList = [a_item + self.mail_postfix  for a_item in self.CCList]
            self.ToList = [a_item + self.mail_postfix  for a_item in self.ToList]

            msg['From'] = self.From+ self.mail_postfix
            msg['To'] = ','.join(self.ToList) 
            msg['Cc'] = ','.join(self.CCList) 
            msg['Subject'] = self.Subject

            s = smtplib.SMTP()         
            s.connect(self.smtp_server, 25)               
            s.sendmail(msg['From'], All_LIST, msg.as_string()) 
            s.quit() 
        except :
            print "send mail error"
