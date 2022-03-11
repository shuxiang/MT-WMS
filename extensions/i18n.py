#coding=utf8

import yaml
import os.path
import time
from flask import session

# 需要两个配置 I18N_PATH & I18N_LOCALE
# I18N_PATH = 翻译需要的YAML文件
# I18N_LOCALE = 默认的语言

INSTANCE_PATH = os.path.abspath(os.path.dirname(os.path.realpath('__file__')))
_CONFIG_MAP = {}

def get_cache_config(path, ctype=None):
    global _CONFIG_MAP
    if not path in _CONFIG_MAP:
        _CONFIG_MAP[path] = [None, time.time()]
    lconfig = _CONFIG_MAP[path]

    mtime = os.path.getmtime(path)
    if mtime > lconfig[1] or not lconfig[0]:
        lconfig[1] = mtime
        with open(path, 'r') as f:
            if ctype == 'yaml':
                lconfig[0] = yaml.load(f.read(), Loader=yaml.FullLoader)
            else:
                lconfig[0] = f.read()

    return lconfig[0]


# i18n format doc: https://www.runoob.com/python/att-string-format.html
class I18N(object):
    def __init__(self):
        self.app = None
        self.reload = False
        self.path = INSTANCE_PATH+'/extensions/i18n.yaml'
        self.locale = 'cn'
        self._data = {}

    def init(self, path=None, locale=None, reload=False):
        self.path = path or self.path
        self.locale = locale or self.locale
        self.reload = reload or self.reload

        with open(self.path, 'r') as f:
            self._data = yaml.load(f.read(), Loader=yaml.FullLoader)

    def init_app(self, app):
        self.app = app
        self.init(app.config.get('I18N_PATH', None), app.config.get('I18N_LOCALE', 'cn'), app.debug)

    @property
    def data(self):
        if self.reload:
            return get_cache_config(self.path, ctype='yaml')
        return self._data
    

    def __call__(self, locale):
        self.locale = locale
        return self

    def t(self, name, **kw):
        return self.data[name][self.locale].format(**kw)

def gtext(name, **kw):
    return i18n(session.get('lang', i18n.locale)).t(name, **kw)

i18n = I18N()

if __name__ == '__main__':
    # print(i18n.data)
    i18n.init()
    print(i18n.t('sample'))
    print(i18n('en').t('sample'))
    print(i18n('cn').t('sample'))
    print(i18n('oo').t('sample', u=u'你', c=0.123456789, d=1))
    print(i18n('en').t(u'样例'))