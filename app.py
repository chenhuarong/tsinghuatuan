#-*- coding:utf-8 -*-

LUCKY_URL = "/weixin"

import os
import sys

path = os.path.dirname(os.path.abspath(__file__)) + '/urlhandler'
if path not in sys.path:
    sys.path.insert(1, path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "urlhandler.settings")

from django.core.handlers.wsgi import WSGIHandler
django_WSGI = WSGIHandler()

from queryhandler import handle_weixin_request

def app(environ, start_response):
    print environ['PATH_INFO']
    if environ['PATH_INFO'] == LUCKY_URL:
        result = handle_weixin_request(environ)
        status = '200 OK'
        headers = [('Content-type', 'text/html')]
        start_response(status, headers)
        return [result.encode('utf8')]
    else:
        return django_WSGI.__call__(environ, start_response)