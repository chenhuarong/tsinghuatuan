#-*- coding:utf-8 -*-
import random
import string
import datetime
from urlhandler.models import *
from queryhandler.settings import QRCODE_URL
from django.db.models import F
from django.db import transaction

from userpage.safe_reverse import *
from queryhandler.weixin_reply_templates import *
from queryhandler.weixin_text_templates import *
from queryhandler.handler_check_templates import *
from queryhandler.weixin_msg import *
from weixinlib.settings import WEIXIN_EVENT_KEYS


def get_user(openid):
    try:
        return User.objects.get(weixin_id=openid, status=1)
    except:
        return None


def get_reply_single_ticket(msg, ticket, now):
    return get_reply_single_news_xml(msg, get_item_dict(
        title=get_text_one_ticket_title(ticket, now),
        description=get_text_one_ticket_description(ticket, now),
        pic_url=get_text_ticket_pic(ticket),
        url=s_reverse_ticket_detail(ticket.unique_id)
    ))


#check user is authenticated or not
def is_authenticated(openid):
    return get_user(openid) is not None


#check help command
def check_help_or_subscribe(msg):
    return handler_check_text(msg, ['帮助', 'help']) or handler_check_event_click(msg, [
        WEIXIN_EVENT_KEYS['help']]) or handler_check_events(msg, ['scan', 'subscribe'])


#get help information
def response_help_or_subscribe_response(msg):
    return get_reply_single_news_xml(msg, get_item_dict(
        title=get_text_help_title(),
        description=get_text_help_description(is_authenticated(get_msg_from(msg))),
        url=s_reverse_help()
    ))


#check book command
def check_bookable_activities(msg):
    return handler_check_text(msg, ['抢啥']) or handler_check_event_click(msg, [WEIXIN_EVENT_KEYS['ticket_book_what']])


#get bookable activities
def response_bookable_activities(msg):
    now = datetime.datetime.fromtimestamp(get_msg_create_time(msg))
    activities_book_not_end = Activity.objects.filter(status=1, book_end__gte=now).order_by('book_start')
    activities_book_end = Activity.objects.filter(status=1, book_end__lt=now, end_time__gte=now)
    activities = list(activities_book_not_end) + list(activities_book_end)
    if len(activities) == 1:
        activity = activities[0]
        return get_reply_single_news_xml(msg, get_item_dict(
            title=get_text_activity_title_with_status(activity, now),
            description=get_text_activity_description(activity, 100),
            pic_url=activity.pic_url,
            url=s_reverse_activity_detail(activity.id)
        ))
    items = []
    for activity in activities:
        items.append(get_item_dict(
            title=get_text_activity_title_with_status(activity, now),
            pic_url=activity.pic_url,
            url=s_reverse_activity_detail(activity.id)
        ))
        if len(items) >= 10:
            break
    if len(items) != 0:
        return get_reply_news_xml(msg, items)
    else:
        return get_reply_text_xml(msg, get_text_no_bookable_activity())


def check_exam_tickets(msg):
    return handler_check_text(msg, ['查票']) or handler_check_event_click(msg, [WEIXIN_EVENT_KEYS['ticket_get']])


#get list of tickets
def response_exam_tickets(msg):
    fromuser = get_msg_from(msg)
    user = get_user(fromuser)
    if user is None:
        return get_reply_text_xml(msg, get_text_unbinded_exam_ticket(fromuser))

    now = datetime.datetime.fromtimestamp(get_msg_create_time(msg))
    activities = Activity.objects.filter(status=1, end_time__gte=now)
    all_tickets = []
    for activity in activities:
        tickets = Ticket.objects.filter(stu_id=user.stu_id, activity=activity, status=1)
        if tickets.exists():
            all_tickets.append(tickets[0])

    if len(all_tickets) == 1:
        ticket = all_tickets[0]
        return get_reply_single_ticket(msg, ticket, now)
    elif len(all_tickets) == 0:
        return get_reply_text_xml(msg, get_text_no_ticket())
    else:
        return get_reply_text_xml(msg, get_text_exam_tickets(all_tickets, now))


def check_fetch_ticket(msg):
    return handler_check_text_header(msg, ['取票'])


#handle order message
def response_fetch_ticket(msg):
    fromuser = get_msg_from(msg)
    user = get_user(fromuser)
    if user is None:
        return get_text_unbinded_fetch_ticket(fromuser)

    received_msg = get_msg_content(msg).split()
    if len(received_msg) > 1:
        key = received_msg[1]
    else:
        return get_reply_text_xml(msg, get_text_usage_fetch_ticket())

    now = datetime.datetime.fromtimestamp(get_msg_create_time(msg))
    activities = Activity.objects.filter(status=1, end_time__gt=now, key=key)
    if not activities.exists():
        return get_reply_text_xml(msg, get_text_no_such_activity())
    else:
        activity = activities[0]
    return fetch_ticket(msg, user, activity, now)


def fetch_ticket(msg, user, activity, now):
    tickets = Ticket.objects.filter(stu_id=user.stu_id, activity=activity, status=1)
    if tickets.exists():
        ticket = tickets[0]
        return get_reply_single_ticket(msg, ticket, now)
    else:
        return get_reply_text_xml(msg, get_text_no_ticket_in_act(activity, now))


#check book command message
def check_book_cmd(msg):
    return handler_check_text_header(msg, ['抢票'])


#handle order message
def get_book_ticket_response(msg):
    if msg['MsgType'] == 'text':
        receive_msg = msg['Content']
        receive_msg = receive_msg.split()
        if len(receive_msg) > 1:
            key = receive_msg[1]
        else:
            return get_reply_text_xml(msg, u'您好，格式不正确！请输入“抢票 活动代称”。\n如：“抢票 马兰花开”')
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
    fromuser = get_msg_from(msg)
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

    #with transaction.commit_on_success():
    with transaction.atomic():
        activities = Activity.objects.select_for_update().filter(status=1, book_end__gte=now, book_start__lte=now, key=key)

        if activities.exists() == 0:
            future_activities = Activity.objects.filter(status=1, book_start__gte=now, key=key)
            if not future_activities.exists():
                old_activities = Activity.objects.filter(status=1, key=key)#已发布的，活动代码为key（可能有多张活动代码相同的活动）
                if not old_activities.exists():
                    return get_reply_text_xml(msg, u'活动不存在或已结束，请重试:)')
                else:
                    #如果有票，返回票的信息
                    if len(old_activities) == 1:#如果有一张票，直接返回电子票
                        tmptics = Ticket.objects.filter(activity = old_activities[0], stu_id=user.stu_id, status=1)
                        if tmptics.exists():
                            description = u'活动时间：%s\n活动地点：%s' % (tmptics[0].activity.start_time.strftime('%Y-%m-%d %H:%M'),
                                                                        tmptics[0].activity.place, )
                            if now < tmptics[0].activity.book_end:
                                description += u'\n回复“退票 %s”即可退票' % (tmptics[0].activity.key, )
                            url = s_reverse_ticket_detail(tmptics[0].unique_id)
                            return get_reply_news_xml(msg, [get_item_dict(
                                title=tmptics[0].activity.name,
                                description=description,
                                pic_url=QRCODE_URL + str(tmptics[0].unique_id),
                                url=url
                            )])
                        #如果没票，返回无票信息
                        else:
                            return get_reply_text_xml(msg, u'很抱歉，您没有抢到该活动的票')
                    elif len(old_activities) > 1: #如果有多个活动，列表形式返回
                        reply_content = []
                        for old_activity in old_activities:
                            old_tickets = Ticket.objects.filter(stu_id=user.stu_id, activity=old_activity, status=1)
                            if old_tickets.exists():
                                item = (u'“%s”<a href="' + s_reverse_ticket_detail(old_tickets[0].unique_id) + '">电子票</a>') % (old_activity.name, )
                                reply_content += [item]
                        return get_reply_text_xml(msg, u'\n-----------------------\n'.join(reply_content) if not (len(reply_content) == 0) else u'您目前没有票')
                    else:#票的数目小于1
                        return get_reply_text_xml(msg, u'活动不存在或已结束，请重试:)')
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
            description = u'活动时间：%s\n活动地点：%s\n回复“退票 %s”即可退票' %(ticket.activity.start_time.strftime('%Y-%m-%d %H:%M'),
                                                                   ticket.activity.place, ticket.activity.key)
            url = s_reverse_ticket_detail(ticket.unique_id)
            return get_reply_news_xml(msg, [get_item_dict(
                title=ticket.activity.name,
                description=description,
                pic_url=QRCODE_URL + str(ticket.unique_id),
                url=url
            )])
        elif tickets[0].status == 0:
            if activity.remain_tickets <= 0:
                return get_reply_text_xml(msg, u'票已抢完，欢迎关注下次活动')
            ticket = tickets[0]
            ticket.status = 1
            ticket.save()
            Activity.objects.filter(status=1, book_end__gte=now, book_start__lte=now, key=key).update(remain_tickets=F('remain_tickets')-1)
            description = u'活动时间：%s\n活动地点：%s\n回复“退票 %s”即可退票' %(ticket.activity.start_time.strftime('%Y-%m-%d %H:%M'),
                                                               ticket.activity.place, ticket.activity.key)
            url = s_reverse_ticket_detail(ticket.unique_id)
            return get_reply_news_xml(msg, [get_item_dict(
                title=ticket.activity.name,
                description=description,
                pic_url=QRCODE_URL + str(ticket.unique_id),
                url=url
            )])
        else:
            url = s_reverse_ticket_detail(tickets[0].unique_id)
            return get_reply_text_xml(msg, u'您已抢到%s的票，不能重复抢票，<a href="%s">查看电子票</a>' % (activity.name, url))


#check return command message
def check_return_cmd(msg):
    return handler_check_text_header(msg, ['退票'])


#return tickets
def return_tickets(msg):
    now = string.atof(msg['CreateTime'])
    now = datetime.datetime.fromtimestamp(now)

    receive_msg = msg['Content']
    receive_msg = receive_msg.split()
    if len(receive_msg) > 1:
        key = receive_msg[1]
    else:
        return get_reply_text_xml(msg, u'您好，格式不正确！请输入“退票 活动代称”。\n如：“退票 马兰花开”将退订马兰花开活动的票。\n（请注意，该操作不可恢复！）')
    activities = Activity.objects.filter(status=1, end_time__gte=now, key=key)

    if not activities.exists():
        return get_reply_text_xml(msg, u'活动不存在或已结束，请重试:)')
    else:
        activity = activities[0]

    if activity.book_start > now:
        start_time = u'%s年%s月%s日%s时%s分' % (activity.book_start.year, activity.book_start.month, activity.book_start.day, activity.book_start.hour, activity.book_start.minute)
        return get_reply_text_xml(msg, u'%s%s开始抢票，<a href="%s">详情</a>' % (activity.name, start_time, s_reverse_activity_detail(activity.id)))
    elif activity.book_end > now:
        fromuser = get_msg_from(msg)
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
            if cmd_list[0] == 'TSINGHUA' and cmd_list[1] == 'BOOK' and cmd_list[2].isdigit():
                return True
    return False


#check unsubscribe event
def check_unsubscribe(msg):
    return handler_check_text(msg, ['解绑']) or handler_check_events(msg, ['unsubscribe'])


#handle unsubscribe event
def get_unsubscibe_response(msg):
    fromuser = get_msg_from(msg)
    if is_authenticated(fromuser):
        user = User.objects.filter(weixin_id=fromuser, status=1).update(status=0)
    return get_reply_text_xml(msg, u'账号绑定已经解除')


#check bind event
def check_bind_account(msg):
    return handler_check_text(msg, ['绑定']) or handler_check_event_click(msg, [WEIXIN_EVENT_KEYS['account_bind']])


#handle bind event
def bind_account(msg):
    fromuser = get_msg_from(msg)
    if is_authenticated(fromuser):
        return get_reply_text_xml(msg, u'若要解绑请回复“解绑”')
    else:
        return get_reply_text_xml(msg, u'<a href="' + s_reverse_validate(fromuser) + '">'
                                       u'点此绑定信息门户账号</a>')


def check_no_book_acts_event(msg):
    return handler_check_event_click(msg, [WEIXIN_EVENT_KEYS['ticket_no_book_recommand']])


def no_book_acts_response(msg):
    return get_reply_text_xml(msg, u'您好，现在没有推荐的抢票活动哟~')