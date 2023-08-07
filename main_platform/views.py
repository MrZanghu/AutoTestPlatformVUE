import datetime
import logging
import pymysql
from . import viewsParams as vp
from django.contrib import auth
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from main_platform.form import UserForm
from main_platform.tasks import case_task,process_xls,suite_task
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from main_platform.validCode import ValidCodeImg
from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from main_platform.models import Project, Module, TestCase,\
    TestSuite, AddCaseIntoSuite, Server, UpLoadsCaseTemplate, \
    TestCaseExecuteResult,TestExecute,TestSuiteExecuteRecord,\
    TestSuiteTestCaseExecuteRecord,JobExecuted
from selenium_apps.models import Case2SuiteForSEA,TestCaseForSEA
from django.db.models import Q
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore,register_job



scheduler= BackgroundScheduler(timezone= "Asia/Shanghai") # 实例化调度器
scheduler.add_jobstore(DjangoJobStore(), "default")
logger= logging.getLogger("main_platform")


def get_test(request):
    '''测试get功能使用'''
    if request.method== "GET":
        id= request.GET.get("id")
        name= request.GET.get("name")
        server= Server.objects.filter(id= id).first()
        data= {
            "code":200,
            "msg":"get查询成功",
            "server":model_to_dict(server),
            # 将序列化数据直接转化为字典
            "name":name,
            "method":"get"
        }
        return JsonResponse(data)


@csrf_exempt
def post_test(request):
    '''测试post功能使用，取消csrf跨域请求限制'''
    if request.method== "POST":
        id= request.POST.get("id")
        name= request.POST.get("name")
        server= Server.objects.filter(id= id).first()
        data= {
            "code":200,
            "msg":"查询成功",
            "server":model_to_dict(server),
            # 将序列化数据直接转化为字典
            "name":name
        }
        return JsonResponse(data)


@csrf_exempt
def put_test(request):
    '''测试功能使用，取消csrf跨域请求限制'''
    if request.method== "PUT":
        data= {
            "code":200,
            "msg":"put查询成功",
            "id":1,
            "name":"name"
        }
        return JsonResponse(data)


def get_code(request):
    '''
    用户模块-登录逻辑-验证码生成
    :param request:
    :return:
    '''
    img= ValidCodeImg()
    fp, verify_code= img.getValidCodeImg()
    request.session["verify_code"]= verify_code
    # 把验证码存在session中用于验证
    return HttpResponse(fp.getvalue(),content_type= "image/png")


def get_paginator(request,data):
    '''每个网页-获取指定页数'''
    paginator= Paginator(data,per_page= 10) # 每页10条
    page= request.GET.get("page")
    try:
        pp= paginator.page(page)
    except:
        pp= paginator.page(1) # 出现所有错误情况，都返回第1页
    return pp


def login(request):
    '''用户模块-登录逻辑'''
    if request.method== "POST":
        login_form= UserForm(request.POST)
        # 对提交的数据进行组件类实例化
        if login_form.is_valid():
            # 校验提交的数据对象，必须验证才能使用cleaned_data
            username= login_form.cleaned_data["username"]
            password= login_form.cleaned_data["password"]
            user= auth.authenticate(username= username,password= password)  # django自带的校验功能
            if user!= None:
                input_code= request.POST.get("verify_code")
                right_code= request.session.get("verify_code")
                if right_code== input_code:
                    auth.login(request, user)
                    request.session['is_login']= True
                    return redirect(reverse("main_platform:index")) # 登录成功跳转到主页
                    # 登录成功跳转到我的
                elif input_code== "6666":
                    auth.login(request, user)
                    request.session['is_login']= True
                    return redirect(reverse("main_platform:index")) # 登录成功跳转到主页
                    # 超级验证码
                else:
                    request.session["message"]= "验证码错误"
                    return redirect(reverse("main_platform:login"))
            else:
                request.session["message"]= "用户名或密码错误"
                return redirect(reverse("main_platform:login"))
        else:
            login_form= UserForm()
            request.session["message"]= "用户名或密码错误"
            return redirect(reverse("main_platform:login"))

    elif request.method== "GET":
        login_form= UserForm()
        return render(request,"atp/login.html",locals())


def get_server_address(env):
    '''测试用例-获取服务器地址'''
    if env:
        env_data= Server.objects.get(env= env)
        if env_data:
            ip= env_data.ip
            port= env_data.port
            if env_data.is_https== 1:
                server_address= "https://{}".format(ip)
            else:
                server_address= "http://{}:{}".format(ip, port)
            return server_address
        else:
            return None
    else:
        return None


def register_jobs(lists,envs,username,types,id,year,month,day,hour,minute):
    '''
    执行用例or集合，进行定时任务注册
    :param lists:
    :param envs:
    :param username:
    :param types: 0->用例，1->集合
    :param id:
    :param hour:
    :param minute:
    :param second:
    :return:
    '''
    scheduler.add_job(do_task_jobs,"cron",id= id,replace_existing= True,year= year,month= month,day= day,
                      hour= hour,minute= minute,args= [lists,envs,username,types,id])
    # 单次任务不会有执行记录，创建JobExecuted用于储存


def do_task_jobs(lists,envs,username,types,id):
    '''
    执行用例or集合的定时任务
    :param lists:
    :param envs:
    :param username:
    :param types: type: 0->用例，1->集合
    :param id:定时任务id
    :return:
    '''
    if lists:
        test_list= [int(x) for x in lists]
        test_list.sort()  # 将id转化成int后排序
        server_address= get_server_address(envs)
        # server_address= False
        if not server_address:
            logger.info(" " * 50)
            logger.info({"code": 404, "msg": "提交的运行环境为空，请选择环境后再提交！"})
            return
        if types== 0:
            logger.info(" " * 50)
            logger.info("######### 已经获取到用例，开始进行批量执行 #########")
            case_task.delay(test_list, server_address, username,id)
        else:
            logger.info(" " * 50)
            logger.info("######### 已经获取到集合，开始进行批量执行 #########")
            suite_task.delay(test_list, server_address, username,id)
    else:
        logger.info(" " * 50)
        logger.info({"code": 404, "msg": "提交的测试用例or集合为空！"})
        return


@register_job(scheduler, "interval", seconds= 30,id= "synchronous_jobs",replace_existing= True)
def synchronous_jobs():
    '''
    定时任务，同步 atp_job_executed & django_apscheduler_djangojob，处理异常结果
    :return:null
    '''
    sql= "SELECT count(*) FROM django_apscheduler_djangojobexecution;"
    sql2= "DELETE FROM django_apscheduler_djangojobexecution;"

    conn= pymysql.connect(host= "127.0.0.1",user= "root", password= "12345678",
                          database= "AutoTestPlatform",charset= "utf8")
    cursor= conn.cursor()
    cursor.execute(sql)
    datas= cursor.fetchone()
    if datas[0]>= 200: # 防止同步任务记录表过大
        cursor2= conn.cursor()
        cursor2.execute(sql2)
        conn.commit()
        cursor2.close()
    cursor.close()
    conn.close()

    jobs= []
    for i in scheduler.get_jobs(): # 读取aps表
        jobs.append(i.id)
    jobs.remove("synchronous_jobs")
    jobs_exe= [x for x in JobExecuted.objects.all()]

    for je in jobs_exe:
        if je.job_id not in jobs: # aps表内无此任务 1/2
            if je.status== 0:
                je.status= 1
                je.save()
            elif je.status== 3:
                je.status= 1
                je.save()
            else:
                pass
        else: # aps表内有此任务 0/3
            if je.status== 1:
                je.status= 0
                je.save()
            elif je.status== 2:
                je.status= 0
                je.save()
            else:
                pass
    logger.info(" " * 50)
    logger.info("同步完成！")


@csrf_exempt
def get_job_name(request):
    '''获取任务名称，判断是否重复'''
    ex_time= request.GET.get("ex_time")
    if ex_time== "":
        ex_time= (datetime.datetime.now() + datetime.timedelta(minutes= 1)).strftime("%Y-%m-%dT%H:%M")
    job_name0= "test_job0_%s"%ex_time # 处理用例和集合并行的问题
    job_name1= "test_job1_%s"%ex_time
    jb0= JobExecuted.objects.filter(job_id= job_name0).first()
    jb1= JobExecuted.objects.filter(job_id= job_name1).first()
    if jb0!= None or jb1!= None:
        return JsonResponse({"msg":"存在相同任务名","status":2001})
    else:
        return JsonResponse({"msg": "不存在相同任务名", "status": 2000})


@login_required
def index(request):
    '''主页'''
    # login_required，这种方式可以实现未登录禁止访问首页的功能
    return render(request,"atp/index.html")


@login_required
def logout(request):
    '''用户模块-登出逻辑'''
    auth.logout(request)
    request.session.flush()
    return redirect("main_platform:login")


@login_required
def project(request):
    '''主页-项目'''
    if request.method== "POST":
        # 如果为post请求
        proj_name= request.POST.get("proj_name")
        if proj_name== "":
            # 未输入直接点击查询，返回所有模块
            proj_name= ""
            projects= Project.objects.order_by("-id")
        else:
            projects= Project.objects.filter(name__contains= proj_name).order_by("-id") # 模糊查询所有项目名
    else:
        proj_name= ""
        projects= Project.objects.order_by("-id")

    data= {
        "pages": get_paginator(request, projects), # 返回分页
        "proj_name":proj_name,
    }
    return render(request,"atp/project.html",data)


@login_required
def module(request):
    '''主页-模块'''
    if request.method== "POST":
        # 如果为post请求
        proj_name= request.POST.get("proj_name")
        if proj_name== "":
            # 未输入直接点击查询，返回所有模块
            proj_name= ""
            modules= Module.objects.order_by("-id")
        else:
            projects= Project.objects.filter(name__contains= proj_name) # 模糊查询所有项目名
            projects_id= [i.id for i in projects] # 找到项目对应id
            modules= Module.objects.filter(belong_project__in= projects_id).order_by("-id")
            # modules= Module.objects.filter(belong_project__module__in= projects_id).order_by("-id")
            # # belong_project__module__in 没有将模块去重
    else:
        proj_name= ""
        modules= Module.objects.order_by("-id")

    data= {
        "pages": get_paginator(request, modules),
        "proj_name":proj_name,
    }
    return render(request,"atp/module.html",data)


@login_required
def test_case(request):
    '''主页-测试用例'''
    if request.method== "GET":
        # 如果为get请求，直接返回所有用例
        cases= TestCase.objects.filter(status= 0).order_by("-id")
        data= {}
        data["pages"]= get_paginator(request, cases)
        data["case_name"]= ""
        return render(request, "atp/test_case.html", data)

    elif request.method== "POST":
        case_name= request.POST.get("case_name")
        ex_case= request.POST.get("ex_case") # 判断是否执行用例的关键字
        ex_time= request.POST.get("ex_time") # 判断执行时间的关键字
        if ex_time in ("",None):
            ex_time= (datetime.datetime.now()+datetime.timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M")
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
                cases= TestCase.objects.filter(status= 0).order_by("-id")
            else:
                cases= TestCase.objects.filter(case_name__contains= case_name,status= 0).order_by("-id")
            data["pages"]= get_paginator(request, cases)
            data["case_name"]= case_name
            return render(request, "atp/test_case.html", data)
        else:
            env= request.POST.get("env")
            test_case_list= request.POST.getlist("testcases_list")
            if len(test_case_list)== 0:
                # 解决传空用例的问题
                cases= TestCase.objects.filter(status= 0).order_by("-id")
                data= {}
                data["pages"]= get_paginator(request, cases)
                data["case_name"]= ""
                return render(request, "atp/test_case.html", data)
            else:
                job_name0= "test_job0_%s" % ex_time  # 处理用例和集合并行的问题
                job_name1= "test_job1_%s" % ex_time
                jb0= JobExecuted.objects.filter(job_id= job_name0).first()
                jb1= JobExecuted.objects.filter(job_id= job_name1).first()
                if jb0!= None or jb1!= None:
                    pass # 解决重复任务名的问题
                else:
                    register_jobs(test_case_list,env,request.user.username,0,"test_job0_%s"%ex_time,
                                  year,month,day,hour,minute)
                    jbe= JobExecuted()  # 记录定时任务
                    jbe.job_id= "test_job0_%s" % ex_time
                    jbe.user= request.user.username
                    jbe.status= 0
                    jbe.save()
                return redirect(reverse("main_platform:test_execute",kwargs= {"jobid":"None"}))


@login_required
def down_test_template(request):
    '''
    测试用例-下载模板文件
    :param request:
    :return:
    '''
    def file_iterator(file, chunk_size= 512):
        with open(file,'rb') as f:
            while True:
                c= f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
    file= "static/downloads/your_project_name.xls"
    file_name= "your_project_name.xls"
    response= StreamingHttpResponse(file_iterator(file))
    response['Content-Type']= 'application/octet-stream'
    response['Content-Disposition']= 'attachment;filename="{0}"'.format(file_name)
    return response


@login_required
def up_test_template(request):
    '''
    测试用例-上传模板文件
    :param request:
    :return:
    '''
    file= request.FILES.get("file_name")
    if not file: # 没文件上传
        pass
    else:
        file_names= str(file)
        up_times= str(datetime.datetime.now().strftime("%H_%M_%S"))
        owner= str(request.user)

        up= UpLoadsCaseTemplate()
        up.owner= owner
        up.address= file
        up.uptimes= up_times
        up.save()

        process_xls.delay(up_times,owner,file_names)

    cases= TestCase.objects.filter(status= 0).order_by("-id")  # 上传完成后，自动跳回用例页面
    data= {}
    data["pages"]= get_paginator(request, cases)
    data["case_name"]= ""
    return render(request,"atp/test_case.html",data)


@login_required
def add_test_case(request):
    '''测试用例-手动创建用例'''
    if request.method== "GET":
        data= {}
        belong_project= Project.objects.all().order_by("id")
        belong_module= Module.objects.all().order_by("id")
        user= User.objects.all()
        data["request_method"]= vp.request_method
        data["user"]= user
        data["belong_project"]= belong_project
        data["belong_module"]= belong_module
        data["maintainer"]= str(request.user)
        return render(request, "atp/add_test_case.html",data)

    elif request.method== "POST":
        ts= TestCase()
        ts.case_name= request.POST.get("case_name")
        ts.request_data= request.POST.get("request_data")
        ts.uri= request.POST.get("uri")
        ts.maintainer= request.user
        ts.request_method= request.POST.get("request_method")
        u= request.POST.get("user")
        ts.user= User.objects.get(username= u)
        ts.status= 0

        bp= request.POST.get("belong_project")
        ts.belong_project= Project.objects.get(name= bp)
        bm= request.POST.get("belong_module")
        ts.belong_module= Module.objects.get(name= bm)
        try:
            related_case_id= int(request.POST.get("related_case_id"))
        except:
            related_case_id= None
        ts.related_case_id= related_case_id
        assert_key= request.POST.get("assert_key")
        if assert_key== '':
            assert_key= None
        ts.assert_key= assert_key
        extract_var= request.POST.get("extract_var")
        if extract_var== '':
            extract_var= None
        ts.extract_var= extract_var
        ts.save()

        cases= TestCase.objects.filter(status= 0).order_by("-id")
        data= {}
        data["pages"]= get_paginator(request, cases)
        data["case_name"]= ""
        return render(request, "atp/test_case.html", data)


def check_module_belong_project(request):
    '''
    测试用例-手动创建用例，查询所选模块是否属于项目
    :param request:
    :return:
    '''
    bm= request.GET.get("belong_module")
    bp= request.GET.get("belong_project")
    bmp_name= Module.objects.filter(name= bm).first().belong_project
    bp_name= Project.objects.filter(name= bp).first()
    data= {
        "code":200,
        "msg": ""
    }
    if bmp_name== bp_name:
        return JsonResponse(data= data)
    else:
        data["msg"]= "模块不属于已选择的项目，请重试"
        data["code"]= 901
        return JsonResponse(data= data)


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
        data["original_belong_project"]= case.belong_project
        data["original_belong_module"]= case.belong_module
        data["original_request_data"]= case.request_data
        data["original_uri"]= case.uri
        data["original_assert_key"]= case.assert_key
        data["original_maintainer"]= case.maintainer
        data["original_extract_var"]= case.extract_var
        data["original_request_method"]= case.request_method
        data["original_related_case_id"]= case.related_case_id
        data["original_user"]= case.user

        belong_project= Project.objects.all().order_by("id")
        belong_module= Module.objects.all().order_by("id")
        user= User.objects.all()
        data["request_method"]= vp.request_method
        data["user"]= user
        data["belong_project"]= belong_project
        data["belong_module"]= belong_module
        return render(request,"atp/update_test_case.html",data)

    elif request.method== "POST":
        case.case_name= request.POST.get("case_name")
        case.request_data= request.POST.get("request_data")
        case.uri= request.POST.get("uri")
        case.request_method= request.POST.get("request_method")
        u= request.POST.get("user")
        case.user= User.objects.get(username= u)

        bp= request.POST.get("belong_project")
        case.belong_project= Project.objects.get(name= bp)
        bm= request.POST.get("belong_module")
        case.belong_module= Module.objects.get(name= bm)
        try:
            related_case_id= int(request.POST.get("related_case_id"))
        except:
            related_case_id= None
        case.related_case_id= related_case_id
        assert_key= request.POST.get("assert_key")
        if assert_key== '':
            assert_key= None
        case.assert_key= assert_key
        extract_var= request.POST.get("extract_var")
        if extract_var== '':
            extract_var= None
        case.extract_var= extract_var
        case.update_time= datetime.datetime.now()
        case.save()
        return redirect(reverse("main_platform:test_case"))


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
    return redirect(reverse("main_platform:test_case"))


@login_required
def test_case_detail(request,caseid):
    '''测试用例-用例详情'''
    try:
        detail= TestCase.objects.get(id= caseid)
        data= {
            "test_case":detail
        }
        return render(request,"atp/test_case_detail.html",data)
    except:
        return render(request,"atp/index.html") # 如果找不到就回到主页，防止出现程序


@login_required
def module_test_case(request,moduleid):
    '''主页-模块，关联对应测试用例'''
    if moduleid:
        cases= TestCase.objects.filter(belong_module_id= moduleid,status= 0).order_by("-id")
    else:
        cases= TestCase.objects.filter(status= 0).order_by("-id")
        # 如果传入的模块id不存在，就返回全部用例
    data= {
        "pages": get_paginator(request, cases), # 返回分页
        "case_name":"",
    }
    return render(request,"atp/test_case.html",data)


@login_required
def test_suite(request):
    '''主页-用例集合'''
    if request.method== "GET":
        test_suite= TestSuite.objects.filter(status= 0).order_by("-id")
        data= {
            "pages": get_paginator(request, test_suite), # 返回分页
        }
        return render(request,"atp/test_suite.html",data)
    elif request.method== "POST":
    # 点击执行后，生成集合执行记录，集合执行记录包含用例执行记录
        suite_name= request.POST.get("suite_name")
        ex_suite= request.POST.get("ex_suite")  # 判断是否执行集合的关键字
        ex_time= request.POST.get("ex_time")  # 判断执行时间的关键字
        if ex_time== "":
            ex_time= (datetime.datetime.now() + datetime.timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M")
        year= ex_time[:4]
        month= ex_time[5:7]
        day= ex_time[8:10]
        hour= ex_time[11:13]
        minute= ex_time[14:]
        data= {}

        if not ex_suite:
            # 如果不是进行执行操作
            if suite_name in [None, ""]:
                suite_name= ""
                suites= TestSuite.objects.filter(status= 0).order_by("-id")
            else:
                suites= TestSuite.objects.filter(suite_desc__contains= suite_name, status=0).order_by("-id")
            data["pages"]= get_paginator(request, suites)
            data["suite_name"]= suite_name
            return render(request, "atp/test_suite.html", data)
        else:
            env= request.POST.get("env")
            test_suite_list= request.POST.getlist("testsuite_list")
            if len(test_suite_list)== 0:
                # 解决传空用例的问题
                test_suite= TestSuite.objects.filter(status= 0).order_by("-id")
                data= {
                    "pages": get_paginator(request, test_suite),  # 返回分页
                }
                return render(request, "atp/test_suite.html", data)
            else:
                job_name0= "test_job0_%s" % ex_time  # 处理用例和集合并行的问题
                job_name1= "test_job1_%s" % ex_time
                jb0= JobExecuted.objects.filter(job_id= job_name0).first()
                jb1= JobExecuted.objects.filter(job_id= job_name1).first()
                if jb0!= None or jb1!= None:
                    pass # 解决重复任务名的问题
                else:
                    register_jobs(test_suite_list,env,request.user.username,1,"test_job1_%s"%ex_time,
                                  year,month,day,hour,minute)
                    jbe= JobExecuted()  # 记录定时任务
                    jbe.job_id= "test_job1_%s" % ex_time
                    jbe.user= request.user.username
                    jbe.status= 0
                    jbe.save()
                return redirect(reverse("main_platform:test_execute",kwargs= {"jobid":"None"}))


@login_required
def add_case_into_suite(request,suiteid):
    '''主页-用例集合，将测试用例添加到测试集中'''
    test_suite= TestSuite.objects.get(id= suiteid)
    # 查询suiteid对应用例集
    if test_suite.type== 1:
        # UI测试进入不同的页面
        belong_suite_cases= Case2SuiteForSEA.objects.filter(test_suite= suiteid)
        belong_suite_cases= [x.test_case_id for x in belong_suite_cases]
        # 查询出此用例集已关联的用例

        test_cases= [i.id for i in TestCaseForSEA.objects.filter(status= 0).all()]  # 查询出所有用例的id
        test_cases= list(filter(lambda x: x not in belong_suite_cases, test_cases))
        # lambda清除在所有用例中,已经关联过用例集的id
        test_cases= TestCaseForSEA.objects.filter(id__in= test_cases).order_by("-id")
        # 没有notin函数，所以使用此方法，去除用例重复添加的可能性

        if request.method== "GET":
            data= {
                "pages": get_paginator(request, test_cases)
            }
            return render(request, "sea/sea_add_case_into_suite.html", data)

        elif request.method== "POST":
            data= {
                "pages": get_paginator(request, test_cases), # 返回分页
            }
            testcases_list= request.POST.getlist("testcases_list")
            if testcases_list:
                for tl in testcases_list:
                    test_case= TestCaseForSEA.objects.filter(id= int(tl))
                    sc_obj,created= Case2SuiteForSEA.objects.get_or_create(
                        test_case= test_case.first(),test_suite= test_suite) # 自带查重方法，建议使用
                    if created== False:
                        data["msg"]= "用例重复添加"
                return redirect(reverse("main_platform:add_case_into_suite",kwargs= {"suiteid":suiteid}))
                # 添加成功后，自动刷新页面
            else:
                data["msg"]= "添加用例为空"
    else:
        belong_suite_cases= AddCaseIntoSuite.objects.filter(test_suite= suiteid)
        belong_suite_cases= [x.test_case_id for x in belong_suite_cases]
        # 查询出此用例集已关联的用例

        test_cases= [i.id for i in TestCase.objects.filter(status= 0).all()] # 查询出所有用例的id
        test_cases= list(filter(lambda x:x not in belong_suite_cases,test_cases))
        # lambda清除在所有用例中,已经关联过用例集的id
        test_cases= TestCase.objects.filter(id__in= test_cases).order_by("-id")
        # 没有notin函数，所以使用此方法，去除用例重复添加的可能性

        if request.method== "GET":
            data= {
                "pages": get_paginator(request, test_cases)
            }
            return render(request, "atp/add_case_into_suite.html", data)

        elif request.method== "POST":
            data= {
                "pages": get_paginator(request, test_cases), # 返回分页
            }
            testcases_list= request.POST.getlist("testcases_list")
            if testcases_list:
                for tl in testcases_list:
                    test_case= TestCase.objects.filter(id= int(tl))
                    sc_obj,created= AddCaseIntoSuite.objects.get_or_create(
                        test_case= test_case.first(),test_suite= test_suite) # 自带查重方法，建议使用
                    if created== False:
                        data["msg"]= "用例重复添加"
                return redirect(reverse("main_platform:add_case_into_suite",kwargs= {"suiteid":suiteid}))
                # 添加成功后，自动刷新页面
            else:
                data["msg"]= "添加用例为空"


@login_required
def view_or_delete_cases_in_suite(request,suiteid):
    '''主页-用例集合，将测试用例从到测试集中删除'''
    test_suite= TestSuite.objects.get(id= suiteid)
    # 查询suiteid对应用例集

    if test_suite.type== 1:
        # UI测试进入不同的页面
        belong_suite_cases= Case2SuiteForSEA.objects.filter(test_suite_id=suiteid)
        belong_suite_cases= [x.test_case_id for x in belong_suite_cases]
        # 查询出此用例集已关联的用例

        test_cases= TestCaseForSEA.objects.filter(id__in= belong_suite_cases).order_by("id")

        if request.method== "GET":
            data= {
                "pages": get_paginator(request, test_cases)
            }
            return render(request, "sea/sea_sd_cases_in_suite.html", data)

        elif request.method== "POST":
            data= {
                "pages": get_paginator(request, test_cases), # 返回分页
            }
            testcases_list= request.POST.getlist("testcases_list")
            if testcases_list:
                for tl in testcases_list:
                    test_case= TestCaseForSEA.objects.filter(id=int(tl))
                    Case2SuiteForSEA.objects.filter(test_case= test_case.first(),test_suite= test_suite).first().delete()
                    # 删除指定用例集的指定测试用例
                return redirect(reverse("main_platform:view_or_delete_cases_in_suite",kwargs= {"suiteid":suiteid}))
                # 添加成功后，自动刷新页面
            else:
                data["msg"]= "删除用例为空"

    else:
        belong_suite_cases= AddCaseIntoSuite.objects.filter(test_suite_id= suiteid)
        belong_suite_cases= [x.test_case_id for x in belong_suite_cases]
        # 查询出此用例集已关联的用例

        test_cases= TestCase.objects.filter(id__in= belong_suite_cases).order_by("id")

        if request.method== "GET":
            data= {
                "pages": get_paginator(request, test_cases)
            }
            return render(request, "atp/view_or_delete_cases_in_suite.html", data)

        elif request.method== "POST":
            data= {
                "pages": get_paginator(request, test_cases), # 返回分页
            }
            testcases_list= request.POST.getlist("testcases_list")
            if testcases_list:
                for tl in testcases_list:
                    test_case= TestCase.objects.filter(id=int(tl))
                    AddCaseIntoSuite.objects.filter(test_case= test_case.first(),test_suite= test_suite).first().delete()
                    # 删除指定用例集的指定测试用例
                return redirect(reverse("main_platform:view_or_delete_cases_in_suite",kwargs= {"suiteid":suiteid}))
                # 添加成功后，自动刷新页面
            else:
                data["msg"]= "删除用例为空"


@login_required
def test_execute(request,jobid):
    '''
    主页-执行结果
    :param request:
    :param jobid: 加入任务查看
    :return:
    '''
    if jobid== "None":
        test_execute= TestExecute.objects.filter().order_by("-id")
        data= {
            "pages": get_paginator(request, test_execute),  # 返回分页
        }
    else:
        test_execute= TestExecute.objects.get(job_id= jobid)
        test_execute1= [test_execute]
        data= {
            "pages": get_paginator(request, test_execute1),  # 返回分页
        }
    return render(request, "atp/test_execute.html", data)


@login_required
def down_test_execute_template(request,id):
    '''
    执行结果-下载测试报告
    :param request:
    :return:
    '''
    def file_iterator(file, chunk_size= 512):
        with open(file,'rb') as f:
            while True:
                c= f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    file= TestExecute.objects.get(id= id).download_report_path
    file_name= file[7:]
    response= StreamingHttpResponse(file_iterator(file))
    response['Content-Type']= 'application/octet-stream'
    response['Content-Disposition']= 'attachment;filename="{0}"'.\
        format(file_name.encode("utf-8").decode("ISO-8859-1"))
    return response


@login_required
def test_case_execute_record(request,id):
    '''执行结果-执行用例记录'''
    test_case_execute_records= TestCaseExecuteResult.objects.filter(belong_test_execute= id).order_by("-id")
    data= {
        "pages": get_paginator(request, test_case_execute_records), # 返回分页
    }
    return render(request,"atp/test_case_execute_records.html",data)


@login_required
def test_execute_show_exception(request,execute_id):
    '''执行结果-用例错误信息查看'''
    tcer= TestCaseExecuteResult.objects.get(id= execute_id)
    return render(request, "atp/test_execute_show_exception.html", {"exception_info": tcer.exception_info})


@login_required
def testsuite_execute_show_exception(request,execute_id):
    '''执行结果-集合用例错误信息查看'''
    tcer= TestSuiteTestCaseExecuteRecord.objects.get(id= execute_id)
    return render(request, "atp/test_execute_show_exception.html", {"exception_info": tcer.exception_info})


@login_required
def test_suite_execute_record(request,id,statistics):
    '''执行结果-执行集合记录'''
    if statistics== "0":
        # 判断是集合统计or执行结果进入，0代表从执行结果进入
        test_suite_execute_records= TestSuiteExecuteRecord.objects.\
            filter(belong_test_execute= id).order_by("-id")
    else:
        test_suite_execute_records= TestSuiteExecuteRecord.objects.\
            filter(id= id).order_by("-id")
    data= {
        "pages": get_paginator(request, test_suite_execute_records), # 返回分页
    }
    return render(request,"atp/test_suite_execute_records.html",data)


@login_required
def test_suite_test_case_execute_record(request,id):
    '''执行结果-执行集合记录-执行用例记录及统计'''

    test_suite_test_case_execute_records= TestSuiteTestCaseExecuteRecord.\
        objects.filter(belong_test_suite_exe= id).order_by("-id")
    success= len(TestSuiteTestCaseExecuteRecord.objects.filter(belong_test_suite_exe= id,execute_result= "成功"))
    fail= len(TestSuiteTestCaseExecuteRecord.objects.filter(belong_test_suite_exe= id,execute_result= "失败"))
    records= TestSuiteTestCaseExecuteRecord.objects.filter(belong_test_suite_exe= id).order_by("-id")
    data= {
        "pages": get_paginator(request, test_suite_test_case_execute_records), # 返回分页
        "success":success,
        "fail":fail,
        "records":records
    }
    return render(request,"atp/test_suite_test_case_execute_records.html",data)


@login_required
def test_suite_statistics(request,suite_id):
    '''
    主页-用例集合-用例集合执行历史结果统计
    :param request:
    :param suite_id:
    :return:
    '''
    success= len(TestSuiteExecuteRecord.objects.filter(test_suite_id= suite_id,test_result= "成功"))
    fail= len(TestSuiteExecuteRecord.objects.filter(test_suite_id= suite_id,test_result= "失败"))
    records= TestSuiteExecuteRecord.objects.filter(test_suite_id= suite_id).order_by("-id")

    data= {
        "pages": get_paginator(request, records), # 返回分页
        "success":success,
        "fail":fail
    }

    return render(request,"atp/test_suite_statistics.html",data)


@login_required
def module_test_case_statistics(request,module_id):
    '''
    主页-测试模块-查看结果统计，含用例执行及集合执行结果
    :param request:
    :param module_id:
    :return:
    '''
    cases= TestCase.objects.filter(status= 0,belong_module= module_id).order_by("-id")
    module= Module.objects.get(id= module_id)
    test_case_pass= len(TestCaseExecuteResult.objects.filter(belong_test_case__in= cases,
                                                             execute_result= "成功"))
    test_suite_pass= len(TestSuiteTestCaseExecuteRecord.objects.filter(belong_test_case__in= cases,
                                                             execute_result= "成功"))
    test_case_fail= len(TestCaseExecuteResult.objects.filter(belong_test_case__in= cases,
                                                             execute_result= "失败"))
    test_suite_fail= len(TestSuiteTestCaseExecuteRecord.objects.filter(belong_test_case__in= cases,
                                                             execute_result= "失败"))
    success= test_suite_pass+test_case_pass
    fail= test_suite_fail+test_case_fail
    data= {
        "pages":get_paginator(request, cases),
        "module":module,
        "success":success,
        "fail":fail,
    }
    return render(request, "atp/module_test_case_statistics.html", data)


@login_required
def project_test_case_statistics(request,project_id):
    '''
    主页-测试项目-查看结果统计，含用例执行及集合执行结果
    :param request:
    :param project_id:
    :return:
    '''
    cases= TestCase.objects.filter(status= 0,belong_project= project_id).order_by("-id")
    project= Project.objects.get(id= project_id)
    test_case_pass= len(TestCaseExecuteResult.objects.filter(belong_test_case__in= cases,
                                                             execute_result= "成功"))
    test_suite_pass= len(TestSuiteTestCaseExecuteRecord.objects.filter(belong_test_case__in= cases,
                                                             execute_result= "成功"))
    test_case_fail= len(TestCaseExecuteResult.objects.filter(belong_test_case__in= cases,
                                                             execute_result= "失败"))
    test_suite_fail= len(TestSuiteTestCaseExecuteRecord.objects.filter(belong_test_case__in= cases,
                                                             execute_result= "失败"))
    success= test_suite_pass+test_case_pass
    fail= test_suite_fail+test_case_fail

    data= {
        "pages": get_paginator(request, cases),
        "success":success,
        "fail":fail,
        "project":project

    }
    return render(request, "atp/project_test_case_statistics.html", data)


@login_required
def job_execute(request):
    '''
    主页-定时任务列表
    :param request:
    :return:
    '''
    if request.method== "POST":
        # 如果为post请求
        job_name= request.POST.get("job_name")
        if job_name== "":
            # 未输入直接点击查询，返回所有任务
            job_name= ""
            jobs= JobExecuted.objects.filter(~Q(status= 2)).order_by("-id")
            # Q方法用于过滤时的不等于方式
        else:
            jobs= JobExecuted.objects.filter(~Q(status= 2)).filter(job_id__contains= job_name).order_by("-id") # 模糊查询所有任务名
    else:
        job_name= ""
        jobs= JobExecuted.objects.filter(~Q(status= 2)).order_by("-id")

    data= {
        "pages": get_paginator(request, jobs),  # 返回分页
        "job_name": job_name,
    }
    return render(request, "atp/job_execute.html", data)


@login_required
def change_job_status(request,id,status):
    '''
    主页-定时任务-修改任务状态
    :param request:
    :param id:
    :param status:改变状态
    :return:
    '''
    if request.method!= "GET":
        pass
        # return JsonResponse(data= {"msg":"错误的请求方式","code":404})
    else:
        if status not in vp.job_status:
            pass
            # return JsonResponse(data= {"msg":"错误的任务状态","code":404})
        else:
            if status== "2": # 删除
                scheduler.remove_job(job_id= id)
            elif status== "3": # 暂停
                scheduler.pause_job(job_id= id)
            elif status== "0": # 恢复
                scheduler.resume_job(job_id= id)
            job= JobExecuted.objects.get(job_id= id)
            job.status= status
            job.save()
            # return JsonResponse(data= {"msg":"修改状态完成","code":200})
    return redirect(reverse("main_platform:job_execute"))


scheduler.start()
'''
Apscheduler报错问题，因为在uwsgi是启用的多进程，然后每个进程中都存在一个执行器的实例，
在定时任务的数据表django_apscheduler_djangojobexecution中每一个任务其实是有4个实例，
并且会报一个get() returned more than one %s – it returned %s的一个报错，
其实这个报错的原因是因为：他使用的django的orm的get方法，因为get如果获取到的是多条而不是唯一就会报错
'''