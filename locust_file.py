import configparser,os,django,logging,json
from locust import HttpUser, task, between,TaskSet
os.environ['DJANGO_SETTINGS_MODULE']= 'AutoTestPlatform.settings'
# 防止locust找不到django的models
django.setup()
import locust_apps.models as loc_models



logger= logging.getLogger("main_platform")


class LocustCase(TaskSet):
    def on_start(self) -> None:
        self.config= configparser.ConfigParser()
        self.config.read("locust_config.ini")
        self.MY_CASE_ID= self.config.get("Parameter", "MY_CASE_ID").replace("'", '"')
        self.MY_SUITE_ID= self.config.get("Parameter", "MY_SUITE_ID").replace("'", '"')

    @task
    def testMethod(self):
        for id in eval(self.MY_CASE_ID):# eval转成list
            self.case= loc_models.TestCase.objects.filter(id= id).first()
            if self.case.request_method== "get":
                try:
                    self.rd= json.loads(self.case.request_data)# 解决两种get的传参方式
                    with self.client.get(self.case.uri,params= self.rd,
                                         catch_response=True) as self.res:
                        # catch_response字段可对res进行断言，修改返回状态
                        if self.case.assert_key != None:
                            self.assert_key_list= self.case.assert_key.split(";")
                            for key_word in self.assert_key_list:
                                # 判断每一个关键字是否可以断言成功
                                if not (key_word in json.dumps(self.res.json(), ensure_ascii=False)):
                                    self.res.failure("用例id【{}】,断言关键字【{}】匹配失败".format(
                                        self.case.id,key_word))
                                    break
                except:
                    with self.client.get(self.case.uri + self.case.request_data,
                                         catch_response=True) as self.res:
                        if self.case.assert_key != None:
                            self.assert_key_list= self.case.assert_key.split(";")
                            for key_word in self.assert_key_list:
                                # 判断每一个关键字是否可以断言成功
                                if not (key_word in json.dumps(self.res.json(), ensure_ascii= False)):
                                    self.res.failure("用例id【{}】,断言关键字【{}】匹配失败".format(
                                        self.case.id,key_word))
                                    break

            elif self.case.request_method== "post":
                with self.client.post(self.case.uri, data= json.loads(self.case.request_data),
                                     catch_response= True) as self.res:
                    # catch_response字段可对res进行断言，修改返回状态
                    if self.case.assert_key != None:
                        self.assert_key_list= self.case.assert_key.split(";")
                        for key_word in self.assert_key_list:
                            # 判断每一个关键字是否可以断言成功
                            if not (key_word in json.dumps(self.res.json(), ensure_ascii= False)):
                                self.res.failure("用例id【{}】,断言关键字【{}】匹配失败".format(
                                        self.case.id,key_word))
                                break
            else:
                pass


class WebsiteUser(HttpUser):
    wait_time= between(0, 2)
    tasks= LocustCase,