__author__ = 'Epsirom'

import urllib2
from queryhandler.settings import INFORMATION_SITE_DOMAIN


def get_information_response(data):
    req = urllib2.Request(url=INFORMATION_SITE_DOMAIN, data=data)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res

