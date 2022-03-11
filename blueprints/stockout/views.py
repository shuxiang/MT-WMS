#coding=utf8

from pprint import pprint

from sqlalchemy import and_, or_, func
from flask import Blueprint, g, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from extensions.database import db
from extensions.permissions import admin_perm, manager_perm, normal_perm

from models.stockout import Stockout, StockoutLine, Alloc, StockoutLineTrans, Box, BoxLine
from models.inv import Inv, InvRfid, InvRfidTrans
from models.warehouse import Location, Warehouse, Area, Workarea
from models.auth import Partner, User
from models.finance import Money, MoneyLine
from blueprints.stockout.action import StockoutAction
from blueprints.inv.action import InvAction
from blueprints.stockout.action_waybill import WaybillAction 

from utils.flask_tools import json_response
from utils.functions import gen_query, get_hash_key, json2mdict_pop, split_list
from utils.functions import update_model_with_fields, m2dict, copy_and_update_model, common_poplist, DictNone
import settings


bp_stockout = Blueprint("stockout", __name__)




# 查询单子， 创建新出库单子
@bp_stockout.route('/stockout', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def stockout_api():
    """
    创建出库单
    post req:
    [{'erp_order_code': 'erp5', 'warehouse_code': 'test', 'owner_code': 'test',
        'lines': [
            {'sku': 'sku1', 'barcode': 'sku1', 'qty': 6}, 
        ]
    }]

    返回创建的订单列表或者查询的订单列表
    get/post resp:
    [{...}]
    """
    if request.method == 'GET':
        # q = {filters:[{}], order_by, single, limit, offset, group_by}
        query = Stockout.query.t_query
        if request.args.get('unpick', '') == 'true':
            query = query.filter(Stockout.id==StockoutLine.stockout_id, StockoutLine.qty_alloc>StockoutLine.qty_pick)
        # print(query.real_sql())
        res = gen_query(request.args.get('q', None), query, Stockout, db=db, per_page=settings.PER_PAGE)
        return json_response(res, indent=4)

    orders = []
    if request.method == 'POST':
        data = request.json
        for d in data:
            lines = d.pop('lines', [])
            exist, order = StockoutAction.create_stockout(d, g)
            if not exist:
                # order.JSON = d
                db.session.add(order)
                # lines
                for ld in lines:
                    if float(ld.get('qty', 0)) <= 0:
                        continue
                    StockoutAction.create_stockout_line(ld, order)
            orders.append(order)

        order.sum_price
        StockoutAction.create_transfer_stockin(order)
        db.session.commit()

    return json_response([order.as_dict for order in orders])


# 获取订单
@bp_stockout.route('/stockout/one/<order_id>', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def stockout_one_api(order_id):
    """
    查询订单
    get req:
    """
    if request.method == 'GET':
        order = Stockout.query.t_query.filter(or_(Stockout.id==order_id, Stockout.order_code==order_id)).first()
        order_data = order.as_dict

        box_lines = []
        for box in Box.query.t_query.filter_by(order_code=order.order_code).all():
            box_data = box.as_dict
            box_data['lines'] = [line.as_dict for line in box.lines]
            box_lines.append(box_data)

        lines_data = []
        for line in order.lines:
            d = line.as_dict
            d['qty_now'] = 0
            lines_data.append(d)

        partner = Partner.query.c_query.filter_by(code=order.partner_code).first()
        partner_data = partner.as_dict if partner else {}
        if not order.price:
            order.sum_price
            db.session.commit()

        return json_response({'order': order_data, 'lines': lines_data, 'box_lines': box_lines, 'partner': partner_data, 'order_boxs': box_lines}, indent=4)

    if request.method == 'PUT':
        # update Stockout
        order = Stockout.query.t_query.filter(or_(Stockout.id==order_id, Stockout.order_code==order_id)).with_for_update().first()
        if order.state != 'create':
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': u'order state is not `create`',}, indent=4)
        order_id = order.id
        order.partner_code = request.json['partner_code'] or order.partner_code
        order.partner_name = request.json.get('partner_name', order.partner_name)
        partner = Partner.query.c_query.filter_by(code=order.partner_code).first()
        if partner:
            order.partner_id = partner.id

        w_user_code = request.json.pop('w_user_code', '')
        if w_user_code:
            u = User.query.c_query.filter_by(code=w_user_code).first()
            if u:
                order.w_user_name = u.name
                order.w_user_code = u.code

        order.order_type = request.json['order_type'] or order.order_type
        for line in request.json['lines']:
            if not line.get('id',None):
                if int(line.get('qty', 0)) <= 0:
                        continue
                StockoutAction.create_stockout_line(line, order)
            elif line['qty'] != '' and line.get('id',None):
                pl = StockoutLine.query.filter_by(id=line['id'], stockout_id=order_id).with_for_update().first()
                pl.qty = line['qty']
                pl.price = line['price'] or pl.price
                pl.supplier_code = line['supplier_code'] or ''
                pl.spec = line['spec'] or ''

        order.sum_price
        db.session.commit()
        return json_response({'status': 'success', 'msg': u'ok',}, indent=4) 

    return ''


# 更新订单信息
@bp_stockout.route('/stockout/info', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def stockout_info_api():
    """
    更新订单头信息
    post req: 
        {}
    """
    if request.method == 'POST':
        data = request.json
        order = Stockout.query.t_query.filter_by(id=data['id']).first()
        order.sender_info = data['sender_info']
        order.receiver_info = data['receiver_info']
        order.date_planned = data['date_planned'][:10] if data.get('date_planned', '') else None
        order.remark = data['remark']

        db.session.commit()

    return json_response({'status': 'success', 'msg': u'ok'})

# 查询订单行
@bp_stockout.route('/<stockout_id>/line', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@bp_stockout.route('/<stockout_id>/line/<line_id>', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def stockout_line_api(stockout_id, line_id=None):
    if request.method == 'GET':
        order = Stockout.query.t_query.filter_by(id=stockout_id).first()
        res = order.as_dict
        res['lines'] = [line.as_dict for line in order.lines]

        return json_response(res, indent=4)

    if request.method == 'DELETE':
        stockout = Stockout.query.t_query.filter_by(id=stockout_id).with_for_update().first()
        if stockout.state == 'create':
            StockoutLine.query.t_query.filter_by(id=line_id, stockout_id=stockout_id).delete()
            db.session.commit()
            return json_response({'status': 'success', 'msg': u'ok',}, indent=4) 
        else:
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': u'order state is not `create`',}, indent=4)

    

# 完成出库单; 强制关闭，未使用； 需要增加一个部分拣货api, 不能用快速拣货
# 如果强制关闭, 已经拣货的不用管, 已分配未拣货的, 取消分配；
@bp_stockout.route('/done/<stockout_id>', methods=('GET', 'POST'))
@normal_perm.require()
def done_api(stockout_id):
    order = Stockout.query.c_query.filter_by(id=stockout_id).with_for_update().first()
    action = StockoutAction()
    # 处理锁定的库存
    for alloc in Alloc.query.filter_by(stockout_id=order.id).with_for_update().all():
        # 已经分配但未拣的，归还原库位
        inv = alloc.lock_inv()
        qty_can = alloc.qty_alloc - alloc.qty_pick
        if inv is not None and qty_can:
            inv.qty_alloc = inv.qty_alloc - qty_can
            inv.qty_able  = inv.qty_able + qty_can
            inv.qty = inv.qty_alloc + inv.qty_able

            action.create_tran(alloc.stockout_line, qty_can, 'unalloc', location_code=alloc.location_code)
        # 不可再拣货
        alloc.qty_alloc = alloc.qty_alloc - qty_can
        # 更新订单行
        oline = alloc.stockout_line
        oline.qty_alloc = oline.qty_alloc - qty_can

    # 关闭订单
    order.state = 'done'
    order.finish()
    
    db.session.commit()

    return json_response({'status': 'success', 'msg': u'ok', 'data': order.as_dict})


# 取消单子；取消操作比较复杂，做成简单的, 创建状态才能取消, 否则先要取消分配; 已经发运或者关闭的单子不能取消分配, 和取消单子
# 取消分配后才能取消
@bp_stockout.route('/cancel/<stockout_id>', methods=('GET', 'POST'))
@normal_perm.require()
def cancel_api(stockout_id):
    order = Stockout.query.c_query.filter_by(id=stockout_id).with_for_update().first()
    if order.state != 'done' and order.state!='cancel':
        order.cancel()
        order.state = 'cancel'
        db.session.commit()

        return json_response({'status': 'success', 'msg': u'ok', 'data': order.as_dict})

    db.session.rollback()
    return json_response({'status': 'fail', 'msg': u'订单操作中，不能取消', 'data': order.as_dict})



# 自动整单分配， 如果不支持部分分配时，库存不足将分配失败
@bp_stockout.route('/alloc/<stockout_id>', methods=('GET', 'POST'))
@normal_perm.require()
def alloc_api(stockout_id):
    """
    自动分配订单; 必需全单分配完成
    post: withlock
        req:pass
        resp: {status: 'success', msg, data: {lineid, [{...}...]}} // alloc list

    获取订单行
    get resp:
        [{...}]
    """
    if request.method == 'POST':
        order = Stockout.query.c_query.filter_by(id=stockout_id).with_for_update().first()
        if order.state_alloc not in ('no', 'part'):
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': u'该订单已经分配过了!'})

        action = StockoutAction(order)
        finish, is_partalloc, line, alloc_dict = action.alloc(stockout_id, order=order)

        # 不允许部分分配, 未完成时回滚
        if not finish and not is_partalloc:
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': u'订单行的货品（%s %s）库存不足'%(line.sku, line.name)})        

        db.session.commit()
        c = 0
        for k, v in alloc_dict.items():
            if v:
                c += 1
            alloc_dict[k] = [a.as_dict for a in v]
        if c == 0:
            return json_response({'status': 'fail', 'msg': u'库存不足'})

        if finish:
            order.state = 'doing'
            order.state_alloc = 'done'
            db.session.commit()
        else:
            return json_response({'status': 'success', 'msg': u'部分分配成功', 'data': alloc_dict})

        return json_response({'status': 'success', 'msg': u'分配完成', 'data': alloc_dict})
    else:
        # 获取订单行
        order = Stockout.query.c_query.filter_by(id=stockout_id).first()
        lines = [line.as_dict for line in order.lines]
        for line in lines:
            line['qty_now'] = 0
        # fetch price
        if not order.price or order.sum_price!=order.price:
            order.price = order.sum_price
            db.session.commit()
        partner = Partner.query.c_query.filter_by(code=order.partner_code).first()
        return json_response({'lines':lines, 'order': order.as_dict, 'partner':partner.as_dict if partner else {}})

    return json_response({'status': 'success', 'msg': 'ok'})


# 自动分配行， 如果不支持部分分配时，库存不足将分配失败； 获取订单行已分配未拣货的明细
@bp_stockout.route('/alloc/<stockout_id>/line', methods=('GET', 'POST'))
@bp_stockout.route('/alloc/<stockout_id>/line/<line_id>', methods=('GET', 'POST'))
@normal_perm.require()
def alloc_line_api(stockout_id, line_id=None):
    """
    自动分配订单行：
    post req: withlock
        [line_id1, linedi2]

    获取订单行已经分配的明细, 未拣货的
    get req:
        [{..}...]
    """

    # 获取订单/订单行已分配的明细
    if request.method == 'GET':
        unpick = request.args.get('unpick', '0') == '1'
        subq = Alloc.query.filter(Alloc.company_code==g.company_code, Alloc.stockout_id==stockout_id)
        if unpick:
            subq =  subq.filter(Alloc.qty_alloc>Alloc.qty_pick)
        if line_id:
            subq = subq.filter(Alloc.stockout_line_id==line_id)

        # sort, 拣货单打印排序
        if unpick:
            if g.owner.print_rule == 'code_desc':
                print_rule = Location.code.desc()
            elif g.owner.print_rule == 'index_asc':
                print_rule = Location.index.asc()
            elif g.owner.print_rule == 'index_desc':
                print_rule = Location.index.desc()
            else:
                print_rule = Location.code.asc()
            subq = subq.filter(Location.code==Alloc.location_code, Location.company_code==g.company_code, \
                    Location.warehouse_code==g.warehouse_code).order_by(print_rule)

        allocs = subq.all()
        return json_response([a.as_dict for a in allocs])

    # 分配订单行
    elif request.method == 'POST':
        order = Stockout.query.filter_by(id=stockout_id, company_code=g.company_code).with_for_update().first()
        if order.state_alloc not in ('no', 'part'):
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': u'该订单已经分配过了!'})

        lines = request.json# [id1, id2...]
        action = StockoutAction(order)

        alloc_dict = {}

        for line_id in lines:
            is_enough, line, alloc_list = action.alloc_line(line_id)

            if not is_enough and not g.owner.is_partalloc:
                db.session.rollback()
                return json_response({'status': 'fail', 'msg': u'订单行的货品（%s %s）库存不足'%(line.sku, line.name)})

            alloc_dict[line_id] = alloc_list

        # 行还有没分配的qty时
        db.session.flush()
        if StockoutLine.query.filter_by(stockout_id=stockout_id).filter(StockoutLine.qty_alloc < StockoutLine.qty).count():
            order.state_alloc = 'part'
        else:
            order.state_alloc = 'done'
        order.state = 'doing'
        db.session.commit()
        for k, v in alloc_dict.items():
            alloc_dict[k] = [a.as_dict for a in v]
        return json_response({'status': 'success', 'msg': u'分配完成', 'data': alloc_dict})


# 指定库位分配，用于任何情况; 指定库位分配 
@bp_stockout.route('/alloc/<stockout_id>/line/specify', methods=('GET', 'POST'))
@normal_perm.require()
def alloc_line_specify_api(stockout_id):
    """
    指定库位分配
    post req: withlock
    {
        line_id:
            [{inv_id, qty}...]
        line_id:
            [{inv_id, qty}...]
    }

    post resp:
    {status, msg, data: {line_id: [{...}...]}} // alloc list
    """
    order = Stockout.query.filter_by(id=stockout_id, company_code=g.company_code).with_for_update().first()
    if order.state_alloc not in ('no', 'part'):
        db.session.rollback()
        return json_response({'status': 'fail', 'msg': u'该订单已经分配过了!'})

    lines = request.json# {line_id: [{inv_id, qty}...]}
    action = StockoutAction(order)

    alloc_dict = {}

    for line_id, invqty in lines.items():
        # print(line_id, invqty)
        # if invqty <= 0:
        #     continue
        is_enough, line, alloc_list, inv = action.alloc_line_by_inv(order, line_id, [iq for iq in invqty if iq['qty'] > 0]) # 去除数量小于０等于０的
        if not is_enough:
            db.session.rollback()
            if not inv:
                return json_response({'status': 'fail', 'msg': u'不能超量分配'})
            return json_response({'status': 'fail', 'msg': u'订单行的货品（%s %s）在库位（%s）库存不足'%(line.sku, line.name, inv.location_code)})

        alloc_dict[line_id] = alloc_list
        order.state = 'doing'

    # 行还有没分配的qty时
    db.session.flush()
    if StockoutLine.query.filter_by(stockout_id=stockout_id).filter(StockoutLine.qty_alloc < StockoutLine.qty).count():
        order.state_alloc = 'part'
    else:
        order.state_alloc = 'done'
    order.state = 'doing'
    db.session.commit()
    for k, v in alloc_dict.items():
        alloc_dict[k] = [a.as_dict for a in v]
    return json_response({'status': 'success', 'msg': u'分配完成', 'data': alloc_dict})


# 通过库存行获取符合的库存，用于指定库位分配
@bp_stockout.route('/alloc/<stockout_id>/line/<line_id>/inv', methods=('GET', 'POST'))
@normal_perm.require()
def alloc_line_inv(stockout_id, line_id):
    order = Stockout.query.filter_by(id=stockout_id, company_code=g.company_code).first()
    if order.state_alloc not in ('no', 'part'):
        return json_response({'status': 'fail', 'msg': u'该订单已经分配过了!'})

    line = StockoutLine.query.filter_by(stockout_id=stockout_id, id=line_id).first()
    invaction = InvAction()
    is_enough, choice = invaction.get_inv_by_stockout_line(line, recommend=True, order=order)

    return json_response([inv.as_dict for inv in choice])





# 快速拣货，已经分配完成的单子才能做快速拣货
@bp_stockout.route('/quick_pick', methods=('GET', 'POST'))
@bp_stockout.route('/quick_pick/<stockout_id>', methods=('GET', 'POST'))
@normal_perm.require()
def quick_pick_api(stockout_id=None):
    """
    post req: withlock
    {
        w_user_code // 拣货人
        w_user_name
        r_user_code　//　领料人
        r_user_name
    }
    """
    if stockout_id:
        # 手动点按钮快速拣货
        order = Stockout.query.filter_by(id=stockout_id, company_code=g.company_code).with_for_update().first()
    else:
        # 扫单快速拣货
        order = Stockout.query.t_query.filter_by(erp_order_code=request.json['erp_order_code']) \
                .with_for_update().first()

    rjson = request.json or {}

    w_user_code = rjson.pop('w_user_code', None)
    w_user_name = rjson.pop('w_user_name', None)

    r_user_code = rjson.pop('r_user_code', None)
    r_user_name = rjson.pop('r_user_name', None)

    if order.state_alloc == 'done' and order.state_pick in ('no', 'part') and order.state not in ('done', 'cancel'):
        # 拣货即移动到发货区库位（PICK）
        # 获取所有alloc行，对alloc进行移库操作
        action = StockoutAction()
        for alloc in Alloc.query.filter_by(stockout_id=order.id).with_for_update().all():
            if alloc.qty_alloc - alloc.qty_pick <= 0:
                continue
            # 移库到发货区
            qty_can = alloc.qty_alloc - alloc.qty_pick
            ok = InvAction.move_qty_alloc(alloc.inv_id, qty_can, alloc.warehouse_code, 'PICK', 'ALLOC_%s'%alloc.id, refid=order.id)
            if ok:
                # 拣货复核数量
                alloc.qty_pick += qty_can
                # 订单行数量
                alloc.stockout_line.qty_pick += qty_can

                # 创建订单行流水
                action.create_tran(alloc.stockout_line, qty_can, 'pick', w_user_code=w_user_code, w_user_name=w_user_name, location_code=alloc.location_code)
                action.create_tran(alloc.stockout_line, qty_can, 'receive', w_user_code=r_user_code, w_user_name=r_user_name, location_code=alloc.location_code)
            else:
                db.session.rollback()
                return json_response({'status': 'fail', 'msg': u'快速拣货失败', 'data': order.as_dict})

        # 修改订单状态
        order.state_pick = 'done'
        order.finish()
        db.session.commit()

        return json_response({'status': 'success', 'msg': u'ok', 'data': order.as_dict})

    return json_response({'status': 'fail', 'msg': u'订单在未分配完成状态（alloc:%s, pick:%s, order:%s）下，不能快速拣货'%(order.state_alloc, order.state_pick, order.state), 'data': order.as_dict})


# 部分拣货, 只捡已经分配的行, 或指定的行; 操作类似于check_pick; 但不扫码, 不扫rfid
@bp_stockout.route('/part_pick/<stockout_id>', methods=('GET', 'POST'))
@bp_stockout.route('/part_pick/<stockout_id>/line/<line_id>', methods=('GET', 'POST'))
@normal_perm.require()
def part_pick_api(stockout_id=None, line_id=None):
    """
    post req: withlock
    {
        lines: [
            {id, qty} // stockout line id, pick number
        ]
        w_user_code // 拣货人
        w_user_name
        r_user_code　//　领料人
        r_user_name
    """
    order = Stockout.query.t_query.filter_by(id=stockout_id, company_code=g.company_code).with_for_update().first()

    rjson = request.json or {}
    
    w_user_code = rjson.pop('w_user_code', None)
    w_user_name = rjson.pop('w_user_name', None)

    r_user_code = rjson.pop('r_user_code', None)
    r_user_name = rjson.pop('r_user_name', None)

    if order.state_alloc in ('part', 'done') and order.state_pick in ('no', 'part') and order.state not in ('done', 'cancel'):
        lines = rjson.get('lines', [])
        # 没有传递行, 则拣指定行的可拣货数量/所有分配的行
        if not lines:
            if line_id:
                oline = StockoutLine.query.t_query.filter_by(stockout_id=order.id, id=line_id).first()
                qty = oline.qty_alloc - oline.qty_pick
                lines = [{'id': oline.id, 'qty': qty}]
            else:
                lines = [{'id': oline.id, 'qty': oline.qty_alloc-oline.qty_pick} for oline in order.lines if oline.qty_alloc > oline.qty_pick]

        action = StockoutAction()

        for line in lines:
            qty = int(line.get('qty', 0))
            # 没有传递数量, 则拣订单行分配数量的可拣货数量
            if not qty:
                oline = StockoutLine.query.t_query.filter_by(stockout_id=order.id, id=line['id']).first()
                qty = oline.qty_alloc - oline.qty_pick
            if qty <= 0:
                continue
            # 查询复核的分配数据行， 符合分配行可能不止一行
            subq = Alloc.query.filter_by(stockout_id=order.id, stockout_line_id=line['id'])
            allocs = subq.filter(Alloc.qty_alloc > Alloc.qty_pick).with_for_update().all()

            if not allocs or sum([a.qty_alloc-a.qty_pick for a in allocs]) < qty:
                db.session.rollback()
                return json_response({'status': 'fail', 'msg': u'这个订单, 该货品分配数量没有这么多, 不能多捡', 'data': order.as_dict})

            # 将捡货的数量均摊到还有可捡数量的分配行里
            inv_id = None
            qty_pick = 0
            for alloc in allocs:
                inv_id = alloc.inv_id
                is_break = False
                if alloc.qty_alloc - alloc.qty_pick >= (qty - qty_pick):
                    qty_can = qty - qty_pick
                    alloc.qty_pick += qty_can
                    alloc.stockout_line.qty_pick += qty_can
                    qty_pick += qty_can
                    is_break = True
                else:
                    qty_can = alloc.qty_alloc - alloc.qty_pick
                    alloc.qty_pick += qty_can
                    alloc.stockout_line.qty_pick += qty_can
                    qty_pick += qty_can

                # 移库到发货区；分配的东西，移动到发货区，就不再带有容器了; 容器号指定为分配的id，作为关联标识
                # 拣货即移动到发货区库位（PICK）
                ok = InvAction.move_qty_alloc(alloc.inv_id, qty_can, alloc.warehouse_code, 'PICK', 'ALLOC_%s'%alloc.id, refid=order.id)
                # 创建订单行流水
                if ok:
                    # action.create_tran(alloc.stockout_line, qty_can, 'pick')
                    action.create_tran(alloc.stockout_line, qty_can, 'pick', w_user_code=w_user_code, w_user_name=w_user_name, location_code=alloc.location_code)
                    action.create_tran(alloc.stockout_line, qty_can, 'receive', w_user_code=r_user_code, w_user_name=r_user_name, location_code=alloc.location_code)
                else:
                    db.session.rollback()
                    return json_response({'status': 'fail', 'msg': u'这个订单, 该货品分配数量没有这么多, 不能多捡', 'data': order.as_dict})
                if is_break:
                    break

        # 修改订单状态
        db.session.flush()
        if StockoutLine.query.filter_by(stockout_id=stockout_id).filter(StockoutLine.qty_pick < StockoutLine.qty).count():
            order.state_pick = 'part'
        else:
            order.state_pick = 'done'
        order.finish()
        db.session.commit()

        return json_response({'status': 'success', 'msg': u'ok', 'data': order.as_dict})

    return json_response({'status': 'fail', 'msg': u'订单在未分配或捡货完成状态（alloc:%s, pick: %s, order:%s）下，不能拣货'%(order.state_alloc, order.state_pick , order.state), 'data': order.as_dict})


# 查询某个条码需要复核的数量
@bp_stockout.route('/check_pick/query/<stockout_id>/line', methods=('POST',))
@normal_perm.require()
def check_pick_query_api(stockout_id=None):
    """
    post req:
    {
        barcode
    }
    reps:
    {
        qty
    }
    """
    # 查询复核的分配数据行， 符合分配行可能不止一行
    subq = Alloc.query.t_query.filter_by(stockout_id=stockout_id, barcode=request.json['barcode'])
    allocs = subq.filter(Alloc.qty_alloc > Alloc.qty_pick).all()

    line = StockoutLine.query.t_query.filter_by(stockout_id=stockout_id, barcode=request.json['barcode']).first()

    real_qty = sum([a.qty_alloc-a.qty_pick for a in allocs]) if allocs else 0
    return json_response({'status': 'success', 'data':{'qty': real_qty, 'name': line.name if line else '', }})#'location':line.location_code if line else ''}})


# 复核拣货，分配或者部分分配的单子才能复核
@bp_stockout.route('/check_pick', methods=('GET', 'POST'))
@bp_stockout.route('/check_pick/<stockout_id>', methods=('GET', 'POST'))
@bp_stockout.route('/check_pick/rfid/<stockout_id>', methods=('GET', 'POST'))
@normal_perm.require()
def check_pick_api(stockout_id=None):
    """
    扫单号，扫条码，扫库位，多次扫后一次性提交或者每次提交
    post req: withlock
    {
        erp_order_code
        lines: [
            {barcode, location:None, qty, rfid_list}
        ]
        w_user_code // 拣货人
        w_user_name
        r_user_code　//　领料人
        r_user_name
    """
    if stockout_id:
        # 手动点按钮快速拣货
        order = Stockout.query.filter_by(id=stockout_id, company_code=g.company_code).with_for_update().first()
    else:
        # 扫单快速拣货
        order = Stockout.query.t_query.filter_by(erp_order_code=request.json['erp_order_code']) \
                .with_for_update().first()
        stockout_id = order.id

    rjson = request.json
    
    w_user_code = rjson.pop('w_user_code', None)
    w_user_name = rjson.pop('w_user_name', None)

    r_user_code = rjson.pop('r_user_code', None) or order.w_user_code or ''
    r_user_name = rjson.pop('r_user_name', None) or order.w_user_name or ''

    if order.state_alloc in ('part', 'done') and order.state_pick in ('no', 'part') and order.state not in ('done', 'cancel'):
        lines = request.json['lines']
        action = StockoutAction()
        for line in lines:
            qty = int(line['qty'])
            if qty <= 0:
                continue

            rfid_list = line.pop('rfid_list', [])

            barcode = line.get('barcode', None)
            if not barcode and rfid_list and len(rfid_list)==1:
                invrfid = InvRfid.query.t_query.filter_by(rfid=rfid_list[0]).first()
                line['barcode'] = invrfid.barcode
            # 查询复核的分配数据行， 符合分配行可能不止一行
            subq = Alloc.query.filter_by(stockout_id=order.id, barcode=line['barcode'])
            if line.get('location', ''):
                subq = subq.filter_by(location_code=line['location'])
            if line.get('lpn', ''):
                subq = subq.filter_by(lpn=line['lpn'])
            allocs = subq.filter(Alloc.qty_alloc > Alloc.qty_pick).with_for_update().all()

            if not allocs or sum([a.qty_alloc-a.qty_pick for a in allocs]) < qty:
                db.session.rollback()
                return json_response({'status': 'fail', 'msg': u'这个订单, 该货品分配数量没有这么多, 不能多捡', 'data': order.as_dict})

            # rfid / 二维码出库
            rfid_invs = []
            if rfid_list:
                stockout_line = StockoutLine.query.filter_by(stockout_id=stockout_id, barcode=line['barcode']).first()
                for rfid in rfid_list:
                    invrfid = InvRfid.query.t_query.filter(InvRfid.rfid==rfid).with_for_update().first()
                    # create invrfid
                    if invrfid is None:
                        invrfid = update_model_with_fields(InvRfid, stockout_line, common_poplist+['qty'], qty=0, rfid=rfid)
                        db.session.add(invrfid)
                    # trans
                    if invrfid is not None:
                        if invrfid.barcode != line['barcode']:
                            db.session.rollback()
                            return json_response({'status': 'fail', 'msg': u'唯一码与货品不匹配', 'data': order.as_dict})
                        rfid_invs.append(invrfid)
                        # 是否判断 rfid==1 ?
                        invrfid.qty = 0
                        invrfid.stockout_order_code = order.order_code
                        invrfid.stockout_date = db.func.current_timestamp()
                        # 系统操作人信息
                        invrfid.out_user_code = g.user.code
                        invrfid.out_user_name = g.user.name
                        # 仓库 领料人信息
                        invrfid.out_w_user_code = r_user_code
                        invrfid.out_w_user_name = r_user_name
                        # --- new invrfid trans ---
                        tran = update_model_with_fields(InvRfidTrans, invrfid, common_poplist, 
                                user_code=g.user.code, user_name=g.user.name, w_user_code=r_user_code, w_user_name=r_user_name,
                                xtype='out', order_type=order.order_type, order_code=order.order_code)
                        db.session.add(tran)


            # 将捡货的数量均摊到还有可捡数量的分配行里
            inv_id = None
            qty_pick = 0
            for alloc in allocs:
                inv_id = alloc.inv_id
                is_break = False
                if alloc.qty_alloc - alloc.qty_pick >= (qty - qty_pick):
                    qty_can = qty - qty_pick
                    alloc.qty_pick += qty_can
                    alloc.stockout_line.qty_pick += qty_can
                    qty_pick += qty_can
                    is_break = True
                else:
                    qty_can = alloc.qty_alloc - alloc.qty_pick
                    alloc.qty_pick += qty_can
                    alloc.stockout_line.qty_pick += qty_can
                    qty_pick += qty_can

                # 移库到发货区；分配的东西，移动到发货区，就不再带有容器了; 容器号指定为分配的id，作为关联标识
                # 拣货即移动到发货区库位（PICK）
                ok = InvAction.move_qty_alloc(alloc.inv_id, qty_can, alloc.warehouse_code, 'PICK', 'ALLOC_%s'%alloc.id, refid=order.id)
                # 创建订单行流水
                if ok:
                    # action.create_tran(alloc.stockout_line, qty_can, 'pick')
                    action.create_tran(alloc.stockout_line, qty_can, 'pick', w_user_code=w_user_code, w_user_name=w_user_name, location_code=alloc.location_code)
                    action.create_tran(alloc.stockout_line, qty_can, 'receive', w_user_code=r_user_code, w_user_name=r_user_name, location_code=alloc.location_code)
                else:
                    db.session.rollback()
                    return json_response({'status': 'fail', 'msg': u'这个订单, 该货品分配数量没有这么多, 不能多捡', 'data': order.as_dict})
                if is_break:
                    break

            # 随便赋予一个inv_id
            for invrfid in rfid_invs:
                invrfid.inv_id = inv_id

        # 修改订单状态
        db.session.flush()
        if StockoutLine.query.filter_by(stockout_id=stockout_id).filter(StockoutLine.qty_pick < StockoutLine.qty).count():
            order.state_pick = 'part'
        else:
            order.state_pick = 'done'
        order.finish()
        db.session.commit()

        return json_response({'status': 'success', 'msg': u'ok', 'data': order.as_dict})

    return json_response({'status': 'fail', 'msg': u'订单在未分配或捡货完成状态（alloc:%s, pick: %s, order:%s）下，不能拣货'%(order.state_alloc, order.state_pick , order.state), 'data': order.as_dict})


# 取消分配： 
#   只能取消某个订单行的所有分配，不能指定某个具体分配
#   部分分配，全部分配，允许取消；归还原库位
#   部分拣货，全部拣货，允许取消分配，但之后要重新上架（从pick库位上架到其它库位）；比如在PC取消后，已经捡到PICK库位的东西，要重新上架到正常库位（stage）
#   修正取消分配时, 已捡货品上架到stage, 未捡货品归回原库位
#           ====>这里修改为，拣货的要全部重新入库，生成退库入库单
#   订单行已经发运，部分发运的，不允许取消
@bp_stockout.route('/cancel_alloc/<stockout_id>', methods=('GET', 'POST'))
@bp_stockout.route('/cancel_alloc/<stockout_id>/line/<line_id>', methods=('GET', 'POST'))
@normal_perm.require()
def cancel_alloc_api(stockout_id=None, line_id=None):
    """
    post req: withlock
    """
    order = Stockout.query.filter_by(id=stockout_id, company_code=g.company_code).with_for_update().first()

    action = StockoutAction()
    ok, msg = action.alloc_cancel(order=order)
    if ok:
        db.session.commit()
        return json_response({'status': 'success', 'msg': u'ok', 'data': order.as_dict})

    db.session.rollback()
    return json_response({'status': 'fail', 'msg':msg, 'data':order.as_dict})


# 发运
#   POST 发运所有已经拣货的分配
#   GET 查询所有可发运的库存
@bp_stockout.route('/ship', methods=('GET', 'POST'))
@bp_stockout.route('/ship/<stockout_id>', methods=('GET', 'POST'))
@normal_perm.require()
def ship_api(stockout_id=None):
    """
    # 拣货的货品都发运掉
    post req: withlock

    # 返回所有可发运的库存
    GET req:

    """
    if stockout_id:
        # 手动点按钮快速拣货
        order = Stockout.query.filter_by(id=stockout_id, company_code=g.company_code).first()
    elif request.args.get('erp_order_code', ''):
        # 查询是否存在可发运的单子
        order = Stockout.query.t_query.filter_by(erp_order_code=request.args['erp_order_code']).first()
    else:
        # 扫单快速拣货
        order = Stockout.query.t_query.filter_by(erp_order_code=request.json['erp_order_code']).first()

    if request.method == 'GET':
        if not order:
            return json_response([])
        invs = Inv.query.filter(Inv.location_code=='PICK', Inv.company_code==g.company_code, Inv.refid==order.id) \
                .filter(Inv.qty_able > 0).all()

        return json_response([inv.as_dict for inv in invs])

    elif request.method == 'POST':
        action = StockoutAction()
        for alloc in Alloc.query.filter(Alloc.qty_pick > 0, Alloc.stockout_id==order.id).with_for_update().all():
            inv = Inv.query.filter(Inv.location_code=='PICK', Inv.lpn=='ALLOC_%s'%alloc.id).with_for_update().first()
            qty_can = inv.qty_able
            # update alloc
            alloc.qty_ship += qty_can
            # update stockout_line
            alloc.stockout_line.qty_ship += qty_can
            # clear inv
            inv.qty_able = 0
            inv.qty = 0

            # create trans
            action.create_tran(alloc.stockout_line, qty_can, 'ship', location_code=alloc.location_code)

        # order state
        db.session.flush()
        if StockoutLine.query.filter_by(stockout_id=order.id).filter(StockoutLine.qty_ship < StockoutLine.qty).count():
            order.state_ship = 'part'
        else:
            order.state_ship = 'done'
            # 关闭订单
            order.state = 'done'

        order.finish()
        db.session.commit()
        return json_response({'status': 'success', 'msg': u'ok', 'data': order.as_dict})


# 订单流水
@bp_stockout.route('/trans/<stockout_id>', methods=('GET',))
@normal_perm.require()
def trans_api(stockout_id=None):
    """
    # 返回所有订单流水
    GET req:

    """
    order = Stockout.query.filter_by(id=stockout_id, company_code=g.company_code).first()
    query = StockoutLineTrans.query.filter_by(stockout_id=order.id)

    pagin = gen_query(request.args.get('q', None), query, StockoutLineTrans, db=db, per_page=settings.PER_PAGE, get_objects=True)
    # 
    objects = []
    for o in pagin.items:
        obj = o.as_dict
        obj['order_line'] = o.stockout_line.as_dict
        objects.append(obj)
    ret =  {
          "num_results": pagin.total,
          "total_pages": pagin.pages,
          "page": pagin.page,
          "per_page": pagin.per_page,
          "objects": objects,
        }
    return json_response(ret, indent=4)


# 包裹信息, 不含行
@bp_stockout.route('/stockout/box/<order_id>', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def stockout_box_api(order_id):
    """
    包裹信息, 不含行
    post req: 
        {}
    """
    if request.method == 'PUT':
        order = Stockout.query.t_query.filter_by(id=order_id).first()
        for box in request.json['box_lines']:
            if not box.get('id', None):
                box = Box(company_code=order.company_code, owner_code=order.owner_code, warehouse_code=order.warehouse_code, order_code=order.order_code, **box)
                box.sale_order_code = order.sale_order_code
                db.session.add(box)

        db.session.commit()

        return json_response({'status': 'success', 'msg': u'ok'})


    order = Stockout.query.filter_by(id=order_id, company_code=g.company_code).first()
    if order.sale_order_code:
        pass

    else:
        out_rfid_list = []
        out_rfid_skulist = []
        out_rfid_weight = 0
        out_rfid_amount = 0
        out_old_amount = 0
        
        def get_amount(rd, rfid_price_type='box_weight'):
            if rfid_price_type == 'box_weight':
                return rd['price']*(rd['weight'] if rd['weight'] else 1) # weight or qty=1
            elif rfid_price_type == 'inner_qty_price':
                return rd['price']*rd['qty_inner']
            else:
                return rd['price']
        # 获取码单信息
        lines = order.lines
        price_dict = {l.sku:l.price for l in lines}
        weight_dict = {l.sku:0 for l in lines}
        boxs_dict = {l.sku:0 for l in lines}
        qty_dict = {l.sku:0 for l in lines}
        rfid_price_type = g.owner.rfid_price_type
        idx = 0
        for rfid in order.rfid_list():
            rd = rfid.as_dict
            rd['price'] = price_dict.get(rfid.sku, 0)
            rd['amount'] = get_amount(rd, rfid_price_type)
            out_rfid_weight += (float(rd['weight'] or 0) or 0)
            if rd['sku'] in weight_dict:
                weight_dict[rd['sku']] += (float(rd['weight'] or 0) or 0)
                boxs_dict[rd['sku']] += 1
                qty_dict[rd['sku']] += rd['qty_inner']
            out_rfid_amount += (float(rd['amount'] or 0) or 0)
            idx += 1
            rd['idx'] = idx
            out_rfid_list.append(rd)

    # sku 合计
    for sku, price in price_dict.items():
        d = DictNone()
        d.sku = sku
        d.weight = weight_dict[sku]
        d.boxs = boxs_dict[sku]
        d.price = price
        d.qty_inner = qty_dict[sku]
        d.amount = float(d.price)*(d.weight if d.weight else d.qty_inner) # if not weight, use qty=boxs
        if d.boxs:
            out_rfid_skulist.append(d)

    # 获取以前的货款, 不包括本单
    out_old_amount = 0
    m = Money.query.with_entities(func.sum(Money.amount).label('amount'), func.sum(Money.real).label('real')) \
            .t_query.filter(Money.come=='income', Money.partner_code==order.partner_code, Money.state!='cancel', Money.code!=order.order_code).first()
    if m:
        out_old_amount = float((m.amount or 0) - (m.real or 0))

    _1, _2, _3 = split_list(out_rfid_list, 3)
    return json_response({'out_rfid_list': out_rfid_list, 
                'out_rfid_weight': out_rfid_weight, 'out_rfid_amount': out_rfid_amount, 
                'out_rfid_skulist': out_rfid_skulist, 'out_old_amount':out_old_amount,
                'out_rfid_list_left':  _1, 'out_rfid_list_mid': _2, 'out_rfid_list_right': _3,}, indent=4)

# 包裹信息, 有明细行
@bp_stockout.route('/stockout/box/pack/<order_id>', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def stockout_box_pack_api(order_id):
    """
    包裹信息, 有明细行
    post req: 
        {
            lines: [
                {sku, qty_pack}
            ]
        }
    """
    box = None
    if request.method == 'POST':
        order = Stockout.query.t_query.filter_by(id=order_id).with_for_update().first()
        lines = request.json['lines']

        if len(lines) > 0:
            box = Box(company_code=order.company_code, owner_code=order.owner_code, warehouse_code=order.warehouse_code, order_code=order.order_code)
            box.sale_order_code = order.sale_order_code
            # 包裹序号+1
            order.box_seq += 1
            box.box_code = 'BOX%s-%s'%(order.box_seq, get_hash_key()[0])

            db.session.add(box)

            for line in lines:
                id = line.pop('id', None)
                stockout_line = StockoutLine.query.t_query.filter_by(stockout_id=order.id, id=id).first()
                qty = int(line.get('qty_pack', 0) or 0)
                if qty:
                    bline = update_model_with_fields(BoxLine, box, common_poplist, qty=qty, **json2mdict_pop(BoxLine, line, ['qty']))
                    bline.order = box
                    db.session.add(bline)
                    # 更新发运数
                    stockout_line.qty_ship += qty
                    if stockout_line.qty_ship  > stockout_line.qty_pick:
                        db.session.rollback()
                        return json_response({'status': 'fail', 'msg': u'打包的数量不能大于`未打包数`!'})

            order.state_ship = 'part'
            db.session.flush()
            if order.state_pick == 'done' and order.lines.filter(StockoutLine.qty_pick > StockoutLine.qty_ship).count() == 0:
                order.state_ship = 'done'
                order.state = 'done'
                order.finish()

            # 获取电子面单
            if g.owner.express_on == 'on':
                db.session.flush()

                action = WaybillAction()
                ok, msg = action.do(order, box, multi=order.box_seq>1)
                if not ok:
                    print(msg)
                    db.session.commit()
                    return json_response({'status': 'success', 'msg': msg, 'waybill_state': 'fail'})

            db.session.commit()
    return json_response({'status': 'success', 'msg': u'ok', 'box': box.as_dict if box else {}, 'waybill_state': 'success'})




# 包裹--手动获取面单
@bp_stockout.route('/stockout/box/waybill/<order_id>/<box_id>', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def stockout_box_waybill_api(order_id, box_id):
    order = Stockout.query.t_query.filter_by(id=order_id).with_for_update().first()
    box = Box.query.t_query.filter_by(order_code=order.order_code, id=box_id).with_for_update().first()

    action = WaybillAction()
    ok, msg = action.do(order, box, multi=order.box_seq>1)
    if not ok:
        print(msg)
        db.session.rollback()
        return json_response({'status': 'fail', 'msg': msg})

    db.session.commit()
    return json_response({'status': 'success', 'msg': msg})


# 包裹--手动获取模板
@bp_stockout.route('/stockout/box/tpl/<box_id>', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def stockout_box_tpl_api(box_id):
    box = Box.query.t_query.filter_by(id=box_id).first()
    return box.tpl


# 反单
@bp_stockout.route('/reverse/<order_id>', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def stockout_reverse_api(order_id):
    from blueprints.stockin.action import StockinAction
    stockout = Stockout.query.c_query.filter_by(id=order_id).with_for_update().first()

    action = StockinAction()
    ok, msg, order = action.fan_order(stockout)
    db.session.commit()

    if ok:
        return json_response({'status': 'success', 'msg':msg, 'order_code': order.order_code})

    return json_response({'status': 'fail', 'msg':msg, 'order_code': ''})
