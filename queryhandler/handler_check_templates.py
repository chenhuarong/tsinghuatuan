#-*- coding:utf-8 -*-


def is_msgtype(msg, msgtype):
    return msg['MsgType'] == msgtype


def handler_check_text(msg, texts):
    return is_msgtype(msg, 'text') and (msg['Content'].lower() in texts)


def handler_check_event_click(msg, event_keys):
    return is_msgtype(msg, 'event') and (msg['Event'] == 'CLICK') and (msg['EventKey'] in event_keys)


def handler_check_events(msg, events):
    return is_msgtype(msg, 'event') and (msg['Event'] in events)


def handler_check_text_header(msg, headers):
    if not is_msgtype(msg, 'text'):
        return False
    tmpstrs = msg['Content'].split()
    if len(tmpstrs) == 0:
        return False
    return tmpstrs[0] in headers