__author__ = 'Epsirom'
from weixinlib.settings import WEIXIN_APPID, WEIXIN_SECRET


def access_token_url_generator():
    return 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (WEIXIN_APPID, WEIXIN_SECRET)


def get_custom_menu_url_generator(access_token):
    return 'https://api.weixin.qq.com/cgi-bin/menu/get?access_token=%s' % (access_token, )


def modify_custom_menu_url_generator(access_token):
    return 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s' % (access_token, )


