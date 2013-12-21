#-*- coding:utf-8 -*-
from userpage.safe_reverse import *
from queryhandler.settings import QRCODE_URL


def time_chs_format(time):
    if time.days > 0:
        result = str(time.days) + u'天'
    elif time.seconds >= 3600:
        result = str(time.seconds / 3600) + u'小时'
    elif time.seconds >= 60:
        result = str(time.seconds / 60) + u'分钟'
    else:
        result = str(time.seconds) + u'秒'
    return result


def get_text_time_standard(dt):
    weekdays = ['一', '二', '三', '四', '五', '六', '日']
    return str(dt.year) + '年' + str(dt.month) + '月' + str(dt.day) + '日 周' + weekdays[dt.isoweekday() - 1] + ' ' \
        + dt.hour + ':' + dt.minute


def get_text_ticket_pic(ticket):
    return QRCODE_URL + str(ticket.unique_id)


def get_text_link(href, title):
    return '<a href="' + href + '">' + title + '</a>'


def get_text_unbinded_template(actname, openid):
    return '对不起，尚未绑定学号，不能' + actname + '。\n' + get_text_link(s_reverse_validate(openid), '点此绑定学号')


def get_text_help_title():
    return '“紫荆之声”使用指南'


def get_text_help_description(isvalidated):
    return '不想错过园子里精彩的资讯？又没时间没心情到处搜罗信息？想要参加高大上的活动却不想提前数小时排队？' \
           '微信“紫荆之声”帮您便捷解决这些问题！快来看看“紫荆之声”怎么使用吧！'\
           + ('\n您尚未绑定学号，回复“绑定”进行相关操作:)' if not isvalidated else '')


def get_text_activity_title_with_status(activity, now):
    title = activity.name
    if activity.book_start > now:
        delta = activity.book_start - now
        title += ('%s后开始抢票' % time_chs_format(delta))
    elif activity.book_end > now:
        title += '抢票进行中'
    else:
        title += '抢票已结束'
    return title


def get_text_activity_description(activity, MAX_LEN):
    act_abstract = activity.description
    if len(act_abstract) > MAX_LEN:
        return act_abstract[0:MAX_LEN] + '...'
    else:
        return act_abstract


def get_text_no_bookable_activity():
    return '您好，目前没有抢票活动'


def get_text_unbinded_exam_ticket(openid):
    return get_text_unbinded_template('查票', openid)


def get_text_one_ticket_title(ticket, now):
    return ticket.activity.name


def get_text_one_ticket_description(ticket, now):
    tmp = '活动时间：' + get_text_time_standard(ticket.activity.start_time) + '\n活动地点：' + ticket.activity.place
    if ticket.activity.book_end > now:
        tmp += ('\n回复“退票 ' + ticket.activity.key + '”即可退票')
    return tmp


def get_text_no_ticket():
    return '您好，您目前没有可用票'


def get_text_exam_tickets(tickets, now):
    reply_content = []
    for ticket in tickets:
        tmp = ticket.activity.name + ' ' + get_text_link(s_reverse_ticket_detail(ticket.unique_id), '电子票')
        bkend = ticket.activity.book_end
        if bkend > now:
            tmp += ('\n（' + time_chs_format(bkend - now) + '内可退票）')
        reply_content.append(tmp)
    return '\n-----------------------\n'.join(reply_content)


def get_text_unbinded_fetch_ticket(openid):
    return get_text_unbinded_template('取票', openid)


def get_text_usage_fetch_ticket():
    return '您好，格式不正确！请输入“取票 活动代称”。\n如：“取票 马兰花开”将向您返回马兰花开活动的电子票。'


def get_text_no_such_activity():
    return '活动不存在或已结束，请重试:)'


def get_text_no_ticket_in_act(activity, now):
    tmp = '您好，没有找到您的票:('
    bkend = activity.book_end
    if bkend > now:
        tmp += '\n该活动距离抢票结束还有' + time_chs_format(bkend - now) + '，快回复“抢票 ' + activity.key + '”试试运气吧！'
    return tmp


def get_text_unbinded_book_ticket(openid):
    return get_text_unbinded_template('抢票', openid)


def get_text_usage_book_ticket():
    return '您好，格式不正确！请输入“抢票 活动代称”。\n如：“抢票 马兰花开”'


def get_text_fail_book_ticket(activity, now):
    return '很抱歉，已经没有余票了，过一段时间再来试试吧:)\n该活动距离抢票结束还有' + time_chs_format(activity.book_end - now)


def get_text_success_book_ticket():
    return '恭喜您，抢票成功！'


def get_text_book_ticket_future(activity, now):
    bkstart = activity.book_start
    return '您好，该活动尚未开始抢票。' + get_text_link(s_reverse_activity_detail(activity.id), '详情') \
           + '\n抢票开始时间：' + get_text_time_standard(bkstart) \
           + '\n（还剩' + time_chs_format(bkstart - now) + '）'


def get_text_existed_book_ticket(ticket):
    return '您已抢到该活动的票，不能重复抢票。\n' + get_text_link(s_reverse_ticket_detail(ticket.unique_id), '查看电子票')


