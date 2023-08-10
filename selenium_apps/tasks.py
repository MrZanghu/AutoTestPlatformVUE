import re
import time
import logging
import unittest
from . import models
from selenium import webdriver
from selenium.webdriver.common.by import By
from utils.process_data import translate_selenium,zip_file
from BeautifulReport import BeautifulReport
from main_platform.celery import ex_cases_app_sea
from main_platform.tasks import ParametrizedTestCase
from main_platform.models import EmailAddress
from send_mails.views import email_for_interface



logger= logging.getLogger("selenium_apps")


class BeginTest(ParametrizedTestCase):
    '''使用unittest进行UI测试'''
    def setUp(self):
        '''用例准备操作'''
        logger.info(" " * 50)
        self.id= list(self.case.keys())[0] # 获取字典中的用例id
        self.test_case= models.TestCaseForSEA.objects.get(id= self.id)
        self.doc= self.test_case.case_name
        logger.info("######### 开始执行UI用例【{}】##########".format(self.test_case))

        self.test_case_steps= list(self.case.values())[0] # 获取字典中的步骤
        self.check_list= [] # 存储所有预期结果对比

        self.option= webdriver.ChromeOptions()
        self.option.add_argument("headless")
        self.driver= webdriver.Chrome(chrome_options= self.option)  # 不启动浏览器
        # self.driver= webdriver.Chrome() # 启动浏览器

        for index,i in enumerate(self.test_case_steps):
            self.check= True # 单步预期结果对比，默认通过
            logger.info("定位路径:{}".format(i[0]))
            logger.info("方法|操作:{}".format(i[1]))
            logger.info("传入参数:{}".format(i[2]))
            logger.info("步骤动作:{}".format(i[3]))
            logger.info("预期结果:{}".format(i[4]))

            print("UI操作第【{}】步骤".format(index+1))
            print("定位路径:{}".format(i[0])
                  + " " * 4 + "方法|操作:{}".format(i[1])
                  + " " * 4 + "传入参数:{}".format(i[2])
                  + " " * 4 + "步骤动作:{}".format(i[3])
                  + " " * 4 + "预期结果:{}".format(i[4]))

            try:
                if i[3]!= None:   # actions优先处理
                    if i[0]!= None: # 网址优先处理
                        self.res= translate_selenium(self.driver,i[3])(i[0])
                    else:
                        if i[2]!= None: # 参数优先处理
                            self.res= translate_selenium(self.driver,i[3])(int(i[2]))
                        else:
                            self.res= translate_selenium(self.driver,i[3])
                else:
                    if i[1]!= None and i[0]!= None: # methods后处理
                        finds,obj= i[0].split("==") # i[0]分割定位方式和对象
                        if finds== "id":
                            finds= By.ID
                        elif finds== "name":
                            finds= By.NAME
                        elif finds== "class_name":
                            finds= By.CLASS_NAME
                        elif finds== "tag_name":
                            finds= By.TAG_NAME
                        elif finds== "link_text":
                            finds= By.LINK_TEXT
                        elif finds== "plink_text":
                            finds= By.PARTIAL_LINK_TEXT
                        elif finds== "xpath":
                            finds= By.XPATH
                        elif finds== "css_selector":
                            finds= By.CSS_SELECTOR

                        self.object= self.driver.find_element(finds,obj)

                        if i[2]!= None: # 参数优先处理
                            self.res= translate_selenium(self.object,i[1])(i[2])
                        else:
                            if i[1][:5]== "mouse":
                                # 暂通过字符mouse来单独处理鼠标操作
                                self.res= translate_selenium(self.driver, i[1], self.object)
                            else:
                                self.res= translate_selenium(self.object, i[1])
                    else:
                        self.res= translate_selenium(self.driver,i[1])  # 处理弹窗

                if i[4] != None and i[4] != self.res: # 进行预期结果对比
                    self.check= False
                    logger.info("断言关键字【{}】匹配失败，实际结果是：【{}】".format(i[4],self.res))
                    print("断言关键字【{}】匹配失败，实际结果是：【{}】".format(i[4],self.res))
            except Exception as e:
                self.check= False
                logger.warning("UI测试执行错误："+str(e))
                print("UI测试执行错误："+str(e))# debug使用
            finally:
                time.sleep(2) # 防止未知错误，均强制2s
                self.check_list.append(self.check)
                print()

    def testMethod(self):
        '''用例断言，判断用例是否通过'''
        if False in self.check_list:
            self.assertEqual(False,True)
            logger.info("用例【%s】执行失败！" % self.test_case)
        else:
            self.assertEqual(True, True)
            logger.info("用例【%s】执行成功！" % self.test_case)

    def tearDown(self):
        '''用例结束操作'''
        self.driver.quit()
        time.sleep(3)


@ex_cases_app_sea.task
def case_task(test_case_list:list, server_address, user,id):
    '''
    进行测试用例的执行操作
    :param test_case_list: 用例id列表
    :param server_address: 服务器信息
    :param user: 执行用户
    :return:
    '''
    list_open= []
    suite= unittest.TestSuite()
    is_screenshot= False # 是否有截图
    for tcl in test_case_list:
        detail= models.TestCaseForSEA.objects.get(id= tcl)
        steps= models.TestCaseSteps.objects.filter(testcaseid_id= detail.id)\
            .values_list("LocationPath","Method","Parameter","Action","Expected")
        # values_list可以将queryset转换成tuple，需要指定字段

        for i in steps:
            if  "screenshot(截图)" in i:
                is_screenshot= True

        steps= [list(i) for i in steps]
        list_open.append({str(tcl):steps})

    for i in list_open:
        suite.addTest(ParametrizedTestCase.parametrize(BeginTest, case= i,
                                                       server_address= server_address,
                                                       type="case"))

    result= BeautifulReport(suite)
    time_= str(time.strftime("%Y_%m_%d_%H:%M:%S", time.localtime(time.time())))
    result.report(filename= "UI测试报告" + time_,
                  description= "自动化测试平台报告",
                  report_dir= "report",
                  theme= "theme_memories")

    if is_screenshot== True:
        zip_file("/report/", "UI测试截图"+time_,[])
        time.sleep(3)
    # 需要再次调用压缩图片和报告





    zip_file("/report/", "UI测试报告"+time_,[time_])

    # 集合和接口的公用，处理并发问题

    # address= EmailAddress.objects.get(id=1).address.split(";")
    # email_for_interface(address,"界面测试报告"+time_+".html")