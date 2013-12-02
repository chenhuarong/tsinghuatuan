#-*- coding:utf-8 -*-

from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict

from datetime import datetime
import json

from django.http import HttpResponseRedirect
from django import template

from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import render_to_response

from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login,logout as auth_logout
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.views.decorators.csrf import csrf_protect

#import database
from urlhandler.models import Activity, Order, Ticket

@csrf_protect
def home(request):
    if not request.user.is_authenticated():
        return render_to_response('login.html', context_instance=RequestContext(request))
    else:
        activities = Activity.objects.all()
        return render_to_response('activity_list.html', {'activities':activities})


def activity_list(request):
    actmodels = Activity.objects.all()
    activities = []
    for act in actmodels:
        activities += [wrap_activity_dict(act)]
    return render_to_response('activity_list.html', {
        'activities': activities,
    })

@csrf_protect
def login(request):
    if not request.POST:
        raise Http404

    rtnJSON = {}

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')

    user = auth.authenticate(username = username, password = password)
    if user is not None and user.is_active:
        auth.login(request, user)
        rtnJSON['message'] = 'success'
        rtnJSON['next'] = '/adminpage/list/'
    else:
        rtnJSON['message'] = 'failed'
        if User.objects.filter(username=username, is_active = True):
            rtnJSON['error'] = 'wrong'
        else:
            rtnJSON['error'] = 'none'

    return HttpResponse(json.dumps(rtnJSON), content_type='application/json')

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/adminpage/')

def str_to_datetime(str):
    return datetime.strptime(str, '%Y-%m-%d %H:%M:%S')


def activity_create(activity):
    preDict = dict()
    for k in ['name', 'key', 'description', 'place', 'max_tickets_per_order', 'total_tickets']:
        preDict[k] = activity[k]
    for k in ['start_time', 'end_time', 'book_start', 'book_end']:
        preDict[k] = str_to_datetime(activity[k])
    preDict['status'] = 1 if activity.has_key('publish') else 0
    newact = Activity.objects.create(**preDict)
    return newact


def activity_modify(activity):
    nowact = Activity.objects.get(id=activity['id'])
    now = datetime.now()
    if nowact.status == 0:
        keylist = ['name', 'key', 'description', 'place', 'max_tickets_per_order', 'total_tickets']
        timelist = ['start_time', 'end_time', 'book_start', 'book_end']
    elif nowact.status == 1:
        if now >= nowact.book_start:
            keylist = ['description', 'place', 'total_tickets']
            timelist = ['start_time', 'end_time']
        else:
            keylist = ['key', 'description', 'place', 'max_tickets_per_order', 'total_tickets']
            timelist = ['start_time', 'end_time']
    elif nowact.status == 2:
        keylist = ['description', 'place']
        timelist = ['start_time', 'end_time']
    elif nowact.staus == 3:
        if now >= nowact.start_time:
            keylist = []
            timelist = []
        else:
            keylist = ['description', 'place']
            timelist = ['start_time', 'end_time']
    for key in keylist:
        setattr(nowact, key, activity[key])
    for key in timelist:
        setattr(nowact, key, str_to_datetime(activity[key]))
    if (nowact.status == 0) and activity.has_key('publish'):
        nowact.status = 1
    nowact.save()
    return nowact


def get_ordered_tickets(activity):
    orders = Order.objects.filter(activity=activity, status=1).all()
    result = 0
    for order in orders:
        result += order.tickets
    return result


def get_checked_tickets(activity):
    return Ticket.objects.filter(activity=activity, isUsed=0).count()


def wrap_activity_dict(activity):
    dt = model_to_dict(activity)
    if (dt['status'] >= 1) and (datetime.now() >= dt['book_start']):
        dt['tickets_ready'] = 1
        dt['ordered_tickets'] = get_ordered_tickets(activity)
        dt['checked_tickets'] = get_checked_tickets(activity)
    return dt


def activity_add(request):
    return render_to_response('activity_detail.html', {
        'activity': {
            'name': u'新建活动',
        }
    }, context_instance=RequestContext(request))


def activity_detail(request, actid):
    try:
        activity = Activity.objects.get(id=actid)
    except:
        raise Http404
    return render_to_response('activity_detail.html', {
        'activity': wrap_activity_dict(activity),
    }, context_instance=RequestContext(request))


class DatetimeJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return json.JSONEncoder.default(self, obj)


def activity_post(request):
    if not request.POST:
        raise Http404
    post = request.POST
    rtnJSON = dict()
    try:
        if post.has_key('id'):
            activity = activity_modify(post)
        else:
            activity = activity_create(post)
            rtnJSON['updateUrl'] = reverse('adminpage.views.activity_detail', kwargs={'actid': activity.id})
        rtnJSON['activity'] = wrap_activity_dict(activity)
    except Exception as e:
        rtnJSON['error'] = str(e)
    return HttpResponse(json.dumps(rtnJSON, cls=DatetimeJsonEncoder), content_type='application/json')

