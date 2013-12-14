from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
                       url(r'^$', 'adminpage.views.home'),
                       url(r'^list/$', 'adminpage.views.activity_list'),
                       url(r'^detail/(?P<actid>\d+)/$', 'adminpage.views.activity_detail'),
                       url(r'^checkin/(?P<actid>\d+)/$', 'adminpage.views.activity_checkin'),
                       url(r'^checkin/(?P<actid>\d+)/check/', 'adminpage.views.activity_checkin_post'),
                       url(r'^add/$', 'adminpage.views.activity_add'),
                       url(r'^delete/$', 'adminpage.views.activity_delete'),
                       url(r'^modify/$', 'adminpage.views.activity_post'),
                       url(r'^login/$', 'adminpage.views.login'),
                       url(r'^logout/$', 'adminpage.views.logout'),
                       url(r'^order/$', 'adminpage.views.order_list'),
                       url(r'^print/(?P<unique_id>\d+)/$', 'adminpage.views.print_ticket'),
                       url(r'^menu/adjust/$', 'adminpage.views.adjust_menu_view'),
                       url(r'^menu/get/$', 'adminpage.views.custom_menu_get'),
                       url(r'^menu/submit/$', 'adminpage.views.custom_menu_modify_post'),
                       )