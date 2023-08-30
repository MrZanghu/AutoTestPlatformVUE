import datetime,json,logging
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from selenium_apps.models import TestCaseForSEA,TestCaseSteps\
    ,Case2SuiteForSEA,TestCaseExecuteResultForSEA
from main_platform.models import JobExecuted,TestSuite
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from main_platform.views import register_jobs
from main_platform.views import test_suite as ts



logger= logging.getLogger("main_platform")


def get_paginator(request,data):
    '''每个网页-获取指定页数'''
    paginator= Paginator(data,per_page= 10) # 每页10条
    page= request.GET.get("page")
    try:
        pp= paginator.page(page)
    except:
        pp= paginator.page(1) # 出现所有错误情况，都返回第1页
    return pp


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

    jb0= JobExecuted.objects.filter(job_id= job_name0).first()
    jb1= JobExecuted.objects.filter(job_id= job_name1).first()
    jb2= JobExecuted.objects.filter(job_id= job_name2).first()
    jb3= JobExecuted.objects.filter(job_id= job_name3).first()

    if (jb0!= None) or (jb1!= None) or (jb2!= None) or (jb3!= None):
        return JsonResponse({"msg":"存在相同任务名","status":2001})
    else:
        return JsonResponse({"msg": "不存在相同任务名", "status": 2000})


@login_required
def test_case(request):
    '''主页-测试用例列表'''
    if request.method== "GET":
        # 如果为get请求，直接返回所有用例
        cases= list(TestCaseForSEA.objects.filter(status= 0).order_by("-create_time").values())
        #  QuerySet转list添加级联数据，方便前台查询，减少数据库新增列
        for case in cases:
            case["suite_desc"]= Case2SuiteForSEA.objects.filter(test_case= case["id"]).first()
            if case["suite_desc"]:
                case["suite_desc"]= case["suite_desc"].test_suite.suite_desc
            else:
                case["suite_desc"]= "暂无集合"
        data= {}
        data["pages"]= get_paginator(request, cases)
        return render(request, "sea/sea_test_case.html", data)

    elif request.method== "POST":
        case_name= request.POST.get("case_name")
        ex_case= request.POST.get("ex_case") # 判断是否执行用例的关键字

        ex_time= request.POST.get("ex_time") # 判断执行时间的关键字
        if ex_time in ("",None):
            ex_time= (datetime.datetime.now()+datetime.timedelta(minutes= 1)).strftime("%Y-%m-%dT%H:%M")
        year= ex_time[:4]
        month= ex_time[5:7]
        day= ex_time[8:10]
        hour= ex_time[11:13]
        minute= ex_time[14:]
        data= {}

        if not ex_case:
            # 如果不是进行执行操作
            if case_name in [None, ""]:
                case_name= ""
                cases= TestCaseForSEA.objects.filter(status= 0).order_by("-create_time")
            else:
                cases= TestCaseForSEA.objects.filter\
                    (case_name__contains= case_name,status= 0).order_by("-create_time")
            data["pages"]= get_paginator(request, cases)
            data["case_name"]= case_name
            return render(request, "sea/sea_test_case.html", data)

        else:
            env= request.POST.get("env")
            test_case_list= request.POST.getlist("testcases_list")

            if len(test_case_list)== 0:
                # 解决传空用例的问题
                cases= TestCaseForSEA.objects.filter(status=0).order_by("-create_time")  # 根据创建时间倒序
                data= {}
                data["pages"]= get_paginator(request, cases)
                data["case_name"]= ""
                return render(request, "sea/sea_test_case.html", data)
            else:
                job_name0= "test_job0_%s" % ex_time  # 处理用例和集合并行的问题
                job_name1= "test_job1_%s" % ex_time
                job_name2= "test_UI_job0_%s" % ex_time  # 处理用例和集合并行的问题
                job_name3= "test_UI_job1_%s" % ex_time

                jb0= JobExecuted.objects.filter(job_id= job_name0).first()
                jb1= JobExecuted.objects.filter(job_id= job_name1).first()
                jb2= JobExecuted.objects.filter(job_id= job_name2).first()
                jb3= JobExecuted.objects.filter(job_id= job_name3).first()

                if (jb0 != None) or (jb1 != None) or (jb2 != None) or (jb3 != None):
                    pass # 解决重复任务名的问题
                else:
                    register_jobs(test_case_list,env,request.user.username,0,"test_UI_job0_%s"%ex_time,
                                  year,month,day,hour,minute)
                    jbe= JobExecuted()  # 记录定时任务
                    jbe.job_id= "test_UI_job0_%s" % ex_time
                    jbe.user= request.user.username
                    jbe.status= 0
                    jbe.save()
                return redirect(reverse("main_platform:test_execute",kwargs= {"jobid":"None"}))


@login_required
def test_case_execute_record(request,id):
    '''执行结果-执行用例记录'''
    test_case_execute_records= TestCaseExecuteResultForSEA.objects.filter(belong_test_execute= id).order_by("-id")
    data= {
        "pages": get_paginator(request, test_case_execute_records), # 返回分页
    }
    return render(request,"sea/sea_case_execute_records.html",data)


@login_required
def test_execute_show_exception(request,execute_id):
    '''执行结果-用例错误信息查看'''
    tcer= TestCaseExecuteResultForSEA.objects.get(id= execute_id)
    return render(request, "sea/sea_execute_show_exception.html", {"exception_info": tcer.exception_info})


@login_required
def test_case_detail(request,caseid):
    '''测试用例-修改用例'''
    if request.method== "GET":
        detail= TestCaseForSEA.objects.get(id= caseid)
        steps= TestCaseSteps.objects.filter(testcaseid_id= detail.id)\
            .values_list("LocationPath","Method","Parameter","Action","Expected")
        # values_list可以将queryset转换成tuple，需要指定字段

        detail_steps= [] # 处理数据加下标
        for i,line in enumerate([list(i) for i in steps]):
            inner_steps= []
            inner_steps.append(str(i+1))
            for j in line:
                inner_steps.append(j)
            detail_steps.append(inner_steps)

        data= {
            "test_case":detail,
            "test_case_steps":detail_steps
        }

        return render(request, "sea/sea_test_case_detail.html", data)
    else:
        pass


@login_required
def add_test_case(request):
    '''
    测试用例-新增用例页面，
    关联项目和模块，这个功能暂时不需要，后期再加
    '''
    if request.method== "GET":
        # 提交表单时获取不到数据，所以通过接口add_test_case_interface来新增
        return render(request, "sea/sea_add_test_case.html",{})


@login_required
def add_test_case_interface(request):
    '''测试用例-新增用例接口'''
    data= {
        "status": 2000,
        "msg": "test",
    }
    try:
        steps= json.loads(request.GET.get("steps"))
        case_name= request.GET.get("case_name")
        steps_list= []
        for step in steps:
            inner_list= []
            for s in step:
                if s in ("/", "", "None","-----------------------------------"):  # 处理前端为空时显示
                    s= None
                inner_list.append(s)
            steps_list.append(inner_list)

        tcfs= TestCaseForSEA() # 创建用例
        tcfs.case_name= case_name
        tcfs.status= 0
        tcfs.user= request.user
        tcfs.length= len(steps_list)
        tcfs.save()

        for sl in steps_list:
            tcs= TestCaseSteps() # 创建关联步骤
            tcs.testcaseid= tcfs
            tcs.LocationPath= sl[0]
            tcs.Method= sl[1]
            tcs.Parameter= sl[2]
            tcs.Action= sl[3]
            tcs.Expected= sl[4]
            tcs.save()

        data["status"]= 2000
        data["msg"]= "提交用例创建成功"
    except Exception as e:
        TestCaseForSEA.objects.filter(user= request.user).last().delete()
        # 如果创建错误，将当前用户最后一条删除
        data["status"]= 2001
        data["msg"]= "提交用例创建失败，请检查"
    return JsonResponse(data)


@login_required
def update_test_case(request,caseid):
    '''测试用例-修改用例'''
    if request.method== "GET":
        detail= TestCaseForSEA.objects.get(id= caseid)
        steps= TestCaseSteps.objects.filter(testcaseid_id= detail.id)\
            .values_list("LocationPath","Method","Parameter","Action","Expected")
        # values_list可以将queryset转换成tuple，需要指定字段

        detail_steps= [] # 处理数据加上下标
        for i,line in enumerate([list(i) for i in steps]):
            inner_steps= []
            inner_steps.append(str(i+1))
            for j in line:
                inner_steps.append(j)
            detail_steps.append(inner_steps)

        data= {
            "test_case":detail,
            "test_case_steps":detail_steps
        }

        return render(request, "sea/sea_update_test_case.html", data)
    else:
        pass


@login_required
def update_test_case_interface(request):
    '''测试用例-修改用例接口'''
    data= {
        "status": 2000,
        "msg": "test",
    }

    try:
        case_id= request.GET.get("case_id")
        steps= json.loads(request.GET.get("steps"))
        detail= TestCaseForSEA.objects.get(id= case_id)
        TestCaseSteps.objects.filter(testcaseid_id= detail.id).delete()
        # 物理删除级联步骤，防止数据表过大

        steps_list= []
        for step in steps:
            inner_list= []
            for s in step:
                if s in ("/", "", "None","-----------------------------------") :  # 处理前端为空时显示
                    s= None
                inner_list.append(s)
            steps_list.append(inner_list)

        detail.length= len(steps_list)
        detail.save()

        for sl in steps_list:
            tcs= TestCaseSteps()  # 创建关联步骤
            tcs.testcaseid= detail
            tcs.LocationPath= sl[0]
            tcs.Method= sl[1]
            tcs.Parameter= sl[2]
            tcs.Action= sl[3]
            tcs.Expected= sl[4]
            tcs.save()

        detail.update_time= datetime.datetime.now()
        detail.save() # 修改更新时间

        data["status"]= 2000
        data["msg"]= "提交用例创建成功"
    except:
        data["status"]= 2001
        data["msg"]= "修改用例失败，请检查"
    return JsonResponse(data)


@login_required
def delete_test_case(request,caseid):
    '''测试用例-删除用例'''
    case= TestCaseForSEA.objects.get(id= caseid)
    case.status= 1
    case.update_time= datetime.datetime.now()
    case.save()

    suite_case= Case2SuiteForSEA.objects.filter(test_case= case)
    # 集合关联的用例需要进行解除
    for i in suite_case:
        i.status= 1
        i.save()

    cases= TestCaseForSEA.objects.filter(status=0).order_by("-create_time")  # 根据创建时间倒序
    data= {}
    data["pages"]= get_paginator(request, cases)
    return render(request, "sea/sea_test_case.html", data)


@login_required
def test_suite(request,suite_type):
    '''主页-UI集合'''
    # 直接调用main_platform的test_suite，统一处理
    return ts(request,suite_type)