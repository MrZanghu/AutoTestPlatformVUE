import os,re
import time
import traceback
import json,zipfile
import requests,logging
from json import JSONDecodeError
from selenium_apps import viewsParams as svp
from main_platform import viewsParams as vp
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# 解决verify= False报错
# 在Run中选择运行，防止pycharm使用单元测试框架运行脚本，导致数据错误



logger= logging.getLogger("main_platform")


def preprocess_request_data(request_data,global_key,related_case_id,output):
    '''
    对于有调用全局变量的用例，进行数据预处理
    :param request_data:
    :return: 返回需要调用的参数
    '''
    try:
        related_cid= "current_id_%s" % str(related_case_id)
        global_var= json.loads(os.environ[global_key])[related_cid]
        requestData= request_data
        for var_name in re.findall(r"\$\{(\w+)\}", request_data):
            requestData= re.sub(r"\$\{%s\}" % var_name, str(global_var[var_name]), requestData)
            # 进行请求参数替换
        if output== 0:
            return (vp.Y_INPUT_NO_OUTPUT, requestData, "ok") # 有入参，无出参
        else:
            return (vp.Y_INPUT_Y_OUTPUT, requestData, "ok") # 有入参，有出参
        # raise ZeroDivisionError # 测试其他Exception使用
    except Exception as e:
        logger.warning("请求数据预处理发生异常，error：{}".format(traceback.format_exc(limit= 3)))
        return 0, request_data, traceback.format_exc()


def request_process(url, request_method, request_data):
    '''
    封装get、post、put请求方法，返回响应数据
    :param url: 测试地址
    :param request_method:请求方法
    :param request_data:请求数据
    :return:
    '''
    logger.info("-------- 开始调用接口 --------")

    if request_method== "get":
        try:
            rd= json.loads(request_data)    # json.loads将str转为dict，如果可以转换则使用params

            if url[:4]== "https":
                headers= {"Content-Type": "application/json"}
                result= requests.get(url= url,data= str(rd),headers= headers,verify= False)
            else:
                result= requests.get(url, params= rd)

            logger.info("接口地址:%s" % result.url)
            logger.info("请求数据:%s" % request_data)
            # raise ZeroDivisionError # 测试其他Exception使用
        except JSONDecodeError:
            rd= request_data

            if url[:4]== "https":
                headers= {"Content-Type": "application/json"}
                result= requests.get(url + str(rd),headers= headers,verify= False)
            else:
                result= requests.get(url + str(rd))

            logger.info("接口地址:%s" % result.url)
            logger.info("请求数据:%s" % request_data)
        except Exception as e:
            # 除了JSONDecodeError之外的报错
            logger.warning("get方法请求发生异常:请求的url是:%s，请求的内容是:%s，"
                        "发生的异常信息如下:%s" % (url, request_data, e))
            result= "get方法请求发生异常:请求的url是:%s,请求的内容是:%s," \
                    "发生的异常信息如下:%s" % (url, request_data, e)
        return result

    elif request_method== "post":
        try:
            rd= json.loads(request_data)    # json.loads将str转为dict

            if url[:4]== "https":
                headers= {"Content-Type": "application/json"}
                result= requests.post(url= url,data= rd,headers= headers,verify= False)
            else:
                result= requests.post(url, data= rd)
                
            logger.info("接口地址:%s" % result.url)
            logger.info("请求数据:%s" % request_data)
            # raise ZeroDivisionError # 测试其他Exception使用
        except JSONDecodeError:
            logger.warning("post方法请求发生异常:请求的url是:%s，请求的内容是:%s,"
                        "发生的异常信息如下:%s" % (url, request_data, "请求参数不是dict"))
            result= "post方法请求发生异常:请求的url是:%s,请求的内容是:%s," \
                    "发生的异常信息如下:%s" % (url, request_data, "请求参数不是dict")
        except Exception as e:
            # 除了JSONDecodeError之外的报错
            logger.warning("post方法请求发生异常:请求的url是:%s，请求的内容是:%s，"
                        "发生的异常信息如下:%s" % (url, request_data, e))
            result= "post方法请求发生异常:请求的url是:%s,请求的内容是:%s," \
                    "发生的异常信息如下:%s" % (url, request_data, e)
        return result

    elif request_method== "put":
        try:
            rd= json.loads(request_data)    # json.loads将str转为dict
            
            if url[:4]== "https":
                headers= {"Content-Type": "application/json"}
                result= requests.put(url= url, data= rd, headers= headers, verify= False)
            else:
                result= requests.put(url, data= rd)
                
            logger.info("接口地址:%s" % result.url)
            logger.info("请求数据:%s" % request_data)
            # raise ZeroDivisionError # 测试其他Exception使用
        except JSONDecodeError:
            logger.warning("put方法请求发生异常:请求的url是:%s，请求的内容是:%s，"
                        "发生的异常信息如下:%s" % (url, request_data, "请求参数不是dict"))
            result= "put方法请求发生异常:请求的url是:%s,请求的内容是:%s," \
                    "发生的异常信息如下:%s" % (url, request_data, "请求参数不是dict")
        except Exception as e:
            # 除了JSONDecodeError之外的报错
            logger.warning("put方法请求发生异常:请求的url是:%s，请求的内容是:%s，"
                        "发生的异常信息如下:%s" % (url, request_data, e))
            result= "put方法请求发生异常:请求的url是:%s,请求的内容是:%s," \
                    "发生的异常信息如下:%s" % (url, request_data, e)
        return result


def get_var_from_response(global_key, response_data, extract_var,current_id):
    '''
    从相应数据中，根据变量提取公式，提取全局变量，用于其他接口用例使用
    :param global_key:
    :param response_data:接口返回值
    :param extract_var:全局变量公式
    :return:
    '''
    logger.info("变量公式:%s" % extract_var)
    try:
        extract_var_list= extract_var.split(";") # 处理多个提取参数
        new_dict= json.loads(os.environ[global_key])

        for evl in extract_var_list:
            var_name= evl.split("||")[0]
            logger.info("变量名称:%s" % var_name)
            regx_exp= evl.split("||")[1]
            logger.info("提取正则:%s" % regx_exp)

            if re.search(regx_exp, response_data):
                global_vars= json.loads(os.environ[global_key])[current_id] # 获取全局变量中的当前case信息
                var_value= re.search(regx_exp, response_data).group(1) # 返回括号匹配第一个成功的
                global_vars[var_name]= var_value
                new_dict[current_id]= global_vars
                os.environ[global_key]= json.dumps(new_dict)
                # {"current_id_14": {"code": "200", "ip": "192.168.31.134"}, "current_id_15": {"method": "get"}}
            else:
                raise Exception
        logger.info("现全局变量:{}".format(os.environ[global_key]))
        return new_dict[current_id]
    except Exception as e:
        logger.warning("无法提取参数，请求公式为{}".format(extract_var))
        return None


def zip_file(src_dir:str,name:str,file_list:list):
    '''
    处理集合报告文件压缩
    :param src_dir: 路径地址
    :param name: zip报告文件名称
    :param file_list: 报告具体名称
    :return:
    '''
    src_dir_all= os.getcwd()+src_dir
    zip_name= src_dir_all+name+".zip"

    z= zipfile.ZipFile(zip_name,'w',zipfile.ZIP_DEFLATED)
    removefile= [] #需要删除的压缩前文件

    if len(file_list)== 0:
        for root, dirs, files in os.walk(src_dir_all):
            fpath= root.replace(src_dir_all, '')
            fpath= fpath and fpath + os.sep or ''  # 为了去除压缩后有绝对路径
            for filename in files:
                if os.path.splitext(filename)[-1].lower()== ".png":
                    # 如果文件格式为png
                    z.write(os.path.join(root, filename), fpath + filename)
                    removefile.append(os.path.join(root, filename))
                else:
                    pass
        z.close()
    else:
        for root, dirs, files in os.walk(src_dir_all):
            fpath= root.replace(src_dir_all, '')
            fpath= fpath and fpath + os.sep or ''  # 为了去除压缩后有绝对路径
            for filename in files:
                if filename[6:25] in file_list:
                    # filename[6:25]就是报告的时间，如2023_08_02_14:45:00
                    if filename[4:6]== "报告" and (os.path.splitext(filename)[-1].lower()== ".zip"):
                        # 目的是为了不要删除UI测试的截图zip
                        pass
                    else:
                        z.write(os.path.join(root, filename), fpath + filename)
                        removefile.append(os.path.join(root, filename))
                else:
                    pass
        z.close()

    for file in removefile:
        try:
            os.remove(file)
        except:
            pass


def translate_selenium(driver,option:str,element= None):
    '''
    处理selenium的对应步骤，Chrome需要关闭输入框自动填充
    :param driver:webdriver本体，或者前端定位元素
    :param option:前端传入的操作步骤
    :param element: 配合鼠标操作，代表前端定位元素
    :return:查询的方法或为空
    :return:
    '''
    if option in svp.actions:
        if option== "open(打开)":
            return driver.get
        elif option== "wait(等待)":
            return driver.implicitly_wait
        elif option== "back(后退)":
            return driver.back()
        elif option== "forward(前进)":
            return driver.forward()
        elif option== "refresh(刷新)":
            return driver.refresh()
        elif option== "screenshot(截图)":
            times= str(int(time.time()))
            # 使用时间戳来存文件
            return driver.save_screenshot(os.path.join("report","UI_%s.png"%times))
        elif option== "gettitle(获取窗口标题)":
            return driver.title
        elif option== "maximizewindow(窗口最大化)":
            return driver.maximize_window()
        elif option== "closewindow(关闭当前页签)":
            return driver.close()

    elif option in svp.methods:
        if option== "selectbytext(下拉框的内容)":
            return Select(driver).select_by_visible_text
        elif option== "selectbyindex(下拉框的下标)":
            return Select(driver).select_by_index

        elif option== "alertgettext(获取弹出框内容)":
            return driver.switch_to.alert.text
        elif option== "alertaccept(点击确认)":
            return driver.switch_to.alert.accept()
        elif option== "alertdismiss(点击取消)":
            return driver.switch_to.alert.textdismiss()

        elif option== "gettext(获取文本属性)":
            return driver.text
        elif option== "gettagname(获取标签类型)":
            return driver.tag_name
        elif option== "getattribute(获取指定属性值)":
            return driver.get_attribute

        elif option== "click(点击)":
            return driver.click()
        elif option== "sendkeys(输入)":
            return driver.send_keys
        elif option== "clear(清除输入框)":
            return driver.clear()
        elif option== "isselect(是否已经被选择)":
            return driver.is_selected()

        elif option== "mouselkclick(模拟鼠标左键单击)":
            return ActionChains(driver).click(element).perform()
        elif option== "mouserkclick(模拟鼠标右键单击)":
            return ActionChains(driver).context_click(element).perform()
        elif option== "mousedclick(模拟鼠标双击)":
            return ActionChains(driver).double_click(element).perform()
        elif option== "mouseclickhold(模拟鼠标左键长按)":
            return ActionChains(driver).click_and_hold(element).perform()
        elif option== "mouserelease(模拟鼠标长按后释放)":
            return ActionChains(driver).release(element).perform()
    else:
        return None