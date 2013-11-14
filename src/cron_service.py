# -*- coding: utf-8 -*-
import re
import urllib
import smtplib
import logging
import datetime
from google.appengine.api import mail
from google.appengine.ext import ereporter
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.urlfetch_errors import DeadlineExceededError
from google.appengine.api.urlfetch_errors import DownloadError
#===============================================================================
# from boxcargae import BoxcarApi
# from string import Template
#===============================================================================
 
_max_fetch_count = 9

def getfx():
    urlget = r'http://fx.cmbchina.com/hq/'
##    rows = html2table(urllib.urlopen(url).read())
    for count in range(_max_fetch_count):
        try:
            url_result = urlfetch.fetch(url=urlget,deadline=10)
            break
        except DeadlineExceededError:
            logging.debug('Ohh, deadline exceeded, kao!')
        except DownloadError:
            logging.debug('Ohh, download error, kao!')
        
    if url_result.status_code == 200:
        trs = re.findall(r'澳大利亚元.*?欧元', url_result.content, re.DOTALL)
        rows = []
        for tr in trs:
            x = re.findall(r'>([^<>]*)(?:</a>)?</td>', tr, re.DOTALL)
            x = map(lambda s: s.strip(), x)
            rows.append(x)
        return rows[0]
    
##def html2table(html):
##    trs = re.findall(r'澳大利亚元.*?欧元', html, re.DOTALL)
##    rows = []
##    for tr in trs:
##        x = re.findall(r'>([^<>]*)(?:</a>)?</td>', tr, re.DOTALL)
##        x = map(lambda s: s.strip(), x)
##        rows.append(x)
##    return rows

##def display():
##    for r in rows:
##        for c in r:
##            print c
##        print

class CRONServiceHandler(webapp.RequestHandler):
    def get(self):            

        haha = getfx()

        fxHist = fxdb.all()
        fxHist.order('-indexTime')
        lastfx = fxHist.get().audOfferRate       
##        logging.debug(lastfx)
##        logging.debug(haha[3])
        if lastfx > haha[3]:
##            logging.debug('⬇')
            mailSubject = '招行澳元汇率提醒:⬇' + haha[3] + ' ' + '[' + haha[6] + ']'
        elif lastfx < haha[3]:
##            logging.debug('⬆')
            mailSubject = '招行澳元汇率提醒:⬆' + haha[3] + ' ' + '[' + haha[6] + ']'
        else:
##            logging.debug('-')
            mailSubject = '招行澳元汇率提醒:-' + haha[3] + ' ' + '[' + haha[6] + ']'
            
        datestring = (datetime.datetime.utcnow()+datetime.timedelta(hours=+8)).strftime("%Y%m%d%H%M%S")
        fxdb(indexTime=datestring,
             audOfferRate=haha[3],
             audBillBidRate=haha[4],
             audUpdateTime=haha[6],
             usdOfferRate=haha[12],
             usdBillBidRate=haha[13],
             usdUpdateTime=haha[15]).put()
        
        mailBody = '澳元卖出价:'+ haha[3] + '\n' + '澳元现汇买入价:' + haha[4] + '\n' + '时间:' + haha[6] + '\n\n' + '美元卖出价:' + haha[12] + '\n' + '美元现汇买入价:' + haha[13] + '\n' + '时间:' + haha[15]
        mailBody += '\n'
##      print mailBody
        
        mail.send_mail(sender="AUD Rate Update <audcny@fx-cmb.appspotmail.com>",
                      to=["AUDRate <audrate@emaillist.io>","AUDRate <audrate@groups.live.com>"],
                      subject=mailSubject,
                      body=mailBody)
        
        #=======================================================================
        # _api_key = 'CMl59ZQnEXv6y9qxpVa1'
        # _api_sec = 'wz5dCO63okFG2vX08nsOmZQctljxtRLIg3xVW9wS'
        # _your_email = 'neilma@hotmail.com'
        # boxcar = BoxcarApi(_api_key,
        #                    _api_sec,
        #                    'http://img.neoease.org/2011/08/star.jpg')    
        # template = Template('Hey $email this was sent')
        # message = template.substitute(email=_your_email)
        # boxcar.notify(_your_email,
        #               mailSubject,
        #               message,
        #               message_id=int(datetime.datetime.now().strftime('%f')) / 1000)
        #=======================================================================

class fxdb(db.Model):
    indexTime       = db.StringProperty()
    audOfferRate    = db.StringProperty()
    audBillBidRate  = db.StringProperty()
    audUpdateTime   = db.StringProperty()
    usdOfferRate    = db.StringProperty()
    usdBillBidRate  = db.StringProperty()
    usdUpdateTime   = db.StringProperty()

logging.getLogger().setLevel(logging.DEBUG)
ereporter.register_logger()
application = webapp.WSGIApplication([('/cron_service', CRONServiceHandler)],debug=True)                                      

def main():


    run_wsgi_app(application)

if __name__ == "__main__":
    main()  
