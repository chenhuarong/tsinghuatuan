__author__ = 'Epsirom'

import urllib2
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def http_get(url):
    req = urllib2.Request(url=url)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res


def http_post(url, data):
    req = urllib2.Request(url=url, data=data)  #urllib2.quote(data, '[{",:}] ').replace('%', '\\x'))
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res


def http_post_dict(url, data):
    return http_post(url, json.dumps(data))


