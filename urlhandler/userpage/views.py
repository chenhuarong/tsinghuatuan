#-*- coding:utf-8 -*-

from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response
from urlhandler.models import User, Activity
from urlhandler.settings import STATIC_URL
import urllib, urllib2
from django.utils import timezone

def home(request):
    return render_to_response('mobile_base.html')

###################### Validate ######################
# request.GET['openid'] must be provided.
def validate_view(request):
    if (not request.GET) or (not 'openid' in request.GET):
        raise Http404
    requestdata = request.GET
    if User.objects.filter(weixin_id=requestdata.get('openid', ''), status=1).exists():
        raise Http404
    return render_to_response('validation.html', {
        'openid': requestdata.get('openid', ''),
        'studentid': requestdata.get('studentid', ''),
    }, context_instance=RequestContext(request))


# Validate Format:
# METHOD 1: learn.tsinghua
# url: https://learn.tsinghua.edu.cn/MultiLanguage/lesson/teacher/loginteacher.jsp
# form: { userid:2011013236, userpass:***, submit1: 登录 }
# success: check substring 'loginteacher_action.jsp'
# validate: userid is number
def validate_through_learn(userid, userpass):
    req_data = urllib.urlencode({'userid': userid, 'userpass': userpass, 'submit1': u'登录'.encode('gb2312')})
    request_url = 'https://learn.tsinghua.edu.cn/MultiLanguage/lesson/teacher/loginteacher.jsp'
    req = urllib2.Request(url=request_url, data=req_data)
    res_data = urllib2.urlopen(req)
    try:
        res = res_data.read()
    except:
        return 'Error'
    if 'loginteacher_action.jsp' in res:
        return 'Accepted'
    else:
        return 'Rejected'

# METHOD 2 is not valid, because student.tsinghua has not linked to Internet
# METHOD 2: student.tsinghua
# url: http://student.tsinghua.edu.cn/checkUser.do?redirectURL=%2Fqingxiaotuan.do
# form: { username:2011013236, password:encryptedString(***) }
# success: response response is null / check response status code == 302
# validate: username is number
def validate_post(request):
    if (not request.POST) or (not 'openid' in request.POST) or \
            (not 'username' in request.POST) or (not 'password' in request.POST):
        raise Http404
    userid = request.POST['username']
    if not userid.isdigit():
        raise Http404
    userpass = request.POST['password'].encode('gb2312')
    validate_result = validate_through_learn(userid, userpass)
    if validate_result == 'Accepted':
        openid = request.POST['openid']
        try:
            User.objects.filter(stu_id=userid, status=1).update(status=0)
        except:
            return HttpResponse('Error')
        try:
            currentUser = User.objects.get(weixin_id=openid)
            currentUser.stu_id = userid
            currentUser.status = 1
            try:
                currentUser.save()
            except:
                return HttpResponse('Error')
        except:
            try:
                newuser = User.objects.create(weixin_id=openid, stu_id=userid, status=1)
                newuser.save()
            except:
                return HttpResponse('Error')
    return HttpResponse(validate_result)

###################### Activity Detail ######################

def details_view(request):
    requestdata = request.GET
    if (not requestdata) or (not 'activityid' in requestdata):
        raise Http404
    activity = Activity.objects.filter(id=requestdata.get('activityid', ''))
    if not activity.exists():
        raise Http404  #current activity is invalid
    act_name = activity[0].name
    act_key = activity[0].key
    act_place = activity[0].place
    act_bookstart = activity[0].book_start
    act_bookend = activity[0].book_end
    act_begintime = activity[0].start_time
    act_endtime = activity[0].end_time
    act_totaltickets = activity[0].total_tickets
    act_perorder = activity[0].max_tickets_per_order
    act_text = activity[0].description
    act_photo = STATIC_URL + "img/mlhk.png"
    cur_time = timezone.now() # use the setting UTC
    if act_bookstart <= cur_time <= act_bookend:
        act_status = u'订票正在进行中，请回复代码：“%s+订票张数”或点击菜单栏中“%s”进行订票'%(act_key,act_name)
    elif cur_time < act_bookstart:
        act_status = u'订票尚未开始，订票时间为:%s-%s'%(act_bookstart, act_bookend)
    else:
        act_status = u'活动订票已结束，可回复代码：%s查询订票结果'%(act_key)
    variables=RequestContext(request,{'act_name':act_name,'activity_text':act_text, 'activity_photo':act_photo,
                                      'act_bookstart':act_bookstart,'act_bookend':act_bookend,'act_begintime':act_begintime,
                                      'act_endtime':act_endtime,'act_totaltickets':act_totaltickets,'act_perorder':act_perorder,
                                      'act_place':act_place, 'act_status':act_status})
    return render_to_response('activitydetails.html', variables)