from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
                       url(r'^$', 'userpage.views.home'),
                       url(r'^validate/try/$', 'userpage.views.validate_post'),
                       url(r'^validate/(?P<openid>\S+)/$', 'userpage.views.validate_view'),
                       url(r'^activity/(?P<activityid>\d+)/$','userpage.views.details_view'),
                       url(r'^ticket/(?P<uid>\S+)/$','userpage.views.ticket_view'),
                       )