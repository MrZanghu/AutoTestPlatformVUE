import os
import json
import time,xlrd
import datetime
import unittest
import traceback,logging
from . import models
from . import viewsParams as vp
from BeautifulReport import BeautifulReport
from django.contrib.auth.models import User
from main_platform.celery import ex_cases_app
from send_mails.views import email_for_interface
from utils.process_data import request_process,get_var_from_response, preprocess_request_data,zip_file



logger= logging.getLogger("main_platform")


class ParametrizedTestCase(unittest.TestCase):
    '''
    1.可实现传入测试用例list自动创建用例集，
    2.不用手动根据用例进行，即 def testcase():pass,
    3.用例csv必须有标志位用于判断，如pass状态设置为0，
    4.继承时，必须以test开头，如testX()
    '''
    def __init__(self, methodName= "runTest",case= None,server_address= None,
                 global_key= None,type= "case"):
        super(ParametrizedTestCase, self).__init__(methodName)
        self.case= case
        self.server_address= server_address
        self.global_key= global_key
        self.type= type

    @staticmethod
    def parametrize(testcase_klass, case= None,server_address= None,global_key= None,type= None):
        testloader= unittest.TestLoader()
        testnames= testloader.getTestCaseNames(testcase_klass)
        suite= unittest.TestSuite()
        for name in testnames:
            suite.addTest(testcase_klass(name, case= case,server_address= server_address,
                                         global_key= global_key,type= type))
        return suite


class BeginTest(ParametrizedTestCase):
    '''使用unittest进行接口测试'''
    skip1= False  # 用于判断请求出错误，默认无错误

    def setUp(self):
        '''用例准备操作，请求接口'''
        BeginTest.skip1= False
        logger.info(" "*50)
        self.test_case= models.TestCase.objects.filter(id= int(self.case.id))[0]
        self.doc= self.test_case.case_name

        logger.info("######### 开始执行用例【{}】##########".format(self.test_case))
        self.result_flag= False  # 用于判断是否请求成功，默认失败
        self.current_id= None
        self.request_data= self.test_case.request_data
        self.extract_var= self.test_case.extract_var
        if self.extract_var== "None":
            self.extract_var= None
        self.assert_key= self.test_case.assert_key
        if self.assert_key== "None":
            self.assert_key= None
        self.related_case_id= self.test_case.related_case_id
        if self.related_case_id== "None":
            self.related_case_id= None
        self.interface_name= self.test_case.uri
        self.belong_project= self.test_case.belong_project
        self.belong_module= self.test_case.belong_module
        self.request_method= self.test_case.request_method
        self.url= "{}{}".format(self.server_address, self.interface_name)
        logger.info("所属项目:{}".format(self.belong_project))
        print("所属项目:{}".format(self.belong_project))
        logger.info("所属模块:{}".format(self.belong_module))
        print("所属模块:{}".format(self.belong_module))
        logger.info("接口名称:{}".format(self.interface_name))
        print("接口名称:{}".format(self.interface_name))
        logger.info("请求方法:{}".format(self.request_method))
        print("请求方法:{}".format(self.request_method))
        logger.info("接口地址:{}".format(self.url))
        print("接口地址:{}".format(self.url))
        logger.info("请求数据:{}".format(self.request_data))
        print("请求数据:{}".format(self.request_data))
        logger.info("断言数据:{}".format(self.assert_key))
        print("断言数据:{}".format(self.assert_key))
        logger.info("提取参数:{}".format(self.extract_var))
        print("提取参数:{}".format(self.extract_var))

        global_var= json.loads(os.environ[self.global_key])
        # 请求参数预处理工作

        if self.extract_var!= None: # 判断是否出参
            self.current_id= "current_id_%s" % str(self.case.id)
            global_var[self.current_id]= {} # {"current_id_23": {"msg": "test","code": "200"}}
            os.environ[self.global_key]= json.dumps(global_var)
            if self.related_case_id!= None:  # 判断是否入参
                self.code,self.request_data,self.error_msg= preprocess_request_data(
                    str(self.request_data),
                    self.global_key,
                    self.related_case_id,
                    1)
                # 有入参，有出参
            else:
                self.code= vp.NO_INPUT_Y_OUTPUT  # 无入参，有出参
        else:
            if self.related_case_id!= None: # 判断是否入参
                self.code, self.request_data, self.error_msg= preprocess_request_data(
                    str(self.request_data),
                    self.global_key,
                    self.related_case_id,
                    0)
                # 有入参，无出参
            else:
                self.code= vp.NO_INPUT_NO_OUTPUT # 无入参，无出参

        if self.type== "case":
            # 加入了用例or集合的判断
            self.execute_record= models.TestCaseExecuteResult.objects.create(
                belong_test_case= self.test_case)
            self.execute_record.belong_test_execute= "test"
        elif self.type== "suite":
            self.execute_record= models.TestSuiteTestCaseExecuteRecord.objects.create(
                belong_test_case= self.test_case)
            self.execute_record.belong_test_suite_exe= "test"

        self.execute_record.status= 1
        self.execute_start_time= time.time() # 执行开始时间，时间戳
        self.execute_record.execute_start_time= \
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.execute_start_time))
        self.execute_record.request_data= self.request_data

        if self.code== 0:
            self.result_flag= False
            BeginTest.skip1= True
            self.execute_record.execute_result= "失败"
            self.execute_record.exception_info= self.error_msg
            self.execute_record.response_data= None
        else:
            try:
                self.res_data= request_process(self.url, self.request_method, self.request_data) # 请求数据
                self.execute_record.response_data= self.res_data.json()
                self.execute_record.execute_result= "成功"
                logger.info("响应数据:{}".format(json.dumps(self.res_data.json(), ensure_ascii= False)))
                print("响应数据:{}".format(json.dumps(self.res_data.json(), ensure_ascii= False)))
                self.result_flag= True
            except Exception as e:
                self.execute_record.response_data= None
                self.execute_record.exception_info= self.res_data
                self.execute_record.execute_result= "失败"
                logger.warning("接口请求异常，error:{}".format(traceback.format_exc(limit=3)))  # 只向上找3层级
                print("接口请求异常，error:{}".format(traceback.format_exc(limit=3)))  # 只向上找3层级
                self.result_flag= False
                BeginTest.skip1= True

    def testMethod(self):
        '''用例断言，判断用例是否通过'''
        if BeginTest.skip1== True:
            self.assertEqual(True,False)
        else:
            if self.assert_key!= None:
                self.assert_key_list= self.assert_key.split(";")
                self.assert_flag= True

                for key_word in self.assert_key_list:
                    if not (key_word in json.dumps(self.res_data.json(), ensure_ascii= False)):
                        logger.warning("断言关键字【{}】匹配失败".format(key_word))
                        print("断言关键字【{}】匹配失败".format(key_word))
                        self.assert_flag= False
                        self.execute_record.execute_result= "失败"
                        break
                    else:
                        logger.info("断言关键字【{}】匹配成功".format(key_word))
                if self.assert_flag== False:
                    self.result_flag= False
                    self.assertEqual(True,False)
                else:
                    self.result_flag= True
                    self.assertEqual(True,True)
            else:
                self.assertEqual(True,True)

    def tearDown(self):
        '''用例结束操作，进行添加全局变量'''
        try:
            if self.result_flag:
                if self.code in [vp.NO_INPUT_Y_OUTPUT, vp.Y_INPUT_Y_OUTPUT]:
                    self.get_extract_var= get_var_from_response(self.global_key,
                                                                json.dumps(self.res_data.json(),
                                                                           ensure_ascii= False),
                                                                            self.extract_var,
                                                                            self.current_id)
                    self.execute_record.extract_var= self.get_extract_var
                logger.info("用例【%s】执行成功！" % self.test_case)
            else:
                self.execute_record.extract_var= None
                logger.warning("用例【%s】执行失败,请检查错误！" % self.test_case)
        except Exception as e:
            # 提取关键字错误时执行
            self.execute_record.extract_var= None
            logger.warning("用例【%s】执行失败,请检查错误！" % self.test_case)

        self.execute_end_time= time.time()
        self.execute_record.execute_end_time= \
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.execute_end_time))
        self.execute_record.execute_total_time= int((self.execute_end_time - self.execute_start_time) * 1000)
        self.execute_record.save()


@ex_cases_app.task
def case_task(test_case_list:list, server_address, user,id):
    '''
    进行测试用例的执行操作
    :param test_case_list: 用例id列表
    :param server_address: 服务器信息
    :param user: 执行用户
    :return:
    '''
    global_key= "ex_time_" + str(int(time.time() * 100000)) # 系统里唯一，目的为每次执行都独立
    os.environ[global_key]= "{}" # 总全局变量
    list_open= []
    suite= unittest.TestSuite()

    for test_case_id in test_case_list:
        list_open.append(models.TestCase.objects.filter(id= int(test_case_id))[0])

    for i in list_open:
        suite.addTest(ParametrizedTestCase.parametrize(BeginTest, case= i,
                                                       server_address= server_address,
                                                       global_key= global_key,
                                                       type= "case"))
    result= BeautifulReport(suite)
    time_= str(time.strftime("%Y_%m_%d_%H:%M:%S",time.localtime(time.time())))
    result.report(filename= "接口测试报告"+time_,
                  description= "自动化测试平台报告",
                  report_dir= "report",
                  theme=  "theme_memories")

    ate= models.TestExecute() # 保存执行记录
    ate.user= user
    ate.type= 0
    ate.job_id= id
    ate.case_or_suite_ids= ','.join(map(str,test_case_list))
    ate.download_report_path= "report/%s.html"%("接口测试报告"+time_)
    ate.save()

    ter= models.TestCaseExecuteResult.objects.filter(belong_test_execute= "test")
    for i in ter: # 对记录关联用例
        i.belong_test_execute= ate.id
        i.save()

    del os.environ[global_key]  # 执行完成，删除全局变量

    address= models.EmailAddress.objects.get(id= 1).address.split(";")
    email_for_interface(address,"接口测试报告"+time_+".html")


@ex_cases_app.task
def process_xls(up_times,owner,file_names):
    '''
    读取Excel用例，创建项目、模块、用例
    :param up_times:
    :param owner:
    :param file_names:
    :return:
    '''
    time.sleep(30)
    file= models.UpLoadsCaseTemplate.objects.\
        filter(uptimes= up_times,owner= owner).first()
    file_address= "static/uploads/"+str(file.address)

    logger.info("######### 用例已经读取，开始写入数据库 #########")
    module_name= xlrd.open_workbook(filename= file_address).sheet_by_index(0)
    project_name= file_names[:-4]

    try:
        p= models.Project.objects.filter(name= project_name)
        if not p:
            project= models.Project()
            project.name= project_name
            project.proj_owner= owner
            project.test_owner= owner
            project.dev_owner= owner
            project.desc= "导入的项目"
            project.save()
            logger.info("创建项目【{}】成功".format(project_name))
            time.sleep(1) # 创建完成后，先等待1s
        else:
            logger.warning("已存在相同项目,名称为【{}】".format(project_name))

        m= models.Module.objects.filter(name= module_name.name)
        if not m:
            module= models.Module()
            module.name= module_name.name
            module.belong_project= models.Project.objects.filter(name= project_name).first()
            logger.info("创建模块时匹配【{}】成功".format(project_name))
            module.test_owner= owner
            module.desc= "导入的模块"
            module.save()
            logger.info("创建模块【{}】成功".format(module_name.name))
            time.sleep(1)  # 创建完成后，先等待1s
        else:
            logger.warning("已存在相同模块,名称为【{}】".format(module_name.name))

        case_list= [] # 需要导入的测试用例集
        related_id_list= [] # 需要进行关联的测试：[(本id,关联id),(本id,关联id)]
        for i in range(1, module_name.nrows):
            rows= module_name.row_values(i)
            for index in range(0,len(rows)):
                if index== 0 and (rows[index] in ["", None]): # id非空判断
                    logger.info("模板文件第【{}】行,创建列为【{}】,填写内容为空".format(i+1, vp.title_list[index]))
                    raise Exception
                if index== 1:
                    if (rows[index] in ["", None]): # case_name非空判断
                        logger.info("模板文件第【{}】行,创建列为【{}】,填写内容为空".format(i+1, vp.title_list[index]))
                        raise Exception
                    elif (len(rows[index])> 128): # case_name长度判断
                        logger.info("模板文件第【{}】行,用例名称过长,内容为【{}】".format(i+1,rows[index]))
                        raise Exception
                if index== 2 and (rows[index] in ["", None]): # uri非空判断
                    logger.info("模板文件第【{}】行,创建列为【{}】,填写内容为空".format(i+1, vp.title_list[index]))
                    raise Exception
                if index== 3 and ((rows[index]) not in vp.request_method): # request_method列表判断
                    logger.info("模板文件第【{}】行,请求方式错误,内容为【{}】".format(i+1,rows[index]))
                    raise Exception
                if index== 4 and (rows[index] in ["", None]): # request_data非空判断
                    logger.info("模板文件第【{}】行,创建列为【{}】,填写内容为空".format(i+1, vp.title_list[index]))
                    raise Exception
                if index== 5 and (rows[index] in ["", None]):
                    rows[index]= None # 断言为空，则改为None
                if index== 6 and (rows[index] not in ["", None]):
                    related_id_list.append((rows[0],rows[index]))
                    # 使用[(本id,关联id),(本id,关联id)],稍后使用关键字进行遍历匹配，拿到数据库id，进行数据更新关联
                if index== 6 and (rows[index] in ["", None]):
                    rows[index]= None # 关联id为空，则改为None
                if index== 7 and (rows[index] in ["", None]):
                    rows[index]= None # 提取变量为空，则改为None
                if index== 8:
                    if rows[index] in ["", None]: # maintainer非空判断
                        logger.info("模板文件第【{}】行,创建列为【{}】,填写内容为空".format(i+1, vp.title_list[index]))
                        raise Exception
                    elif (len(rows[index])> 18): # maintainer长度判断
                        logger.info("模板文件第【{}】行,用例名称过长,内容为【{}】".format(i+1,rows[index]))
                        break
                        # raise Exception
                if index== 9 and (User.objects.filter(username= rows[index]).exists()== False):
                        logger.info("模板文件第【{}】行,创建列为【{}】,责任人不存在".format(i+1, vp.title_list[index]))
                        raise Exception

            case_list.append(models.TestCase(
                case_name= rows[1],
                belong_project= models.Project.objects.get(name= project_name),
                belong_module= models.Module.objects.get(name= module_name.name),
                uri= rows[2],
                request_method= rows[3],
                request_data= rows[4],
                assert_key= rows[5],
                related_case_id= rows[6],
                extract_var= rows[7],
                maintainer= rows[8],
                status= 0,
                user= User.objects.get(username= rows[9]),
            ))

        models.TestCase.objects.bulk_create(case_list) # 系统批量导入
        flag_time= str(datetime.datetime.now() - datetime.timedelta(seconds= 3))
        # 导入3s内的数据才查询,防止出现重复用例导入,出现关联错误

        if len(related_id_list)!= 0:
            for id in related_id_list:  # 进行数据库id的重新关联
                for i in range(1, module_name.nrows):
                    rows= module_name.row_values(i)
                    if rows[0]== id[0]:
                        original_case= models.TestCase.objects.get(
                            create_time__gte= flag_time,
                            case_name= rows[1],
                            uri= rows[2],
                            request_method= rows[3],
                            request_data= rows[4])
                        for j in range(1, module_name.nrows):
                            rows_inner= module_name.row_values(j)
                            if rows_inner[0]== id[1]:
                                relate_case= models.TestCase.objects.get(
                                    create_time__gte= flag_time,
                                    case_name= rows_inner[1],
                                    uri= rows_inner[2],
                                    request_method= rows_inner[3],
                                    request_data= rows_inner[4]).id
                                original_case.related_case_id= relate_case
                                original_case.save()
    except Exception as e:
        logger.warning("用例导入错误，请检查上传文件正确性")


@ex_cases_app.task
def suite_task(test_suite_list:list,server_address, user,id):
    '''
    进行测试集合的执行操作
    :param test_suite_list: 集合id列表
    :param server_address: 服务器信息
    :param user: 执行用户
    :return:
    '''
    list_dict= {} # {"":[],"":[]}
    zipfiles= [] # 压缩集合报告文件
    suites_time_= str(time.strftime("%Y_%m_%d_%H:%M:%S", time.localtime(time.time())))
    for ts in test_suite_list:
        # 双循环解析集合对应的测试用例
        list_open= []
        test_case_list= models.AddCaseIntoSuite.objects.filter(test_suite_id= int(ts))
        for tc in test_case_list:
            list_open.append(tc.test_case)
        list_dict[ts]= list_open

    for k,v in list_dict.items():
        # 循环集合
        global_key= "ex_time_" + str(int(time.time() * 100000))  # 系统里唯一，目的为每次执行都独立
        os.environ[global_key]= "{}"  # 总全局变量
        suite= unittest.TestSuite()
        for i in v:
            suite.addTest(ParametrizedTestCase.parametrize(BeginTest, case= i,
                                                           server_address= server_address,
                                                           global_key= global_key,
                                                           type= "suite"))
        result= BeautifulReport(suite)

        time_= str(time.strftime("%Y_%m_%d_%H:%M:%S", time.localtime(time.time())))
        result.report(filename= "接口测试报告" + time_,
                      description= "自动化测试平台报告",
                      report_dir= "report",
                      theme= "theme_memories")
        zipfiles.append(time_)

        del os.environ[global_key]  # 执行完成，删除全局变量

        tser= models.TestSuiteExecuteRecord()  # 保存集合记录
        suite_id= models.TestSuite.objects.filter(id= int(k)).first()
        tser.belong_test_execute= "test"
        tser.test_suite= suite_id
        tser.status= 1
        tser.test_result= "成功"
        tser.creator= user
        tser.save()

        tstcer= models.TestSuiteTestCaseExecuteRecord.objects.filter(belong_test_suite_exe= "test")
        for ts1 in tstcer: # 集合下用例有失败，则集合失败
            if ts1.execute_result== "失败":
                tser.test_result= "失败"
                tser.save()
                break

        for ts2 in tstcer:
            ts2.belong_test_suite_exe= tser.id
            ts2.save()

        time.sleep(30) # 防止报告命名冲突

    zip_file("/report/","接口测试报告"+suites_time_,zipfiles)

    ate= models.TestExecute()  # 保存执行记录
    ate.user= user
    ate.type= 1
    ate.job_id= id
    ate.case_or_suite_ids= ','.join(map(str, test_suite_list))
    ate.download_report_path= "report/%s.zip" % ("接口测试报告" + suites_time_)
    ate.save()

    ter= models.TestSuiteExecuteRecord.objects.filter(belong_test_execute= "test")
    for i in ter:  # 对记录关联用例
        i.belong_test_execute= ate.id
        i.save()

    address= models.EmailAddress.objects.get(id= 1).address.split(";")
    email_for_interface(address,"接口测试报告"+suites_time_+".zip")
