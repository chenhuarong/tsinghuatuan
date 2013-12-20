from django.core.urlresolvers import reverse


def s_reverse_admin_home():
    return reverse('adminpage.views.home')


def s_reverse_activity_list():
    return reverse('adminpage.views.activity_list')


def s_reverse_activity_checkin(actid):
    return reverse('adminpage.views.activity_checkin', kwargs={'actid': actid})


def s_reverse_activity_checkin_post(actid):
    return reverse('adminpage.views.activity_checkin_post', kwargs={'actid': actid})


def s_reverse_admin_login_post():
    return reverse('adminpage.views.login')


def s_reverse_admin_logout():
    return reverse('adminpage.views.logout')


def s_reverse_activity_delete():
    return reverse('adminpage.views.activity_delete')


def s_reverse_activity_add():
    return reverse('adminpage.views.activity_add')


def s_reverse_activity_detail(actid):
    return reverse('adminpage.views.activity_detail', kwargs={'actid': actid})


def s_reverse_activity_post():
    return reverse('adminpage.views.activity_post')


def s_reverse_order_index():
    return reverse('adminpage.views.order_index')


def s_reverse_order_login():
    return reverse('adminpage.views.order_login')


def s_reverse_order_logout():
    return reverse('adminpage.views.order_logout')


def s_reverse_order_list():
    return reverse('adminpage.views.order_list')


def s_reverse_print_ticket(unique_id):
    return reverse('adminpage.views.print_ticket', kwargs={'unique_id': unique_id})


def s_reverse_adjust_menu():
    return reverse('adminpage.views.adjust_menu_view')


def s_reverse_get_menu():
    return reverse('adminpage.views.custom_menu_get')


def s_reverse_modify_menu():
    return reverse('adminpage.views.custom_menu_modify_post')

