from celery.result import AsyncResult
from django.http import HttpResponse
from send_mails.tasks import send_emails
from main_platform import celery_app



def email_for_interface(address,report_id):
    '''
    发送邮件，内部接口
    :param address:
    :param report_id:
    :return:
    '''
    send_result= send_emails.delay(address,report_id)
    return HttpResponse(send_result)


def get_result(request):
    '''
    根据id查询查询结果，暂时不启用
    :param nid:
    :return:
    '''
    nid= request.GET.get("nid")
    print(nid)

    r= AsyncResult(nid,app= celery_app)
    return HttpResponse(r.status)