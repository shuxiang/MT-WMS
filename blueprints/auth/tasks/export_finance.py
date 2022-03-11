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

from models.finance import Money, MoneyLine, MoneySummary

from utils.upload import get_file_content
from utils.functions import clear_empty, gen_query, export_attr
from utils.base import DictNone, Dict
from utils.flask_tools import gen_csv, gen_xlsx

import settings

# 
#@hueyapp.task()
@celeryapp.task
def export_finance(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    ret = export_finance_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=user_code, user_name=user_name)
    db.session.close()
    return ret

def export_finance_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    task = Async.query.get(task_id)
    print('handle async task_id ==> ', task_id, task.async_id)

    success = True
    exc_info = ''

    try:
        task.code = 'export_finance'
        # q = {filters:[{}], order_by, single, limit, offset, group_by}
        q = args.get('q', '')
        query = Money.query.filter_by(company_code=company_code, warehouse_code=warehouse_code, owner_code=owner_code)
        query = gen_query(q, query, Money, db=db, export=True)

        keys = ("id","code",'partner_code',"xtype","come","amount","real", 'state', "remark","date_forcount",'create_time')
        title2 = ('ID',"关联单号","合作伙伴",'类型',"收支","总额","实额","状态",'备注',"业务日期",'创建时间')
        title = [keys, title2]

        table = []
        table = [[getattr(o, k, '') for k in keys] for o in query.all()]

        #lines = query.all()
        #order = lines[0].order

        #table = [[getattr(o, k, '') or getattr(order, k, '') for k in keys] for o in lines]
        sio = gen_xlsx(title, table, fname=task.code, is_titles=True, get_file=True)

        ext = task.name or '.xlsx'
        file_path = os.path.join(settings.UPLOAD_DIR, str(datetime.now().date()) + '_' + str(uuid4())[:8] + ext)
        with open(file_path, 'wb') as f:
            f.write(sio.getvalue())

        print(file_path)
        task.link = file_path
        db.session.flush()
        exc_info = 'save export_finance xlsx'
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