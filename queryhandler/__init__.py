#-*- coding:utf-8 -*-
import urllib
import hashlib
import xml.etree.ElementTree as ET
from django.utils.encoding import smart_str
from weixinlib.settings import WEIXIN_TOKEN
from queryhandler.tickethandler import *
from queryhandler.query_transfer import get_information_response

handler_list = [
    {'check': check_bookable_activities,    'response': response_bookable_activities},
    {'check': check_exam_tickets,           'response': response_exam_tickets},
    {'check': check_book_ticket,            'response': response_book_ticket},
    {'check': check_help_or_subscribe,      'response': response_help_or_subscribe_response},
    {'check': check_unsubscribe,            'response': get_unsubscibe_response},
    {'check': check_bind_account,           'response': bind_account},
    {'check': check_book_event,             'response': response_book_event},
    {'check': check_return_cmd,             'response': return_tickets},
    {'check': check_fetch_ticket,           'response': response_fetch_ticket},
    {'check': check_no_book_acts_event,     'response': no_book_acts_response},
]


# entry of weixin handler
def handle_weixin_request(environ):
    if environ['REQUEST_METHOD'] == 'GET':
        data = urldecode(environ['QUERY_STRING'])
        return check_weixin_signature(data)
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
            # if msg['MsgType'] == 'image':
            #     return get_reply_text_xml(msg, u'对不起，暂不支持图片消息')
            # elif msg['MsgType'] == 'voice':
            #     return get_reply_text_xml(msg, u'对不起，暂不支持音频消息')
            # elif msg['MsgType'] == 'video':
            #     return get_reply_text_xml(msg, u'对不起，暂不支持视频消息')
            # elif msg['MsgType'] == 'location':
            #     return get_reply_text_xml(msg, u'对不起，暂不支持位置消息')
            # elif msg['MsgType'] == 'link':
            #     return get_reply_text_xml(msg, u'对不起，暂不支持链接消息')
            # else:
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


# check signature as the weixin API document provided
def check_weixin_signature(data):
    signature = data['signature']
    timestamp = data['timestamp']
    nonce = data['nonce']
    echostr = data['echostr']
    token = WEIXIN_TOKEN

    tmp_list = [token, timestamp, nonce]
    tmp_list.sort()
    tmpstr = '%s%s%s' % tuple(tmp_list)
    tmpstr = hashlib.sha1(tmpstr).hexdigest()
    if tmpstr == signature:
        return echostr
    else:
        return None


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