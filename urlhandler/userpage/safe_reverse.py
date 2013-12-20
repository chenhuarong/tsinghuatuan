from django.core.urlresolvers import reverse
from queryhandler.settings import SITE_DOMAIN


def s_reverse_validate(openid):
    return SITE_DOMAIN + reverse('userpage.views.validate_view', kwargs={'openid': openid})


def s_reverse_activity_detail(activityid):
    return SITE_DOMAIN + reverse('userpage.views.details_view', kwargs={'activityid': activityid})


def s_reverse_ticket_detail(uid):
    return SITE_DOMAIN + reverse('userpage.views.ticket_view', kwargs={'uid': uid})


def s_reverse_help():
    return SITE_DOMAIN + reverse('userpage.views.help_view')


