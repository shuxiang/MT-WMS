#coding=utf8

import traceback

from extensions.database import db
from extensions.hueyext import hueyapp
from extensions.celeryext import celeryapp
from models.asyncmodel import Async
from models.warehouse import Warehouse, Area, Workarea, Location
from models.inv import Good, Category, Inv
from models.auth import Partner, Seq

from models.inv import InvMove, InvAdjust, InvCount

from utils.upload import get_file_content
from utils.functions import clear_empty
from utils.base import DictNone

# 
#@hueyapp.task()
@celeryapp.task
def import_invmove(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    ret = import_invmove_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=user_code, user_name=user_name)
    db.session.close()
    return ret

def import_invmove_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    task = Async.query.get(task_id)
    print('handle async task_id ==> ', task_id, task.async_id)

    task.get_file()
    content = get_file_content(task.link)

    success = True
    exc_info = ''

    try:
        task.code = 'inv_move'
        series_code = Seq.make_order_code('IM', company_code, warehouse_code, owner_code)
        for row in content:
            d = DictNone(clear_empty(row))
            if not d.series_code:
                d.series_code = series_code
            # 创建订单
            # if InvMove.query.filter_by(company_code=company_code, warehouse_code=warehouse_code, owner_code=owner_code, \
            #         series_code=d.series_code).count() > 0:
            #     continue
            line = InvMove(company_code=company_code, warehouse_code=warehouse_code, owner_code=owner_code, source='import')
            line.series_code = d.series_code

            line.sku = d.sku
            line.barcode = d.barcode or d.sku
            line.name = d.name
            line.location_code = d.location_code
            line.qty = int(d.qty)
            line.move_type = 'user'
            line.remark = d.remark

            line.stockin_date = d.stockin_date or None

            line.supplier_code = d.supplier_code or ''
            line.quality_type = d.quality_type or 'ZP'
            line.product_date = d.product_date or None
            line.expire_date  = d.expire_date or None
            line.batch_code   = d.batch_code or ''
            line.virtual_warehouse = d.virtual_warehouse or ''
            line.spec = d.spec

            line.style   = d.style or ''
            line.color   = d.color or ''
            line.size    = d.size or ''

            line.lpn = d.lpn
            line.dest_warehouse_code = d.dest_warehouse_code or warehouse_code
            line.dest_location_code = d.dest_location_code
            line.dest_lpn = d.dest_lpn or ''

            db.session.add(line)

        db.session.flush()
        exc_info = 'save inv_move: %s'%len(content)
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
def import_invadjust(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    ret = import_invadjust_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=user_code, user_name=user_name)
    db.session.close()
    return ret

def import_invadjust_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    task = Async.query.get(task_id)
    print('handle async task_id ==> ', task_id, task.async_id)

    task.get_file()
    content = get_file_content(task.link)

    success = True
    exc_info = ''

    try:
        task.code = 'inv_adjust'
        series_code = Seq.make_order_code('IA', company_code, warehouse_code, owner_code)
        for row in content:
            d = DictNone(clear_empty(row))
            if not d.series_code:
                d.series_code = series_code
            # 创建订单
            # if InvAdjust.query.filter_by(company_code=company_code, warehouse_code=warehouse_code, owner_code=owner_code, \
            #         series_code=d.series_code).count() > 0:
            #     continue
            line = InvAdjust(company_code=company_code, warehouse_code=warehouse_code, owner_code=owner_code, source='import')
            line.series_code = d.series_code

            line.sku = d.sku
            line.barcode = d.barcode or d.sku
            line.name = d.name
            line.location_code = d.location_code
            line.qty_before = int(d.qty_before)
            line.qty_after = int(d.qty_after)
            line.qty_diff = int(d.qty_diff)
            line.remark = d.remark

            line.stockin_date = d.stockin_date or None

            line.supplier_code = d.supplier_code or ''
            line.quality_type = d.quality_type or 'ZP'
            line.product_date = d.product_date or None
            line.expire_date  = d.expire_date or None
            line.batch_code   = d.batch_code or ''
            line.virtual_warehouse = d.virtual_warehouse or ''
            line.spec = d.spec

            line.style   = d.style or ''
            line.color   = d.color or ''
            line.size    = d.size or ''

            line.lpn = d.lpn

            db.session.add(line)

        db.session.flush()
        exc_info = 'save inv_adjust: %s'%len(content)
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
def import_invcount(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    ret = import_invcount_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=user_code, user_name=user_name)
    db.session.close()
    return ret

def import_invcount_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    task = Async.query.get(task_id)
    print('handle async task_id ==> ', task_id, task.async_id)

    task.get_file()
    content = get_file_content(task.link)

    success = True
    exc_info = ''

    try:
        task.code = 'inv_count'
        series_code = Seq.make_order_code('IC', company_code, warehouse_code, owner_code)
        for row in content:
            d = DictNone(clear_empty(row))
            if not d.series_code:
                d.series_code = series_code
            # 查询盘点单，并更新数量
            subq = InvCount.query.filter_by(company_code=company_code, warehouse_code=warehouse_code, owner_code=owner_code) \
                .filter_by(series_code=d.series_code, sku=d.sku, location_code=d.location_code, lpn=d.lpn or '', state='create')

            # if d.stockin_date and d.stockin_date!='None':
            #     subq = subq.filter_by(stockin_date=d.stockin_date)

            if d.supplier_code:
                subq = subq.filter_by(supplier_code=d.supplier_code)
            if d.quality_type:
                subq = subq.filter_by(quality_type=d.quality_type)
            if d.product_date and d.product_date!='None':
                subq = subq.filter_by(product_date=d.product_date)
            if d.expire_date and d.expire_date!='None':
                subq = subq.filter_by(expire_date=d.expire_date)
            if d.batch_code:
                subq = subq.filter_by(batch_code=d.batch_code)
            if d.virtual_warehouse:
                subq = subq.filter_by(virtual_warehouse=d.virtual_warehouse)
            if d.spec:
                subq = subq.filter_by(spec=d.spec)
            if d.style:
                subq = subq.filter_by(style=d.style)
            if d.color:
                subq = subq.filter_by(color=d.color)
            if d.size:
                subq = subq.filter_by(size=d.size)

            line = subq.first()
            if line:
                line.qty = int(d.qty)
                line.qty_real = int(d.qty_real)

            else:
                # 创建订单
                # if InvCount.query.filter_by(company_code=company_code, warehouse_code=warehouse_code, owner_code=owner_code, \
                #         series_code=d.series_code).count() > 0:
                #     continue

                if not d.sku or not d.qty:
                    continue
                line = InvCount(company_code=company_code, warehouse_code=warehouse_code, owner_code=owner_code, source='import')
                line.series_code = d.series_code

                line.sku = d.sku
                line.barcode = d.barcode or d.sku
                line.name = d.name or d.sku
                line.location_code = d.location_code
                line.qty = int(d.qty)
                line.qty_real = int(d.qty_real)
                line.remark = d.remark

                # if d.stockin_date:
                #     line.stockin_date = d.stockin_date
                if d.supplier_code:
                    line.supplier_code = d.supplier_code or ''
                if d.quality_type:
                    line.quality_type = d.quality_type or 'ZP'
                if d.product_date:
                    line.product_date = d.product_date
                if d.expire_date:
                    line.expire_date  = d.expire_date
                line.batch_code   = d.batch_code or ''
                line.virtual_warehouse = d.virtual_warehouse or ''
                line.spec = d.spec or ''

                line.style   = d.style or ''
                line.color   = d.color or ''
                line.size    = d.size or ''

                line.lpn = d.lpn or ''

                db.session.add(line)

        db.session.flush()
        exc_info = 'save inv_count: %s'%len(content)
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
    