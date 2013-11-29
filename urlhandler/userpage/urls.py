from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
                       url(r'^$', 'userpage.views.home'),
                       url(r'^validate/$', 'userpage.views.validate_view'),
                       url(r'^validate/try$', 'userpage.views.validate_post'),
                       )