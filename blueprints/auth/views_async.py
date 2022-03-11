# coding: utf-8

import os
import time
import os.path
from importlib import import_module
import traceback
from datetime import datetime
import json
from sqlalchemy import or_, and_, func
from flask import Blueprint, request, session, url_for, g, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from utils.flask_tools import json_response
from utils.functions import gen_query
from utils.upload import save_request_file
import settings

from extensions.database import db
from extensions.permissions import admin_perm, manager_perm, normal_perm

from models.asyncmodel import Async


# MUST ADD THIS CODE: import and write to func_map
# import 
from blueprints.auth.tasks.import_base import import_location
from blueprints.auth.tasks.import_base import import_area
from blueprints.auth.tasks.import_base import import_workarea
from blueprints.auth.tasks.import_base import import_warehouse
from blueprints.auth.tasks.import_base import import_employee

from blueprints.auth.tasks.import_stockin import import_stockin
from blueprints.auth.tasks.import_stockout import import_stockout

from blueprints.auth.tasks.import_inv import import_invcount
from blueprints.auth.tasks.import_inv import import_invadjust
from blueprints.auth.tasks.import_inv import import_invmove

# export
from blueprints.auth.tasks.export_base import export_goodmap, export_good
from blueprints.auth.tasks.export_inv import export_inv, export_invcount, export_invmove
from blueprints.auth.tasks.export_invwarn import export_invwarn
from blueprints.auth.tasks.export_stockin import export_stockin
from blueprints.auth.tasks.export_stockout import export_stockout
from blueprints.auth.tasks.export_finance import export_finance

import settings


bp_async = Blueprint("async", __name__)

# MUST ADD THIS CODE
FUNC_MAP = {
    # //import
    'blueprints.auth.tasks.import_base:import_location':  ('import', u'库位导入', 'location', u'/static/xlsx/库位.xlsx', 3),
    #'blueprints.auth.tasks.import_base:import_area':      ('import', u'库区导入','area', u'/static/xlsx/库区.xlsx', 0),
    #'blueprints.auth.tasks.import_base:import_workarea':  ('import', u'工作区导入','workarea', u'/static/xlsx/工作区.xlsx', 0),
    #'blueprints.auth.tasks.import_base:import_warehouse': ('import', u'仓库导入','warehouse', u'/static/xlsx/仓库.xlsx', 0),

    'blueprints.auth.tasks.import_base:import_inv':      ('import', u'库存导入','inv', u'/static/xlsx/库存.xlsx', 4),
    'blueprints.auth.tasks.import_base:import_good':     ('import', u'货品导入','good', u'/static/xlsx/货品.xlsx', 2),
    'blueprints.auth.tasks.import_base:import_goodmap':     ('import', u'配料清单导入','goodmap', u'/static/xlsx/货品配料.xlsx', 3),
    'blueprints.auth.tasks.import_base:import_category': ('import', u'货类导入','category', u'/static/xlsx/货类.xlsx', 1),

    'blueprints.auth.tasks.import_base:import_partner': ('import', u'供合作伙伴导入','partner', u'/static/xlsx/合作伙伴.xlsx', 0),
    'blueprints.auth.tasks.import_base:import_employee': ('import', u'员工导入','employee', u'/static/xlsx/员工.xlsx', 3),

    'blueprints.auth.tasks.import_stockin:import_stockin':   ('import', u'入库单导入','stockin', u'/static/xlsx/入库单.xlsx', 5),
    'blueprints.auth.tasks.import_stockout:import_stockout': ('import', u'出库单导入','stockout', u'/static/xlsx/出库单.xlsx', 6),

    'blueprints.auth.tasks.import_inv:import_invcount': ('import', u'盘点单导入','invcount', u'/static/xlsx/盘点单.xlsx', 8),
    #'blueprints.auth.tasks.import_inv:import_invadjust': ('import', u'调整单导入','invadjust', u'/static/xlsx/调整单.xlsx', 8),
    'blueprints.auth.tasks.import_inv:import_invmove':  ('import', u'移库单导入','invmove', u'/static/xlsx/移库单.xlsx', 8),

    # //export
    'blueprints.auth.tasks.export_base:export_good':  ('export', u'货品导出','export_good', u'', 14),
    'blueprints.auth.tasks.export_base:export_partner':  ('export', u'合作伙伴导出','export_partner', u'', 14),
    'blueprints.auth.tasks.export_base:export_goodmap':  ('export', u'配料清单导出','export_goodmap', u'', 14),
    'blueprints.auth.tasks.export_inv:export_inv':  ('export', u'库存导出','export_inv', u'', 10),
    'blueprints.auth.tasks.export_invwarn:export_invwarn':  ('export', u'库存告警导出','export_invwarn', u'', 10),
    'blueprints.auth.tasks.export_inv:export_invcount':  ('export', u'盘点单导出','export_invcount', u'', 11),
    'blueprints.auth.tasks.export_inv:export_invmove':  ('export', u'移库单导出','export_invmove', u'', 11),
    'blueprints.auth.tasks.export_stockin:export_stockin':  ('export', u'入库单导出','export_stockin', u'', 12),
    'blueprints.auth.tasks.export_stockout:export_stockout':  ('export', u'出库单导出','export_stockout', u'', 13),

    'blueprints.auth.tasks.export_finance:export_finance':  ('export', u'财务费用导出','export_finance', u'', 20),
}
CRM_FUNC_MAP = {
}
# 异步任务列表
@bp_async.route('', methods=('GET',))
@normal_perm.require()
def async_api():
    """
    获取异步任务列表
    get req:
        pass
    """
    # q = {filters:[{}], order_by, single, limit, offset, group_by}
    query = Async.query.t_query
    pagin = gen_query(request.args.get('q', None), query, Async, db=db, per_page=settings.PER_PAGE, get_objects=True)

    objects = []
    for o in pagin.items:
        obj = o.as_dict
        obj['link'] = o.link
        obj['exc_info'] = o.exc_info
        objects.append(obj)

    res =  {
          "num_results": pagin.total,
          "total_pages": pagin.pages,
          "page": pagin.page,
          "per_page": pagin.per_page,
          "objects": objects
        }
    return json_response(res, indent=4)

# 导入表单
@bp_async.route("/table_import", methods=["GET", 'POST'])
@bp_async.route("/table_import/sync", methods=["GET", 'POST'])
@bp_async.route("/table_import/crm", methods=["GET", 'POST'])
@normal_perm.require()
def table_import_api():
    """
    post req:
    {
        name, xtype, func, func_name, remark
        file // 上传的文件对象
    }
    """
    if request.method == 'GET':
        if 'crm' in request.path:
            data = [{'key': k, 'func': k, 'xtype': v[0], 'name': v[1], 'code':v[2], 'link':v[3], 'func_name': v[1], 'sort': v[-1]} for k,v in CRM_FUNC_MAP.items()]
        else:
            data = [{'key': k, 'func': k, 'xtype': v[0], 'name': v[1], 'code':v[2], 'link':v[3], 'func_name': v[1], 'sort': v[-1]} for k,v in FUNC_MAP.items()]
        data = sorted(data, key=lambda x: x['sort'])
        return json_response(data)

    elif request.method == 'POST':
        req = request.json or request.form.to_dict()

        name = req['name']
        xtype = req['xtype']
        func = req['func']
        func_name = req['func_name']
        code = req.get('code', '')
        
        fname, file_path = save_request_file(settings.UPLOAD_DIR, company_id=g.user.company_id)

        task = Async()
        ret = None
        task_id = None

        task.name = fname if fname else name        
        task.state = 'doing'
        task.xtype = xtype
        task.code = code
        task.func = func
        task.func_name = func_name
        task.company_code = g.company_code
        task.warehouse_code = g.warehouse_code
        task.owner_code = g.owner_code
        task.remark = req.get('remark', fname)

        try:
            task.link = file_path
            db.session.add(task)
            db.session.commit()
            task_id = task.id
            
            # start task
            if settings.IS_WINDOWS:
                function = import_module(func.split(':')[0]).__dict__[func.split(':')[1]+'_sync']
                ret = function(*[g.company_code, g.warehouse_code, g.owner_code, request.args, task.id, g.user.code, g.user.name])
            else:
                function = import_module(func.split(':')[0]).__dict__[func.split(':')[1]]
                ret = function.apply_async([g.company_code, g.warehouse_code, g.owner_code, request.args, task.id, g.user.code, g.user.name], expires=10*60, queue="import") # 10 minute timeout
            #ret = function.schedule([g.company_code, g.warehouse_code, g.owner_code, request.args, task.id, g.user.code, g.user.name], delay=2)
            task.async_id = str(ret.id)
            if not name:
                task.name = '%s_%s'%(func_name, str(datetime.now())[:19])

            db.session.commit()
        except Exception as e:
            err = traceback.format_exc()
            print(err)
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': err})

        #task = Async.query.get(task_id)
        data = task.as_dict
        data['exc_info'] = task.exc_info
        data['link'] = task.link
        # if 'sync' in request.path:
        #     data['result'] = ret.get()
        return json_response({'status': 'success', 'msg':'ok', 'data': data})


    return json_response({'status': 'success', 'msg': 'ok'})


# 导出表单
@bp_async.route("/table_export", methods=["GET", 'POST'])
@normal_perm.require()
def table_export_api():
    """
    post req:
    {
        name, xtype, func, func_name, remark
    }
    """
    if request.method == 'GET':
        return json_response(FUNC_MAP)

    elif request.method == 'POST':
        req = request.json or request.form.to_dict()
        name = req['name']
        xtype = req['xtype']
        code = req.get('code', '')
        func = req['func']
        func_name = req['func_name']


        task = Async()
        task_id = None

        task.name = name
        task.state = 'doing'
        task.xtype = xtype
        task.code = code
        task.func = func
        task.func_name = func_name
        task.company_code= g.company_code
        task.warehouse_code = g.warehouse_code
        task.owner_code = g.owner_code
        task.remark = req.get('remark', '')

        try:
            db.session.add(task)
            db.session.commit()
            task_id = task.id

            # start task
            if settings.IS_WINDOWS:
                function = import_module(func.split(':')[0]).__dict__[func.split(':')[1]+'_sync']
                ret = function(*[g.company_code, g.warehouse_code, g.owner_code, request.args, task.id, g.user.code, g.user.name])
            else:
                function = import_module(func.split(':')[0]).__dict__[func.split(':')[1]]
                ret = function.apply_async([g.company_code, g.warehouse_code, g.owner_code, request.args, task.id, g.user.code, g.user.name], expires=10*60, queue='export') # 10 minute timeout
            #ret = function.schedule([g.company_code, g.warehouse_code, g.owner_code, request.args, task.id, g.user.code, g.user.name], delay=2) # 10 minute timeout
            task.async_id = str(ret.id)
            if not name:
                task.name = '%s_%s'%(func_name, str(datetime.now())[:19])

            db.session.commit()
        except Exception as e:
            err = traceback.format_exc()
            print(err)
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': err})

        task = Async.query.get(task_id)
        data = task.as_dict
        data['exc_info'] = task.exc_info
        data['link'] = task.link
        return json_response({'status': 'success', 'msg':'ok', 'data': data})


    return json_response({'status': 'success', 'msg': 'ok'})


# only celery
# 查看异步任务的状态
@bp_async.route("/status/<task_id>", methods=["GET",])
@normal_perm.require()
def status_task_api(task_id):
    task = Async.query.t_query.filter_by(id=task_id).first()
    func = task.func.split(':')
    function = import_module(func[0]).__dict__[func[1]]

    _task = func.AsyncResult(task.async_id)
    if _task.state == 'PENDING':
        pass
    elif _task.state != 'FAILURE':
        task.state = 'done'
    else:
        task.state = 'fail'
        task.exc_info = task.exc_info or _task.info

    db.session.commit()

    data = task.as_dict
    data['exc_info'] = task.exc_info
    data['link'] = task.link
    return json_response({'status': 'success', 'msg':'ok', 'data': data})

# 下载异步任务的文件
@bp_async.route("/download/<task_id>", methods=["GET",])
@normal_perm.require()
def download_task_api(task_id):
    task = Async.query.t_query.filter(or_(Async.id==task_id, Async.oss_link==task_id)).first()

    def get_file(task):
        task.get_file()
        ext = os.path.splitext(task.name)[1] or '.xlsx'
        return send_file(task.link,
                         attachment_filename=task.name + ext,
                         as_attachment=True,
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    if task.link and task.state == 'done':
        return get_file(task)
    elif task.state == 'doing':
        timeout = 0
        while timeout <= 30:
            time.sleep(1)
            task = Async.query.t_query.filter_by(id=task_id).first()
            if task.state == 'done':
                return get_file(task)
            if task.state == 'fail':
                return json_response({'status': 'fail', 'msg': u'下载失败, 请到 `导入导出` 查看失败原因!'})
            timeout += 1

        return json_response({'status': 'fail', 'msg': u'超时了, 请到 `导入导出` 去下载文件'})
    else:
        return json_response({'status': 'fail', 'msg': u'下载失败, 请到 `导入导出` 查看失败原因!'})



# 上传文件, 通用
@bp_async.route('/upload/file', methods=('GET', 'POST', 'PUT', 'DELETE'))
@bp_async.route('/upload/file/<task_id>', methods=('GET', 'POST', 'PUT', 'DELETE'))
@normal_perm.require()
def upload_file_api(task_id=None):
    if request.method == 'POST' or request.method == 'PUT':
        from utils.upload import save_request_file_to_oss
        msg = 'no file'
        try:
            company_id = g.user.company_id
            path, name, oname = save_request_file_to_oss(settings.UPLOAD_DIR, save2oss=True, 
                filedir='', bucketname='wms-export', request_file_name='file', company_id=str(company_id))
            
            task = Async()
            task._link = path
            task.name = u'上传文件-%s'%oname
            task.code = name
            task.oss_link = name
            task.state = 'done'
            task.xtype = 'import'
            task.func = '/upload/file'
            task.func_name = '/upload/file'
            task.company_code= g.company_code
            task.warehouse_code = g.warehouse_code
            task.owner_code = g.owner_code
            task.remark = oname

            db.session.add(task)
            db.session.commit()

            return json_response({'status': 'success', 'msg': 'ok', 'filename': name, 'task_id':task.id, 'osslink':name, 'origin_name':oname})
        except:
            msg = traceback.format_exc()
        return json_response({'status': 'fail', 'msg': msg})

    if request.method == 'DELETE':
        task = Async.query.t_query.filter(or_(Async.id==task_id, Async.oss_link==task_id)).first()
        task.unlink_file()
        db.session.delete(task)
        db.session.commit()

        return json_response({'status': 'success', 'msg': 'ok'})



