#-*- coding:utf-8 -*-
import random
import string
import time,datetime
from urlhandler.models import *
from queryhandler.settings import QRCODE_URL
from django.db.models import F
from django.db import transaction



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
    if is_authenticated(msg['FromUserName']):
        reply_content = u''
    else:
        reply_content = u'<a href="http://tsinghuatuan.duapp.com/userpage/validate/?openid=%s">' \
                        u'点此绑定信息门户账号</a>\r\n' % msg['FromUserName']
    reply_content += u'您好，回复以下关键字可以得到相应结果:\r\n抢啥 抢票 查票 帮助'
    return get_reply_text_xml(msg, reply_content)


#check book command
def check_bookable_activities(msg):
    if msg['MsgType'] == 'text' and msg['Content'] == '抢啥':
        return 1
    if msg['MsgType'] == 'event' and msg['Event']=='CLICK' and msg['EventKey'] == 'TSINGHUA_WECHAT_BOOK_ACTIVITY':
        return 1
    return 0


#get bookable activities
def get_bookable_activities(msg):
    now = string.atof(msg['CreateTime'])
    now = datetime.datetime.fromtimestamp(now)
    activities = Activity.objects.filter(status=1, end_time__gte=now).order_by('book_start')
    items = ''
    num = 0
    for activity in activities:
        item = '<item><Title><![CDATA[%s]]></Title><Description><![CDATA[%s]]></Description>' \
               '<PicUrl><![CDATA[%s]]></PicUrl><Url><![CDATA[%s]]></Url></item>'
        title = activity.name+'(%s)'
        if activity.book_start > now:
            title = title % u'抢票未开始'
        elif activity.book_end > now:
            title = title % u'抢票进行中'
        else:
            title = title % u'抢票已结束'
        item = item % (title, activity.description, activity.pic_url, 'http://tsinghuatuan.duapp.com/userpage/activity/?activityid='+str(activity.id))
        items += item
        num += 1
        if num == 10:
            break
    if num != 0:
        return get_reply_news_xml(msg, items, num)
    else:
        return get_reply_text_xml(msg, u'您好，目前没有抢票活动')


#check ticket command
def check_ticket_cmd(msg):
    if msg['MsgType'] == 'text' and msg['Content'] == '查票':
        return 1
    if msg['MsgType'] == 'event' and msg['Event']=='CLICK' and msg['EventKey'] == 'TSINGHUA_WECHAT_TICKET':
        return 1
    else:
        return 0


#get list of tickets
def get_tickets(msg):
    if is_authenticated(msg['FromUserName']):
        user = User.objects.get(weixin_id=msg['FromUserName'])
    else:
        return get_reply_text_xml(msg, u'对不起，尚未绑定账号，不能查票，<a href="http://tsinghuatuan.duapp.com/userpage/validate/?openid=%s">点此绑定信息'
                                       u'门户账号</a>' % msg['FromUserName'])

    now = string.atof(msg['CreateTime'])
    activities = Activity.objects.filter(status=1, end_time__gte=datetime.datetime.fromtimestamp(now))
    reply_content = []
    all_tickets = []
    for activity in activities:
        tickets =  Ticket.objects.filter(user=user, activity=activity, status=1)
        if tickets.exists():
            all_tickets.append(tickets[0])
            item = u'%s1张，回复“%s”取票' % (activity.name, activity.key)
            reply_content += [item]

    if len(all_tickets) == 1:
        ticket = all_tickets[0]
        item = '<item><Title><![CDATA[%s]]></Title><Description><![CDATA[%s]]></Description>' \
               '<PicUrl><![CDATA[%s]]></PicUrl><Url><![CDATA[%s]]></Url></item>'
        description = u'活动时间：%s\r\n活动地点：%s\r\n回复%s qx退票' %(ticket.activity.start_time.strftime('%Y-%m-%d %H:%M'),
                                                           ticket.activity.place, ticket.activity.key)
        url =  'http://tsinghuatuan.duapp.com/userpage/ticket/?uid=%s' % ticket.unique_id
        item = item % (ticket.activity.name, description, QRCODE_URL + str(ticket.unique_id), url)
        return get_reply_news_xml(msg, item, 1)
    else:
        return get_reply_text_xml(msg, '\r\n'.join(reply_content) if not (len(reply_content) == 0) else u'您目前没有票')


#check book command message
def check_activity_key(msg):
    if msg['MsgType'] != 'text':
        return 0
    receive_msg = msg['Content']
    receive_msg = receive_msg.split()
    if len(receive_msg) == 0:
        return 0
    now = string.atof(msg['CreateTime'])
    now = datetime.datetime.fromtimestamp(now)
    activities = Activity.objects.filter(status=1, end_time__gte=now, key = receive_msg[0])
    if not activities.exists():                 # book command is correct and the activity is at booking stage
        return 0
    if len(receive_msg) == 1:
        return 1
    return 0

#handle order message
def get_activity_key_response(msg):
    if is_authenticated(msg['FromUserName']):
        user = User.objects.get(weixin_id=msg['FromUserName'])
    else:
        return get_reply_text_xml(msg, u'对不起，尚未绑定账号，不能取票，<a href="http://tsinghuatuan.duapp.com/userpage/validate/?openid=%s">'
                                       u'点此绑定信息门户账号</a>' % msg['FromUserName'])

    now = string.atof(msg['CreateTime'])
    now = datetime.datetime.fromtimestamp(now)
    receive_msg = msg['Content']
    receive_msg = receive_msg.split()
    activities = Activity.objects.filter(status=1,end_time__gte=now, key=receive_msg[0])
    activity = activities[0]

    tickets =  Ticket.objects.filter(user=user, activity=activity, status=1)
    if tickets.exists():
        ticket = tickets[0]
        item = '<item><Title><![CDATA[%s]]></Title><Description><![CDATA[%s]]></Description>' \
               '<PicUrl><![CDATA[%s]]></PicUrl><Url><![CDATA[%s]]></Url></item>'
        description = u'活动时间：%s\r\n活动地点：%s\r\n回复%s qx退票' %(ticket.activity.start_time.strftime('%Y-%m-%d %H:%M'),
                                                           ticket.activity.place, ticket.activity.key)
        url =  'http://tsinghuatuan.duapp.com/userpage/ticket/?uid=%s' % ticket.unique_id
        item = item % (ticket.activity.name, description, QRCODE_URL + str(ticket.unique_id),
                       url)
        return get_reply_news_xml(msg, item, 1)
    else:
        if activity.book_start > now:
            start_time = u'%s年%s月%s日%s时%s分' % (activity.book_start.year, activity.book_start.month, activity.book_start.day, activity.book_start.hour, activity.book_start.minute)
            return get_reply_text_xml(msg, u'%s%s开始抢票，<a href="%s">详情</a>' % (activity.name, start_time, 'http://tsinghuatuan.duapp.com'
                                                                                                                '/userpage/activity/?activityid='+str(activity.id)))
        elif activity.book_end > now:
            return get_reply_text_xml(msg, u'现在是抢票时间哦')
        else:
            return get_reply_text_xml(msg, u'没有%s的票'% activity.key)

#check return command
def check_return_cmd(msg):
    if msg['MsgType'] != 'text':
        return 0
    receive_msg = msg['Content']
    receive_msg = receive_msg.split()
    if len(receive_msg) == 0:
        return 0
    now = string.atof(msg['CreateTime'])
    now = datetime.datetime.fromtimestamp(now)
    activities = Activity.objects.filter(status=1, end_time__gte=now, key=receive_msg[0])
    if not activities.exists():                 # book command is correct and the activity is at booking stage
        return 0
    if len(receive_msg) > 1:
        return 1
    return 0

#return tickets
def return_tickets(msg):
    now = string.atof(msg['CreateTime'])
    now = datetime.datetime.fromtimestamp(now)

    receive_msg = msg['Content']
    receive_msg = receive_msg.split()
    activities = Activity.objects.filter(status=1, end_time__gte=now, key=receive_msg[0])
    activity = activities[0]

    if len(receive_msg) == 2 and receive_msg[1].lower() == 'qx':
        if activity.book_start > now:
            start_time = u'%s年%s月%s日%s时%s分' % (activity.book_start.year, activity.book_start.month, activity.book_start.day, activity.book_start.hour, activity.book_start.minute)
            return get_reply_text_xml(msg, u'%s%s开始抢票，<a href="%s">详情</a>' % (activity.name, start_time, 'http://tsinghuatuan.duapp.com'
                                                                                                         '/userpage/activity/?activityid='+str(activity.id)))
        elif activity.book_end > now:
            if is_authenticated(msg['FromUserName']):
                user = User.objects.get(weixin_id=msg['FromUserName'])
            else:
                return get_reply_text_xml(msg, u'对不起，尚未绑定账号，不能退票，<a href="http://tsinghuatuan.duapp.com/userpage/'
                                               u'validate/?openid=%s">点此绑定信息门户账号</a>' % msg['FromUserName'])

            tickets = Ticket.objects.filter(user=user, activity=activity, status=1)
            if tickets.exists():   # user has already booked the activity
                ticket = tickets[0]
                ticket.status = 0
                ticket.save()
                Activity.objects.filter(status=1, end_time__gte=now, key=receive_msg[0]).update(remain_tickets=F('remain_tickets')+1)
                return get_reply_text_xml(msg, u'退票成功，欢迎关注下次活动')
            else:
                return get_reply_text_xml(msg, u'未找到您的抢票记录，退票失败')
        else:
            return get_reply_text_xml(msg, u'抢票时间已过，不能退票，可以将票转让于他人')
    else:
        return get_reply_text_xml(msg, u'输入的命令不合法，%s qx表示退票'% activity.key)

#check book event
def check_book_event(msg):
    if msg['MsgType'] == 'event' and msg['Event']=='CLICK' and msg['EventKey'] == 'TSINGHUA_WECHAT_BOOK':
        return 1
    if msg['MsgType'] == 'text' and msg['Content'] == '抢票':
        return 1
    return 0


#handle book event
def get_book_ticket_response(msg):
    if is_authenticated(msg['FromUserName']):
        user = User.objects.get(weixin_id=msg['FromUserName'])
    else:
        return get_reply_text_xml(msg, u'对不起，尚未绑定账号，不能抢票，<a href="http://tsinghuatuan.duapp.com/userpage/validate/?openid=%s">'
                                       u'点此绑定信息门户账号</a>' % msg['FromUserName'])

    now = string.atof(msg['CreateTime'])
    now = datetime.datetime.fromtimestamp(now)

    random_string = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])
    while Ticket.objects.filter(unique_id=random_string).exists():
        random_string = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])
    with transaction.commit_on_success():
        activities = Activity.objects.select_for_update().filter(status=1, book_end__gte=now, book_start__lte=now)
        if activities.exists() == 0:
            future_activities = Activity.objects.filter(status=1, book_start__gte=now).order_by('book_start')
            if len(future_activities) == 0:
                return get_reply_text_xml(msg, u'暂时没有抢票活动')
            else:
                future_activity = future_activities[0]
                start_time = u'%s年%s月%s日%s时%s分' % (future_activity.book_start.year, future_activity.book_start.month, future_activity.book_start.day, future_activity.book_start.hour, future_activity.book_start.minute)
                return get_reply_text_xml(msg, u'%s%s开始抢票，<a href="%s">详情</a>' % (future_activity.name, start_time, 'http://tsinghuatuan.duapp.com'
                                                                                                                '/userpage/activity/?activityid='+str(future_activity.id)))
        else:
            activity = activities[0]
        tickets = Ticket.objects.select_for_update().filter(user=user, activity=activity)
        if tickets.exists() == 0:
            if activity.remain_tickets == 0:
                return  get_reply_text_xml(msg, u'票已抢完，欢迎关注下次活动')
            ticket = Ticket(
                user = user,
                activity = activity,
                unique_id = random_string,
                status = 1,
                seat = ''
            )
            ticket.save()
            Activity.objects.filter(status=1, book_end__gte=now, book_start__lte=now).update(remain_tickets=F('remain_tickets')-1)
            item = '<item><Title><![CDATA[%s]]></Title><Description><![CDATA[%s]]></Description>' \
                   '<PicUrl><![CDATA[%s]]></PicUrl><Url><![CDATA[%s]]></Url></item>'
            description = u'活动时间：%s\r\n活动地点：%s\r\n回复%s qx退票' %(ticket.activity.start_time.strftime('%Y-%m-%d %H:%M'),
                                                               ticket.activity.place, ticket.activity.key)
            url =  'http://tsinghuatuan.duapp.com/userpage/ticket/?uid=%s' % ticket.unique_id
            item = item % (ticket.activity.name, description, QRCODE_URL + str(ticket.unique_id), url)
            return get_reply_news_xml(msg, item, 1)
        elif tickets[0].status == 0:
            if activity.remain_tickets == 0:
                return  get_reply_text_xml(msg, u'票已抢完，欢迎关注下次活动')
            ticket = tickets[0]
            ticket.status = 1
            ticket.save()
            Activity.objects.filter(status=1, book_end__gte=now, book_start__lte=now).update(remain_tickets=F('remain_tickets')-1)
            item = '<item><Title><![CDATA[%s]]></Title><Description><![CDATA[%s]]></Description>' \
                   '<PicUrl><![CDATA[%s]]></PicUrl><Url><![CDATA[%s]]></Url></item>'
            description = u'活动时间：%s\r\n活动地点：%s\r\n回复%s qx退票' %(ticket.activity.start_time.strftime('%Y-%m-%d %H:%M'),
                                                               ticket.activity.place, ticket.activity.key)
            url =  'http://tsinghuatuan.duapp.com/userpage/ticket/?uid=%s' % ticket.unique_id
            item = item % (ticket.activity.name, description, QRCODE_URL + str(ticket.unique_id), url)
            return get_reply_news_xml(msg, item, 1)
        else:
            url =  'http://tsinghuatuan.duapp.com/userpage/ticket/?uid=%s' % tickets[0].unique_id
            return get_reply_text_xml(msg, u'您已抢到%s的票，不能重复抢票，<a href="%s">查看电子票</a>' % (activity.name, url))


#check subscribe event
def check_subscribe(msg):
    if msg['MsgType'] == 'event' and msg['Event'] == 'subscribe':
        return 1
    return 0


#handle subscribe event
def get_subscibe_response(msg):
    return get_help_response(msg)


#check unsubscribe event
def check_unsubscribe(msg):
    if msg['MsgType'] == 'event' and msg['Event'] == 'unsubscribe':
        return 1
    if msg['MsgType'] == 'text' and msg['Content'] == '解绑':
        return 1
    return 0


#handle unsubscribe event
def get_unsubscibe_response(msg):
    if is_authenticated(msg['FromUserName']):
        user = User.objects.get(weixin_id=msg['FromUserName'])
        user.status = 0
        user.save()
    return get_reply_text_xml(msg, u'账号绑定已经解除')


#check bind event
def check_bind_account(msg):
    if msg['MsgType'] == 'event' and msg['Event']=='CLICK' and msg['EventKey'] == 'TSINGHUA_WECHAT_BIND':
        return 1
    if msg['MsgType'] == 'text' and msg['Content'] == '绑定':
        return 1
    return 0


#handle bind event
def bind_account(msg):
    if is_authenticated(msg['FromUserName']):
        return get_reply_text_xml(msg, u'若要解绑请回复“解绑”')
    else:
        return get_reply_text_xml(msg, u'<a href="http://tsinghuatuan.duapp.com/userpage/validate/?openid=%s">'
                                       u'点此绑定信息门户账号</a>' % msg['FromUserName'])