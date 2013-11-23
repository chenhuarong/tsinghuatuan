#-*- coding:utf-8 -*-

# 这个文件用于微信文本消息测试。运行后会不断读取键盘输入，每个输入对应返回的结果会直接输出。
# the result will do nothing of transition to handle all kinds of return types(we have two types at least, that is text and link).
import sys
import urllib2
import time
from settings import LOCAL_PORT
from settings import LUCKY_URL
import xml.etree.ElementTree as ET

url = 'http://localhost:' + str(LOCAL_PORT) + LUCKY_URL
FROM_USER_NAME = 'WeixinSimulator'
while True:
    line = raw_input()
    ext_tpl = '<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[%s]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>'
    ext_tpl = ext_tpl % (FROM_USER_NAME, FROM_USER_NAME, str(int(time.time())), 'text',   line)
    req = urllib2.Request(url = url, data = ext_tpl)
    resdata = urllib2.urlopen(req)
    res = resdata.read()
    res = unicode(res, "utf-8")
    print res
