__author__ = 'Epsirom'



from weixinlib.url_generators import *



WEIXIN_URLS = {
    'access_token': access_token_url_generator,
    'get_custom_menu': get_custom_menu_url_generator,
    'modify_custom_menu': modify_custom_menu_url_generator,

}
