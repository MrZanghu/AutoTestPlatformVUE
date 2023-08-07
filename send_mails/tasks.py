import time,os
from django.core.mail import EmailMessage
from main_platform.celery import ex_cases_app
from AutoTestPlatform.settings import EMAIL_HOST_USER



@ex_cases_app.task
def send_emails(recipient:list,report_id:str):
    '''
    异步任务，延迟30s发送
    :param recipient:收件人地址
    :return:
    '''
    time.sleep(10)
    emails= EmailMessage(
        subject= "自动化测试平台报告",
        body= "请下载附件查看测试结果",
        from_email= EMAIL_HOST_USER,    # 发件人
        to= recipient,   # 收件人
        reply_to= [EMAIL_HOST_USER,],  # 默认回信地址
        headers= {"MessageId":"AutoTestPlatformMails"}
    )
    cur= os.path.dirname(os.getcwd())
    filepath= os.path.join(cur,"AutoTestPlatform/report",report_id)
    emails.attach_file(filepath,mimetype= None)
    emails.send()