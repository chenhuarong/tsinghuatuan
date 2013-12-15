#-*- coding:utf-8 -*-

__author__ = 'Epsirom'

from queryhandler.settings import WEIXIN_TOKEN


WEIXIN_APPID = 'wxb2545ef150be8096'

WEIXIN_SECRET = 'c0739f56c0f676c0e2850ef286d754bf'

WEIXIN_CUSTOM_MENU_TEMPLATE = {
    "button": [
        {
            "name": "资讯",
            "sub_button": [
                {
                    "type": "click",
                    "name": "活动",
                    "key": "TSINGHUA_ACTIVITY",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "讲座",
                    "key": "TSINGHUA_LECTURE",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "新闻",
                    "key": "TSINGHUA_NEWS",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "人物",
                    "key": "TSINGHUA_FIGURE",
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
                {
                    "type": "click",
                    "name": "指路",
                    "key": "TSINGHUA_PATH",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "绑定",
                    "key": "TSINGHUA_BIND",
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