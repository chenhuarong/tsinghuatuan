#-*- coding:utf-8 -*-

import time


def get_reply_template_xml(msg, msgtype, content):
    return '<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s' \
           '</CreateTime><MsgType><![CDATA[%s]]></MsgType>%s</xml>' \
           % (msg.get('FromUserName', ''), msg.get('ToUserName', ''), int(time.time()), msgtype, content)


def get_reply_text_xml(msg, reply_content):
    return get_reply_template_xml(msg, 'text', '<Content><![CDATA[%s]]></Content>' % reply_content)


# get reply xml(reply news), using msg(source dict object) and reply_content(news, string)
#def get_reply_news_xml(msg, articles, num):
#    ext_tpl = '<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s' \
#              '</CreateTime><MsgType><![CDATA[%s]]></MsgType><ArticleCount>%s</ArticleCount><Articles>%s</Articles>' \
#              '</xml>'
#    ext_tpl = ext_tpl % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 'news', str(num), articles)
#    return ext_tpl

def get_reply_article_xml(article):
    return '<item>' \
           '<Title><![CDATA[%s]]></Title>' \
           '<Description><![CDATA[%s]]></Description>' \
           '<PicUrl><![CDATA[%s]]></PicUrl>' \
           '<Url><![CDATA[%s]]></Url>' \
           '</item>' \
           % (article.get('title', ''), article.get('description', ''),
              article.get('pic_url', ''), article.get('url', ''))


def get_reply_news_xml(msg, articles):
    if len(articles) > 10:
        tenarticles = articles[0:10]
    else:
        tenarticles = articles
    tmpxml = []
    for article in tenarticles:
        tmpxml.append(get_reply_article_xml(article))
    return get_reply_template_xml(msg, 'news', '<ArticleCount>%s</ArticleCount>'
                                               '<Articles>%s</Articles>'
                                               % (len(tenarticles), ''.join(tmpxml)))


def get_reply_single_news_xml(msg, article):
    return get_reply_news_xml(msg, [article])


