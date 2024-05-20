"""
Django settings for GPAXF project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import logging.config
import os.path
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-8bz*a8scy7l8l&6-&^t759tov*k$@vq=a$tuq#_qo3eg9qgxj^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main_platform',
    'locust_apps',
    'send_mails',
    'selenium_apps',
    'django_celery_results', # 用于异步任务
    'django_apscheduler',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'AutoTestPlatform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR,"templates"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'AutoTestPlatform.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': BASE_DIR / 'db.sqlite3',
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'AutoTestPlatform',
        'USER': 'root',
        'PASSWORD': '12345678',
        'HOST': '127.0.0.1',
        'PORT': '3306'
    }
}

CACHES = {
    'default': {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "TIMEOUT":60*60*2,
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

STATIC_URL = '/static/'

STATICFILES_DIRS= [os.path.join(BASE_DIR,"static"),]
# 静态地址路径

MEDIA_ROOT= os.path.join(BASE_DIR,"static/uploads")
# 上传文件路径

MEDIA_KEY_PREFIX= "/static/uploads"
# 上传文件的前缀地址

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

FONT_PATH = os.path.join(BASE_DIR,"static/font/Avenir.ttc")
# 设置验证码字体文件

LOGIN_URL = 'main_platform:login'
# login_required 使用，跳回到登录页面

CELERY_BROKER_URL = 'redis://127.0.0.1:6379/2'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_BACKEND = 'django-db' # 存储位置为db
CELERY_TASK_SERIALIZER = 'json' # 异步celery的设置
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERYD_HIJACK_ROOT_LOGGER = False # 禁用CELERYD自己的日志，输出到指定位置

LOGGING_DIR= os.path.join(BASE_DIR,"logs") # 日志配置
if not os.path.exists(LOGGING_DIR):
    os.makedirs(LOGGING_DIR)

LOGGING= {
    'version': 1,
    'disable_existing_loggers':False,
    'formatters':{
        'simple':{
            'format':'%(asctime)s \"%(module)s:%(funcName)s:%(lineno)d\" [%(levelname)s]- %(message)s'
        }
    },
    'handlers':{
        'console':{
            'level':'ERROR',
            'class':'logging.StreamHandler',
        },
        'celery':{
            'level':'DEBUG',
            'formatter':'simple',
            'class':'logging.handlers.RotatingFileHandler',
            'filename':os.path.join(LOGGING_DIR,'ATP.log'),
            'maxBytes':1024 * 1024 * 10,
            'backupCount':3,
        },
    },
    'loggers':{
        'main_platform':{
            'handlers':['console','celery'],
            'propagate':True,
            'level':'DEBUG',
        },
        'selenium_apps':{
            'handlers':['console','celery'],
            'propagate':True,
            'level':'DEBUG',
        },
    },
}
logging.config.dictConfig(LOGGING)

EMAIL_HOST = 'smtp.qq.com'  # 发送方的smtp服务器地址
EMAIL_PORT = 465    # smtp服务端口
EMAIL_HOST_USER = '1058753233@qq.com'       # 发送方邮箱地址
EMAIL_HOST_PASSWORD = 'espzoxhtcichbejj'   # 获得的授权码
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = None
EMAIL_TIMEOUT = None
DEFAULT_FROM_EMAIL = '1058753233@qq.com'  # 和 EMAIL_HOST_USER  相同