import pymysql
from main_platform.celery import ex_cases_app as celery_app



__all__= ('celery_app',)
pymysql.version_info = (1, 4, 13, "final", 0)   # 指定版本
pymysql.install_as_MySQLdb()    # 伪装成mysql