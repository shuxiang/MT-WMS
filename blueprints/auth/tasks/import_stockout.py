#coding=utf8

import traceback

from extensions.database import db
from extensions.hueyext import hueyapp
from extensions.celeryext import celeryapp
from models.asyncmodel import Async
from models.warehouse import Warehouse, Area, Workarea, Location
from models.inv import Good, Category, Inv
from models.auth import Partner, Seq

from models.stockout import Stockout, StockoutLine
from blueprints.stockout.action import StockoutAction

from utils.upload import get_file_content
from utils.functions import clear_empty
from utils.base import DictNone

# 
#@hueyapp.task()
@celeryapp.task
def import_stockout(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    ret = import_stockout_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=user_code, user_name=user_name)
    db.session.close()
    return ret

def import_stockout_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    task = Async.query.get(task_id)
    print('handle async task_id ==> ', task_id, task.async_id)

    task.get_file()
    content = get_file_content(task.link)

    success = True
    exc_info = ''

    try:
        order_dict = DictNone()
        task.code = 'stockout'
        for row in content:
            d = DictNone(clear_empty(row))
            if not d.erp_order_code:
                continue
            # 创建订单
            if d.erp_order_code not in order_dict:
                if Stockout.query.filter_by(company_code=company_code, warehouse_code=warehouse_code, owner_code=owner_code, \
                        erp_order_code=d.erp_order_code).count() > 0:
                    continue
                order = Stockout(company_code=company_code, warehouse_code=warehouse_code, owner_code=owner_code, 
                        source='import', user_code=user_code, user_name=user_name)
                order_dict[d.erp_order_code] = order

                order.erp_order_code = d.erp_order_code
                order.order_code = Seq.make_order_code('C', company_code, warehouse_code, owner_code)
                order.xtype = d.xtype or 'B2B'
                order.order_type = d.order_type
                order.date_planned = d.date_planned
                order.source = 'custom'
                order.remark = d.remark or ''
                order.partner_code = d.partner_code or ''
                order.partner_name = d.partner_name or ''

                order.sender_info = {'name': d.sender, 'tel': d.sender_tel, 'address': d.sender_address}
                order.receiver_info = {'name': d.receiver, 'tel': d.receiver_tel, 'address': d.receiver_address}
                order.supplier_info = {'supplier_code': d.supplier_code}
                order.express_info = {'express_code': d.express_code}
                order.invoice_info = {'invoice': d.invoice}
                # order.JSON = {'custom1': d.custom1, 'custom2': d.custom2, 'custom3': d.custom3, 'custom4': d.custom4}

                db.session.add(order)
            else:
                order = order_dict[d.erp_order_code]

            if not d.sku or not d.qty:
                continue
            line = StockoutLine(company_code=company_code, warehouse_code=warehouse_code, owner_code=owner_code)
            line.erp_order_code = order.erp_order_code
            line.order_code = order.order_code
            line.sku = d.sku
            line.barcode = d.barcode or d.sku
            line.name = d.name or d.sku
            line.qty = int(d.qty)
            line.remark = d.remark or ''

            line.supplier_code = d.supplier_code or ''

            # line.supplier_code = d.supplier_code or ''
            # line.quality_type = d.quality_type or 'ZP'
            # line.product_date = d.product_date or None
            # line.expire_date  = d.expire_date or None
            # line.batch_code   = d.batch_code or ''
            # line.virtual_warehouse = d.virtual_warehouse or ''
            # line.spec = d.spec or ''

            line.style   = d.style or ''
            line.color   = d.color or ''
            line.size    = d.size or ''
            line.unit    = d.unit or ''
            # line.JSON    = {'custom1': d.custom1, 'custom2': d.custom2, 'custom3': d.custom3, 'custom4': d.custom4}

            db.session.add(line)
            line.stockout = order

        db.session.flush()
        exc_info = 'save stockout: %s'%len(content)
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
    





