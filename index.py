#-*- coding:utf-8 -*-

# wsgi entry for bae

from app import app

from bae.core.wsgi import WSGIApplication
application = WSGIApplication(app)
