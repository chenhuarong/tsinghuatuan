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

from urlhandler.models import User as Booker

@csrf_protect
def home(request):
    if not request.user.is_authenticated():
        return render_to_response('login.html', context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('adminpage.views.activity_list'))

def activity_list(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('adminpage.views.home'))

    actmodels = Activity.objects.all()
    activities = []
    for act in actmodels:
        activities += [wrap_activity_dict(act)]
    return render_to_response('activity_list.html', {
        'activities': activities,
    })


def login(request):
    if not request.POST:
        raise Http404

    rtnJSON = {}

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')

    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        auth.login(request, user)
        rtnJSON['message'] = 'success'
        rtnJSON['next'] = reverse('adminpage.views.activity_list')
    else:
        rtnJSON['message'] = 'failed'
        if User.objects.filter(username=username, is_active=True):
            rtnJSON['error'] = 'wrong'
        else:
            rtnJSON['error'] = 'none'

    return HttpResponse(json.dumps(rtnJSON), content_type='application/json')


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('adminpage.views.home'))


def str_to_datetime(str):
    return datetime.strptime(str, '%Y-%m-%d %H:%M:%S')


def activity_create(activity):

    preDict = dict()
    for k in ['name', 'key', 'description', 'place', 'pic_url', 'total_tickets']:
        preDict[k] = activity[k]
    for k in ['start_time', 'end_time', 'book_start', 'book_end']:
        preDict[k] = str_to_datetime(activity[k])
    preDict['status'] = 1 if ('publish' in activity) else 0
    preDict['remain_tickets'] = preDict['total_tickets']
    newact = Activity.objects.create(**preDict)
    return newact


def activity_modify(activity):
    nowact = Activity.objects.get(id=activity['id'])
    now = datetime.now()
    if nowact.status == 0:
        keylist = ['name', 'key', 'description', 'place', 'pic_url', 'total_tickets']
        timelist = ['start_time', 'end_time', 'book_start', 'book_end']
    elif nowact.status == 1:
        if now >= nowact.start_time:
            keylist = []
            timelist = []
        elif now >= nowact.book_start:
            keylist = ['description', 'place', 'pic_url']
            timelist = ['start_time', 'end_time']
        else:
            keylist = ['description', 'place', 'pic_url', 'total_tickets']
            timelist = ['start_time', 'end_time']
    for key in keylist:
        setattr(nowact, key, activity[key])
    for key in timelist:
        setattr(nowact, key, str_to_datetime(activity[key]))
    if (nowact.status == 0) and ('publish' in activity):
        nowact.status = 1
    nowact.save()
    return nowact


def get_checked_tickets(activity):
    return Ticket.objects.filter(activity=activity, status=2).count()


def wrap_activity_dict(activity):
    dt = model_to_dict(activity)
    if (dt['status'] >= 1) and (datetime.now() >= dt['book_start']):
        dt['tickets_ready'] = 1
        dt['ordered_tickets'] = int(activity.total_tickets) - int(activity.remain_tickets)
        dt['checked_tickets'] = get_checked_tickets(activity)
    return dt


def activity_add(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('adminpage.views.home'))

    return render_to_response('activity_detail.html', {
        'activity': {
            'name': u'新建活动',
        }
    }, context_instance=RequestContext(request))


def activity_detail(request, actid):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('adminpage.views.home'))

    try:
        activity = Activity.objects.get(id=actid)

        unpublished = (activity.status == 0)
    except:
        raise Http404
    return render_to_response('activity_detail.html', {
        'activity': wrap_activity_dict(activity),
        'unpublished': unpublished
    }, context_instance=RequestContext(request))


class DatetimeJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return json.JSONEncoder.default(self, obj)


def activity_post(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('adminpage.views.home'))

    if not request.POST:
        raise Http404
    post = request.POST
    rtnJSON = dict()
    try:
        if 'id' in post:
            activity = activity_modify(post)
        else:
            activity = activity_create(post)
            rtnJSON['updateUrl'] = reverse('adminpage.views.activity_detail', kwargs={'actid': activity.id})
        rtnJSON['activity'] = wrap_activity_dict(activity)
    except Exception as e:
        rtnJSON['error'] = str(e)
    return HttpResponse(json.dumps(rtnJSON, cls=DatetimeJsonEncoder), content_type='application/json')

def order_list(request):

    UID = 1
    orders = []
    try:
        qset = Ticket.objects.filter(user_id = UID)
        item = {}
        for x in qset:
            activity = Activity.objects.get(id = x.activity_id)

            item['name'] = activity.name

            item['start_time'] = activity.start_time

            item['end_time'] = activity.end_time
            item['place'] = activity.place
            item['seat'] = x.seat
            item['valid'] = x.status
            item['unique_id'] = x.unique_id

        orders.append(item)
    except:
        raise Http404
    return render_to_response('order_list.html', {
        'orders': orders,
    }, context_instance=RequestContext(request))

def print_ticket(request, unique_id):
    try:
        ticket = Ticket.objects.get(unique_id = unique_id)
        activity = Activity.objects.get(id = ticket.activity_id)
        qr_addr = "http://tsinghuaqr.duapp.com/fit/" + unique_id
    except:
        raise Http404
    return render_to_response('print_ticket.html', {
        'qr_addr': qr_addr,
        'activity': activity
    },context_instance=RequestContext(request))
