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
import settings

from models.stockout import Stockout, StockoutLine
from blueprints.stockout.action import StockoutAction

from utils.functions import clear_empty, gen_query, export_attr
from utils.base import DictNone, Dict
from utils.flask_tools import gen_csv, gen_xlsx

# 
#@hueyapp.task()
@celeryapp.task
def export_stockout(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    ret = export_stockout_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=user_code, user_name=user_name)
    db.session.close()
    return ret

def export_stockout_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    task = Async.query.get(task_id)
    print('handle async task_id ==> ', task_id, task.async_id)

    success = True
    exc_info = ''

    try:
        task.code = 'export_stockout'
        # q = {filters:[{}], order_by, single, limit, offset, group_by}
        q = args.get('q', '')
        query = Stockout.query.filter_by(company_code=company_code, warehouse_code=warehouse_code, owner_code=owner_code)
        query = gen_query(q, query, Stockout, db=db, export=True)

        keys = ("erp_order_code", 'order_code', 'o.state',"sku","barcode","name","qty","qty_alloc","qty_pick","qty_ship","xtype","order_type","unit","date_planned","o.remark",'o.create_time')
        title2 = ("订单号", 'wms单号', '状态',"货品码","条码","货品名称","预期数量","分配数量","拣货数量","发运数量","订单类型","上游订单类型","单位","计划发货时间","备注",'创建时间')

        title = [keys, title2]

        table = []
        for order in query.all():
            table += [[export_attr(k, o, order) for k in keys] for o in order.lines]

        # table = [[getattr(o, k, '') for k in keys] for o in query.all()]
        sio = gen_xlsx(title, table, fname='sample', is_titles=True, get_file=True)

        ext = task.name or '.xlsx'
        file_path = os.path.join(settings.UPLOAD_DIR, str(datetime.now().date()) + '_' + str(uuid4())[:8] + ext)
        with open(file_path, 'wb') as f:
            f.write(sio.getvalue())

        print(file_path)
        task.link = file_path
        db.session.flush()
        exc_info = 'save export_stockout xlsx'
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
    





