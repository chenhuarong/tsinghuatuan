#-*- coding:utf-8 -*-
import urllib
import hashlib
import xml.etree.ElementTree as ET
from django.utils.encoding import smart_str
from weixinlib.settings import WEIXIN_TOKEN
from queryhandler.tickethandler import *
from queryhandler.query_transfer import get_information_response

handler_list = [
    {'check': check_book_event,             'response': response_book_event},
    {'check': check_book_ticket,            'response': response_book_ticket},
    {'check': check_cancel_ticket,          'response': response_cancel_ticket},
    {'check': check_bookable_activities,    'response': response_bookable_activities},
    {'check': check_exam_tickets,           'response': response_exam_tickets},
    {'check': check_help_or_subscribe,      'response': response_help_or_subscribe_response},
    {'check': check_unsubscribe_or_unbind,  'response': response_unsubscribe_or_unbind},
    {'check': check_bind_account,           'response': response_bind_account},
    {'check': check_fetch_ticket,           'response': response_fetch_ticket},
    {'check': check_no_book_acts_event,     'response': response_no_book_acts},
    {'check': check_get_activity_menu,      'response': response_get_activity_menu},
    {'check': check_xnlhwh,                 'response': response_xnlhwh},
]


# entry of weixin handler
def handle_weixin_request(environ):
    data = urldecode(environ['QUERY_STRING'])
    if not check_weixin_signature(data):
        print '!!!!! Check weixin signature failed !!!!!'
        return ''
    if environ['REQUEST_METHOD'] == 'GET':
        return data['echostr']
    elif environ['REQUEST_METHOD'] == 'POST':
        try:
            request_body_size = int(environ['CONTENT_LENGTH'])
            request_body = environ['wsgi.input'].read(request_body_size)
        except (TypeError, ValueError):
            request_body = None

        raw_str = smart_str(unicode(request_body, "utf-8"))
        msg = parse_msg_xml(ET.fromstring(raw_str))
        try:
            #recognize type of message and return result
            for handler in handler_list:
                if handler['check'](msg):
                    return handler['response'](msg)
        except Exception as e:
            print 'Error occured!!!!!!' + str(e)
            return get_reply_text_xml(msg, u'对不起，没有找到您需要的信息 T T')
        try:
            return get_information_response(request_body)
        except Exception as e:
            print 'Error occured!!!!!!' + str(e)
            return get_reply_text_xml(msg, u'对不起，没有找到您需要的信息:(')


#last_timestamp = int((datetime.datetime.now() + datetime.timedelta(seconds=-5)).strftime('%s'))


# check signature as the weixin API document provided
def check_weixin_signature(data):
    #global last_timestamp
    signature = data['signature']
    timestamp = data['timestamp']
    #timestamp_int = int(timestamp)
    #if timestamp_int < last_timestamp - 5:
    #    return False
    nonce = data['nonce']
    token = WEIXIN_TOKEN

    tmp_list = [token, timestamp, nonce]
    tmp_list.sort()
    tmpstr = '%s%s%s' % tuple(tmp_list)
    tmpstr = hashlib.sha1(tmpstr).hexdigest()
    if tmpstr == signature:
        #last_timestamp = timestamp_int
        return True
    else:
        return False


# convert string 'a=1&b=2&c=3' to dict {'a':1,'b':2,'c':3}
def urldecode(query):
    d = {}
    a = query.split('&')
    for s in a:
        if s.find('='):
            k, v = map(urllib.unquote, s.split('='))
            d[k] = v
    return d


# convert XML List object to Python dict object
def parse_msg_xml(root_elem):
    msg = {}
    if root_elem.tag == 'xml':
        for child in root_elem:
            msg[child.tag] = smart_str(child.text)
    return msg