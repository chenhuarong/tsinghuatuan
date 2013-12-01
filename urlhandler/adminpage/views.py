#-*- coding:utf-8 -*-

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django import template

from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import render_to_response, RequestContext

from django.views.decorators.csrf import csrf_protect

from django.contrib import auth
from django.contrib.auth.decorators import login_required

from django.db.models import Q

import datetime

#import database

from urlhandler.models import Activity

@csrf_protect
def home(request):
    #return HttpResponse('login.html')
    return render_to_response('login.html',context_instance=RequestContext(request))

def activity_detail(request, actid):
    return HttpResponse(str(actid))

def activity_list(request):

    activities = Activity.objects.all()
    return render_to_response('activity_list.html', locals())

def avtivity_new(request):
    pass

@csrf_protect
def login(request):
    username = request.POST['username']
    password = request.POST['password']

    user = auth.authenticate(username = username, password = password)
    if user is not None:
        auth.login(request, user)

        activities = Activity.objects.all()
        return render_to_response('activity_list.html',locals())
    else:
        message = "用户名或密码不正确，请重新输入"
        return render_to_response('login.html', locals())

def logout(request):
    auth.logout(request)
    return render_to_response('/',context_instance=RequestContext(request))
