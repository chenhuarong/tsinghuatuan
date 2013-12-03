#-*- coding:utf-8 -*-
import string
import time,datetime
from urlhandler.models import *


# get reply xml(reply text), using msg(source dict object) and reply_content(text, string)
def get_reply_text_xml(msg, reply_content):
    ext_tpl = '<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s' \
              '</CreateTime><MsgType><![CDATA[%s]]></MsgType><Content><![CDATA[%s]]></Content></xml>'
    ext_tpl = ext_tpl % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 'text', reply_content)
    return ext_tpl


# get reply xml(reply news), using msg(source dict object) and reply_content(news, string)
def get_reply_news_xml(msg, articles, num):
    ext_tpl = '<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s' \
              '</CreateTime><MsgType><![CDATA[%s]]></MsgType><ArticleCount>%s</ArticleCount><Articles>%s</Articles>' \
              '</xml>'
    ext_tpl = ext_tpl % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 'news', str(num), articles)
    return ext_tpl


#check user is authenticated or not
def is_authenticated(username):
    users = User.objects.filter(weixin_id = username)
    if users.exists():
        user = users[0]
        return user.status
    else:
        return 0

#check help command
def check_help(msg):
    if msg['MsgType'] == 'text' and msg['Content'] == '帮助':
        return 1
    if msg['MsgType'] == 'event' and msg['Event']=='CLICK'and msg['EventKey'] == 'TSINGHUA_WECHAT_HELP':
        return 1
    if msg['MsgType'] == 'event' and msg['Event'] == 'scan':
        return 1
    return 0

#get help information
def get_help_response(msg):
    user = User.objects.get(weixin_id = msg['FromUserName'])
    if user.status == 0:
        reply_content = u'<a href="http://tsinghuatuan.duapp.com/userpage/validate/?openid=%s">' \
                        u'点此绑定信息门户账号</a>\r\n' % msg['FromUserName']
    else:
        reply_content = ''
    reply_content += u'您好，回复以下关键字可以得到相应结果:\r\n订票 订单 帮助'
    return get_reply_text_xml(msg, reply_content)


#check book command
def check_book(msg):
    if msg['MsgType'] == 'text' and msg['Content'] == '订票':
        return 1
    if msg['MsgType'] == 'event' and msg['Event']=='CLICK' and msg['EventKey'] == 'TSINGHUA_WECHAT_BOOK':
        return 1
    return 0


#get bookable activities
def get_bookable_activities(msg):
    now = string.atof(msg['CreateTime'])
    activitys = Activity.objects.filter(end_time__gt=datetime.datetime.fromtimestamp(now)).order_by('book_start')
    items = ''
    num = 0
    for activity in activitys:
        item = '<item><Title><![CDATA[%s]]></Title><Description><![CDATA[%s]]></Description>' \
               '<PicUrl><![CDATA[%s]]></PicUrl><Url><![CDATA[%s]]></Url></item>'
        item = item % (activity.name, activity.description, 'http://student.tsinghua.edu.cn/upload/20131030/43571383148723104.png',
                       'http://tsinghuatuan.duapp.com/userpage/activity/?activityid='+str(activity.id))
        items += item
        num += 1
        if num == 10:
            break
    if num != 0:
        return get_reply_news_xml(msg, items, num)
    else:
        return get_reply_text_xml(msg, u'您好，目前没有活动:D')


#check order command
def check_order(msg):
    if msg['MsgType'] == 'text' and msg['Content'] == '订单':
        return 1
    else:
        return 0


#get order of tickets
def get_order(msg):
    if is_authenticated(msg['FromUserName']):
        user = User.objects.get(weixin_id=msg['FromUserName'])
    else:
        return get_reply_text_xml(msg, u'对不起，尚未绑定账号，不能查看订单，<a href="http://tsinghuatuan.duapp.com/userpage/validate/?openid=%s">点此绑定信息'
                                       u'门户账号</a>\r\n' % msg['FromUserName'])

    now = string.atof(msg['CreateTime'])
    activitys = Activity.objects.filter(end_time__gte=datetime.datetime.fromtimestamp(now))
    reply_content = []
    for activity in activitys:
        orders = Order.objects.filter(user=user, activity=activity)
        if orders.exists():
            order = orders[0]
            if order.status == 1:
                item = u'预订%s%s张，抽签未开始' % (activity.name, order.tickets)
                reply_content += [item]
            elif order.status == 2:
                item = u'%s%s张，订票失败\r\n' % (activity.name, order.tickets)
                reply_content += [item]
            elif order.status == 3:
                item = u'%s%s张，订票成功!<a href="http://sailon.duappp.com">点此查看电子票</a>\r\n' % (activity.name, order.tickets)
                reply_content += [item]
    return get_reply_text_xml(msg, '\r\n'.join(reply_content) if not (len(reply_content) == 0) else u'您目前没有订单')


#check book command message
def check_book_cmd(msg):
    if msg['MsgType'] != 'text':
        return 0
    receive_msg = msg['Content']
    receive_msg = receive_msg.split()
    if len(receive_msg) > 2 or len(receive_msg) == 0:
        return 0

    now = string.atof(msg['CreateTime'])
    activitys = Activity.objects.filter(book_end__gt=datetime.datetime.fromtimestamp(now)).filter(key = receive_msg[0])
    if not activitys.exists():                 # book command is correct and the activity is at booking stage
        return 0

    if len(receive_msg) == 1:
        return 1
    elif len(receive_msg) == 2:
        return 1
    return 0

#handle order message, like 'mlhk 2' means order 2 tickets of Malanhuakai
def book_tickets(msg):
    if is_authenticated(msg['FromUserName']):
        user = User.objects.get(weixin_id=msg['FromUserName'])
    else:
        return get_reply_text_xml(msg, u'对不起，尚未绑定账号，不能订票，<a href="http://tsinghuatuan.duapp.com/userpage/validate/?openid=%s">'
                                       u'点此绑定信息门户账号</a>\r\n' % msg['FromUserName'])

    now = string.atof(msg['CreateTime'])
    receive_msg = msg['Content']
    receive_msg = receive_msg.split()
    if len(receive_msg) == 1:
        receive_msg.append('1')
    activitys = Activity.objects.filter(book_end__gt=datetime.datetime.fromtimestamp(now)).filter(key=receive_msg[0])
    activity = activitys[0]

    if receive_msg[1].isdigit():
        orders = Order.objects.filter(user=user, activity=activity)
        if orders.exists() == 0:   # user has not booked this activity before  or the order is cancelled
            tickets_num = int(receive_msg[1])            # change number in book command into integer
            if tickets_num < 1:
                return get_reply_text_xml(msg, u'订票数量不能小于1')
            elif tickets_num > activity.max_tickets_per_order:
                return get_reply_text_xml(msg, u'订票数量不能大于%s' % activity.max_tickets_per_order)
            order = Order(
                user=user,
                activity=activity,
                status=1,
                tickets=tickets_num
            )
            order.save()
            reply_content = u'预订%s的票%s张，订票时间结束后，系统会自动抽签，请回复"订单"查询。如需修改订票信息，' \
                            u'请回复%s qx先取消订票，然后再重新订票' % (activity.name, receive_msg[1], activity.key)
        elif orders[0].status == 0:
            tickets_num = int(receive_msg[1])
            if tickets_num < 1:
                return get_reply_text_xml(msg, u'订票数量不能小于1')
            elif tickets_num > activity.max_tickets_per_order:
                return get_reply_text_xml(msg, u'订票数量不能大于%s' % activity.max_tickets_per_order)
            order = orders[0]
            order.tickets = tickets_num
            order.status = 1
            order.save()
            reply_content = u'修改成功，预订%s的票%s张，订票时间结束后，系统会自动抽签，请回复"订单"查询。' % (activity.name, receive_msg[1])
        else:
            reply_content = u'您已经预订%s的票%s张，请不要重复订票。如需修改订票信息，请回复%s qx先取消订票，' \
                            u'然后再重新订票' % (activity.name, str(orders[0].tickets), activity.key)
    elif receive_msg[1].lower() == 'qx':
        orders = Order.objects.filter(user=user, activity=activity)
        if orders.exists():   # user has already booked the activity
            order = orders[0]
            order.status = 0
            order.save()
            reply_content = u'您的订票记录已取消，可以重新订票'
        else:
            reply_content = u'未找到您的订票记录，取消订票失败'
    else:
        reply_content = u'您输入的格式有误，请重新输入，%s后必须跟空格加数字' % activity.key
    return get_reply_text_xml(msg, reply_content)


#check subscribe event
def check_subscribe(msg):
    if msg['MsgType'] == 'event' and msg['Event'] == 'subscribe':
        return 1
    return 0


#handle subscribe event
def get_subscibe(msg):
    users = User.objects.filter(weixin_id=msg['FromUserName'])
    if not users.exists():
        user = User(
            weixin_id=msg['FromUserName'],
            stu_id=0,
            status=0
        )
        user.save()
    return get_help_response(msg)


#check unsubscribe event
def check_unsubscribe(msg):
    if msg['MsgType'] == 'event' and msg['Event'] == 'unsubscribe':
        return 1
    if msg['MsgType'] == 'text' and msg['Content'] == '解除账号绑定':
        return 1
    return 0


#handle unsubscribe event
def get_unsubscibe(msg):
    user = User.objects.get(weixin_id=msg['FromUserName'])
    user.status = 0
    user.save()
    return get_help_response(msg)


#check bind event
def check_bind_account(msg):
    if msg['MsgType'] == 'event' and msg['Event']=='CLICK' and msg['EventKey'] == 'TSINGHUA_WECHAT_BIND':
        return 1
    return 0


#handle bind event
def bind_account(msg):
    if is_authenticated(msg['FromUserName']):
        return get_reply_text_xml(msg, u'若要解绑请回复"解除账号绑定"')
    else:
        return get_reply_text_xml(msg, u'<a href="http://tsinghuatuan.duapp.com/userpage/validate/?openid=%s">'
                                       u'点此绑定信息门户账号</a>\r\n' % msg['FromUserName'])