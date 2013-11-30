#-*- coding:utf-8 -*-

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django import template

from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import render_to_response

from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login,logout as auth_logout
from django.contrib.auth.decorators import login_required

import datetime

#import database
from urlhandler.models import Activity


def home(request):
    activities = Activity.objects.all()
    return render_to_response('activity_home.html', locals())
    #return render_to_response('activity_management.html', locals())
