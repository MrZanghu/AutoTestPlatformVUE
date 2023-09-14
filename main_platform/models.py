import datetime
from django.db import models
from django.contrib.auth.models import User
from smart_selects.db_fields import GroupedForeignKey



'''
Note:
1.解决删除数据后的id自增问题
    set @auto_id=0;
    UPDATE atp_test_case_execute_result set id= (@auto_id:= @auto_id+1);
    ALTER TABLE atp_test_case_execute_result AUTO_INCREMENT=1;
'''


class Project(models.Model):
    '''项目模型'''
    id= models.AutoField(primary_key= True)
    name= models.CharField("项目名称", max_length= 128, unique= True, blank= True, null= True)
    proj_owner= models.CharField("项目负责人", max_length= 20, blank= True, null= True)
    test_owner= models.CharField("测试负责人", max_length= 20, blank= True, null= True)
    dev_owner= models.CharField("开发负责人", max_length= 20, blank= True, null= True)
    desc= models.CharField("项目描述", max_length= 256, blank= True, null= True)
    create_time= models.DateTimeField("项目创建时间", auto_now_add= True)
    update_time= models.DateTimeField("项目更新时间", auto_now= True, blank= True, null= True)

    # 打印对象时返回项目名称
    def __str__(self):
        return self.name

    class Meta:
        db_table= "atp_project"
        verbose_name= "项目信息表"
        verbose_name_plural= "项目信息表"


class Module(models.Model):
    '''模块模型'''
    id= models.AutoField(primary_key= True)
    name= models.CharField("模块名称", max_length= 128, blank= True, null= True)
    belong_project= models.ForeignKey(Project, on_delete= models.CASCADE)
    # 和项目绑定的外键
    test_owner= models.CharField("测试负责人", max_length= 20, blank= True, null= True)
    desc= models.CharField("简要描述", max_length= 256, blank= True, null= True)
    create_time= models.DateTimeField("创建时间", auto_now_add= True)
    update_time= models.DateTimeField("更新时间", auto_now= True, blank= True, null= True)

    def __str__(self):
        return self.name

    class Meta:
        db_table= "atp_module"
        verbose_name= "模块信息表"
        verbose_name_plural= "模块信息表"


class TestCase(models.Model):
    '''用例模型'''
    id= models.AutoField(primary_key= True)
    case_name= models.CharField("用例名称", max_length= 128, blank= True, null= True)
    belong_project= models.ForeignKey(Project, on_delete= models.CASCADE, verbose_name= "所属项目")
    belong_module= GroupedForeignKey(Module, "belong_project", on_delete= models.CASCADE, verbose_name= "所属模块")
    # GroupedForeignKey 可以支持在 admin 新增数据时，展示该模型类的关联表数据
    request_data= models.CharField("请求数据", max_length= 1024, blank= True, null= True, default= "")
    uri= models.CharField("接口地址", max_length= 1024, blank= True, null= True, default= "")
    assert_key= models.CharField("断言内容", max_length= 1024, blank= True, null= True)
    maintainer= models.CharField("编写人员", max_length= 20, blank= True, null= True, default= "")
    extract_var= models.CharField("提取变量表达式", max_length= 1024, blank= True, null= True)
    # 用来提取结果中的值：userid||userid":(\d+)
    request_method= models.CharField("请求方式", max_length= 128, blank= True, null= True)
    status= models.IntegerField(blank= True, null= True,help_text="0:表示有效，1:表示无效，用于软删除",default= 0)
    related_case_id= models.IntegerField(blank= True, null= True,default= None) # 提取其他用例的参数使用
    create_time= models.DateTimeField("创建时间", auto_now_add= True)
    update_time= models.DateTimeField("更新时间", auto_now= True, blank= True, null= True)
    user= models.ForeignKey(User, on_delete= models.CASCADE, verbose_name= "责任人", blank= True, null= True)

    def __str__(self):
        return self.case_name

    class Meta:
        db_table= "atp_test_case"
        verbose_name= "测试用例表"
        verbose_name_plural= "测试用例表"


class TestExecute(models.Model):
    '''执行记录总页模型'''
    id= models.AutoField(primary_key= True)
    created_time= models.DateTimeField("执行时间", auto_now_add= True)
    user= models.CharField(max_length= 128, blank= True, null= True)
    type= models.IntegerField(default= 0, blank= True, null= True) # 0代表用例，1代表集合，2代表UI用例，3代表UI集合
    case_or_suite_ids= models.CharField(max_length= 1024, blank= True, null= True) # 用于保存执行的用例/集合结果表id
    download_report_path= models.CharField(max_length= 1024, blank= True, null= True) # 报告路径
    job_id= models.CharField(max_length= 128, blank= True, null= True) # 关联的任务id

    class Meta:
        db_table= "atp_test_execute"
        verbose_name= "执行结果记录表"
        verbose_name_plural= "执行结果记录表"


class TestCaseExecuteResult(models.Model):
    '''用例执行记录模型'''
    id= models.AutoField(primary_key= True)
    belong_test_execute= models.CharField(max_length= 128, blank= True, null= True) # 关联的记录id
    belong_test_case= models.ForeignKey(TestCase, on_delete= models.CASCADE, verbose_name="所属用例")
    status= models.IntegerField(blank= True, null= True, help_text="0：表示未执行，1：表示已执行")
    exception_info= models.CharField(max_length= 2048, blank= True, null= True)
    request_data= models.CharField("请求数据", max_length= 1024, blank= True, null= True)
    response_data= models.CharField("响应数据", max_length= 1024, blank= True, null= True)
    execute_result= models.CharField("执行结果", max_length= 1024, blank= True, null= True)  # 成功/失败
    extract_var= models.CharField("提取变量", max_length= 1024, blank= True, null= True)  # 响应成功后提取变量
    execute_total_time= models.CharField("执行总计耗时", max_length= 300, blank= True, null= True)
    execute_start_time= models.CharField("执行开始时间", max_length= 300, blank= True, null= True)
    execute_end_time= models.CharField("执行结束时间", max_length= 300, blank= True, null= True)
    created_time= models.DateTimeField("创建时间", auto_now_add= True)
    updated_time= models.DateTimeField("更新时间", auto_now= True, blank= True, null= True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table= "atp_test_case_execute_result"
        verbose_name= "用例执行结果记录表"
        verbose_name_plural= "用例执行结果记录表"


def uploads_file(instance,filename):
    '''上传测试用例的文件名修改'''
    times= datetime.datetime.now().strftime("%H_%M_%S")
    y= datetime.datetime.now().strftime("%Y")
    m= datetime.datetime.now().strftime("%m")
    d= datetime.datetime.now().strftime("%d")
    if filename[-4:]== ".xls":
        filenames= filename.replace(".xls","_")+times+".xls"
    else:
        filenames= filename.replace(".json","_")+times+".json"
    return "{}/{}/{}".format(y,m+d,filenames)


class UpLoadsCaseTemplate(models.Model):
    '''上传测试用例模板'''
    address= models.FileField(upload_to= uploads_file, blank= True, null= True)
    uptimes= models.CharField("上传时间",max_length= 128, blank= True, null= True)
    create_time= models.DateTimeField(auto_now_add= True)
    owner= models.CharField(max_length= 64, blank= True, null= True)

    class Meta:
        db_table= "atp_uploads_case_template"


class TestSuite(models.Model):
    '''用例集模型'''
    id= models.AutoField(primary_key= True)
    suite_desc= models.CharField("用例集合描述", max_length= 128, blank= True, null= True)
    type= models.IntegerField("用例集合类型",blank= True, null= True,choices= ((1,"UI"),(0,"API")))
    status= models.IntegerField(blank= True, null= True, help_text="0:表示有效，1:表示无效，用于软删除",default= 0)
    creator= models.CharField(max_length= 20, blank= True, null= True)
    create_time= models.DateTimeField("创建时间", auto_now= True)  # 创建时间-自动获取当前时间

    class Meta:
        db_table= "atp_test_suite"
        verbose_name= "用例集合表"
        verbose_name_plural= "用例集合表"


class TestSuiteExecuteRecord(models.Model):
    '''集合执行记录模型'''
    id= models.AutoField(primary_key= True)
    belong_test_execute= models.CharField(max_length= 128, blank= True, null= True)  # 关联的记录id
    test_suite= models.ForeignKey(TestSuite, on_delete= models.CASCADE, verbose_name= "测试集合")
    status= models.IntegerField(verbose_name= "执行状态", blank= True, null= True, default= 0)
    test_result= models.CharField(max_length= 50, blank= True, null= True) # 集合执行成功/失败
    creator= models.CharField(max_length=50, blank= True, null= True)
    create_time= models.DateTimeField("创建时间", auto_now= True)   # 创建时间-自动获取当前时间

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table= "atp_test_suite_execute_record"
        verbose_name= "集合执行结果记录表"
        verbose_name_plural= "集合执行结果记录表"


class TestSuiteTestCaseExecuteRecord(models.Model):
    '''集合执行记录-用例执行记录模型'''
    id= models.AutoField(primary_key=True)
    belong_test_suite_exe= models.CharField(max_length=128, blank= True, null= True)  # 关联的记录id
    belong_test_case= models.ForeignKey(TestCase, on_delete= models.CASCADE, verbose_name= "所属用例")
    status= models.IntegerField(blank= True, null= True, help_text="0：表示未执行，1：表示已执行")
    exception_info= models.CharField(max_length= 2048, blank= True, null= True)
    request_data= models.CharField("请求数据", max_length= 1024, blank= True, null= True)
    response_data= models.CharField("响应数据", max_length= 1024, blank= True, null= True)
    execute_result= models.CharField("执行结果", max_length= 1024, blank= True, null= True)  # 成功/失败
    extract_var= models.CharField("提取变量", max_length= 1024, blank= True, null= True)  # 响应成功后提取变量
    execute_total_time= models.CharField("执行总计耗时", max_length= 300, blank= True, null= True)
    execute_start_time= models.CharField("执行开始时间", max_length= 300, blank= True, null= True)
    execute_end_time= models.CharField("执行结束时间", max_length= 300, blank= True, null= True)
    created_time= models.DateTimeField("创建时间", auto_now_add= True)
    updated_time= models.DateTimeField("更新时间", auto_now= True, null= True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table= "atp_test_suite_test_case_execute_record"
        verbose_name= "集合执行里的用例记录表"
        verbose_name_plural= "集合执行里的用例记录表"


class AddCaseIntoSuite(models.Model):
    '''向用例集添加用例模型'''
    id= models.AutoField(primary_key= True)
    test_suite= models.ForeignKey(TestSuite, on_delete= models.CASCADE, verbose_name= "用例集合")
    test_case= models.ForeignKey(TestCase, on_delete= models.CASCADE, verbose_name= "测试用例")
    status= models.IntegerField(verbose_name="是否有效", blank= True, null= True, default= 0,
                                help_text= '0：有效，1：无效')
    create_time= models.DateTimeField("创建时间", auto_now=True)  # 创建时间-自动获取当前时间

    class Meta:
        db_table= "atp_add_case_into_suite"
        verbose_name= "用例集中添加用例表"
        verbose_name_plural= "用例集中添加用例表"


class Server(models.Model):
    '''用来存测试环境/开发环境的服务器信息'''
    id= models.AutoField(primary_key= True)
    env= models.CharField("环境", max_length= 50, blank= True, null= True, default= "")
    ip= models.CharField("IP地址", max_length= 50, blank= True, null= True, default= "")
    port= models.CharField("端口号", max_length= 50, blank= True, null= True, default= "")
    is_https= models.IntegerField(verbose_name="请求方式为Https", blank= True, null= True, default= 0,
                                    help_text= '0：否，1：是')
    remark= models.CharField("备注", max_length= 256, blank= True, null= True)
    create_time= models.DateTimeField("创建时间", auto_now_add= True)
    update_time= models.DateTimeField("更新时间", auto_now= True, blank= True, null= True)

    def __str__(self):
        return self.env

    class Meta:
        db_table= "atp_server"
        verbose_name= "环境配置表"
        verbose_name_plural= "环境配置表"


class EmailAddress(models.Model):
    '''用来存测试环境/开发环境的测试报告收件人信息'''
    id= models.AutoField(primary_key= True)
    address= models.CharField("收件人", max_length= 256, blank= True, null= True,help_text= "多个收件人使用英文;来分隔")
    create_time= models.DateTimeField("创建时间", auto_now_add= True)

    def __str__(self):
        return self.address

    class Meta:
        db_table= "atp_email_address"
        verbose_name= "报告收件人表"
        verbose_name_plural= "报告收件人表"


class JobExecuted(models.Model):
    id= models.AutoField(primary_key= True)
    job_id= models.CharField("任务名称",max_length= 128, blank= True, null= True)
    status= models.IntegerField("任务状态",default= 0,blank= True, null= True,
                                help_text="0为未开始，1为已完成，2为删除，3为暂停")
    run_time= models.DateTimeField("执行时间", auto_now_add= True)
    user= models.CharField("负责人",max_length= 64, blank= True, null= True)

    class Meta:
        db_table= "atp_job_executed"
        verbose_name= "定时任务表"
        verbose_name_plural= "定时任务表"