#-*- coding:utf-8 -*-

# 这个文件用于微信文本消息测试。运行后会不断读取键盘输入，每个输入对应返回的结果会直接输出。
# the result will do nothing of transition to handle all kinds of return types(we have two types at least, that is text and link).
import sys
import urllib2
import time
from settings import LOCAL_PORT
from settings import LUCKY_URL
import xml.etree.ElementTree as ET
import qrcode

url = 'http://localhost:' + str(LOCAL_PORT) + LUCKY_URL
url_token = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wxb2545ef150be8096&secret=c0739f56c0f676c0e2850ef286d754bf"
url_menu = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=tXiFoEsjnwcql3eC3ae_L3hF5OJbtPvoc8HTWwPRndt23ncxtwO9dZ27tNKl777i_39pNH6WeJKlt1kH1gz62iD8js8A8JN7DTRF2CLDCGtpx-NnYOxrM9mgzVfKAO6N_ptLfNe39XfcxKMVAZxl4g"
FROM_USER_NAME = 'test2'
while True:
    line = raw_input()
    ext_tpl = '<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime>' \
              '<MsgType><![CDATA[%s]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>'
    evt_tpl ='<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime>' \
             '<MsgType><![CDATA[event]]></MsgType><Event><![CDATA[%s]]></Event><EventKey><![CDATA[%s]]></EventKey></xml>'
    data = '{"button":[{"name":"资讯","sub_button":[{"type":"click","name":"活动","key":"TSINGHUA_ACTIVITY"},' \
           '{"type":"click","name":"讲座","key":"TSINGHUA_LECTURE"},{"type":"click","name":"新闻","key":' \
           '"TSINGHUA_NEWS"},{"type":"click","name":"人物","key":"TSINGHUA_FIGURE"}]},{"name":"服务",' \
           '"sub_button":[{"type":"click","name":"抢啥","key":"TSINGHUA_BOOK_WHAT"},{"type":"click","name":' \
           '"查票","key":"TSINGHUA_TICKET"},{"type":"click","name":"指路","key":"TSINGHUA_PATH"},' \
           '{"type":"click","name":"绑定","key":"TSINGHUA_BIND"}]},{"name":"抢票","sub_button":' \
           '[{"type":"click","name":"新年音乐会","key":"TSINGHUA_BOOK_1"},{"type":"click","name":"新年晚会",' \
           '"key":"TSINGHUA_BOOK_2"}]}]}'
    ext_tpl = ext_tpl % (FROM_USER_NAME, FROM_USER_NAME, str(int(time.time())), 'text', '取票 新年')
   #evt_tpl = evt_tpl % (FROM_USER_NAME, FROM_USER_NAME, str(int(time.time())), 'CLICK', 'TSINGHUA_BOOK_1')
    req = urllib2.Request(url = url, data = ext_tpl)
    #req = urllib2.Request(url=url_menu, data = data)
    resdata = urllib2.urlopen(req)
    res = resdata.read()
    res = unicode(res, "utf-8")
    print res
