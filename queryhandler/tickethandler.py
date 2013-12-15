#-*- coding:utf-8 -*-
import random
import string
import time,datetime
from urlhandler.models import *
from queryhandler.settings import QRCODE_URL
from django.db.models import F
from django.db import transaction

from userpage.safe_reverse import *


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
    for user in users:
        if user.status == 1:
            return 1
    return 0

#check help command
def check_help(msg):
    if msg['MsgType'] == 'text' and (msg['Content'] == '帮助' or msg['Content'].lower() == 'help'):
        return 1
    if msg['MsgType'] == 'event' and msg['Event'] == 'CLICK'and msg['EventKey'] == 'TSINGHUA_HELP':
        return 1
    if msg['MsgType'] == 'event' and msg['Event'] == 'scan':
        return 1
    return 0


#get help information
def get_help_response(msg):
    fromuser = msg['FromUserName']
    if is_authenticated(fromuser):
        reply_content = u''
    else:
        reply_content = u'<a href="' + s_reverse_validate(fromuser) + '">' \
                        u'点此绑定信息门户账号</a>\n'
    reply_content += u'您好，回复以下关键字可以得到相应结果:\n抢啥 查票 帮助'
    return get_reply_text_xml(msg, reply_content)


#check book command
def check_bookable_activities(msg):
    if msg['MsgType'] == 'text' and msg['Content'] == '抢啥':
        return 1
    if msg['MsgType'] == 'event' and msg['Event'] == 'CLICK' and msg['EventKey'] == 'TSINGHUA_BOOK_WHAT':
        return 1
    return 0


def format(time):
    if time.days > 0:
        result = time.days + u'天'
    elif time.seconds >= 3600:
        result = str(time.seconds / 3600) + u'小时'
    elif time.seconds >= 60:
        result = str(time.seconds / 60) + u'分钟'
    elif time.seconds > 0:
        result = time.seconds + u'秒'
    return result


#get bookable activities
def get_bookable_activities(msg):
    now = string.atof(msg['CreateTime'])
    now = datetime.datetime.fromtimestamp(now)
    activities_book_not_end = Activity.objects.filter(status=1, book_end__gte=now).order_by('book_start')
    activities_book_end = Activity.objects.filter(status=1, book_end__lt=now, end_time__gte=now)
    activities = list(activities_book_not_end) + list(activities_book_end)
    items = ''
    num = 0
    for activity in activities:
        item = '<item><Title><![CDATA[%s]]></Title><Description><![CDATA[%s]]></Description>' \
               '<PicUrl><![CDATA[%s]]></PicUrl><Url><![CDATA[%s]]></Url></item>'
        title = activity.name+ u'（%s）'
        if activity.book_start > now:
            delta = activity.book_start - now
            content = u'%s后开始抢票' % format(delta)
            title = title % content
        elif activity.book_end > now:
            title = title % u'抢票进行中'
        else:
            title = title % u'抢票已结束'
        item = item % (title, activity.description, activity.pic_url, s_reverse_activity_detail(activity.id))
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
    if msg['MsgType'] == 'event' and msg['Event'] == 'CLICK' and msg['EventKey'] == 'TSINGHUA_TICKET':
        return 1
    else:
        return 0


#get list of tickets
def get_tickets(msg):
    fromuser = msg['FromUserName']
    if is_authenticated(fromuser):
        user = User.objects.get(weixin_id=fromuser, status = 1)
    else:
        return get_reply_text_xml(msg, '对不起，尚未绑定账号，不能查票，<a href="' + s_reverse_validate(fromuser) + '">点此绑定信息门户账号</a>')

    now = string.atof(msg['CreateTime'])
    activities = Activity.objects.filter(status=1, end_time__gte=datetime.datetime.fromtimestamp(now))
    reply_content = []
    all_tickets = []
    for activity in activities:
        tickets = Ticket.objects.filter(stu_id=user.stu_id, activity=activity, status=1)
        if tickets.exists():
            all_tickets.append(tickets[0])
            item = u'“%s”<a href="' + s_reverse_ticket_detail(tickets[0].unique_id) + '">电子票</a>' % (activity.name, )
            reply_content += [item]

    if len(all_tickets) == 1:
        ticket = all_tickets[0]
        item = '<item><Title><![CDATA[%s]]></Title><Description><![CDATA[%s]]></Description>' \
               '<PicUrl><![CDATA[%s]]></PicUrl><Url><![CDATA[%s]]></Url></item>'
        description = u'活动时间：%s\n活动地点：%s\n回复“退票 %s”即可退票' %(ticket.activity.start_time.strftime('%Y-%m-%d %H:%M'),
                                                           ticket.activity.place, ticket.activity.key)
        url = s_reverse_ticket_detail(ticket.unique_id)
        item = item % (ticket.activity.name, description, QRCODE_URL + str(ticket.unique_id), url)
        return get_reply_news_xml(msg, item, 1)
    else:
        return get_reply_text_xml(msg, u'\n-----------------------\n'.join(reply_content) if not (len(reply_content) == 0) else u'您目前没有票')


#check fetch command message
def check_fetch_cmd(msg):
    if msg['MsgType'] != 'text':
        return 0
    receive_msg = msg['Content']
    receive_msg = receive_msg.split()
    if receive_msg[0] != '取票':
        return 0
    return 1


#handle order message
def get_fetch_cmd_response(msg):
    fromuser = msg['FromUserName']
    if is_authenticated(fromuser):
        user = User.objects.get(weixin_id=fromuser, status=1)
    else:
        return get_reply_text_xml(msg, u'对不起，尚未绑定账号，不能取票，<a href="' + s_reverse_validate(fromuser) + '">'
                                       u'点此绑定信息门户账号</a>')

    now = string.atof(msg['CreateTime'])
    now = datetime.datetime.fromtimestamp(now)
    receive_msg = msg['Content']
    receive_msg = receive_msg.split()
    if len(receive_msg) > 1:
        key = receive_msg[1]
    else:
        return get_reply_text_xml(msg, u'您好，格式不正确！请输入“取票 活动代称”，如：“取票 马兰花开”将向您返回马兰花开活动的电子票。')
    activities = Activity.objects.filter(status=1,end_time__gte=now, key=key)

    if not activities.exists():
        return get_reply_text_xml(msg, u'活动不存在，请重试:)')
    else:
        activity = activities[0]

    tickets =  Ticket.objects.filter(stu_id=user.stu_id, activity=activity, status=1)
    if tickets.exists():
        ticket = tickets[0]
        item = '<item><Title><![CDATA[%s]]></Title><Description><![CDATA[%s]]></Description>' \
               '<PicUrl><![CDATA[%s]]></PicUrl><Url><![CDATA[%s]]></Url></item>'
        description = u'活动时间：%s\n活动地点：%s\n回复“退票 %s”即可退票' %(ticket.activity.start_time.strftime('%Y-%m-%d %H:%M'),
                                                               ticket.activity.place, ticket.activity.key)
        url = s_reverse_ticket_detail(ticket.unique_id)
        item = item % (ticket.activity.name, description, QRCODE_URL + str(ticket.unique_id), url)
        return get_reply_news_xml(msg, item, 1)
    else:
        return get_reply_text_xml(msg, u'没有%s的票' % activity.name)


#check book command message
def check_book_cmd(msg):
    if msg['MsgType'] != 'text':
        return 0
    receive_msg = msg['Content']
    receive_msg = receive_msg.split()
    if receive_msg[0] != '抢票':
        return 0
    return 1

#handle order message
def get_book_ticket_response(msg):
    if msg['MsgType'] == 'text':
        receive_msg = msg['Content']
        receive_msg = receive_msg.split()
        if len(receive_msg) > 1:
            key = receive_msg[1]
        else:
            return get_reply_text_xml(msg, u'您好，格式不正确！请输入“抢票 活动代称”，如：“抢票 马兰花开”')
    else:
        cmd_list = msg['EventKey'].split('_')
        activity_id = int(cmd_list[2])
        activity = Activity.objects.filter(id = activity_id)
        if activity.exists():
            activity = activity[0]
            key = activity.key
        else:
            key = 'INVALID_KEY'
    return book_ticket(msg, key)

def book_ticket(msg, key):
    fromuser = msg['FromUserName']
    if is_authenticated(fromuser):
        user = User.objects.get(weixin_id=fromuser, status=1)
    else:
        return get_reply_text_xml(msg, u'对不起，尚未绑定账号，不能抢票，<a href="' + s_reverse_validate(fromuser) + '">'
                                       u'点此绑定信息门户账号</a>')

    #get cmd content
    now = string.atof(msg['CreateTime'])
    now = datetime.datetime.fromtimestamp(now)

    #generate random string for ticket
    random_string = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])
    while Ticket.objects.filter(unique_id=random_string).exists():
        random_string = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])

    with transaction.commit_on_success():
        activities = Activity.objects.select_for_update().filter(status=1, book_end__gte=now, book_start__lte=now, key=key)

        if activities.exists() == 0:
            future_activities = Activity.objects.filter(status=1, book_start__gte=now, key=key)
            if not future_activities.exists():
                old_activities = Activity.objects.filter(status=1, key=key)#已发布的，活动代码为key（可能有多张活动代码相同的活动）
                if not old_activities.exists():
                    return get_reply_text_xml(msg, u'活动不存在，请重试:)')
                else:
                    #如果有票，返回票的信息
                    if len(old_activities) == 1:#如果有一张票，直接返回电子票
                        tmptics = Ticket.objects.filter(activity = old_activities[0], stu_id=user.stu_id, status=1)
                        if tmptics.exists():
                            item = '<item><Title><![CDATA[%s]]></Title><Description><![CDATA[%s]]></Description>' \
                                   '<PicUrl><![CDATA[%s]]></PicUrl><Url><![CDATA[%s]]></Url></item>'
                            description = u'活动时间：%s\n活动地点：%s' %(tmptics[0].activity.start_time.strftime('%Y-%m-%d %H:%M'),
                                                                               tmptics[0].activity.place, )
                            if now < tmptics[0].activity.book_end:
                                description += u'\n回复“退票 %s”即可退票' % (tmptics[0].activity.key, )
                            url = s_reverse_ticket_detail(tmptics[0].unique_id)
                            item = item % (tmptics[0].activity.name, description, QRCODE_URL + str(tmptics[0].unique_id), url)
                            return get_reply_news_xml(msg, item, 1)
                        #如果没票，返回无票信息
                        else:
                            return get_reply_text_xml(msg, u'很抱歉，您没有抢到该活动的票')
                    elif len(old_activities) > 1: #如果有多个活动，列表形式返回
                        reply_content = []
                        for old_activity in old_activities:
                            old_tickets =  Ticket.objects.filter(stu_id=user.stu_id, activity=old_activity, status=1)
                            if old_tickets.exists():
                                item = u'“%s”<a href="' + s_reverse_ticket_detail(old_tickets[0].unique_id) + '">电子票</a>' % (old_activity.name, )
                                reply_content += [item]
                        return get_reply_text_xml(msg, u'\n-----------------------\n'.join(reply_content) if not (len(reply_content) == 0) else u'您目前没有票')
                    else:#票的数目小于1
                        return get_reply_text_xml(msg, u'该活动不存在')
            else:
                future_activity = future_activities[0]
                start_time = u'%s年%s月%s日%s时%s分' % (future_activity.book_start.year, future_activity.book_start.month, future_activity.book_start.day, future_activity.book_start.hour, future_activity.book_start.minute)
                return get_reply_text_xml(msg, u'%s%s开始抢票，<a href="%s">详情</a>' % (future_activity.name, start_time, s_reverse_activity_detail(future_activity.id)))
        else:
            activity = activities[0]

        tickets = Ticket.objects.select_for_update().filter(stu_id=user.stu_id, activity=activity)
        
        if tickets.exists() == 0:
            if activity.remain_tickets <= 0:
                return  get_reply_text_xml(msg, u'票已抢完，欢迎关注下次活动')
            ticket = Ticket(
                stu_id = user.stu_id,
                activity = activity,
                unique_id = random_string,
                status = 1,
                seat = ''
            )
            ticket.save()
            Activity.objects.filter(status=1, book_end__gte=now, book_start__lte=now, key=key).update(remain_tickets=F('remain_tickets')-1)
            item = '<item><Title><![CDATA[%s]]></Title><Description><![CDATA[%s]]></Description>' \
                   '<PicUrl><![CDATA[%s]]></PicUrl><Url><![CDATA[%s]]></Url></item>'
            description = u'活动时间：%s\n活动地点：%s\n回复“退票 %s”即可退票' %(ticket.activity.start_time.strftime('%Y-%m-%d %H:%M'),
                                                                   ticket.activity.place, ticket.activity.key)
            url = s_reverse_ticket_detail(ticket.unique_id)
            item = item % (ticket.activity.name, description, QRCODE_URL + str(ticket.unique_id), url)
            return get_reply_news_xml(msg, item, 1)
        elif tickets[0].status == 0:
            if activity.remain_tickets <= 0:
                return get_reply_text_xml(msg, u'票已抢完，欢迎关注下次活动')
            ticket = tickets[0]
            ticket.status = 1
            ticket.save()
            Activity.objects.filter(status=1, book_end__gte=now, book_start__lte=now).update(remain_tickets=F('remain_tickets')-1)
            item = '<item><Title><![CDATA[%s]]></Title><Description><![CDATA[%s]]></Description>' \
                   '<PicUrl><![CDATA[%s]]></PicUrl><Url><![CDATA[%s]]></Url></item>'
            description = u'活动时间：%s\n活动地点：%s\n回复%s qx退票' %(ticket.activity.start_time.strftime('%Y-%m-%d %H:%M'),
                                                               ticket.activity.place, ticket.activity.key)
            url = s_reverse_ticket_detail(ticket.unique_id)
            item = item % (ticket.activity.name, description, QRCODE_URL + str(ticket.unique_id), url)
            return get_reply_news_xml(msg, item, 1)
        else:
            url = s_reverse_ticket_detail(tickets[0].unique_id)
            return get_reply_text_xml(msg, u'您已抢到%s的票，不能重复抢票，<a href="%s">查看电子票</a>' % (activity.name, url))


#check return command message
def check_return_cmd(msg):
    if msg['MsgType'] != 'text':
        return 0
    receive_msg = msg['Content']
    receive_msg = receive_msg.split()
    if receive_msg[0] != '退票':
        return 0
    return 1


#return tickets
def return_tickets(msg):
    now = string.atof(msg['CreateTime'])
    now = datetime.datetime.fromtimestamp(now)

    receive_msg = msg['Content']
    receive_msg = receive_msg.split()
    if len(receive_msg) > 1:
        key = receive_msg[1]
    else:
        return get_reply_text_xml(msg, u'您好，格式不正确！请输入“退票 活动代称”，如：“退票 马兰花开”会将退订马兰花开活动的票（该操作不可恢复，请谨慎回复！）')
    activities = Activity.objects.filter(status=1, end_time__gte=now, key=key)

    if not activities.exists():
        return get_reply_text_xml(msg, u'活动不存在，请重试:)')
    else:
        activity = activities[0]

    if activity.book_start > now:
        start_time = u'%s年%s月%s日%s时%s分' % (activity.book_start.year, activity.book_start.month, activity.book_start.day, activity.book_start.hour, activity.book_start.minute)
        return get_reply_text_xml(msg, u'%s%s开始抢票，<a href="%s">详情</a>' % (activity.name, start_time, s_reverse_activity_detail(activity.id)))
    elif activity.book_end > now:
        fromuser = msg['FromUserName']
        if is_authenticated(fromuser):
            user = User.objects.get(weixin_id=fromuser, status=1)
        else:
            return get_reply_text_xml(msg, u'对不起，尚未绑定账号，不能退票，<a href="' + s_reverse_validate(fromuser)
                                           + '">点此绑定信息门户账号</a>')

        tickets = Ticket.objects.filter(stu_id=user.stu_id, activity=activity, status=1)
        if tickets.exists():   # user has already booked the activity
            ticket = tickets[0]
            ticket.status = 0
            ticket.save()
            Activity.objects.filter(status=1, end_time__gte=now, key=key).update(remain_tickets=F('remain_tickets')+1)
            return get_reply_text_xml(msg, u'退票成功，欢迎关注下次活动')
        else:
            return get_reply_text_xml(msg, u'未找到您的抢票记录，退票失败')
    else:
        return get_reply_text_xml(msg, u'抢票时间已过，不能退票，可以将票转让于他人')

#check book event
def check_book_event(msg):
    if msg['MsgType'] == 'event' and msg['Event']=='CLICK':
        cmd_list = msg['EventKey'].split('_')
        if len(cmd_list) == 3:
            if cmd_list[0] == 'TSINGHUA' and cmd_list[1] == 'BOOK' and  cmd_list[2].isdigit():
                return 1
    return 0


#check subscribe event
def check_subscribe(msg):
    if msg['MsgType'] == 'event' and msg['Event'] == 'subscribe':
        return 1
    return 0


#handle subscribe event
def get_subscibe_response(msg):
    reply_content = u'您好，欢迎关注清小团公共平台，<a href="' + s_reverse_validate(msg['FromUserName']) + '">' \
                    u'点此绑定信息门户账号</a>\n'
    reply_content += u'回复以下关键字可以得到相应结果:\n抢啥 查票 帮助'
    return get_reply_text_xml(msg, reply_content)


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
        user = User.objects.filter(weixin_id=msg['FromUserName'], status=1).update(status=0)
    return get_reply_text_xml(msg, u'账号绑定已经解除')


#check bind event
def check_bind_account(msg):
    if msg['MsgType'] == 'event' and msg['Event']=='CLICK' and msg['EventKey'] == 'TSINGHUA_BIND':
        return 1
    if msg['MsgType'] == 'text' and msg['Content'] == '绑定':
        return 1
    return 0


#handle bind event
def bind_account(msg):
    fromuser = msg['FromUserName']
    if is_authenticated(fromuser):
        return get_reply_text_xml(msg, u'若要解绑请回复“解绑”')
    else:
        return get_reply_text_xml(msg, u'<a href="' + s_reverse_validate(fromuser) + '">'
                                       u'点此绑定信息门户账号</a>')

def check_no_book_acts_event(msg):
    if msg['MsgType'] == 'event' and msg['Event']=='CLICK' and msg['EventKey'] == 'TSINGHUA_NO_BOOK_ACTS':
        return 1
    return 0

def no_book_acts_response(msg):
    fromuser = msg['FromUserName']
    if is_authenticated(fromuser):
        return get_reply_text_xml(msg, u'您好，现在没有推荐的抢票活动哟~')