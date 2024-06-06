from django.urls import re_path,path
from locust_apps import views



app_name= "[locust_apps]"
urlpatterns= [
    path(r'test_case/loc/get_job_name/',views.get_job_name, name= "get_job_name"),
    path(r'test_case/', views.test_case,name= "test_case"),
    path(r'add_test_case/', views.add_test_case,name= "add_test_case"),
    re_path(r'^update_test_case/(?P<caseid>\d+)/', views.update_test_case,name= "update_test_case"),
    re_path(r'^delete_test_case/(?P<caseid>\d+)/', views.delete_test_case,name= "delete_test_case"),
    re_path(r'^test_case_detail/(?P<caseid>\d+)/', views.test_case_detail, name="test_case_detail"),
    re_path(r'^test_suite/(?P<suite_type>\d+)/', views.test_suite,name= "test_suite"),
    path(r'test_suite/loc/get_job_name/', views.get_job_name, name="get_job_name"),
    re_path(r'^test_case_execute_record/(?P<id>\d+)/',
            views.test_case_execute_record, name="test_case_execute_record"),
]