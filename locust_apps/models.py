from django.db import models



class TestCase(models.Model):
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