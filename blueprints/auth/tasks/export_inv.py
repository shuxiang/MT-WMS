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
from models.inv import Good, Category, Inv
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
def export_inv(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    ret = export_inv_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=user_code, user_name=user_name)
    db.session.close()
    return ret

def export_inv_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    task = Async.query.get(task_id)
    print('handle async task_id ==> ', task_id, task.async_id)

    success = True
    exc_info = ''

    try:
        task.code = 'export_inv'
        # q = {filters:[{}], order_by, single, limit, offset, group_by}
        q = args.get('q', '')
        without_batch = 'without_batch' in q
        
        query = Inv.query.filter(Inv.location_code!='PICK', Inv.qty>0)
        if without_batch:
            query = query.with_entities(
                    func.sum(Inv.qty).label('sum_qty'), 
                    func.sum(Inv.qty_able).label('sum_qty_able'), 
                    func.sum(Inv.qty_alloc).label('sum_qty_alloc'), 
                    Inv) \
                .filter_by(company_code=company_code, warehouse_code=warehouse_code, owner_code=owner_code) \
                .group_by(Inv.location_code, Inv.sku)
            query = gen_query(q, query, Inv, db=db, export=True)
        else:
            query = query.filter_by(company_code=company_code, warehouse_code=warehouse_code, owner_code=owner_code)
            query = gen_query(q, query, Inv, db=db, export=True)

        fmt = [
            ("id","ID"),
            ("sku","货品码"),
            ("barcode","条码"),
            ("name","货品名称"),
            ("location_code","库位"),
            ("qty","数量"),
            ("qty_alloc","锁定数"),
            ("qty_able","可用数"),
            ("category_code","货类码"),
            ("unit","单位"),
            ("spec","规格"),
            ("supplier_code", '供应商'),
            ("product_date","*生产日期"),
            ("batch_code","*批次号"),
            ("quality_type","*质量"),
            ("lpn","*容器"),
            ("area_code","库区码"),
            ("workarea_code","工作区码"),
        ]
        keys = [i[0] for i in fmt]
        title = [keys, [i[1] for i in fmt]]

        table = []
        if without_batch:
            for o in query.all():
                obj = Dict(o[-1].as_dict)
                obj.qty = int(o.sum_qty)
                obj.qty_able = int(o.sum_qty_able)
                obj.qty_alloc = int(o.sum_qty_alloc)
                table.append([getattr(obj, k, '') for k in keys])
        else:
            table = [[getattr(o, k, '') for k in keys] for o in query.all()]
        sio = gen_xlsx(title, table, fname='sample', is_titles=True, get_file=True)

        ext = task.name or '.xlsx'
        file_path = os.path.join(settings.UPLOAD_DIR, str(datetime.now().date()) + '_' + str(uuid4())[:8] + ext)
        with open(file_path, 'wb') as f:
            f.write(sio.getvalue())

        print(file_path)
        task.link = file_path
        db.session.flush()
        exc_info = 'save export_inv xlsx'
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
def export_invcount(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    ret = export_invcount_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=user_code, user_name=user_name)
    db.session.close()
    return ret

def export_invcount_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    task = Async.query.get(task_id)
    print('handle async task_id ==> ', task_id, task.async_id)

    success = True
    exc_info = ''

    try:
        task.code = 'export_invcount'
        # q = {filters:[{}], order_by, single, limit, offset, group_by}
        q = args.get('q', '')
        query = InvCount.query.filter_by(company_code=company_code, warehouse_code=warehouse_code, owner_code=owner_code)
        query = gen_query(q, query, InvCount, db=db, export=True)

        keys = ("series_code","owner_code","sku","barcode","name","location_code","qty","qty_real","lpn",)
        title2 = ("单号","货主码","货品码","条码","名称","库位","数量","盘点数量","容器",)
        title = [keys, title2]

        table = [[getattr(o, k, '') for k in keys] for o in query.all()]
        sio = gen_xlsx(title, table, fname='sample', is_titles=True, get_file=True)

        ext = task.name or '.xlsx'
        file_path = os.path.join(settings.UPLOAD_DIR, str(datetime.now().date()) + '_' + str(uuid4())[:8] + ext)
        with open(file_path, 'wb') as f:
            f.write(sio.getvalue())

        print(file_path)
        task.link = file_path
        db.session.flush()
        exc_info = 'save export_invcount xlsx'
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
def export_invmove(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    ret = export_invmove_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=user_code, user_name=user_name)
    db.session.close()
    return ret

def export_invmove_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    task = Async.query.get(task_id)
    print('handle async task_id ==> ', task_id, task.async_id)

    success = True
    exc_info = ''

    try:
        task.code = 'export_invmove'
        # q = {filters:[{}], order_by, single, limit, offset, group_by}
        q = args.get('q', '')
        query = InvMove.query.filter_by(company_code=company_code, warehouse_code=warehouse_code, owner_code=owner_code)
        query = gen_query(q, query, InvMove, db=db, export=True)

        keys = ("series_code","sku","barcode","name","location_code","lpn","qty","dest_location_code","dest_lpn",)
        title2 = ("单号","货品码","条码","名称","原库位", "原容器","数量", "目标库位","目标容器",)
        title = [keys, title2]

        table = [[getattr(o, k, '') for k in keys] for o in query.all()]
        sio = gen_xlsx(title, table, fname='sample', is_titles=True, get_file=True)

        ext = task.name or '.xlsx'
        file_path = os.path.join(settings.UPLOAD_DIR, str(datetime.now().date()) + '_' + str(uuid4())[:8] + ext)
        with open(file_path, 'wb') as f:
            f.write(sio.getvalue())

        print(file_path)
        task.link = file_path
        db.session.flush()
        exc_info = 'save export_invmove xlsx'
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
    



