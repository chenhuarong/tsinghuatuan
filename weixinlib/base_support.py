__author__ = 'Epsirom'

from weixinlib.settings import WEIXIN_TOKEN
from weixinlib.weixin_urls import WEIXIN_URLS
import json
from weixinlib import http_get
import hashlib


#last_timestamp = int((datetime.datetime.now() + datetime.timedelta(seconds=-5)).strftime('%s'))


# check signature as the weixin API document provided
def check_weixin_signature(signature, timestamp, nonce):
    #global last_timestamp
    #timestamp_int = int(timestamp)
    #if timestamp_int < last_timestamp - 5:
    #    return Falsech
    token = WEIXIN_TOKEN

    tmp_list = [token, timestamp, nonce]
    tmp_list.sort()
    tmpstr = '%s%s%s' % tuple(tmp_list)
    tmpstr = hashlib.sha1(tmpstr).hexdigest()
    if tmpstr == signature:
        #last_timestamp = timestamp_int
        return True
    else:
        return False


def get_access_token():
    url = WEIXIN_URLS['access_token']()
    res = http_get(url)
    rjson = json.loads(res)
    if 'errorcode' in rjson:
        raise res
    return rjson['access_token']

