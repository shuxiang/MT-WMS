#coding=utf8
import os
import os.path
import json
import traceback
from sqlalchemy import func, or_
from pprint import pprint
from datetime import datetime
from random import randint

from flask import Blueprint, g, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from extensions.database import db
from extensions.permissions import admin_perm, manager_perm, normal_perm

from models.inv import Inv, Good, Category, InvRfid
from models.inv import InvMove, InvAdjust, InvCount, InvWarn
from models.warehouse import Location
from blueprints.inv.action import InvAction, InvCountAction, InvMoveAction, InvAdjustAction

from utils.flask_tools import json_response, gen_csv
from utils.functions import update_model_with_fields, m2dict, copy_and_update_model, common_poplist, json2mdict_pop
from utils.functions import gen_query, make_q
from utils.base import Dict, DictNone
import settings

bp_inv_replenish = Blueprint("inv_replenish", __name__)



# 补货移库
# 计算需要移库的数量, 已经移库的数量
@bp_inv_replenish.route('/compute/move', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def compute_move_api():

    def get_qty_move(line):
        o = InvMove.query.with_entities(func.sum(InvMove.qty_real).label('qty')).t_query \
                .filter(~InvMove.state.in_(['done', 'cancel'])) \
                .filter(InvMove.sku==line['sku']) \
                .filter(InvMove.dest_location_code==line['location_code']) \
                .filter(InvMove.move_type=='replenish') \
                .first()
        return (o.qty or 0) if o else 0

    # # TODO , 要不要做分页, 后端生成, 还是前端传一页数据过来生成; 目前是做成分页, 每个补货移库, 最多20条
    if request.method == 'GET':
        # huey job
        argstr = request.args.get('q', '')
        q = make_q(argstr)
        subq = gen_query(argstr, InvWarn.query.t_query, InvWarn, db=db, export=True)
        pagin = subq.paginate(q.page, per_page=(q.per_page or settings.PER_PAGE))
        
        invaction = InvAction()
        table = []
        for line in pagin.items:
            d = DictNone()

            d.sku = line.sku
            d.barcode = line.barcode
            d.name = line.name
            d.location_code = line.location_code
            d.qty_real = invaction.get_inv_qty(d.sku, location_code=d.location_code)
            d.qty_warn = line.min_qty
            d.max_qty = line.max_qty

            d.qty_move = get_qty_move(d)
            d.qty_buy = d.max_qty - d.qty_real
            d.qty_buy2 = d.qty_buy - d.qty_move
            d.qty_buy2 = 0 if d.qty_buy2 <= 0 else d.qty_buy2
            table.append(d)
        # gen_move
        lines_num = 0
        series_code = None
        if table:
            data = DictNone()
            data.warehouse_code = g.warehouse_code
            data.company_code = g.company_code
            data.owner_code = g.owner_code
            data.move_type = 'replenish'

            action = InvMoveAction()
            series_code = action.gen_series_code(g.company_code, g.warehouse_code, g.owner_code)

            for line in table:
                if line.qty_buy2 > 0:
                    line.qty = line.qty_buy2
                    line.qty_real = line.qty_buy2

                    line.dest_location_code = line.location_code
                    # 选取合适的库存行, 来进行移库分配, 可能要拆多行； 直接进行move_out操作
                    line.location_code = ''
                    n = replenish_move_out(line, series_code)

                    lines_num += n

        if lines_num > 0:
            db.session.commit()
            return json_response({'status': 'success', 'msg': 'ok', 'data': table, 'series_code': series_code})
        else:
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': u'不需要补货, 可能已经存在补货单未完成', 'data': table})

def replenish_move_out(line, series_code=None):
    query = Inv.query.t_query.filter(Inv.location_code!='PICK') \
                    .filter_by(sku=line.sku) \
                    .filter_by(spec=line.spec or '') \
                    .filter(Inv.qty_able > 0) \
                    .filter(Inv.location_code!=line.dest_location_code) # important
    if g.owner.is_enable_supplier_batch:
        query = query.filter_by(supplier_code=line.supplier_code)
    invs =  query.order_by(Inv.qty_able.desc()).all()

    qty = 0
    n = 0
    for inv in invs:
        if qty < line.qty:
            move = update_model_with_fields(InvMove, inv, common_poplist, user_code=g.user.code, user_name=g.user.name, remark='',
                series_code=series_code, dest_warehouse_code=g.warehouse_code, **json2mdict_pop(InvMove, line))
            move.state = 'doing'
            move.location_code = inv.location_code
            move.move_type = 'replenish'
            db.session.add(move)
            db.session.flush()

            _qty = 0
            if inv.qty_able >= (line.qty - qty): # 大于未补数量
                _qty = (line.qty - qty)
            else:
                _qty = inv.qty_able # 小于未补数量

            # lock
            inv = Inv.query.t_query.with_for_update().filter_by(id=inv.id).first()
            if inv.qty_able < _qty:
                _qty = inv.qty_able

            qty += _qty # 已补数量
            if _qty > 0: # 如果还有库存
                move.qty = _qty
                move.qty_real = _qty
                ok = InvAction.move(inv, _qty, dest_w=g.warehouse_code, dest_lc='PICK', dest_lpn='MOVE_%s'%move.id, is_move=True, move_type='out')
            else:
                db.session.delete(move)
            n += 1

    return n


@bp_inv_replenish.route('/invwarn', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
def invwarn_api():
    if request.method == 'GET':
        # q = {filters:[{}], order_by, single, limit, offset, group_by}
        query = InvWarn.query.t_query
        res = gen_query(request.args.get('q', None), query, InvWarn, db=db, per_page=settings.PER_PAGE)
        return json_response(res, indent=4)

    if request.method == 'POST' or request.method == 'PUT':
        data = request.json
        obj = InvWarn.query.t_query.filter_by(sku=data['sku'], location_code=data['location_code']).first()
        if obj is not None:
            obj.update(data)
        else:
            obj = InvWarn(company_code=g.company_code, owner_code=g.owner_code, warehouse_code=g.warehouse_code, **data)
            db.session.add(obj)
        db.session.commit()
        return json_response({'status': 'success', 'msg': 'ok', 'data': obj.as_dict}, indent=4)