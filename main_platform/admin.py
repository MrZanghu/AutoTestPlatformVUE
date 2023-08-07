from django.contrib import admin
from .models import Project,Module,TestCase,TestSuite,Server,EmailAddress



class ProjectAdmin(admin.ModelAdmin):
    '''项目管理'''
    list_display= ("id","name","proj_owner","test_owner",
                   "dev_owner","desc","create_time","update_time")
    list_per_page= 10


class ModuleAdmin(admin.ModelAdmin):
    '''模块管理'''
    list_display= ("id","name","belong_project","test_owner",
                   "desc","create_time","update_time")
    list_per_page= 10


class TestCaseAdmin(admin.ModelAdmin):
    '''用例管理'''
    list_display= ("id", "case_name", "belong_project", "belong_module", "request_data",
                    "uri", "assert_key", "maintainer","extract_var", "request_method",
                    "status", "create_time", "update_time", "user")
    list_per_page= 10


class TestSuiteAdmin(admin.ModelAdmin):
    '''用例集管理'''
    list_display= ("id","suite_desc","type","creator","create_time")
    list_per_page= 10


class ServerAdmin(admin.ModelAdmin):
    '''环境管理'''
    list_display= ("id", "env", "ip", "port","is_https" ,"remark", "create_time")
    list_per_page= 10


class EmailAdmin(admin.ModelAdmin):
    '''环境管理'''
    list_display= ("id","address","create_time")
    list_per_page= 10


admin.site.register(Project,ProjectAdmin)
admin.site.register(Module,ModuleAdmin)
admin.site.register(TestCase,TestCaseAdmin)
admin.site.register(TestSuite,TestSuiteAdmin)
admin.site.register(Server,ServerAdmin)
admin.site.register(EmailAddress,EmailAdmin)


admin.site.site_header= "自动化测试平台"
admin.site.site_title= "自动化测试平台"