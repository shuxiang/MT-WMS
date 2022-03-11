#coding=utf8

import traceback
from collections import OrderedDict
from datetime import datetime
import uuid
from uuid import uuid4
import os
import os.path
from sqlalchemy import func, and_, or_

from extensions.database import db
from extensions.hueyext import hueyapp
from extensions.celeryext import celeryapp
from models.asyncmodel import Async
from models.warehouse import Warehouse, Area, Workarea, Location
from models.inv import Good, Category, Inv
from models.auth import Partner

from models.inv import InvMove, InvAdjust, InvCount

from utils.upload import get_file_content
from utils.functions import clear_empty, gen_query, make_q
from utils.base import DictNone, Dict
from utils.flask_tools import gen_csv, gen_xlsx

import settings

# 
#@hueyapp.task()
@celeryapp.task
def export_invwarn(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    ret = export_invwarn_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=user_code, user_name=user_name)
    db.session.close()
    return ret

def export_invwarn_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    task = Async.query.get(task_id)
    print('handle async task_id ==> ', task_id, )
    print(task.async_id)

    success = True
    exc_info = ''

    try:
        task.code = 'export_invwarn'
        # q = {filters:[{}], order_by, single, limit, offset, group_by}
        qty_real = func.sum(Inv.qty_able).label('qty_real')

        argstr = args.get('q', '')
        q = make_q(argstr)
        tab = q.get('tab', '1')

        subq = gen_query(argstr, Good.query.filter(Good.company_code==company_code, Good.owner_code==owner_code), Good, db=db, export=True)
        subq0 = Inv.query.filter(Inv.company_code==company_code, Inv.warehouse_code==warehouse_code, Inv.owner_code==owner_code) \
                .with_entities(Inv.sku.label('sku'), Inv.qty_able.label('qty_able')).filter(Inv.location_code!='PICK').subquery()

        if tab == '1':
            subq = subq.outerjoin(subq0, subq0.c.sku==Good.code).with_entities(Good.code, Good.barcode, Good.name, Good.max_qty, subq0.c.qty_able) \
                    .filter(Good.max_qty>0) \
                    .group_by(Good.code).having(subq0.c.qty_able>Good.max_qty).order_by(None)
        if tab == '2':
            subq = subq.outerjoin(subq0, subq0.c.sku==Good.code).with_entities(Good.code, Good.barcode, Good.name, Good.min_qty, subq0.c.qty_able) \
                    .filter(Good.min_qty>0) \
                    .group_by(Good.code).having(or_(subq0.c.qty_able<Good.min_qty, subq0.c.qty_able==None)).order_by(None)

        table = []
        for line in subq.all():
            d = DictNone()
            d.sku = line.code
            d.barcode = line.barcode
            d.name = line.name
            d.qty_real = line.qty_able or 0
            d.qty_warn = line.min_qty
            table.append(d)

        fmt = [
            ("sku","货品码"),
            ("barcode","条码"),
            ("name","货品名称"),
            ("qty_real","可用数量"),
            ("qty_warn","告警数量"),
        ]
        keys = [i[0] for i in fmt]
        title = [keys, [i[1] for i in fmt]]

        xtable = [[getattr(o, k, '') for k in keys] for o in table]
        sio = gen_xlsx(title, xtable, fname='sample', is_titles=True, get_file=True)

        ext = task.name or '.xlsx'
        file_path = os.path.join(settings.UPLOAD_DIR, str(datetime.now().date()) + '_' + str(uuid4())[:8] + ext)
        with open(file_path, 'wb') as f:
            f.write(sio.getvalue())

        print(file_path)
        task.link = file_path
        db.session.flush()
        exc_info = 'save export_invwarn xlsx'
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
    

