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
def get_reply_news_xml(msg, articles, num):
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

        return get_help_response(msg)

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

#处理文本消息,并返回对应结果
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
        return get_reply_news_xml(msg, items, num)
    elif(msg['Content'] == '订票'):
        activitys = Activity.objects.filter(book_end__gt = datetime.datetime.now())
        reply_content = ''
        if(len(activitys) != 0):
            for activity in activitys:
                content = u'%s将于%s在%s举行,%s至%s为开放订票时间，现在您可以订票，如需订票请回复%s'
                content = content %(activity.name, activity.start_time.strftime('%Y-%m-%d %H:%M'),
                                                activity.end_time.strftime('%Y-%m-%d %H:%M'), activity.book_start.strftime('%Y-%m-%d %H:%M'),
                                                activity.book_end.strftime('%Y-%m-%d %H:%M'), activity.key)
                reply_content = reply_content + '\r\n' + content
        else:
            reply_content =  u'对不起，目前没有活动开放订票'
        return get_reply_text_xml(msg, reply_content)
    else:
        receive_msg = msg['Content']
        receive_msg = receive_msg.split()
        if(len(receive_msg) == 1):
            receive_msg.append('1')
            return get_order_result(msg, receive_msg)
        elif(len(receive_msg) == 2):      #命令长度为2
            return get_order_result(msg, receive_msg)
        else:
            return get_reply_text_xml(msg, u'对不起，您输入的格式有误')
    return get_help_response(msg)

def get_event_response(msg):
    if(msg['Event'] == 'subscribe'):
        user = User(
            weixin_id = msg['FromUserName'],
            stu_id = 0,
            status = 1
        )
        user.save()
        return get_help_response(msg)
    elif(msg['Event'] == 'unsubscribe'):
        user = User.objects.get(weixin_id=msg['FromUserName'])
        user.status = 0
        user.save()
        return get_reply_text_xml(msg, u'感谢您使用清小团助手')
    elif(msg['Event'] == 'scan'):
        return get_help_response(msg)
    return get_help_response(msg)




def get_order_result(msg, receive_msg):
    user = User.objects.filter(weixin_id = msg['FromUserName'])
    if(len(user) == 0):
        return get_reply_text_xml(msg, u'尚未绑定账号，<a href="http://sailon.duapp.com">点此绑定信息门户账号</a>')
    else:
        user = user[0]

    activitys = Activity.objects.filter(book_end__gt = datetime.datetime.now()).filter(key = receive_msg[0])
    if(len(activitys) > 0):                 #订票命令格式正确且在订票阶段
        activity = activitys[0]
        if(receive_msg[1].isdigit()):
            orders = Order.objects.filter(user = user, activity = activity)
            if(len(orders) == 0):   #用户没有预订过该活动的票或者订单已经取消
                tickets_num = int(receive_msg[1])            #将命令格式中后者转为数字
                if(tickets_num < 1):
                    return get_reply_text_xml(msg, u'订票数量不能小于1')
                elif(tickets_num > activity.max_tickets_per_order):
                    return get_reply_text_xml(msg, u'订票数量不能大于%s'% activity.max_tickets_per_order)
                order = Order(
                    user = user,
                    activity = activity,
                    status = 0,
                    tickets = tickets_num
                )
                order.save()
                reply_content = u'预订%s的票%s张，订票时间结束后，系统会自动抽签，请及时查询。如需修改订票信息，' \
                                u'请先回复%s qx来取消订票，然后再重新订票'%(activity.name, str(orders[0].tickets, activity.key))
            elif(orders[0].status == 0):
                tickets_num = int(receive_msg[1])
                if(tickets_num < 1):
                    return get_reply_text_xml(msg, u'订票数量不能小于1')
                elif(tickets_num > activity.max_tickets_per_order):
                    return get_reply_text_xml(msg, u'订票数量不能大于%s'% activity.max_tickets_per_order)
                orders[0].tickets = tickets_num
                orders[0].status = 1
                orders[0].save()
                reply_content = u'修改成功，预订%s的票%s张，订票时间结束后，系统会自动抽签，请及时查询'%(activity.name, str(orders[0].tickets))
            else:
                reply_content = u'您已经预订%s的票%s张，请不要重复订票。如需修改订票信息，请先回复%s qx来取消订票，' \
                                u'然后再重新订票'% (activity.name, str(orders[0].tickets), activity.key)
        elif(receive_msg[1] == 'qx'):
            orders = Order.objects.filter(user = user, activity = activity)
            if(len(orders) != 0):   #用户订票记录已存在
                orders[0].status = 0
                orders[0].save()
                reply_content = u'您的订票记录已经取消，现在可以重新订票了:D'
            else:
                reply_content = u'没有找到您的订票记录，取消订票失败'
        else:
            reply_content = u'您输入的格式有误，请重新输入，%s后必须跟空格加数字' % activity.key
        return get_reply_text_xml(msg, reply_content)
    else:
        return get_reply_text_xml(msg, u'您输入的命令不存在，请重新输入')


def get_help_response(msg):
    user = User.objects.filter(weixin_id = msg['FromUserName'])
    if(len(user) == 0):
       reply_content = u'<a href="http://sailon.duapp.com">点此绑定信息门户账号</a>\r\n'
    else:
        reply_content = ''
    reply_content = reply_content + u'''您好，回复以下关键字可以得到相应结果:
                    活动 订票'''
    return get_reply_text_xml(msg, reply_content)