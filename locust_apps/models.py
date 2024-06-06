from django.db import models
from main_platform.models import TestSuite



class LocTestCase(models.Model):
    '''用例模型'''
    id= models.AutoField(primary_key= True)
    case_name= models.CharField("用例名称", max_length= 128, blank= True, null= True)
    uri= models.CharField("接口地址", max_length= 1024, blank= True, null= True, default= "")
    request_method= models.CharField("请求方式", max_length=128, blank=True, null=True)
    request_data= models.CharField("请求数据", max_length=1024, blank=True, null=True, default="")
    assert_key= models.CharField("断言内容", max_length=1024, blank=True, null=True)
    maintainer= models.CharField("编写人员", max_length= 20, blank= True, null= True, default= "")
    status= models.IntegerField(blank= True, null= True,help_text="0:表示有效，1:表示无效，用于软删除",default= 0)
    create_time= models.DateTimeField("创建时间", auto_now_add= True)
    update_time= models.DateTimeField("更新时间", auto_now= True, blank= True, null= True)

    def __str__(self):
        return self.case_name

    class Meta:
        db_table= "loc_test_case"
        verbose_name= "测试用例表"
        verbose_name_plural= "测试用例表"


class AddLocCase2Suite(models.Model):
    '''向用例集添加用例模型'''
    id= models.AutoField(primary_key= True)
    test_suite= models.ForeignKey(TestSuite, on_delete= models.CASCADE, verbose_name= "用例集合")
    test_case= models.ForeignKey(LocTestCase, on_delete= models.CASCADE, verbose_name= "测试用例")
    status= models.IntegerField(verbose_name="是否有效", blank= True, null= True, default= 0,
                                help_text= '0：有效，1：无效')
    create_time= models.DateTimeField("创建时间", auto_now=True)  # 创建时间-自动获取当前时间

    class Meta:
        db_table= "loc_add_case_into_suite"
        verbose_name= "用例集中添加用例表"
        verbose_name_plural= "用例集中添加用例表"


class TestExecuteResult(models.Model):
    '''压力执行记录模型'''
    id= models.AutoField(primary_key= True)
    belong_test_execute= models.CharField(max_length=128, blank=True, null=True)  # 关联的记录id
    status= models.IntegerField(blank= True, null= True, help_text="0：表示未执行，1：表示已执行")
    type= models.IntegerField(blank= True, null= True, help_text="0：表示用例，1：表示集合")
    case_suite_list= models.CharField("用例/集合id列表", max_length= 1024, blank= True, null= True)
    ex_u= models.IntegerField(blank= True, null= True)
    ex_r= models.IntegerField(blank= True, null= True)
    ex_t= models.IntegerField(blank= True, null= True)
    creator= models.CharField(max_length=50, blank= True, null= True)
    create_time= models.DateTimeField("创建时间", auto_now= True)   # 创建时间-自动获取当前时间

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table= "loc_test_execute_result"
        verbose_name= "压力执行结果记录表"
        verbose_name_plural= "压力执行结果记录表"