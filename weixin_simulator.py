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
url_token = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wxb2545ef150be8096&secret=c0739f56c0f676c0e2850ef286d754bf"
url_menu = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=y_yyhJmDinOV9WvE4cVorZ5YDR2xXsNKgL36khCQYHNoxqKxyATwS860wANpUz0DndXwBeAMAGLhtmkO1QAONvMQwak3WKKM9Btj-9Y17j0sVSMiXjCA3h9wPSYmTLg8vMXsUPVmy8mzGRf8fzuVzw"
FROM_USER_NAME = 'WeixinSimulator'
while True:
    line = raw_input()
    ext_tpl = '<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime>' \
              '<MsgType><![CDATA[%s]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>'
    evt_tpl ='<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime>' \
             '<MsgType><![CDATA[event]]></MsgType><Event><![CDATA[%s]]></Event><EventKey><![CDATA[%s]]></EventKey></xml>'
    data = ' {"button":[{"name":"活动","sub_button":[{"type":"view","name":"新年音乐会","url":"http://student.tsinghua.edu.cn/"},' \
           '{"type":"view","name":"马兰花开","url":"http://student.tsinghua.edu.cn/"},{"type":"click","name":"全部",' \
           '"key":"TSINGHUATUAN_ALL"}]},{"type":"click","name":"订票","key":"TSINGHUATUAN_BOOK"},{"type":"click",' \
           '"name":"订单","key":"TSINGHUATUAN_ORDER"}]}'
    ext_tpl = ext_tpl % (FROM_USER_NAME, FROM_USER_NAME, str(int(time.time())), 'text', line)
    #evt_tpl = evt_tpl % (FROM_USER_NAME, FROM_USER_NAME, str(int(time.time())), 'CLICK', 'TSINGHUATUAN_ORDER')
    req = urllib2.Request(url = url, data = ext_tpl)
    #req = urllib2.Request(url = url_menu, data = data)
    resdata = urllib2.urlopen(req)
    res = resdata.read()
    res = unicode(res, "utf-8")
    print res
