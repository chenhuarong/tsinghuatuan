#-*- coding:utf-8 -*-
#add ../urlhandler/ to lib path
import urllib
import hashlib
import time, datetime
import string
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
              '</CreateTime><MsgType><![CDATA[%s]]></MsgType><Content><![CDATA[%s]]></Content></xml>'
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

#handle text message and response
def get_text_response(msg):
    if(msg['Content'] == '活动'):
        return get_activities(msg)
    elif(msg['Content'] == '订票'):
        return get_book_key(msg)
    elif(msg['Content'] == '订单'):
        return get_order(msg)
    elif(msg['Content'] == '帮助'):
        return get_help_response(msg)
    else:
        receive_msg = msg['Content']
        receive_msg = receive_msg.split()
        if(len(receive_msg) == 1):
            receive_msg.append('1')
            return get_order_result(msg, receive_msg)
        elif(len(receive_msg) == 2):      #命令长度为2
            return get_order_result(msg, receive_msg)
        else:
            return get_reply_text_xml(msg, u'您输入的格式有误，请重新输入')
    return get_help_response(msg)

#handle event message and response
def get_event_response(msg):
    if(msg['Event'] == 'subscribe'):
        users = User.objects.filter(weixin_id = msg['FromUserName'])
        if(users.exists() == 0):
            user = User(
                weixin_id = msg['FromUserName'],
                stu_id = 0,
                status = 1
            )
            user.save()
        else:
            user = users[0]
            user.status = 1
            user.save()
        return get_help_response(msg)
    elif(msg['Event'] == 'unsubscribe'):
        user = User.objects.get(weixin_id = msg['FromUserName'])
        user.status = 0
        user.save()
    elif(msg['Event'] == 'scan'):
        return get_help_response(msg)
    elif(msg['Event'] == 'CLICK' and msg['EventKey'] == 'TSINGHUATUAN_ALL'):
        return get_activities(msg)
    elif(msg['Event'] == 'CLICK' and msg['EventKey'] == 'TSINGHUATUAN_BOOK'):
        return get_book_key(msg)
    elif(msg['Event'] == 'CLICK' and msg['EventKey'] == 'TSINGHUATUAN_ORDER'):
        return get_order(msg)
    return get_help_response(msg)



#handle order message, like 'mlhk 2' means order 2 tickets of Malanhuakai
def get_order_result(msg, receive_msg):
    if(is_authenticated(msg['FromUserName'])):
        user = User.objects.get(weixin_id = msg['FromUserName'])
    else:
        return get_reply_text_xml(msg, u'<a href="http://tsinghuatuan.duapp.com/userpage/validate/?openid=%s">点此绑定信息门户账号</a>\r\n' %  msg['FromUserName'])

    now = string.atof(msg['CreateTime'])
    activitys = Activity.objects.filter(book_end__gt = datetime.datetime.fromtimestamp(now)).filter(key = receive_msg[0])

    if(activitys.exists()):                 #book command is correct and the activity is at booking stage
        activity = activitys[0]
        if(receive_msg[1].isdigit()):
            orders = Order.objects.filter(user = user, activity = activity)
            if(orders.exists() == 0):   #user has not booked this activity before  or the order is cancelled
                tickets_num = int(receive_msg[1])            #chang number in book command into integer
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
                                u'请先回复%s qx来取消订票，然后再重新订票'%(activity.name, str(tickets_num), activity.key)
            elif(orders[0].status == 0):
                tickets_num = int(receive_msg[1])
                if(tickets_num < 1):
                    return get_reply_text_xml(msg, u'订票数量不能小于1')
                elif(tickets_num > activity.max_tickets_per_order):
                    return get_reply_text_xml(msg, u'订票数量不能大于%s'% activity.max_tickets_per_order)
                orders[0].tickets = tickets_num
                orders[0].status = 1
                orders[0].save()
                reply_content = u'修改成功，预订%s的票%s张，订票时间结束后，系统会自动抽签，请及时查询'%(activity.name, str(tickets_num))
            else:
                reply_content = u'您已经预订%s的票%s张，请不要重复订票。如需修改订票信息，请先回复%s qx来取消订票，' \
                                u'然后再重新订票'% (activity.name, str(orders[0].tickets), activity.key)
        elif(receive_msg[1] == 'qx' or receive_msg[1] == 'QX'):
            orders = Order.objects.filter(user = user, activity = activity)
            if(orders.exists()):   #user has already booked the activity
                order = orders[0]
                order.status = 0
                order.save()
                reply_content = u'您的订票记录已取消，可以重新订票了:D'
            else:
                reply_content = u'未找到您的订票记录，取消订票失败'
        else:
            reply_content = u'您输入的格式有误，请重新输入，%s后必须跟空格加数字' % activity.key
        return get_reply_text_xml(msg, reply_content)
    else:
        return get_reply_text_xml(msg, u'您输入的命令不存在，请重新输入')

def is_authenticated(username):
    users = User.objects.filter(weixin_id = username)
    if(users.exists()):
        return 1
    else:
        return 0
    return 1

#get help information
def get_help_response(msg):
    user = User.objects.get(weixin_id = msg['FromUserName'])
    if(user.status == 1):
       reply_content = u'<a href="http://tsinghuatuan.duapp.com/userpage/validate/?openid=%s">点此绑定信息门户账号</a>\r\n' %  msg['FromUserName']
    else:
        reply_content = ''
    reply_content = reply_content + u'您好，回复以下关键字可以得到相应结果:\r\n活动 订票 订单 帮助'
    return get_reply_text_xml(msg, reply_content)


#get activities
def get_activities(msg):
    now = string.atof(msg['CreateTime'])
    activitys = Activity.objects.filter(end_time__gt = datetime.datetime.fromtimestamp(now)).order_by('book_start')
    items = ''
    num = 0
    for activity in activitys:
        item = '<item><Title><![CDATA[%s]]></Title><Description><![CDATA[%s]]></Description>' \
               '<PicUrl><![CDATA[%s]]></PicUrl><Url><![CDATA[%s]]></Url></item>'
        item = item % (activity.name, activity.description, 'http://student.tsinghua.edu.cn/upload/20131030/43571383148723104.png',
                       'http://student.tsinghua.edu.cn/topic/mlhk/mlhk/index.html')
        items  = items + item
        num = num + 1
        if(num == 10):
            break
    if(num != 0):
        return get_reply_news_xml(msg, items, num)
    else:
        return get_reply_text_xml(msg, u'您好，目前没有活动:D')
    return get_reply_text_xml(msg, u'您好，目前没有活动:D')

def get_book_key(msg):
    now = string.atof(msg['CreateTime'])
    activitys = Activity.objects.filter(book_end__gte = datetime.datetime.fromtimestamp(now)).filter(book_start__lte = datetime.datetime.fromtimestamp(now))
    reply_content = ''
    if(activitys.exists()):
        for activity in activitys:
            content = u'%s将于%s在%s举行,%s至%s为开放订票时间，订票请回复%s,回复%s 2表示您要订2张票'
            content = content %(activity.name, activity.start_time.strftime('%Y-%m-%d %H:%M'),
                                activity.end_time.strftime('%Y-%m-%d %H:%M'), activity.book_start.strftime('%Y-%m-%d %H:%M'),
                                activity.book_end.strftime('%Y-%m-%d %H:%M'), activity.key, activity.key)
            reply_content = reply_content + '\r\n' + content
    else:
        reply_content =  u'对不起，目前没有活动开放订票'
    return get_reply_text_xml(msg, reply_content)

def get_order(msg):
    if(is_authenticated(msg['FromUserName'])):
        user = User.objects.get(weixin_id = msg['FromUserName'])
    else:
        return get_reply_text_xml(msg, u'<a href="http://tsinghuatuan.duapp.com/userpage/validate/?openid=%s">点此绑定信息门户账号</a>\r\n' %  msg['FromUserName'])

    now = string.atof(msg['CreateTime'])
    activitys = Activity.objects.filter(end_time__gte = datetime.datetime.fromtimestamp(now))
    reply_content = u''
    for activity in activitys:
        orders = Order.objects.filter(user = user, activity = activity)
        if(orders.exists()):
            order = orders[0]
            if(order.status == 1):
                item = u'预订%s%s张，抽签未开始\r\n' %(activity.name, order.tickets)
                reply_content = reply_content + item
            elif(order.status == 2):
                item = u'%s%s张，订票失败\r\n'%(activity.name, order.tickets)
                reply_content = reply_content + item
            elif(order.status == 3):
                item = u'%s%s张，订票成功!<a href="http://sailon.duappp.com">点此查看电子票</a>\r\n'%(activity.name, order.tickets)
                reply_content = reply_content + item
    if(reply_content == u''):
        reply_content = u'您目前没有订单'
    return get_reply_text_xml(msg, reply_content)