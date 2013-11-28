#-*- coding:utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response

def home(request):
    return render_to_response('mobile_base.html')


def validate_view(request):

    return HttpResponse('Hi')


# Validate Format:
# METHOD 1: learn.tsinghua
# url: https://learn.tsinghua.edu.cn/MultiLanguage/lesson/teacher/loginteacher.jsp
# form: { userid:2011013236, userpass:***, submit1: 登录 }
# success: check substring 'loginteacher_action.jsp'
# validate: userid is number

# METHOD 2: student.tsinghua
# url: http://student.tsinghua.edu.cn/checkUser.do?redirectURL=%2Fqingxiaotuan.do
# form: { username:2011013236, password:encryptedString(***) }
# success: response response is null / check response status code == 302
# validate: username is number
def validate_post(request):

    return HttpResponse('Hi')