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
url_menu = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=LiBa8GTr0BVuDBj74gqVaM-nJ1zkP0K27c1F5WiFcw9kDvlc_MGPogSj95SbRANkfQfqgspUJ3i_AHL-AbpwhF-n51omSDnUTqR7O2ThNUlYk6GdwAXZEO0w4DQw1o_gMdniYKFMofzIhJQ4_yhLeQ"
FROM_USER_NAME = 'WeixinSimulator'
while True:
    line = raw_input()
    ext_tpl = '<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime>' \
              '<MsgType><![CDATA[%s]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>'
    evt_tpl ='<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime>' \
             '<MsgType><![CDATA[event]]></MsgType><Event><![CDATA[%s]]></Event><EventKey><![CDATA[%s]]></EventKey></xml>'
    data = '{"button":[{"name":"资讯","sub_button":[{"type":"click","name":"新闻","key":"TSINGHUA_WECHAT_NEWS"},' \
           '{"type":"click","name":"热门活动","key":"TSINGHUA_WECHAT_ACTIVITY"},{"type":"click","name":"讲座","key":' \
           '"TSINGHUA_WECHAT_LECTURE"},{"type":"click","name":"查询","key":"TSINGHUA_WECHAT_QUERY"}]},{"name":"服务",' \
           '"sub_button":[{"type":"click","name":"查","key":"TSINGHUA_WECHAT_BOOK_ACTIVITY"},{"type":"click","name":' \
           '"抢","key":"TSINGHUA_WECHAT_BOOK"},{"type":"click","name":"票","key":"TSINGHUA_WECHAT_TICKET"},' \
           '{"type":"click","name":"指路","key":"TSINGHUA_WECHAT_PATH"},{"type":"click",' \
           '"name":"聊天","key":"TSINGHUA_WECHAT_CHAT"}]},{"name":"其他","sub_button":[{"type":"click","name":"绑定",' \
           '"key":"TSINGHUA_WECHAT_BIND"},{"type":"click","name":"部门","key":"TSINGHUA_WECHAT_DEPARTMENT"},{"type":' \
           '"click","name":"社团","key":"TSINGHUA_WECHAT_COMMUNITY"},{"type":"click","name":"吐槽","key":"TSINGHUA_WECHAT_CONFIDE"},' \
           '{"type":"click","name":"帮助","key":"TSINGHUA_WECHAT_HELP"}]}]}'
    #ext_tpl = ext_tpl % (FROM_USER_NAME, FROM_USER_NAME, str(int(time.time())), 'text', '帮助')
    evt_tpl = evt_tpl % (FROM_USER_NAME, FROM_USER_NAME, str(int(time.time())), 'CLICK', 'TSINGHUA_WECHAT_BOOK')
    #req = urllib2.Request(url = url, data = evt_tpl)
    req = urllib2.Request(url=url_menu, data=data)
    resdata = urllib2.urlopen(req)
    res = resdata.read()
    res = unicode(res, "utf-8")
    print res
