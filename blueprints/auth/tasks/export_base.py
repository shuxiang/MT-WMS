#coding=utf8

import traceback
from collections import OrderedDict
from datetime import datetime
import uuid
from uuid import uuid4
import os
import os.path
from sqlalchemy import func

from extensions.database import db
from extensions.hueyext import hueyapp
from extensions.celeryext import celeryapp
from models.asyncmodel import Async
from models.warehouse import Warehouse, Area, Workarea, Location
from models.inv import Good, Category, Inv, GoodMap
from models.auth import Partner

from models.inv import InvMove, InvAdjust, InvCount

from utils.upload import get_file_content
from utils.functions import clear_empty, gen_query
from utils.base import DictNone, Dict
from utils.flask_tools import gen_csv, gen_xlsx

import settings

# 
#@hueyapp.task()
@celeryapp.task
def export_goodmap(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    ret = export_goodmap_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=user_code, user_name=user_name)
    db.session.close()
    return ret

def export_goodmap_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    task = Async.query.get(task_id)
    print('handle async task_id ==> ', task_id, task.async_id)

    success = True
    exc_info = ''

    try:
        task.code = 'export_goodmap'
        # q = {filters:[{}], order_by, single, limit, offset, group_by}
        q = args.get('q', '')
        
        query = GoodMap.query

        query = query.filter_by(company_code=company_code, owner_code=owner_code)
        query = gen_query(q, query, GoodMap, db=db, export=True)

        fmt = [
            ("code","货品码"),
            ("barcode","条码"),
            ("name","货品名称"),
            ("subcode","配件货品码"),
            ("subbarcode","配件条码"),
            ("subname","配件货品名称"),
            ("qty","数量"),
        ]
        keys = [i[0] for i in fmt]
        title = [keys, [i[1] for i in fmt]]

        table = [[getattr(o, k, '') for k in keys] for o in query.all()]
        sio = gen_xlsx(title, table, fname='sample', is_titles=True, get_file=True)

        ext = task.name or '.xlsx'
        file_path = os.path.join(settings.UPLOAD_DIR, str(datetime.now().date()) + '_' + str(uuid4())[:8] + ext)
        with open(file_path, 'wb') as f:
            f.write(sio.getvalue())

        print(file_path)
        task.link = file_path
        db.session.flush()
        exc_info = 'save export_goodmap xlsx'
    except:
        exc_info = traceback.format_exc()
        success = False

    if success:
        db.session.commit()
        task.state = 'done'
        task.exc_info = 'SUCCESS'
    else:
        db.session.rollback()
        task.state = 'fail'
        task.exc_info = exc_info[-1500:]
        print(exc_info)

    db.session.commit()


#@hueyapp.task()
@celeryapp.task
def export_good(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    ret = export_good_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=user_code, user_name=user_name)
    db.session.close()
    return ret

def export_good_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    task = Async.query.get(task_id)
    print('handle async task_id ==> ', task_id, task.async_id)

    success = True
    exc_info = ''

    try:
        task.code = 'export_good'
        # q = {filters:[{}], order_by, single, limit, offset, group_by}
        q = args.get('q', '')
        
        query = Good.query

        query = query.filter_by(company_code=company_code, owner_code=owner_code)
        query = gen_query(q, query, Good, db=db, export=True)

        fmt = [
            ("code","货品码"),
            ("barcode","条码"),
            ("name","货品名称"),
            ('category_code', '货类码'),
            ("price","价格"),
            ("cost_price","成本"),
            ("spec","规格"),
            ("unit","单位"),
            ("brand","品牌"),
            ("weight","重量"),
        ]
        keys = [i[0] for i in fmt]
        title = [keys, [i[1] for i in fmt]]

        table = [[getattr(o, k, '') for k in keys] for o in query.all()]
        sio = gen_xlsx(title, table, fname='sample', is_titles=True, get_file=True)

        ext = task.name or '.xlsx'
        file_path = os.path.join(settings.UPLOAD_DIR, str(datetime.now().date()) + '_' + str(uuid4())[:8] + ext)
        with open(file_path, 'wb') as f:
            f.write(sio.getvalue())

        print(file_path)
        task.link = file_path
        db.session.flush()
        exc_info = 'save export_good xlsx'
    except:
        exc_info = traceback.format_exc()
        success = False

    if success:
        db.session.commit()
        task.state = 'done'
        task.exc_info = 'SUCCESS'
    else:
        db.session.rollback()
        task.state = 'fail'
        task.exc_info = exc_info[-1500:]
        print(exc_info)

    db.session.commit()


#@hueyapp.task()
@celeryapp.task
def export_partner(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    ret = export_partner_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=user_code, user_name=user_name)
    db.session.close()
    return ret

def export_partner_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    task = Async.query.get(task_id)
    print('handle async task_id ==> ', task_id, task.async_id)

    success = True
    exc_info = ''

    try:
        task.code = 'export_partner'
        # q = {filters:[{}], order_by, single, limit, offset, group_by}
        q = args.get('q', '')
        
        query = Partner.query

        query = query.filter_by(company_code=company_code)
        query = gen_query(q, query, Partner, db=db, export=True)

        fmt = zip('code,xtype,name,tel,email,contact,address,remark'.split(','), '合作伙伴编码,合作类型,名称,手机,邮箱,其它联系方式,地址,备注'.split(','))

        keys = [i[0] for i in fmt]
        title = [keys, [i[1] for i in fmt]]

        table = [[getattr(o, k, '') for k in keys] for o in query.all()]
        sio = gen_xlsx(title, table, fname='sample', is_titles=True, get_file=True)

        ext = task.name or '.xlsx'
        file_path = os.path.join(settings.UPLOAD_DIR, str(datetime.now().date()) + '_' + str(uuid4())[:8] + ext)
        with open(file_path, 'wb') as f:
            f.write(sio.getvalue())

        print(file_path)
        task.link = file_path
        db.session.flush()
        exc_info = 'save export_partner xlsx'
    except:
        exc_info = traceback.format_exc()
        success = False

    if success:
        db.session.commit()
        task.state = 'done'
        task.exc_info = 'SUCCESS'
    else:
        db.session.rollback()
        task.state = 'fail'
        task.exc_info = exc_info[-1500:]
        print(exc_info)

    db.session.commit()
