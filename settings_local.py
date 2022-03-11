#coding=utf8
import os
import platform

print('----------------load local config file-----------------')

# output traceback
PROPAGATE_EXCEPTIONS = True

SQLALCHEMY_ECHO = os.environ.get('SQLALCHEMY_ECHO', 'FALSE') == 'TRUE'
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'mysql+pymysql://wms:wms870129@127.0.0.1:3306/wmsbase?charset=utf8')

SQLALCHEMY_BINDS = {
    'auth': os.environ.get('SQLALCHEMY_DATABASE_URI_bind_auth', 'mysql+pymysql://wms:wms870129@127.0.0.1:3306/mfos_auth?charset=utf8'),
}

DEBUG = os.environ.get('DEBUG', 'TRUE') == 'TRUE'
HOST = '0.0.0.0'
PORT = 5002

PER_PAGE = int(os.environ.get('PER_PAGE', 20))
STATIC_DIR = os.environ.get('STATIC_DIR', 'static')
TPL_DIR = os.environ.get('TPL_DIR', 'templates')

SECRET_KEY = os.environ.get('SECRET_KEY', '\xce\xa1\xc3\xa5\xfa\xec\xd4\xe6\xc9\xcd\xfa')
SESSION_COOKIE_NAME = os.environ.get('SESSION_COOKIE_NAME', 'mtwms') # 同一ip不同端口，名字相同的cookie在浏览器里会互相影响

TEST_USER_ID = int(os.environ.get('TEST_USER_ID', '2'))

CORS_HOST = os.environ.get('CORS_HOST', '*')
#CORS_HOST = os.environ.get('CORS_HOST', 'http://127.0.0.1:9030')#PDA

CORS = os.environ.get('CORS', 'TRUE') == 'TRUE'


# ----- 系统配置 ------

# 启用保存到 数据库
UPLOAD_TO_DB = False
# 保存图片到OSS
UPLOAD_IMG_TO_OSS = os.environ.get('UPLOAD_IMG_TO_OSS', False) == 'TRUE'

# 是否使用手机验证码
USE_TELCODE = False

# 货品基准价格计算选取的采购单期限, 默认最近半年
GOOD_PRICE_CRON_DAYS = os.environ.get('GOOD_PRICE_CRON_DAYS', 30*6)


# redis
#REDIS_URL = '127.0.0.1'
#REDIS_PORT = 6379

# 序列号加上日期
SEQ_MONTH = os.environ.get('SEQ_MONTH', 'TRUE') == 'TRUE'
SEQ_OWNER = os.environ.get('SEQ_OWNER', 'TRUE') == 'TRUE'

# OSS aliyun images prefix
OSS_URL_PREFIX = os.environ.get('OSS_URL_PREFIX', '')


# celery
# CELERYD_MAX_TASKS_PER_CHILD = 10
CELERY_BROKER_URL = 'sqla+' + SQLALCHEMY_DATABASE_URI #'mysql://root:123456@127.0.0.1:3306/wms?charset=utf8'
CELERY_RESULT_BACKEND = 'db+' + SQLALCHEMY_DATABASE_URI #'mysql://root:123456@127.0.0.1:3306/wms?charset=utf8'
BROKER_URL = CELERY_BROKER_URL
RESULT_BACKEND = CELERY_RESULT_BACKEND


# 是否windows 系统
IS_WINDOWS = platform.system() == 'Windows'

