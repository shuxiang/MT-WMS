#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import os.path
from types import ModuleType, FunctionType

# common
INSTANCE_PATH = os.path.abspath(os.path.dirname(os.path.realpath('__file__')))
DEBUG = True
MODE  = os.environ.get('MODE', '')

# 开发服务器用的 HOST和PORT，用apache部署，此项无用
HOST = '0.0.0.0'
PORT = 5000

# sqlalchemy
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'mysql://root:123456@127.0.0.1:3306/mfos?charset=utf8')

SQLALCHEMY_BINDS = {
    'auth': 'mysql://root:123456@127.0.0.1:3306/mfos_auth?charset=utf8',
}

SQLALCHEMY_ECHO = False
SQLALCHEMY_POOL_RECYCLE = 180#3minutes
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_POOL_TIMEOUT = 10
SQLALCHEMY_TRACK_MODIFICATIONS = False

# session
SECRET_KEY = '\xce\xa2\xce\xa2\xba\xec\xd4\xe6\xc9\xcc\xff'

PERMANENT_SESSION_LIFETIME = 2678400
SESSION_COOKIE_NAME = 'mf'


# login
LOG_FILE = os.path.join(os.path.join(INSTANCE_PATH, 'log'), 'wms.log')

# pagin
PER_PAGE = 20

# 支持跨域要用*
CORS = True
CORS_HOST = '*'
CORS_HOST = os.environ.get('CORS_HOST', 'http://127.0.0.1:5002') # http://47.96.118.117:5050

# upload dir & export dir # 上传文件保存到本地, 不适合分布式部署多机的情况
UPLOAD_DIR = os.path.join(INSTANCE_PATH, 'upload')
# 启用保存到 数据库
UPLOAD_TO_DB = False
# 保存图片到OSS
UPLOAD_IMG_TO_OSS = True

# 推荐库位数
RECOMMEND_LOCATIONS = 10

# templates & static dir
TPL_DIR = 'templates'
STATIC_DIR = 'static'


# ----- 系统配置 ------
# 启用财务
ENABLE_FINANCE = os.environ.get('ENABLE_FINANCE', False)


# 序列号加上日期
SEQ_MONTH = os.environ.get('SEQ_MONTH', 'TRUE') == 'TRUE'
SEQ_OWNER = os.environ.get('SEQ_OWNER', 'FALSE') == 'TRUE'

# 是否使用手机验证码
USE_TELCODE = True


# 是否windows 系统
IS_WINDOWS = False


FLASK_SETTINGS = {}
local_vars = {k:locals().get(k, None) for k in locals().keys()}
for k, v in local_vars.items():
    if type(v) not in (ModuleType, FunctionType, type) and k[:2] != '__' and k not in ('FLASK_SETTINGS', 'k'):
        FLASK_SETTINGS[k] = v

# load local config file
if os.path.exists(os.path.join(INSTANCE_PATH, 'settings_local.py')):
    import settings_local
    from settings_local import *
    for k in dir(settings_local):
        #print(k, getattr(settings_local, k))
        if k[:2] != '__':
            FLASK_SETTINGS[k] = getattr(settings_local, k)

# for k,v in FLASK_SETTINGS.items():
#     print(k, '---->', v)










