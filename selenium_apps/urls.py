from django.urls import re_path,path
from selenium_apps import views



app_name= "[send_mails]"
urlpatterns= [
    path(r'test_case/', views.test_case,name= "test_case"),
    re_path(r'^test_case_detail/(?P<caseid>\d+)/', views.test_case_detail, name="test_case_detail"),

    path(r'add_test_case/', views.add_test_case,name= "add_test_case"),
    path(r'add_test_case_interface/', views.add_test_case_interface,name= "add_test_case_interface"),
    re_path(r'^test_case_execute_record/(?P<id>\d+)/',
            views.test_case_execute_record, name="test_case_execute_record"),
    re_path('test_execute_show_exception/(?P<execute_id>[0-9]+)$',
            views.test_execute_show_exception, name="test_execute_show_exception"),

    re_path(r'^update_test_case/(?P<caseid>\d+)/', views.update_test_case, name= "update_test_case"),
    path(r'update_test_case_interface/', views.update_test_case_interface,name= "update_test_case_interface"),
    re_path(r'^delete_test_case/(?P<caseid>\d+)/', views.delete_test_case, name="delete_test_case"),
    path(r'test_case/sea/get_job_name/',views.get_job_name, name= "get_job_name"),

    re_path(r'^test_suite/(?P<suite_type>\d+)/', views.test_suite,name= "test_suite"),
]