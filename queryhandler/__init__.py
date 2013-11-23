#-*- coding:utf-8 -*-
#add ../urlhandler/ to lib path
import sys
sys.path.append("urlhandler")
import urllib
import hashlib
import time, datetime
import random
import xml.etree.ElementTree as ET
from django.utils.encoding import smart_str
from queryhandler.settings import WEIXIN_TOKEN
from urlhandler.models import *

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

# get reply xml(reply text), using msg(source dict object) and reply_content(text, string)
def get_reply_text_xml(msg, reply_content):
    ext_tpl = '<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s' \
              '</CreateTime><MsgType><![CDATA[%s]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>'
    ext_tpl = ext_tpl % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 'text', reply_content)
    return ext_tpl

# get reply xml(reply news), using msg(source dict object) and reply_content(news, string)
def get_reply_news_xml(msg, num, articles):
    ext_tpl = '<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s' \
              '</CreateTime><MsgType><![CDATA[%s]]></MsgType><ArticleCount>%s</ArticleCount><Articles>%s</Articles></xml>'
    ext_tpl = ext_tpl % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 'text',str(num), articles)
    return ext_tpl

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

        raw_str = smart_str(request_body)
        msg = parse_msg_xml(ET.fromstring(raw_str))

        #recognize type of message and return result
        #message
        if(msg['MsgType'] == 'text'):
            return get_text_response(msg)
        elif(msg['MsgType'] == 'image'):
            return get_reply_text_xml(msg, u'对不起，暂不支持图片消息')
        elif(msg['MsgType'] == 'voice'):
            return get_reply_text_xml(msg, u'对不起，暂不支持音频消息')
        elif(msg['MsgType'] =='video'):
            return get_reply_text_xml(msg, u'对不起，暂不支持视频消息')
        elif(msg['MsgType'] == 'location'):
            return get_reply_text_xml(msg, u'对不起，暂不支持位置消息')
        elif(msg['MsgType'] == 'link'):
            return get_reply_text_xml(msg, u'对不起，暂不支持链接消息')

        #event
        elif(msg['MsgType'] == 'event'):
            return get_event_response(msg)

        return default_weixin_response(msg)

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

def get_text_response(msg):
    if(msg['Content'] == '活动'):
        activitys = Activity.objects.filter(end_time__gt = datetime.datetime.now())
        items = ''
        num = 0
        for activity in activitys:
            item = '<item><Title><![CDATA[%s]]></Title><Description><![CDATA[%s]]></Description>' \
                   '<PicUrl><![CDATA[%s]]></PicUrl><Url><![CDATA[%s]]></Url></item>'
            item = item % (activity.name, activity.description, 'http://student.tsinghua.edu.cn/upload/20131030/43571383148723104.png',
                           'http://student.tsinghua.edu.cn/topic/mlhk/mlhk/index.html')
            items  = items + item
            num = num + 1
        return get_reply_news_xml(msg, num, items)
    elif(msg['Content'] == '订票'):
        return default_weixin_response(msg)
    return default_weixin_response(msg)

def get_event_response(msg):
    return get_reply_news_xml(msg, u'大帝sb')

# just a demo:)
def default_weixin_response(data):
    rnd = random.randint(0, 1)
    if rnd == 0:
        return get_reply_text_xml(data, u'大帝sb')
    else:
        return get_reply_text_xml(data, u'福哥sb')