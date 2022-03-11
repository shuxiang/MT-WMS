#coding=utf8

import os
import os.path
import settings
from huey import RedisHuey, SqliteHuey

# init huey for crontab; not celery; Redis(host=u'localhost', port=6379, db=0, password=None)
if settings.FLASK_SETTINGS.get('REDIS_URL', None):
    hueyapp = RedisHuey(host=settings.FLASK_SETTINGS.get('REDIS_URL'), port=settings.FLASK_SETTINGS.get('REDIS_PORT'), db=3)
else:
    hueyapp = SqliteHuey(filename=os.path.join(os.path.join(settings.INSTANCE_PATH, 'log'), 'huey.db'))

