# -*- coding:utf-8 -*-
import warnings

warnings.filterwarnings("ignore")
import sys
# 兼容函数py3/py2
import builtins
builtins.__dict__['unicode'] = str
builtins.__dict__['xrange'] = range

import os
import os.path
import settings
import traceback
import datetime

from flask import Flask, request, redirect, url_for, g, session, send_from_directory
from flask import make_response, jsonify, send_file, current_app
from flask_login import current_user
from flask_login import LoginManager
from flask_login import login_user, current_user
from flask_principal import Principal, identity_loaded, UserNeed, RoleNeed
from flask_principal import identity_changed, Identity
from flask_migrate import Migrate

from extensions.database import db
from extensions.i18n import i18n
#from extensions.celeryext import celeryapp
#from extensions.cacheext import cache
from extensions.celeryext import celeryapp

from blueprints.auth.tasks.cron_base import hueyapp

from blueprints.auth.views import bp_auth
from blueprints.auth.views_async import bp_async
from blueprints.inv.views import bp_inv
from blueprints.inv.views_replenish import bp_inv_replenish
from blueprints.inv.views_freeze import bp_inv_freeze
from blueprints.stockin.views import bp_stockin
from blueprints.stockout.views import bp_stockout
from blueprints.stockout.views_merge import bp_merge
from blueprints.warehouse.views import bp_warehouse
from blueprints.index.views import bp_index
from blueprints.index.chart_views import bp_chart
from blueprints.finance.views import bp_finance
from blueprints.finance.stat_views import bp_finance_stat
from blueprints.qimen.views import bp_qimen


_BLUEPRINTS = (
    # 认证系统
    (bp_auth, "/auth"),

    # WMS
    # 库存
    (bp_inv, '/inv'),
    # 库存补货
    (bp_inv_replenish, '/inv/replenish'),
    # 库存冻结
    (bp_inv_freeze, '/inv/freeze'),
    # 入库
    (bp_stockin, '/stockin'),
    # 出库
    (bp_stockout, '/stockout'),
    (bp_merge, '/stockout/merge'),
    # 仓库
    (bp_warehouse, '/warehouse'),

    # 财务
    (bp_finance, '/finance'),
    # 财务数据统计
    (bp_finance_stat, '/finance/stat'),
    
    # 异步导入导出与首页
    (bp_async, '/async'),

    # 图表
    (bp_chart, '/chart'),

    # openapi
    (bp_qimen, '/open/qimen'),

    (bp_index, ''), # / /pda /erp /crm
)


def _set_allow_origin(response):
    #response.headers['Access-Control-Allow-Origin'] = '*'
    # 允许跨域 进行身份认证
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '') or settings.CORS_HOST
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    # # axios奇怪的post不带上预设的header;非简单请求：http://www.ruanyifeng.com/blog/2016/04/cors.html
    response.headers['Access-Control-Allow-Headers'] = 'Access-Control-Allow-Origin,Content-Type,Authorization,warehouse_code,owner_code,factory_code,X-Requested-With,*'
    response.headers['Access-Control-Allow-Methods'] = 'POST,GET,OPTIONS,DELETE,PUT,PATCH,*'
    return response


def create_app(config_file=None):
    app = Flask(__name__, static_folder=settings.STATIC_DIR, template_folder=settings.TPL_DIR)
    if config_file:
        app.config.from_pyfile(config_file)
    else:
        for k, v in settings.FLASK_SETTINGS.items():
            app.config[k] = v

    # session
    app.permanent_session_lifetime =  datetime.timedelta(settings.PERMANENT_SESSION_LIFETIME)

    # init i18n
    i18n.init_app(app)

    # init database
    db.init_app(app)
    migrate = Migrate(app, db)

    # init celery
    celeryapp.init_app(app)

    # # init cache, python3 not support
    # cache.init_app(app)

    # init blueprint
    for blueprint, url_prefix in _BLUEPRINTS:
        app.register_blueprint(blueprint, url_prefix=url_prefix)

    # init restless; must init database first
    # restless = APIManager(app, flask_sqlalchemy_db=db)

    # print(app.url_map)
    if app.config.get("CORS"):
        app.after_request(_set_allow_origin)

    # init auth
    Principal(app)
    login_manager = LoginManager(app)
    @login_manager.user_loader
    def load_user(userid):
        # Return an instance of the User model
        return db.Model.registry._class_registry['User'].query.get(userid)

    return app

# INSTANCE_PATH = os.path.dirname(os.path.realpath('__file__'))
# config_file = os.path.join(INSTANCE_PATH, 'settings.py')
application = create_app() #create_app(config_file)


@identity_loaded.connect_via(application)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user
    g.user = current_user

    # Add the UserNeed to the identity
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

        # custom init company & warehouse & owner
        g.company_code = g.user.company_code
        _warehouse_code = request.headers.get('warehouse_code', '') or request.args.get('warehouse_code', '')
        _owner_code = request.headers.get('owner_code', '') or request.args.get('owner_code', '')

        # 仓库设置
        warehouse_code = session.get('_w', '') or _warehouse_code
        warehouses_list = g.user.get_warehouses
        if not warehouse_code:
            if warehouses_list:
                warehouse_code = warehouses_list[0].code
            else:
                warehouse_code = 'default'
        else:
            if warehouse_code not in g.user.warehouses:
                if g.user.is_manager:
                    pass
                else:
                    warehouse_code = warehouses_list[0].code if warehouses_list else 'default'
        g.warehouse_code = warehouse_code
        g.warehouse = db.M('Warehouse').query.filter_by(company_code=g.company_code, code=warehouse_code).first()
        session['_w'] = warehouse_code

        # 货主设置
        owner_code = session.get('_o', '') or _owner_code
        owners_list = g.user.get_owners
        if not owner_code:
            if owners_list:
                owner_code = owners_list[0].code
            else:
                owner_code = 'default'
        else:
            if owner_code not in g.user.owners:
                if g.user.is_manager:
                    pass
                else:
                    owner_code = owners_list[0].code if owners_list else 'default'
        g.owner_code = owner_code
        g.owner = db.M('Partner').query.filter_by(company_code=g.company_code, code=owner_code, xtype='owner').first()
        session['_o'] = owner_code

        # 仓库设置
        session['_f'] = 'default'

        print('tenant=========> owner:%s, warehouse:%s, company:%s, user:%s'%(owner_code, warehouse_code, g.company_code, g.user.code))

    else:
        g.user = None

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    if hasattr(current_user, 'get_perms'):
        for role in current_user.get_perms:
            identity.provides.add(RoleNeed(role))


# ------ response handler --------

app = application

@app.after_request
def after_request(resp):
    # before_response
    if app.debug:
        resp.headers['Cache-Control'] = 'no-cache'
        resp.headers['Pragma'] = 'no-cache'
        resp.headers['Expires'] = '0'

    # # companyid for traefik route, use openresty replace
    # if getattr(g, 'user', None) is not None:
    #     cid = str(g.user.company_id)
    #     resp.set_cookie('cid', cid)
    #     if not app.debug:
    #         resp.headers['cid'] = cid
    db.session.commit()
    return resp

@app.before_request
def before_request():
    if app.debug:
        User = db.M('User')
        test_user_id = settings.FLASK_SETTINGS.get('TEST_USER_ID')
        if test_user_id:
            u = User.query.get(test_user_id)
            login_user(u)
            identity_changed.send(current_app._get_current_object(), identity=Identity(u.id))

    # 通过HTTP HEAD 的 Authorization 来判断是否通过是用户，用来做api认证
    auth = request.headers.get('Authorization', '') or request.args.get('Authorization', '')
    if auth:
        User = db.M('User')
        Company = db.M('Company')
        u = User.query.filter(User._apikey==auth).first()
        if not u:
            u = User.query.filter(User.company_code==Company.code, Company.apikey==auth).first()
        if u:
            login_user(u)
            identity_changed.send(current_app._get_current_object(), identity=Identity(u.id))


@app.errorhandler(500)
def http500(error):
    db.session.rollback()
    db.session.close()
    return jsonify(msg='%s, HTTP 500!'%error), 500

@app.errorhandler(Exception)
def catch_all_except(error):
    traceback.print_exc()
    db.session.rollback()
    db.session.close()
    return jsonify(msg='%s, HTTP 500!'%error), 500

@app.errorhandler(401)
def http401(error):
    return jsonify(msg='%s, You need permission!'%error), 401

@app.errorhandler(403)
def http403(error):
    return jsonify(msg='%s, You need permission!'%error), 403

@app.errorhandler(404)
def http404(error):
    return jsonify(msg='%s, Where are you!'%error), 404

@app.route('/static/upload/<path:path>')
def send_static_upload(path):
    # /static/upload/images/:company_id/xx.jpeg
    return send_from_directory(settings.UPLOAD_DIR, path)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory(settings.STATIC_DIR, path)

@app.route('/website/assets/<path:path>')
def send_static_website_assets(path):
    return send_from_directory(settings.TPL_DIR, os.path.join('website/assets', path))


