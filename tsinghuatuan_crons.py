
import os
import sys

path = os.path.dirname(os.path.abspath(__file__)).replace('\\','/') + '/urlhandler'
if path not in sys.path:
    sys.path.insert(1, path)
os.environ.setdefault('SSAST_DEPLOYMENT', 'tsinghuatuan')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "urlhandler.settings")

from weixinlib.custom_menu import *
import json


def auto_clean_custom_menus():
    custom_buttons = get_custom_menu()
    current_menu = []
    for button in custom_buttons:
        sbtns = button.get('sub_button', [])
        if len(sbtns) > 0:
            tmpkey = sbtns[0].get('key', '')
            if (not tmpkey.startswith(WEIXIN_BOOK_HEADER + 'W')) and tmpkey.startswith(WEIXIN_BOOK_HEADER):
                current_menu = sbtns
                break
    if auto_clear_old_menus(current_menu):
        modify_custom_menu(json.dumps(get_custom_menu_with_book_acts(current_menu), ensure_ascii=False).encode('utf8'))


auto_clean_custom_menus()
