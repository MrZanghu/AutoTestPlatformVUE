from django.db import models
from main_platform.models import TestSuite
from django.contrib.auth.models import User



class TestCaseForSEA(models.Model):
    '''用例模型'''
    id= models.AutoField(primary_key= True)
    case_name= models.CharField("用例名称", max_length= 256, blank= True, null=True)
    status= models.IntegerField(blank= True, null= True, help_text="0:表示有效，1:表示无效，用于软删除", default= 0)
    create_time= models.DateTimeField("创建时间", auto_now_add= True)
    update_time= models.DateTimeField("更新时间", auto_now=True, blank=True, null=True)
    user= models.CharField("创建人", max_length= 20, blank= True, null= True)
    length= models.IntegerField("步长",blank= True, null= True,default= 0)

    # 打印对象时返回项目名称
    def __str__(self):
        return self.case_name

    class Meta:
        db_table= "sea_test_case"
        verbose_name= "测试用例表"
        verbose_name_plural= "测试用例表"


class TestCaseSteps(models.Model):
    '''用例模型-测试步骤'''
    id= models.AutoField(primary_key= True)
    testcaseid= models.ForeignKey(TestCaseForSEA,on_delete= models.CASCADE, verbose_name= "所属用例")
    LocationPath= models.CharField("定位路径", max_length= 256, blank= True, null=True)
    Method= models.CharField("方法|操作", max_length= 256, blank= True, null=True)
    Parameter= models.CharField("传入参数", max_length= 256, blank= True, null=True)
    Action= models.CharField("步骤动作", max_length= 256, blank= True, null=True)
    Expected= models.CharField("预期结果", max_length= 256, blank= True, null=True)
    status= models.IntegerField(blank= True, null= True, help_text="0:表示有效，1:表示无效，用于软删除", default= 0)
    create_time= models.DateTimeField("创建时间", auto_now_add= True)

    # 打印对象时返回项目名称
    def __str__(self):
        return self.testcaseid

    class Meta:
        db_table= "sea_test_case_steps"
        verbose_name= "用例步骤表"
        verbose_name_plural= "用例步骤表"


class Case2SuiteForSEA(models.Model):
    '''向用例集添加用例模型'''
    id= models.AutoField(primary_key= True)
    test_suite= models.ForeignKey(TestSuite, on_delete= models.CASCADE, verbose_name= "用例集合")
    test_case= models.ForeignKey(TestCaseForSEA, on_delete= models.CASCADE, verbose_name= "测试用例")
    status= models.IntegerField(verbose_name="是否有效", blank= True, null= True, default= 0,
                                help_text= '0：有效，1：无效')
    create_time= models.DateTimeField("创建时间", auto_now=True)  # 创建时间-自动获取当前时间

    class Meta:
        db_table= "sea_case_2_suite"
        verbose_name= "用例集中添加用例表"
        verbose_name_plural= "用例集中添加用例表"


class TestCaseExecuteResultForSEA(models.Model):
    '''用例执行记录模型'''
    id= models.AutoField(primary_key= True)
    belong_test_execute= models.CharField(max_length= 128, blank= True, null= True) # 关联的记录id
    belong_test_case= models.ForeignKey(TestCaseForSEA, on_delete= models.CASCADE, verbose_name= "所属用例")
    status= models.IntegerField(blank= True, null= True, help_text="0：表示未执行，1：表示已执行")
    length= models.IntegerField("步长",blank= True, null= True,default= 0)
    execute_result= models.CharField("执行结果", max_length= 1024, blank= True, null= True)  # 成功/失败
    exception_info= models.CharField(max_length= 2048, blank= True, null= True)
    execute_total_time= models.CharField("执行总计耗时", max_length= 300, blank= True, null= True)
    execute_start_time= models.CharField("执行开始时间", max_length= 300, blank= True, null= True)
    execute_end_time= models.CharField("执行结束时间", max_length= 300, blank= True, null= True)
    created_time= models.DateTimeField("创建时间", auto_now_add= True)
    updated_time= models.DateTimeField("更新时间", auto_now= True, blank= True, null= True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table= "sea_test_case_execute_result"
        verbose_name= "用例执行结果记录表"
        verbose_name_plural= "用例执行结果记录表"


class Case2SuiteExecuteResultForSEA(models.Model):
    '''
        集合执行记录-用例执行记录模型，
        特意为UI集合编写，其他复用TestSuiteExecuteRecord
    '''
    id= models.AutoField(primary_key=True)
    belong_test_suite_exe= models.CharField(max_length=128, blank= True, null= True)  # 关联TestSuiteExecuteRecord的id
    belong_test_case= models.ForeignKey(TestCaseForSEA, on_delete= models.CASCADE, verbose_name= "所属用例")
    status= models.IntegerField(blank= True, null= True, help_text="0：表示未执行，1：表示已执行")
    length= models.IntegerField("步长",blank= True, null= True,default= 0)
    execute_result= models.CharField("执行结果", max_length= 1024, blank= True, null= True)  # 成功/失败
    exception_info= models.CharField(max_length= 2048, blank= True, null= True)
    execute_total_time= models.CharField("执行总计耗时", max_length= 300, blank= True, null= True)
    execute_start_time= models.CharField("执行开始时间", max_length= 300, blank= True, null= True)
    execute_end_time= models.CharField("执行结束时间", max_length= 300, blank= True, null= True)
    created_time= models.DateTimeField("创建时间", auto_now_add= True)
    updated_time= models.DateTimeField("更新时间", auto_now= True, blank= True, null= True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table= "sea_case2suite_execute_result"
        verbose_name= "用例执行结果记录表"
        verbose_name_plural= "用例执行结果记录表"