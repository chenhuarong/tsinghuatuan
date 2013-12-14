__author__ = 'Epsirom'

from weixinlib.settings import WEIXIN_TOKEN
from weixinlib.weixin_urls import WEIXIN_URLS
import json
from weixinlib import http_get


def get_access_token():
    url = WEIXIN_URLS['access_token']()
    res = http_get(url)
    rjson = json.loads(res)
    if 'errorcode' in rjson:
        raise res
    return rjson['access_token']

