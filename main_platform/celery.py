import os
from celery import Celery



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AutoTestPlatform.settings')
# 修改为项目的settings
ex_cases_app= Celery('main_platform')
# 修改为项目名称
ex_cases_app.config_from_object('django.conf:settings', namespace='CELERY')
ex_cases_app.conf.update(
    broker_heartbeat= None,
    worker_max_tasks_per_child= 20)
# 配置celery broker_heartbeat是redis断开后重连
# worker_max_tasks_per_child是防止celery内存泄露 定期销毁work


ex_cases_app_sea= Celery('selenium_apps')
# 修改为项目名称
ex_cases_app_sea.config_from_object('django.conf:settings', namespace='CELERY_SEA')
ex_cases_app_sea.conf.update(
    broker_heartbeat= None,
    worker_max_tasks_per_child= 20)