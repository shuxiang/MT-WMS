#!/usr/bin/env python
# -- coding: utf-8--

from celery import Celery

# CELERY_BROKER_URL = 'redis://localhost:6379/9'#flask-celery=2.4.3
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/9'

# app.config['CELERY_BROKER_URL'] = CELERY_BROKER_URL
# app.config['CELERY_RESULT_BACKEND'] = CELERY_RESULT_BACKEND


class CeleryBase(Celery):

    def init_app(self, app):
        try:# for workers
            self.conf.update(app.config)
        except:pass
        TaskBase = self.Task
        class ContextTask(TaskBase):
            abstract = True
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return TaskBase.__call__(self, *args, **kwargs)
        self.Task = ContextTask

celeryapp = CeleryBase()
# celery.conf.add_defaults(app.config)
