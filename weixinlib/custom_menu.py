__author__ = 'Epsirom'

from weixinlib.settings import WEIXIN_TOKEN
from weixinlib.weixin_urls import WEIXIN_URLS
from weixinlib.base_support import get_access_token
from weixinlib import http_get, http_post_dict, http_post
import json


def get_custom_menu():
    access_token = get_access_token()
    url = WEIXIN_URLS['get_custom_menu'](access_token)
    res = http_get(url)
    rjson = json.loads(res)
    return rjson.get('menu',{}).get('button', [])


def modify_custom_menu(buttons):
    access_token = get_access_token()
    url = WEIXIN_URLS['modify_custom_menu'](access_token)
    res = http_post(url, buttons)
    return res

