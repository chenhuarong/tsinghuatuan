from weixinlib.weixin_urls import WEIXIN_URLS
from weixinlib.base_support import get_access_token
from weixinlib import http_get, http_post
from weixinlib.settings import WEIXIN_BOOK_HEADER, get_custom_menu_with_book_acts
from urlhandler.models import Activity
import json
import datetime


def get_custom_menu():
    access_token = get_access_token()
    url = WEIXIN_URLS['get_custom_menu'](access_token)
    res = http_get(url)
    rjson = json.loads(res)
    return rjson.get('menu', {}).get('button', [])


def modify_custom_menu(buttons):
    #print buttons
    access_token = get_access_token()
    url = WEIXIN_URLS['modify_custom_menu'](access_token)
    res = http_post(url, buttons)
    return res


def check_if_activity_out(actid, actsHolder):
    try:
        activity = Activity.objects.get(id=actid, status=1)
        if actsHolder:
            actsHolder[WEIXIN_BOOK_HEADER + str(actid)] = activity
    except:
        return True
    if datetime.datetime.now() >= activity.end_time:
        return True
    return False


def auto_clear_old_menus(buttons):
    activities = {}
    toremove = []
    flag = False
    for button in buttons:
        try:
            if check_if_activity_out(int(button['key'].split('_')[-1]), actsHolder=activities):
                toremove.append(button)
                flag = True
        except:
            continue
    for mv in toremove:
        buttons.remove(mv)
    while len(buttons) > 5:
        dstBtn = buttons[0]
        for button in buttons:
            if activities[button['key']].book_start > activities[dstBtn['key']].book_start:
                dstBtn = button
        buttons.remove(dstBtn)
        flag = True
    return flag


def add_new_custom_menu(name, key):
    buttons = get_custom_menu()
    current_menu = []
    flag = False
    for button in buttons:
        sbtns = button.get('sub_button', [])
        if len(sbtns) > 0:
            tmpkey = sbtns[0].get('key', '')
            if (not tmpkey.startswith(WEIXIN_BOOK_HEADER + 'W')) and tmpkey.startswith(WEIXIN_BOOK_HEADER):
                current_menu = sbtns
                break
    for menu in current_menu:
        if menu['key'] == key:
            flag = True
            break
    if not flag:
        current_menu.append({
            'type': 'click',
            'name': name,
            'key': key,
            'sub_button': [],
        })
    auto_clear_old_menus(current_menu)
    return modify_custom_menu(json.dumps(get_custom_menu_with_book_acts(current_menu), ensure_ascii=False).encode('utf8'))

