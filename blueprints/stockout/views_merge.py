#coding=utf8

from pprint import pprint

from sqlalchemy import and_, or_, func
from flask import Blueprint, g, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from extensions.database import db
from extensions.permissions import admin_perm, manager_perm, normal_perm

from models.stockout import Stockout, StockoutLine, Alloc, StockoutLineTrans, Box, BoxLine, StockoutMerge
from models.inv import Inv, InvRfid, InvRfidTrans
from models.warehouse import Location, Warehouse, Area, Workarea
from models.auth import Partner, User
from blueprints.stockout.action import StockoutAction
from blueprints.inv.action import InvAction
from blueprints.stockout.action_merge import MergeAction

from utils.flask_tools import json_response
from utils.functions import gen_query, get_hash_key, json2mdict_pop
from utils.functions import update_model_with_fields, m2dict, copy_and_update_model, common_poplist, sqla_res2dict
import settings


bp_merge = Blueprint("stockout_merge", __name__)




# 查询单子， 创建新出库单子
@bp_merge.route('', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def merge_api():
    if request.method == 'GET':
        # q = {filters:[{}], order_by, single, limit, offset, group_by}
        query = StockoutMerge.query.t_query

        res = gen_query(request.args.get('q', None), query, StockoutMerge, db=db, per_page=settings.PER_PAGE)
        return json_response(res, indent=4)

    if request.method == 'POST':
        action = MergeAction()
        order = action.create_merge(request.json.get('remark', ''))
        db.session.flush()

        num = 0
        for out in Stockout.query.t_query.filter(Stockout.order_code.in_(request.json['lines'])).with_for_update().all():
            if out.state=='create' and out.state_alloc=='no':
                out.merge_order_code = order.order_code
                num += 1

        if num > 1:
            db.session.commit()
        else:
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': u'部分订单不能合单'})

        return json_response({'status': 'success', 'msg': u'ok', 'order_code': order.order_code})

# 获取订单
@bp_merge.route('/one/<order_id>', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def merge_one_api(order_id):
    """
    """
    if request.method == 'GET':
        order = StockoutMerge.query.t_query.filter(or_(StockoutMerge.id==order_id, StockoutMerge.order_code==order_id)).first()
        order_data = order.as_dict

        stockout_orders = []
        for out in order.orders:
            out_data = out.as_dict
            stockout_orders.append(out_data)
            out_data['lines'] = [line.as_dict for line in out.lines]

        query = Alloc.query.t_query.with_entities(
                func.sum(Alloc.qty_alloc).label('qty_alloc'),
                func.sum(Alloc.qty_pick).label('qty_pick'),
                func.sum(Alloc.qty_ship).label('qty_ship'),
                Alloc.id.label('id'),
                Alloc.sku.label('sku'),
                Alloc.name.label('name'),
                Alloc.barcode.label('barcode'),
                Alloc.spec.label('spec'),
                Alloc.unit.label('unit'),
                Alloc.location_code.label('location_code'),
                Alloc.lpn.label('lpn'),
            ).filter(Alloc.stockout_id==Stockout.id, Stockout.merge_order_code==order.order_code, 
                Stockout.company_code==order.company_code, Stockout.warehouse_code==order.warehouse_code, Stockout.owner_code==order.owner_code) \
            .filter(Location.company_code==order.company_code, Location.warehouse_code==order.warehouse_code, Location.code==Alloc.location_code)

        for rule in g.owner.alloc_rules:
            if rule == 'index_location_desc': # 库位远的优先，库位序大的排前面
                query = query.order_by(Location.index.desc(), Location.code.asc())
            else: # 库位近的优先, 库位序小的排前面
                query = query.order_by(Location.index.asc(), Location.code.asc())

        allocs = query.group_by(Alloc.sku, Alloc.spec, Alloc.location_code, Alloc.lpn).all()
        order_allocs = [sqla_res2dict(alloc) for alloc in allocs]

        if order.state not in ('cancel', 'done'):
            order.calc_state()
            db.session.commit()

        return json_response({
                'order': order_data,
                'stockout_orders': stockout_orders,
                'order_allocs': order_allocs,
            }, indent=4)

    if request.method == 'DELETE':
        order = StockoutMerge.query.t_query.filter(or_(StockoutMerge.id==order_id, StockoutMerge.order_code==order_id)).with_for_update().first()

        if order.state_pick == 'no' and order.state!='done':
            # 取消单据分配
            if order.state_alloc in ('part', 'done'):
                for out in order.orders:
                    if out.state!='done' and out.state_pick=='no' and out.state_alloc in ('part', 'done'):
                        # TODO, 同时取消订单的分配
                        # out.cancel_alloc(); db.session.flush()
                        pass

            # 清空单据
            for out in order.orders:
                out.merge_order_code = ''
            # db.session.delete(order)
            order.state = 'cancel'
            order.state_alloc = 'no'
            order.state_pick  = 'no'
            order.state_ship  = 'no'
        else:
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': u'单据已经拣货了, 不能取消'})

        db.session.commit()
        return json_response({'status': 'success', 'msg': u'ok'})

    # 添加一个订单
    if request.method == 'PUT':
        order = StockoutMerge.query.t_query.filter(or_(StockoutMerge.id==order_id, StockoutMerge.order_code==order_id)).with_for_update().first()
        stockout_id = request.json['stockout_id']
        out = Stockout.query.t_query.filter(id=stockout_id, merge_order_code=order.order_code).with_for_update().first()
        
        if out is not None and out.state_alloc=='no' and out.state not in ('cancel', 'done'):
            out.merge_order_code = order.order_code
            order.calc_state()
        else:
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': u'订单不存在' if out is None else u'订单已经在处理, 无法添加'})

        db.session.commit()
        return json_response({'status': 'success', 'msg': u'ok'})

# 剔除其中某个订单
@bp_merge.route('/throw/<order_id>', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def merge_throw_api(order_id):
    order = StockoutMerge.query.t_query.filter(or_(StockoutMerge.id==order_id, StockoutMerge.order_code==order_id)).with_for_update().first()
    stockout_id = request.json['stockout_id']
    out = Stockout.query.t_query.filter_by(id=stockout_id, merge_order_code=order.order_code).with_for_update().first()
    
    if out is not None:
        out.merge_order_code = ''

    db.session.flush()
    order.calc_state()
    db.session.commit()

    return json_response({'status': 'success', 'msg': u'ok'})


@bp_merge.route('/alloc/<order_id>', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def merge_alloc_api(order_id):
    if request.method == 'POST':
        order = StockoutMerge.query.t_query.filter(or_(StockoutMerge.id==order_id, StockoutMerge.order_code==order_id)).with_for_update().first()


        action = StockoutAction() 

        for out in order.orders:
            if out.state not in ('cancel', 'done') and out.state_alloc != 'done':
                finish, is_partalloc, line, alloc_dict = action.alloc(out.id, order=out)
                # if not finish and not is_partalloc:
                db.session.flush()
        
        order.calc_state()
        db.session.commit()

        return json_response({'status': 'success', 'msg': u'ok', 'state_alloc': order.state_alloc})

    if request.method == 'GET':
        order = StockoutMerge.query.t_query.filter(or_(StockoutMerge.id==order_id, StockoutMerge.order_code==order_id)).first()
        box_dict = {o.order_code: i+1  for i, o in enumerate(order.orders)}
        
        if g.owner.print_rule == 'code_desc':
            print_rule = Location.code.desc()
        elif g.owner.print_rule == 'index_asc':
            print_rule = Location.index.asc()
        elif g.owner.print_rule == 'index_desc':
            print_rule = Location.index.desc()
        else:
            print_rule = Location.code.asc()

        query = Alloc.query.t_query.filter(
                    Alloc.order_code==Stockout.order_code, 
                    Stockout.company_code==Alloc.company_code, 
                    Stockout.owner_code==Alloc.owner_code, 
                    Stockout.warehouse_code==Alloc.warehouse_code
                ) \
            .filter(Stockout.merge_order_code==order.order_code) \
            .filter(Alloc.qty_alloc > Alloc.qty_pick) \
            .filter(
                Alloc.location_code==Location.code, 
                Alloc.company_code==Location.company_code, 
                Alloc.warehouse_code==Location.warehouse_code)

        allocs = query.order_by(print_rule, Alloc.sku, Alloc.order_code).all()

        loc_sku_qty_dict = {"%s#%s"%(o.location_code, o.sku): o.qty for o in query.with_entities(
                func.sum(Alloc.qty_alloc-Alloc.qty_pick).label('qty'), 
                Alloc.location_code.label('location_code'), 
                Alloc.sku.label('sku')) \
            .group_by(Alloc.location_code, Alloc.sku).all()}

        # # 计算Alloc, 根据单据的数量与单号, 一种SKU-qty_alloc分配到托盘号
        oqty = {}
        data = []
        for o in allocs:
            k = '%s#%s#%s'%(o.order_code, o.location_code, o.sku)
            if k not in oqty:
                oqty[k] = 0
                data.append(o)
            oqty[k] += (o.qty_alloc - o.qty_pick)

        table = []
        for o in data:
            d = o.as_dict
            table.append(d)
            k = '%s#%s#%s'%(o.order_code, o.location_code, o.sku)

            d['box'] = box_dict[d['order_code']]
            d['total'] = loc_sku_qty_dict.get("%s#%s"%(d['location_code'], d['sku']), 0)
            d['_text'] = "%s / %s (#%s)"%(oqty[k], d['total'], d['box'])

        return json_response({'status': 'success', 'msg': u'播种单', 'data': table})


@bp_merge.route('/pick/<order_id>', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def merge_pick_api(order_id):
    if request.method == 'POST':
        order = StockoutMerge.query.t_query.filter(or_(StockoutMerge.id==order_id, StockoutMerge.order_code==order_id)).with_for_update().first()


        action = StockoutAction()

        for out in order.orders:
            action.pick(out)
            db.session.flush()

        order.calc_state()
        db.session.commit()

        return json_response({'status': 'success', 'msg': u'ok', 'state_alloc': order.state_alloc})