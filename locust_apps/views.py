import datetime
from main_platform import viewsParams as vp
from django.http import JsonResponse
from locust_apps.models import TestCase
from django.shortcuts import render, redirect,reverse
from main_platform.models import JobExecuted
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from main_platform.views import register_jobs
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User



@csrf_exempt
def get_job_name(request):
    '''获取任务名称，判断是否重复'''
    ex_time= request.GET.get("ex_time")
    if ex_time== "":
        ex_time= (datetime.datetime.now() + datetime.timedelta(minutes= 1)).strftime("%Y-%m-%dT%H:%M")
    job_name0= "test_job0_%s"%ex_time # 处理用例和集合并行的问题
    job_name1= "test_job1_%s"%ex_time
    job_name2= "test_UI_job0_%s"%ex_time # 处理用例和集合并行的问题
    job_name3= "test_UI_job1_%s"%ex_time
    job_name4= "test_LOC_job0_%s"%ex_time # 处理用例和集合并行的问题
    job_name5= "test_LOC_job1_%s"%ex_time

    jb0= JobExecuted.objects.filter(job_id= job_name0).first()
    jb1= JobExecuted.objects.filter(job_id= job_name1).first()
    jb2= JobExecuted.objects.filter(job_id= job_name2).first()
    jb3= JobExecuted.objects.filter(job_id= job_name3).first()
    jb4= JobExecuted.objects.filter(job_id= job_name4).first()
    jb5= JobExecuted.objects.filter(job_id= job_name5).first()

    if (jb0!= None) or (jb1!= None) or (jb2!= None) or (jb3!= None)or (jb4!= None)or (jb5!= None):
        return JsonResponse({"msg":"存在相同任务名","status":2001})
    else:
        return JsonResponse({"msg": "不存在相同任务名", "status": 2000})


def get_paginator(request,data):
    '''每个网页-获取指定页数，使用框架自带的分页，这个作废'''
    paginator= Paginator(data,per_page= 99999) # 每页10条
    page= request.GET.get("page")
    try:
        pp= paginator.page(page)
    except:
        pp= paginator.page(1) # 出现所有错误情况，都返回第1页
    return pp


@login_required
def test_case(request):
    '''主页-测试用例'''
    if request.method== "GET":
        # 如果为get请求，直接返回所有用例
        cases= TestCase.objects.filter(status= 0).order_by("-id")
        data= {}
        data["pages"]= cases
        data["case_name"]= ""
        return render(request, "loc/test_case.html", data)

    elif request.method== "POST":
        case_name= request.POST.get("case_name")
        ex_case= request.POST.get("ex_case") # 判断是否执行用例的关键字
        ex_time= request.POST.get("ex_time") # 判断执行时间的关键字
        ex_u= request.POST.get("ex_u") # 用户总量
        ex_r= request.POST.get("ex_r") # 每秒启动
        ex_t= request.POST.get("ex_t") # 持续时间

        if ex_time in ("",None):
            ex_time= (datetime.datetime.now()+datetime.timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M")
        year= ex_time[:4]
        month= ex_time[5:7]
        day= ex_time[8:10]
        hour= ex_time[11:13]
        minute= ex_time[14:]
        data= {}

        if ex_case is None:
            # 如果获取不到字段，则为None，返回test_case原页面
            if case_name in [None, ""]:
                case_name= ""
                cases= TestCase.objects.filter(status= 0).order_by("-id")
            else:
                cases= TestCase.objects.filter(case_name__contains= case_name,status= 0).order_by("-id")
            data["pages"]= get_paginator(request, cases)
            data["case_name"]= case_name
            return render(request, "loc/test_case.html", data)
        else:
            env= request.POST.get("env")
            test_case_list= request.POST.getlist("testcases_list")
            if len(test_case_list)== 0:
                # 解决传空用例的问题
                cases= TestCase.objects.filter(status= 0).order_by("-id")
                data= {}
                data["pages"]= get_paginator(request, cases)
                data["case_name"]= ""
                return render(request, "loc/test_case.html", data)
            else:
                if datetime.datetime.now()> datetime.datetime.strptime(ex_time, "%Y-%m-%dT%H:%M"):
                    # 解决传错误时间的问题
                    cases= TestCase.objects.filter(status=0).order_by("-id")
                    data= {}
                    data["pages"]= get_paginator(request, cases)
                    data["case_name"]= ""
                    return render(request, "atp/test_case.html", data)
                else:
                    job_name0= "test_job0_%s" % ex_time  # 处理用例和集合并行的问题
                    job_name1= "test_job1_%s" % ex_time
                    job_name2= "test_UI_job0_%s" % ex_time  # 处理用例和集合并行的问题
                    job_name3= "test_UI_job1_%s" % ex_time
                    job_name4= "test_LOC_job0_%s" % ex_time  # 处理用例和集合并行的问题
                    job_name5= "test_LOC_job1_%s" % ex_time

                    jb0= JobExecuted.objects.filter(job_id=job_name0).first()
                    jb1= JobExecuted.objects.filter(job_id=job_name1).first()
                    jb2= JobExecuted.objects.filter(job_id=job_name2).first()
                    jb3= JobExecuted.objects.filter(job_id=job_name3).first()
                    jb4= JobExecuted.objects.filter(job_id=job_name4).first()
                    jb5= JobExecuted.objects.filter(job_id=job_name5).first()

                    if (jb0 != None) or (jb1 != None) or (jb2 != None) or (jb3 != None)or (jb4 != None)or (jb5 != None):
                        pass # 解决重复任务名的问题
                    else:
                        with open("locust_config.ini", 'w') as file:# 写入读取的配置文件中，方便后续使用
                            file.write('[Parameter]\n')  # 写入新的section
                            file.write('MY_CASE_ID= %s\n'%test_case_list)  # 写入用例的id
                            file.write('MY_SUITE_ID= "None"\n')  # 集合为空

                        register_jobs(test_case_list,env,request.user.username,0,"test_LOC_job0_%s"%ex_time,
                                      year,month,day,hour,minute,u= ex_u,r= ex_r,t= ex_t)
                        jbe= JobExecuted()  # 记录定时任务
                        jbe.job_id= "test_LOC_job0_%s" % ex_time
                        jbe.user= request.user.username
                        jbe.status= 0
                        jbe.save()
                    return redirect(reverse("main_platform:test_execute",kwargs= {"jobid":"None"}))


@login_required
def add_test_case(request):
    '''测试用例-手动创建用例'''
    if request.method== "GET":
        data= {}
        user= User.objects.all()
        data["request_method"]= vp.request_method
        data["responsible_user"]= user
        data["maintainer"]= str(request.user)
        return render(request, "loc/add_test_case.html",data)

    elif request.method== "POST":
        ts= TestCase()
        ts.case_name= request.POST.get("case_name")
        ts.request_data= request.POST.get("request_data")
        ts.uri= request.POST.get("uri")
        ts.maintainer= request.user
        ts.request_method= request.POST.get("request_method")
        ts.status= 0

        assert_key= request.POST.get("assert_key")
        if assert_key== '':
            assert_key= None
        ts.assert_key= assert_key
        ts.save()

        return redirect(reverse("locust_apps:test_case"))


@login_required
def delete_test_case(request,caseid):
    '''
    测试用例-手动逻辑删除用例
    :param request:
    :return:
    '''
    case= TestCase.objects.get(id= caseid)
    case.status= 1
    case.update_time= datetime.datetime.now()
    case.save()
    return redirect(reverse("locust_apps:test_case"))


@login_required
def update_test_case(request,caseid):
    '''
    测试用例-手动更新用例
    :param request:
    :return:
    '''
    case= TestCase.objects.get(id= caseid)
    if request.method== "GET":
        data= {}
        data["original_id"]= case.id
        data["original_case_name"]= case.case_name
        data["original_request_data"]= case.request_data
        data["original_uri"]= case.uri
        data["original_assert_key"]= case.assert_key
        data["original_maintainer"]= case.maintainer
        data["original_request_method"]= case.request_method
        data["request_method"]= vp.request_method
        return render(request,"loc/update_test_case.html",data)

    elif request.method== "POST":
        case.case_name= request.POST.get("case_name")
        case.request_data= request.POST.get("request_data")
        case.uri= request.POST.get("uri")
        case.request_method= request.POST.get("request_method")
        assert_key= request.POST.get("assert_key")
        if assert_key== '':
            assert_key= None
        case.assert_key= assert_key
        case.update_time= datetime.datetime.now()
        case.save()
        return redirect(reverse("locust_apps:test_case"))


@login_required
def test_case_detail(request,caseid):
    '''测试用例-用例详情'''
    try:
        detail= TestCase.objects.get(id= caseid)
        data= {
            "test_case":detail
        }
        return render(request,"loc/test_case_detail.html",data)
    except:
        return render(request,"atp/index.html") # 如果找不到就回到主页，防止出现程序