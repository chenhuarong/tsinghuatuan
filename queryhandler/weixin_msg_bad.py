#-*- coding:utf-8 -*-

import time
from abc import ABCMeta, abstractmethod


class weixin_content_base:
    __metaclass__ = ABCMeta

    @abstractmethod
    def msg_type(self):
        return 'base'

    @abstractmethod
    def __str__(self):
        return 'base'


class weixin_text(weixin_content_base):
    content = ''

    def __init__(self, content=''):
        self.content = content

    def msg_type(self):
        return 'text'

    def __str__(self):
        return '<MsgType><![CDATA[text]]></MsgType>' \
               '<Content><![CDATA[%s]]></Content>' % self.content


class weixin_image(weixin_content_base):
    media_id = 0

    def __init__(self, media_id=0):
        self.media_id = media_id

    def msg_type(self):
        return 'image'

    def __str__(self):
        return '<MsgType><![CDATA[image]]></MsgType>' \
               '<Image><MediaId><![CDATA[%s]]></MediaId></Image>' % self.media_id


class weixin_voice(weixin_content_base):
    media_id = 0

    def __init__(self, media_id=0):
        self.media_id = media_id

    def msg_type(self):
        return 'voice'

    def __str__(self):
        return '<MsgType><![CDATA[voice]]></MsgType>' \
               '<Voice><MediaId><![CDATA[%s]]></MediaId></Voice>' % self.media_id


class weixin_video(weixin_content_base):
    media_id = 0
    title = ''
    description = ''

    def __init__(self, media_id=0, title='', description=''):
        self.media_id = media_id
        self.title = title
        self.description = description

    def msg_type(self):
        return 'video'

    def __str__(self):
        return '<MsgType><![CDATA[video]]></MsgType>' \
               '<Video>' \
               '<MediaId><![CDATA[%s]]></MediaId>' \
               '<Title><![CDATA[%s]]></Title>' \
               '<Description><![CDATA[%s]]></Description>' \
               '</Video>' % (self.media_id, self.title, self.description)


class weixin_music(weixin_content_base):
    title = ''
    description = ''
    music_url = ''
    hq_music_url = ''
    thumb_media_id = 0

    def __init__(self, title='', description='', music_url='', hq_music_url='', thumb_media_id=0):
        self.title = title
        self.description = description
        self.music_url = music_url
        self.hq_music_url = hq_music_url
        self.thumb_media_id = thumb_media_id

    def msg_type(self):
        return 'music'

    def __str__(self):
        return '<MsgType><![CDATA[music]]></MsgType>' \
               '<Music>' \
               '<Title><![CDATA[%s]]></Title>' \
               '<Description><![CDATA[%s]]></Description>' \
               '<MusicUrl><![CDATA[%s]]></MusicUrl>' \
               '<HQMusicUrl><![CDATA[%s]]></HQMusicUrl>' \
               '<ThumbMediaId><![CDATA[%s]]></ThumbMediaId>' \
               '</Music>' % (self.title, self.description, self.music_url, self.hq_music_url, self.thumb_media_id)


class weixin_article_item(weixin_content_base):
    title = ''
    description = ''
    pic_url = ''
    url = ''

    def __init__(self, title='', description='', pic_url='', url=''):
        self.title = title
        self.description = description
        self.pic_url = pic_url
        self.url = url

    def msg_type(self):
        return 'article'

    def __str__(self):
        return '<item>' \
               '<Title><![CDATA[%s]]></Title>' \
               '<Description><![CDATA[%s]]></Description>' \
               '<PicUrl><![CDATA[%s]]></PicUrl>' \
               '<Url><![CDATA[%s]]></Url>' \
               '</item>' % (self.title, self.description, self.pic_url, self.url)


class weixin_articles(weixin_content_base):
    __articles = []

    def __init__(self):
        self.__articles = []

    def add_article(self, title, description, pic_url, url):
        if len(self.__articles) >= 10:
            raise Exception('Too many articles! Weixin articles can not be more than 10.')
        self.__articles.append(weixin_article_item(title=title, description=description, pic_url=pic_url, url=url))

    def clear_articles(self):
        self.__articles[:] = []

    def msg_type(self):
        return 'news'

    def __str__(self):
        tmpstrlst = []
        for article in self.__articles:
            tmpstrlst.append(str(article))
        return '<MsgType><![CDATA[news]]></MsgType>' \
               '<ArticleCount>%s</ArticleCount>' \
               '<Articles>%s</Articles>' % (len(self.__articles), ''.join(tmpstrlst))


class weixin_location(weixin_content_base):
    location_x = 0
    location_y = 0
    scale = 20
    label = ''

    def __init__(self, location_x=0, location_y=0, scale=20, label=''):
        self.location_x = location_x
        self.location_y = location_y
        self.scale = scale
        self.label = label

    def msg_type(self):
        return 'location'

    def __str__(self):
        return '<MsgType><![CDATA[location]]></MsgType>' \
               '<Location_X>%s</Location_X>' \
               '<Location_Y>%s</Location_Y>' \
               '<Scale>%s</Scale>' \
               '<Label><![CDATA[%s]]></Label>' % (self.location_x, self.location_y, self.scale, self.label)


class weixin_link(weixin_content_base):
    title = ''
    description = ''
    url = ''

    def __init__(self, title='', description='', url=''):
        self.title = title
        self.description = description
        self.url = url

    def msg_type(self):
        return 'link'

    def __str__(self):
        return '<MsgType><![CDATA[link]]></MsgType>' \
               '<Title><![CDATA[%s]]></Title>' \
               '<Description><![CDATA[%s]]></Description>' \
               '<Url><![CDATA[%s]]></Url>' % (self.title, self.description, self.url)


class weixin_event(weixin_content_base):
    event = ''
    event_key = ''

    def __init__(self, event='', event_key=''):
        self.event = event
        self.event_key = event_key

    def msg_type(self):
        return 'event'

    def __str__(self):
        return '<MsgType><![CDATA[event]]></MsgType>' \
               '<Event><![CDATA[%s]]></Event>' \
               '<EventKey><![CDATA[%s]]></EventKey>' % (self.event, self.event_key)


class weixin_msg:
    from_user = ''
    to_user = ''
    create_time = int(time.time())
    content = weixin_content_base()

    def __init__(self, from_user='', to_user='', create_time=int(time.time()), content=''):
        self.from_user = from_user
        self.to_user = to_user
        self.create_time = create_time
        self.content = content

    def exchange_from_to(self):
        tmp_usr = self.from_user
        self.from_user = self.to_user
        self.to_user = tmp_usr
        return self

    def __str__(self):
        return '<xml>' \
               '<ToUserName><![CDATA[%s]]></ToUserName>' \
               '<FromUserName><![CDATA[%s]]></FromUserName>' \
               '<CreateTime>%s</CreateTime>' \
               '%s' \
               '</xml>' % (self.to_user, self.from_user, self.create_time, str(self.content))


def is_text(msg):
    return msg.content.msg_type() == 'text'


def is_image(msg):
    return msg.content.msg_type() == 'image'


def is_voice(msg):
    return msg.content.msg_type() == 'voice'


def is_video(msg):
    return msg.content.msg_type() == 'video'


def is_location(msg):
    return msg.content.msg_type() == 'location'


def is_link(msg):
    return msg.content.msg_type() == 'link'


def is_news(msg):
    return msg.content.msg_type() == 'news'


def get_weixin_msg(msg):
    if msg['MsgType'] == 'text':
        content = weixin_text(msg['Content'])
    elif msg['MsgType'] == 'image':
        content = weixin_image(msg[''])


