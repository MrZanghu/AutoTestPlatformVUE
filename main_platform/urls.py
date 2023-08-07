from django.urls import re_path,path
from main_platform import views


app_name= "[main_platform]"
urlpatterns= [
    path(r'get_test/', views.get_test,name= "get_test"),
    path(r'post_test/', views.post_test,name= "post_test"),
    path(r'put_test/', views.put_test,name= "put_test"),
    # 本机测试使用

    path(r'index/', views.index,name= "index"),
    path(r'login/', views.login,name= "login"),
    path(r'get_code/', views.get_code,name= "get_code"),
    path(r'logout/', views.logout,name= "logout"),
    # 登录相关

    path(r'project/', views.project,name= "project"),
    path(r'module/', views.module,name= "module"),
    path(r'test_case/', views.test_case,name= "test_case"),
    re_path(r'^test_case_detail/(?P<caseid>\d+)/', views.test_case_detail,name= "test_case_detail"),
    # 模块相关

    path(r'down_test_template/', views.down_test_template,name= "down_test_template"),
    path(r'up_test_template/', views.up_test_template,name= "up_test_template"),
    path(r'add_test_case/', views.add_test_case,name= "add_test_case"),
    re_path(r'^update_test_case/(?P<caseid>\d+)/', views.update_test_case,name= "update_test_case"),
    re_path(r'^delete_test_case/(?P<caseid>\d+)/', views.delete_test_case,name= "delete_test_case"),
    path(r'check_module_belong_project/',
        views.check_module_belong_project,name= "check_module_belong_project"),
    path(r'down_test_template/', views.down_test_template,name= "down_test_template"),
    re_path(r'^module_test_case/(?P<moduleid>\d+)/', views.module_test_case, name="module_test_case"),
    # 新增用例相关

    path(r'test_suite/', views.test_suite,name= "test_suite"),
    re_path(r'^add_case_into_suite/(?P<suiteid>\d+)/', views.add_case_into_suite,name= "add_case_into_suite"),
    re_path(r'^view_or_delete_cases_in_suite/(?P<suiteid>\d+)/', views.view_or_delete_cases_in_suite,
        name= "view_or_delete_cases_in_suite"),
    # 用例集相关

    re_path(r'test_execute/(?P<jobid>[\s\S]*)/', views.test_execute, name= "test_execute"),
    re_path(r'^down_test_execute_template/(?P<id>\d+)/',
        views.down_test_execute_template, name= "down_test_execute_template"),
    re_path(r'^test_case_execute_record/(?P<id>\d+)/',
        views.test_case_execute_record, name= "test_case_execute_record"),
    re_path('test_execute_show_exception/(?P<execute_id>[0-9]+)$',
            views.test_execute_show_exception, name= "test_execute_show_exception"),
    re_path('testsuite_execute_show_exception/(?P<execute_id>[0-9]+)$',
            views.testsuite_execute_show_exception, name="testsuite_execute_show_exception"),
    re_path(r'^test_suite_execute_record/(?P<id>\d+)/(?P<statistics>\d+)/',
        views.test_suite_execute_record, name= "test_suite_execute_record"),
    # 执行记录相关

    re_path(r'^test_suite_statistics/(?P<suite_id>\d+)/',
            views.test_suite_statistics, name="test_suite_statistics"),
    re_path(r'^test_suite_tc_execute_record/(?P<id>\d+)/',
            views.test_suite_test_case_execute_record,
            name="test_suite_tc_execute_record"),  # 地址路径不能过长，导致读取不出id
    re_path(r'^module_test_case_statistics/(?P<module_id>\d+)/',
            views.module_test_case_statistics, name="module_test_case_statistics"),
    re_path(r'^project_test_case_statistics/(?P<project_id>\d+)/',
            views.project_test_case_statistics, name="project_test_case_statistics"),
    # 统计结果相关

    path(r'job_execute/', views.job_execute, name= "job_execute"),
    re_path(r'^change_job_status/(?P<id>([\s\S]*))/(?P<status>\d+)/',
            views.change_job_status, name= "change_job_status"),
    path(r'test_case/atp/get_job_name/',views.get_job_name, name= "get_job_name"),
    path(r'test_suite/atp/get_job_name/',views.get_job_name, name= "get_job_name"),
    # 任务相关
]