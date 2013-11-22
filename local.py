#-*- coding:utf-8 -*-

# this file is prepared for run server locally
# if deployed in bae, index.py will work, but it will be totally the same as local.

from wsgiref.simple_server import make_server
from app import app

LOCAL_PORT = 8000

httpd = make_server('', LOCAL_PORT, app)
httpd.serve_forever()
