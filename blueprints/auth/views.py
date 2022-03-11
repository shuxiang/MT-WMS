# coding=utf8
import json
import os
import os.path
import traceback
from pprint import pprint
from random import randint

from flask import Blueprint, request, session, current_app, \
    url_for, render_template, make_response, redirect, jsonify, g
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_principal import Principal, Identity, AnonymousIdentity, identity_changed

from extensions.database import db
from extensions.permissions import admin_perm, manager_perm, normal_perm

from models.auth import User, Partner, Config, Big, Company
from models.inv import Category, Good
from models.warehouse import Warehouse, Area, Workarea, Location

from blueprints.auth.action import AuthAction

from utils.flask_tools import json_response, is_xhr
from utils.functions import gen_query, clear_empty, json2mdict, json2mdict_pop, DictNone
from utils import base
from utils.sms import send_register_msg_253

import settings

bp_auth = Blueprint("auth", __name__)




# TODO
# 手机注册，方便联系到客户
# 注册时，生成默认仓库等一系列默认基础信息，默认基础配置
@bp_auth.route('/register', methods=('GET', 'POST',))
def register_api():
    use_telcode = settings.USE_TELCODE

    if request.method == 'POST':
        ret = {'status':'fail', 'msg':''}

        form = request.json or request.form

        code = form.get('user_code', '')
        vcode = form.get('user_vcode', '')
        passwd = form.get('user_password', '')
        name = form.get('user_name', '')
        company = form.get('company', '')
        email = form.get('email', '')
        address = form.get('address', '')
        remark = form.get('remark', '')

        ok, msg = False, ''
        ret = {'status': 'success', 'msg': ''}
        if settings.USE_TELCODE and vcode != session['regcode']:
            ok = False
            msg = u'验证码不对'
        elif code and passwd and company and name:
            data = DictNone()
            data.user = DictNone()
            data.user.code = code or name
            data.user.name = name or code
            data.user.password = passwd
            data.user.email = email
            data.user.tel = code
            data.user.contact = name
            data.user.email = email
            data.user.address = address
            data.user.remark = remark

            data.name = company
            data.code = company
            data.contact = name
            data.tel = code
            data.email = email
            data.address = address
            data.remark = remark
            # pprint(data)
            ok, comp, manager, msg = AuthAction.register(data)
        else:
            ok = False
            msg = u'wrong data'

        if ok:
            db.session.commit()
        else:
            db.session.rollback()
            ret = {'status': 'fail', 'msg': msg}

        if request.is_json or is_xhr(request):
            return json_response(ret)
        return render_template('register.html', error=ret, use_telcode=use_telcode)

    return render_template('register.html', use_telcode=use_telcode)


@bp_auth.route('/register/code', methods=('GET', 'POST',))
def register_code_api():
    if request.method == 'GET':
        tel = request.args.get('tel', '') or request.form.get('tel', '') or request.json.get('tel', '')
        code = '%04d'%randint(1, 9999)
        session['regcode'] = code
        # send to sms API； msg = u'您的验证码是%s。如非本人操作，请忽略本短信'
        ok, msg = send_register_msg_253(tel, code)
        if not ok:
            return json_response({'status': 'fail', 'msg': msg}) 
        return json_response({'status': 'success', 'msg': 'ok', 'code': code})
    else:
        if request.args.get('regcode', '') == session['regcode']:
            return json_response({'status': 'success', 'msg': 'ok'})
        return json_response({'status': 'fail', 'msg': 'fail'})



# 获取公司所有用户列表, 更新，创建
@bp_auth.route('/company', methods=('GET', 'POST', 'PUT', 'DELETE'))
@bp_auth.route('/company/<company_id>', methods=('GET', 'POST', 'PUT', 'DELETE'))
@normal_perm.require()
def company_api(company_id=None):
    """
    get req:
        restless q

    post req:
        {...}

    put req:
        {...}
    """
    if request.method == 'GET':
        query = Company.query
        if g.user.is_agent:
            query = query.filter_by(agent=g.user.code)
        elif g.user.is_admin:
            pass
        else:# 只能查集团内的公司
            if g.user.company.group:
                query = query.filter(Company.group.ilike('%%%s%%'%g.user.company.group))

        res = gen_query(request.args.get('q', None), query, Company, db=db, per_page=settings.PER_PAGE)
        return  json_response(res)

    elif request.method == 'POST':
        ok, comp, manager, msg = AuthAction.register(request.json)
        if ok:
            db.session.commit()
            return json_response({'status': 'success', 'msg': 'ok'})
        else:
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': msg})

    elif request.method == 'PUT':
        Company.query.filter_by(id=company_id).update(json2mdict_pop(Company, clear_empty(request.json)))
        db.session.commit()

        return json_response({'status': 'success', 'msg': 'ok'})


# 设置公司logo
@bp_auth.route('/company/<company_id>/image', methods=('GET', 'POST', 'PUT', 'DELETE'))
@manager_perm.require()
def company_image_api(company_id=None):
    if request.method == 'POST':
        comp = Company.query.get(company_id)
        from utils.upload import save_request_file, save_image

        msg = u'无图片'
        try:
            fname, file_path = save_request_file(settings.UPLOAD_DIR, company_id=company_id)
            # 保存图片
            fmt = os.path.splitext(fname)[1][1:]
            with open(file_path, 'rb') as f:
                blob = f.read()
            if blob:
                path, osslink = save_image(settings.UPLOAD_DIR, blob, fmt, settings.UPLOAD_IMG_TO_OSS, company_id=company_id)
                if settings.UPLOAD_IMG_TO_OSS:
                    iurl = settings.OSS_URL_PREFIX + osslink
                else:
                    iurl = '/static/upload/images/%s/%s'%(company_id, osslink)
                comp.image_url = iurl
                db.session.commit()

                return json_response({'status': 'success', 'msg': 'ok', 'image_url': comp.image_url, 'image_path': comp.image_path})
        except:
            msg = traceback.print_exc()
        return json_response({'status': 'fail', 'msg': msg})

@bp_auth.route('/login', methods=['GET', 'POST'])
def login_api():
    if request.method == 'POST':
        ret = {'status':'fail', 'msg':''}
        form = request.json or request.form
        code = form.get('code', '')
        passwd = form.get('password', '')
        company = form.get('company', '')
        if  code and passwd and company:
            user = AuthAction.auth_user(code, passwd, company)
            if user:    
                login_user(user)
                
                # Tell Flask-Principal the identity changed
                identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
                nginx_host = os.environ.get('NGINX_HOST', '')

                if user.is_client:
                    if request.is_json or is_xhr(request):
                        ret['msg'] = u'登录地址不对, 自助采购请在 %s 登录'% (nginx_host+url_for('index.vue_banksale_index'))
                        resp = json_response(ret)
                    else:
                        resp = redirect(nginx_host+url_for('index.vue_banksale_index'))

                    AuthAction.set_openresty_cookie(user, resp)
                    return resp

                if request.is_json or is_xhr(request):
                    ret['status'] = 'success'
                    ret['Authorization'] = user.apikey
                    ret['warehouse_code'] = g.warehouse_code
                    ret['owner_code'] = g.owner_code
                    resp = json_response(ret)

                else:
                    resp = redirect(nginx_host+url_for('index.vue_index'))

                AuthAction.set_openresty_cookie(user, resp)
                return resp
            else:
                ret['msg'] = u'用户名或者密码或者公司不正确'
        else:
            ret['msg'] = u'请填写完整信息'

        print(dir(request))
        if request.is_json or is_xhr(request):
            return json_response(ret)
        return render_template('mtwms_login.html', error=ret, test=os.environ.get('ENV', '')=='TEST')

    elif getattr(g, 'user', None) is not None and current_app.debug == False:
        nginx_host = os.environ.get('NGINX_HOST', '')
        resp = redirect(nginx_host+url_for('index.vue_index'))
        AuthAction.set_openresty_cookie(g.user, resp)
        return resp

    return render_template('mtwms_login.html', test=os.environ.get('ENV', '')=='TEST')

@bp_auth.route('/login/pda', methods=['GET', 'POST'])
def login_pda_api():
    if request.method == 'POST':
        ret = {'status':'fail', 'msg':''}
        form = request.json or request.form
        code = form.get('code', '')
        passwd = form.get('password', '')
        company = form.get('company', '')
        if  code and passwd and company:
            user = AuthAction.auth_user(code, passwd, company)
            if user:
                login_user(user)
                
                # Tell Flask-Principal the identity changed
                identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
                nginx_host = os.environ.get('NGINX_HOST', '')

                if request.is_json or is_xhr(request):
                    ret['status'] = 'success'
                    ret['Authorization'] = user.apikey
                    ret['warehouse_code'] = g.warehouse_code
                    ret['owner_code'] = g.owner_code
                    resp = json_response(ret)
                else:
                    resp = redirect(nginx_host+url_for('index.vue_pda_index'))
                AuthAction.set_openresty_cookie(user, resp)
                return resp
            else:
                ret['msg'] = u'用户名或者密码或者公司不正确'
        else:
            ret['msg'] = u'请填写完整信息'
        if request.is_json or is_xhr(request):
            return json_response(ret)
        return render_template('login_pda.html', error=ret)

    return render_template('login_pda.html')

@bp_auth.route('/logout', methods=['GET', 'POST'])
@bp_auth.route('/logout/pda', methods=['GET', 'POST'])
@normal_perm.require()
def logout_api():
    # Remove the user information from the session
    logout_user()

    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    # Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())

    if request.is_json or is_xhr(request):
        # ajax请求
        resp = json_response(status='success', msg='success')

    else:
        nginx_host = os.environ.get('NGINX_HOST', '')
        if 'pda' in request.path:
            resp = redirect(nginx_host+'/auth/login/pda')
        else:
            resp = redirect(nginx_host+'/auth/login')

    # 删除 openresty cookie
    resp.delete_cookie('oip')
    return resp


# 获取当前登录用户的信息
@bp_auth.route('/current_user', methods=('GET', 'POST',))
@normal_perm.require()
def current_user_api():
    """
    返回当前用户信息
    get resp:
        {...}
    """
    if request.method == 'GET':
        data = g.user.as_dict
        data['owners'] = data['owners'].split(',') if data['owners'] else []
        data['warehouses'] = data['warehouses'].split(',') if data['warehouses'] else []
        data['vroles'] = data['vroles'].split(',') if data['vroles'] else []
        data['menus'] = data['menus'].split(',') if data['menus'] else []
        data['vmenus'] = {m:True for m in data['menus']}
        data['v_roles'] = {'vr_%s'%m:True for m in data['vroles']}
        data.pop('password')
        data['need_change_pwd'] = g.user.need_change_pwd

        resp = json_response(data)

        AuthAction.set_openresty_cookie(g.user, resp)
        return resp


# POST 设置 仓库与货主, PUT 设置 借贷人
@bp_auth.route('/current_tenant', methods=('GET', 'POST', 'PUT'))
@normal_perm.require()
def current_tenant_api():
    """
    设置仓库与货主
    post resp:
        {owner_code, warehouse_code}
    """
    if request.method == 'POST':
        _owners = [o.as_dict for o in Partner.query.filter_by(company_code=g.company_code, xtype='owner').all()]
        owners  = [o.as_dict for o in g.user.get_owners] if not g.user.is_manager else _owners

        _warehouses = [w.as_dict for w in Warehouse.query.filter_by(company_code=g.company_code).all()]
        warehouses = [o.as_dict for o in g.user.get_warehouses] if not g.user.is_manager else _warehouses

        factories = []


        current_owner = Partner.query.filter_by(company_code=g.company_code, code=g.owner_code).first()
        comp = Company.query.filter_by(code=g.company_code).first()

        if request.json:
            session['_w'] = request.json.get('warehouse_code', g.warehouse_code or 'default')
            session['_o'] = request.json.get('owner_code', g.owner_code or 'default')

        return json_response({
                'tenant': {
                    'Authorization': g.user.apikey,
                    'owner_code': session['_o'] or 'default', 
                    'warehouse_code': session['_w'] or 'default',
                    'warehouse_name': Warehouse.query.filter_by(company_code=g.company_code, code=(session['_w'] or 'default')).first().name
                },
                'owner_conf': current_owner.conf,
                'owners': owners, 
                'warehouses': warehouses,
                'factories': factories,
                'company': comp.as_dict,
                'user': g.user.as_dict,
            })
    

# 获取公司所有用户列表, 更新，创建，删除用户
@bp_auth.route('/user', methods=('GET', 'POST', 'PUT', 'DELETE'))
@bp_auth.route('/user/<user_id>', methods=('GET', 'POST', 'PUT', 'DELETE'))
@normal_perm.require()
def user_api(user_id=None):
    """
    get req:
        restless q

    post req:
        {...}

    put req:
        {...}

    delete req:
        pass
    """
    if request.method == 'GET':
        if g.user.is_admin:
            query = User.query
        else:
            query = User.query.filter(User.company_code==g.company_code, User.state!='delete')
            # 超级管理员才能管理代理商
            query = query.filter(~User.roles.ilike('%%agent%%'))
            # 监控员才能看到其它账户
            if not g.user.is_monitor:
                query =query.filter(User.xtype=='user')
        res = gen_query(request.args.get('q', None), query, User, db=db, per_page=settings.PER_PAGE)
        for o in res['objects']:
            o.pop('password')
            o['owners'] = o['owners'].split(',') if o.get('owners',[]) else []
            o['warehouses'] = o['warehouses'].split(',') if o.get('warehouses',[]) else []
            o['vroles'] = o['vroles'].split(',') if o.get('vroles', []) else []
            o['menus'] = o['menus'].split(',') if o.get('menus', []) else []
        return  json_response(res)

    elif request.method == 'POST':
        data = clear_empty(request.json)
        data['owners'] = ",".join(data.get('owners',[])) if type(data.get('owners',[])) is list else data.get('owners',[])
        data['warehouses'] = ",".join(data.get('warehouses',[])) if type(data.get('warehouses',[])) is list else data.get('warehouses',[])
        data['vroles'] = ','.join(data.get('vroles', [])) if type(data.get('vroles', [])) is list else data.get('vroles',[])
        data['menus'] = ','.join(data.get('menus', [])) if type(data.get('menus', [])) is list else data.get('menus',[])
        ok, user = AuthAction.create_user(is_employee=data.pop('is_employee', False), **json2mdict(User, data))
        if ok:
            db.session.commit()
            return json_response({'status': 'success', 'data': user.to_json(), 'msg':'ok'})
        else:
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': user})

    elif request.method == 'PUT':
        remark = request.json.pop('remark', '')
        data = clear_empty(request.json)
        is_employee = data.pop('is_employee', False)
        data['owners'] = ",".join(data.get('owners',[])) if type(data.get('owners',[])) is list else data.get('owners',[])
        data['warehouses'] = ",".join(data.get('warehouses',[])) if type(data.get('warehouses',[])) is list else data.get('warehouses',[])
        data['vroles'] = ','.join(data.get('vroles', [])) if type(data.get('vroles', [])) is list else data.get('vroles',[])
        data['menus'] = ','.join(data.get('menus', [])) if type(data.get('menus', [])) is list else data.get('menus',[])
        xd = json2mdict_pop(User, data)
        xd['remark'] = remark

        user = User.query.filter_by(company_code=g.company_code, id=user_id).first()
        if g.user.is_admin:
            u = User.query.filter_by(id=user_id).first()
            u.update(xd)
        else:
            u = User.query.filter_by(company_code=g.company_code, id=user_id).first()
            u.update(xd)
        db.session.flush()
        db.session.commit()

        return json_response({'status': 'success', 'msg': 'ok'})

    elif request.method == 'DELETE':
        if g.user.is_admin:
            User.query.filter_by(id=user_id).update({'state': 'delete'})
        else:
            User.query.filter_by(company_code=g.company_code, id=user_id).update({'state': 'delete'})
        db.session.commit()

        return json_response({'status': 'success', 'msg': 'ok'})

# 获取公司所有用户列表, 更新，创建，删除用户
@bp_auth.route('/user/client', methods=('GET', 'POST', 'PUT', 'DELETE'))
@normal_perm.require()
def user_client_api(user_id=None):
    """
    get req:
        restless q
    """
    if request.method == 'GET':
        if g.user.is_admin:
            query = User.query
        else:
            query = User.query.filter(User.company_code==g.company_code, User.state!='delete')
            # 超级管理员才能管理代理商
            query = query.filter(~User.roles.ilike('%%agent%%'))
        query = query.filter(User.xtype=='client')

        res = gen_query(request.args.get('q', None), query, User, db=db, per_page=settings.PER_PAGE)
        for o in res['objects']:
            o.pop('password')
            o['owners'] = o['owners'].split(',') if o.get('owners',[]) else []
            o['warehouses'] = o['warehouses'].split(',') if o.get('warehouses',[]) else []
            o['vroles'] = o['vroles'].split(',') if o.get('vroles', []) else []
            o['menus'] = o['menus'].split(',') if o.get('menus', []) else []
        return  json_response(res)


@bp_auth.route('/user/reset-passwd', methods=('GET', 'POST', 'PUT', 'DELETE'))
@normal_perm.require()
def user_reset_passwd_api(user_id=None):
    user = AuthAction.auth_user(g.user.code, request.json.pop('oldpass'), g.company_code)
    if user is not None:
        user.set_password(request.json.pop('newpass'))
        db.session.commit()
        return json_response({'status': 'success', 'msg': 'ok'})

    return json_response({'status': 'fail', 'msg': u'旧密码不对'})


@bp_auth.route('/translation', methods=('GET', 'POST', 'OPTIONS'))
@normal_perm.require()
def translation_api():
    if request.method == 'GET':

        query = Config.query.filter_by(company_code=g.company_code, owner_code=g.owner_code, code='translation')
        res = gen_query(request.args.get('q', None), query, Config, db=db, per_page=settings.PER_PAGE)

        translation = {}
        for i in res['objects']:
            if i['subcode'] not in translation:
                translation[i['subcode']] = {}
            translation[i['subcode']][i['str1']] = i['str2']

        # 获取base字段
        translation['sub_in_type'] = translation.get('sub_in_type', {})
        translation['sub_in_type'].update(dict(base.in_type))
        translation['sub_out_type'] = translation.get('sub_out_type', {})
        translation['sub_out_type'].update(dict(base.out_type))
        translation['taobao'] = dict(base.taobao)
        translation['kdniao'] = dict(base.kdniao)
        translation['express_type'] = dict(base.express_type)

        return json_response(translation, indent=4)

    return ''


@bp_auth.route('/config', methods=('GET', 'POST', 'PUT'))
@bp_auth.route('/config/<config_id>', methods=('GET', 'POST', 'PUT'))
@normal_perm.require()
def config_api(config_id=None):
    """
    返回配置列表
    get req:

    post req:
        {...}
    """
    if request.method == 'GET':
        # q = {filters:[{}], order_by, single, limit, offset, group_by}
        query = Config.query.filter_by(company_code=g.company_code).order_by(Config.code.asc(), Config.index.asc())
        res = gen_query(request.args.get('q', None), query, Config, db=db, per_page=settings.PER_PAGE)
        for o in res['objects']:
            o['bool1'] = str(int(o['bool1']))
            o['bool2'] = str(int(o['bool2']))
            o['bool3'] = str(int(o['bool3']))
        return json_response(res, indent=4)

    elif request.method == 'PUT':
        data = request.json
        data['bool1'] = int(data['bool1'])
        data['bool2'] = int(data['bool2'])
        data['bool3'] = int(data['bool3'])
        Config.query.filter_by(id=config_id, company_code=g.company_code).update(json2mdict_pop(Config, clear_empty(data)))
        db.session.commit()
        return json_response({'status': 'success', 'msg': 'ok'})

    elif request.method == 'POST':
        data = request.json
        data['bool1'] = int(data.get('bool1',0))
        data['bool2'] = int(data.get('bool2',0))
        data['bool3'] = int(data.get('bool3',0))

        query = Config.query.filter_by(company_code=g.company_code, owner_code=g.owner_code, code=data['code'], subcode=data['subcode'])

        # if query.count() > 0:
        #     return json_response({'status': 'fail', 'msg': u'已经存在相同的配置'})

        if data['code'] == 'translation':
            if not data.get('str1', None):
                data['str1'] = data['str2']
            if query.filter_by(str1=data['str1']).count() > 0:
                return json_response({'status': 'fail', 'msg': u'已经存在相同的配置项'})

        conf = Config(company_code=g.company_code, **clear_empty(data))
        if not conf.owner_code:
            conf.owner_code = g.owner_code
        if not conf.warehouse_code:
            conf.warehouse_code = g.warehouse_code
        db.session.add(conf)
        db.session.commit()
        return json_response({'status': 'success', 'msg': 'ok', 'data': conf.as_dict})

    return ''

@bp_auth.route('/setting', methods=('GET', 'POST', 'PUT'))
@normal_perm.require()
def setting_api():
    if request.method == 'POST':
        data = request.json
        code = data['value']
        multi = data.get('multi', False)
        options_multi = data.get('options_multi', False)
        query = Config.query.filter_by(company_code=g.company_code, owner_code=g.owner_code, code=code)

        # {value: 'overcharge', label:'入库/启用超收', options: [{label: '启用', val:'0', xtype:'bool', name:'bool1'}]}, 
        subcode = data.get('subcode', '')
        if subcode:
            query = query.filter_by(subcode=subcode)
        options = data['options']
        if options:
            if multi:
                query.delete()
                db.session.flush()
                for idx, opt in enumerate(options):
                    if options_multi:
                        conf = Config(company_code=g.company_code, warehouse_code=g.warehouse_code, owner_code=g.owner_code, code=code, subcode=code, label=data['label'], multi=multi, options_multi=True, index=idx)
                        db.session.add(conf)

                        for opt2 in opt:
                            if opt2['xtype'] == 'bool':
                                opt2['val'] = True if opt2['val'] == '1' else False
                            setattr(conf, opt2['name'], opt2['val'])
                    else:
                        conf = Config(company_code=g.company_code, warehouse_code=g.warehouse_code, owner_code=g.owner_code, code=code, subcode=code, label=data['label'], xtype=opt['xtype'], multi=multi)
                        db.session.add(conf)
                        if opt['xtype'] == 'bool':
                            opt['val'] = True if opt['val'] == '1' else False
                        setattr(conf, opt['name'], opt['val'])
            else:
                conf = query.first()
                if not conf:
                    conf = Config(company_code=g.company_code, warehouse_code=g.warehouse_code, owner_code=g.owner_code, code=code, subcode=code, label=data['label'], xtype=options[0]['xtype'], multi=multi)
                    db.session.add(conf)
                for opt in options:
                    if opt['xtype'] == 'bool':
                        opt['val'] = True if opt['val'] == '1' else False
                    setattr(conf, opt['name'], opt['val'])
        
        db.session.commit()
        return json_response({'status': 'success', 'msg': 'ok', 'data': conf.as_dict})

    return ''


# 注销公司
@bp_auth.route('/logoff/<company_code>', methods=('GET', 'POST',))
@admin_perm.require()
def logoff_api(company_code):
    action = AuthAction()
    comp = Company.query.filter_by(code=company_code).first()
    action.logoff(company_code)
    db.session.rollback()

    return json_response({'status': 'success', 'msg': 'ok'})