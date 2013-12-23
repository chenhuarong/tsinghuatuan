#-*- coding:utf-8 -*-
from userpage.safe_reverse import *
from queryhandler.settings import QRCODE_URL


def time_chs_format(time):
    if time.days != 0:
        result = str(time.days) + u'天'
    elif time.seconds >= 3600:
        result = str(time.seconds / 3600) + u'小时'
    elif time.seconds >= 60:
        result = str(time.seconds / 60) + u'分钟'
    else:
        result = str(time.seconds) + u'秒'
    return result


def get_text_two_digit(num):
    if num < 10:
        return '0' + str(num)
    else:
        return str(num)


def get_text_time_standard(dt):
    weekdays = ['一', '二', '三', '四', '五', '六', '日']
    return str(dt.year) + '年' + get_text_two_digit(dt.month) + '月' \
        + get_text_two_digit(dt.day) + '日 周' + weekdays[dt.isoweekday() - 1] + ' ' \
        + get_text_two_digit(dt.hour) + ':' + get_text_two_digit(dt.minute)


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
        title += ('\n（%s后开始抢票）' % time_chs_format(delta))
    elif activity.book_end > now:
        title += '\n（抢票进行中）'
    else:
        title += '\n（抢票已结束）'
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


def get_text_seat_desc_BC(seat):
    if seat == 'B':
        return '您的座位在B区，请从东南口进入。'
    elif seat == 'C':
        return '您的座位在C区，请从西北口进入。'
    else:
        return '您的座位信息无效'


def get_text_one_ticket_description(ticket, now):
    tmp = '活动时间：' + get_text_time_standard(ticket.activity.start_time) + '\n活动地点：' + ticket.activity.place
    if ticket.activity.seat_status == 1:
        tmp += ('\n' + get_text_seat_desc_BC(ticket.seat))
    if ticket.activity.book_end > now:
        tmp += ('\n回复“退票 ' + ticket.activity.key + '”即可退票。')
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


def get_text_no_such_activity(actname=''):
    if actname == '':
        return '活动不存在或已结束，请重试:)'
    else:
        return '活动不存在或不在' + actname + '时间范围内，请重试:)'


def get_text_no_ticket_in_act(activity, now):
    tmp = '您好，没有找到您的票:('
    bkend = activity.book_end
    if bkend > now:
        tmp += '\n该活动距离抢票结束还有' + time_chs_format(bkend - now) + '，快回复“抢票 ' + activity.key + '”试试运气吧！'\
               + get_text_link(s_reverse_activity_detail(activity.id), '详情')
    return tmp


def get_text_unbinded_book_ticket(openid):
    return get_text_unbinded_template('抢票', openid)


def get_text_usage_book_ticket():
    return '您好，格式不正确！请输入“抢票 活动代称”。\n如：“抢票 马兰花开”'


def get_text_fail_book_ticket(activity, now):
    return '很抱歉，已经没有余票了，过一段时间再来试试吧:)\n该活动距离抢票结束还有' + time_chs_format(activity.book_end - now)


def get_text_success_book_ticket():
    return '恭喜您，抢票成功！\n'


def get_text_book_ticket_future(activity, now):
    bkstart = activity.book_start
    return '您好，该活动还没开始抢票哟~' + get_text_link(s_reverse_activity_detail(activity.id), '详情') \
           + '\n抢票开始时间：' + get_text_time_standard(bkstart) \
           + '\n（还剩' + time_chs_format(bkstart - now) + '）'


def get_text_existed_book_ticket(ticket):
    return '您已抢到该活动的票，不能重复抢票。\n' + get_text_link(s_reverse_ticket_detail(ticket.unique_id), '查看电子票')


def get_text_unbinded_cancel_ticket(openid):
    return get_text_unbinded_template('退票', openid)


def get_text_usage_cancel_ticket():
    return '您好，格式不正确！请输入“退票 活动代称”。\n如：“退票 马兰花开”将退订马兰花开活动的票。\n（请注意，该操作不可恢复！）'


def get_text_success_cancel_ticket():
    return '退票成功，欢迎关注下次活动'


def get_text_fail_cancel_ticket():
    return '未找到您的抢票记录，退票失败'


def get_text_timeout_cancel_ticket():
    return '该活动的抢票时间已过，不能退票，您可以将票转让给他人（直接转发电子票即可）'


def get_text_unbind_success(openid):
    return '学号绑定已经解除\n' + get_text_link(s_reverse_validate(openid), '重新绑定')


def get_text_binded_account(stuid):
    return '您已经绑定了学号' + stuid + '，若要解绑请回复“解绑”'


def get_text_to_bind_account(openid):
    return '抢票等功能必须绑定学号后才能使用。\n' + get_text_link(s_reverse_validate(openid), '点此绑定学号')


def get_text_hint_no_book_acts():
    return '您好，现在没有推荐的抢票活动哟~'


def get_text_timeout_book_event():
    return '该活动已过抢票时间，您没有抢到票:('


def get_text_existed_book_event():
    return ''
    #return '您已有票，自动切换为取票。\n'


def get_text_usage_get_activity_menu():
    return '您好，格式不正确！请输入“节目单 活动代称”。\n如：“节目单 新年联欢晚会”将向您返回新年联欢晚会的节目单。'


def get_text_fail_get_activity_menu(activity, now):
    sst = activity.start_time
    return '您好，活动开始后才可以查看节目单哟~\n活动开始时间：' + get_text_time_standard(sst) \
           + '\n（还剩' + time_chs_format(sst - now) + '）'


def get_text_title_activity_menu(activity):
    return activity.name + ' - 节目单'


def get_text_desc_activity_menu(activity):
    return '活动开始时间：' + get_text_time_standard(activity.start_time) \
           + '\n活动结束时间：' + get_text_time_standard(activity.end_time)


def get_text_no_activity_menu():
    return '您好，该活动未提供节目单。'


