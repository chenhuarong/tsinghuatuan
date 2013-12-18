#-*- coding:utf-8 -*-

__author__ = 'Epsirom'

from queryhandler.settings import WEIXIN_TOKEN


WEIXIN_APPID = 'wx92e46b77ae0a6834'

WEIXIN_SECRET = 'a4fb3162fb38f3b385e444285245074b'

WEIXIN_EVENT_KEYS = {
    'info_activity': 'V1001_TODAT_ACTIVE',
    'info_lecture': 'V1001_TODAT_LECTURE',
    'info_news': 'V1001_SCHOOL_NEWS',
    'info_organization': 'V1001_OGNIZATION',
    'ticket_book_what': 'TSINGHUA_BOOK_WHAT',
    'ticket_get': 'TSINGHUA_TICKET',
    'account_bind': 'TSINGHUA_BIND',
    'help': 'TSINGHUA_HELP',
    'ticket_no_book_recommand': 'TSINGHUA_NO_BOOK_ACTS',
    'ticket_book_header': 'TSINGHUA_BOOK_',
    'modern_figure': 'V1001_MODERN_FIGURE',
}

WEIXIN_CUSTOM_MENU_TEMPLATE = {
    "button": [
        {
            "name": "资讯",
            "sub_button": [
                {
                    "type": "click",
                    "name": "活动",
                    "key": "V1001_TODAT_ACTIVE",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "讲座",
                    "key": "V1001_TODAT_LECTURE",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "新闻",
                    "key": "V1001_SCHOOL_NEWS",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "人物",
                    "key": "V1001_MODERN_FIGURE",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "协会",
                    "key": "V1001_OGNIZATION",
                    "sub_button": []
                }
            ]
        },
        {
            "name": "服务",
            "sub_button": [
                {
                    "type": "click",
                    "name": "抢啥",
                    "key": "TSINGHUA_BOOK_WHAT",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "查票",
                    "key": "TSINGHUA_TICKET",
                    "sub_button": []
                },
                #{
                #    "type": "click",
                #    "name": "指路",
                #    "key": "TSINGHUA_PATH",
                #    "sub_button": []
                #},
                {
                    "type": "click",
                    "name": "绑定",
                    "key": "TSINGHUA_BIND",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "帮助",
                    "key": "TSINGHUA_HELP",
                    "sub_button": []
                }
            ]
        },
        {
            "name": "抢票",
            "sub_button": []
        }
    ]
}

WEIXIN_BOOK_HEADER = 'TSINGHUA_BOOK_'

def get_custom_menu_with_book_acts(actbtns):
    tmpmenu = WEIXIN_CUSTOM_MENU_TEMPLATE.copy()
    book_btn = tmpmenu['button'][2]
    if len(actbtns) == 0:
        book_btn['type'] = 'click'
        book_btn['key'] = 'TSINGHUA_NO_BOOK_ACTS'
    else:
        book_btn['sub_button'] = actbtns
    return tmpmenu

