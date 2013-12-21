#-*- coding:utf-8 -*-


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


def get_text_help_title():
    return '“紫荆之声”使用指南'


def get_text_help_description(isvalidated):
    return '不想错过园子里精彩的资讯？又没时间没心情到处搜罗信息？想要参加高大上的活动却不想提前数小时排队？' \
           '微信“紫荆之声”帮您便捷解决这些问题！快来看看“紫荆之声”怎么使用吧！'\
           + ('\n您尚未绑定学号，回复“绑定”进行相关操作:)' if isvalidated else '')


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


