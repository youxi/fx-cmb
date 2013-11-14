# -*- coding: utf-8 -*-
import re
import urllib
import smtplib
import logging
from google.appengine.api import mail
from google.appengine.ext import ereporter
from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.ext.webapp.util import run_wsgi_app
 
def html2table(html):
    trs = re.findall(r'澳大利亚元.*?欧元', html, re.DOTALL)
    rows = []
    for tr in trs:
        x = re.findall(r'>([^<>]*)(?:</a>)?</td>', tr, re.DOTALL)
        x = map(lambda s: s.strip(), x)
        rows.append(x)
    return rows

##def display():
##    for r in rows:
##        for c in r:
##            print c
##        print

class InitHandler(webapp.RequestHandler): 
    def get(self):            
        url = r'http://fx.cmbchina.com/hq/'
##        html = urllib.urlopen(url).read()
        result = urlfetch.fetch(url)
        if result.status_code == 200:
            html = result.content
            rows = html2table(html)
            
            print 'Content-Type: text/plain'
            print ''
            print 'Hello world'

            haha = rows[0]
            print  '澳元卖出价:',haha[3]
            print  '澳元现汇买入价:',haha[4]
            print  '时间:',haha[6]
            print 
            print  '美元卖出价:',haha[12]
            print  '美元现汇买入价:',haha[13]
            print  '时间:',haha[15]
            print
        else:
            print 'Content-Type: text/plain'
            print ''
            print 'Ohh...Deadline exceeded'

logging.getLogger().setLevel(logging.DEBUG)
ereporter.register_logger()
application = webapp.WSGIApplication([('/', InitHandler)],debug=True)                                      

def main():


    run_wsgi_app(application)

if __name__ == "__main__":
    main()
    
##mailBody = '澳元卖出价:'+ haha[3] + '\n' + '澳元现汇买入价:' + haha[4] + '\n' + '时间:' + haha[6] + '\n\n' + '美元卖出价:' + haha[12] + '\n' + '美元现汇买入价:' + haha[13] + '\n' + '时间:' + haha[15]
##mailBody += '\n'
##print mailBody
##
##mail.send_mail(sender="AUD Rate Update <audcny@fx-cmb.appspotmail.com>",
##              to="AUDRate <audrate@googlegroups.com>",
##              subject="招行澳元汇率提醒: " + haha[3] + ' ' + '[' + haha[6] + ']',
##              body=mailBody)
