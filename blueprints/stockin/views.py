#coding=utf8

from sqlalchemy import or_, and_
from flask import Blueprint, g, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from extensions.database import db
from extensions.permissions import admin_perm, manager_perm, normal_perm

from models.stockin import Stockin, StockinLine, StockinLineTrans
from models.inv import Inv, InvRfid
from models.auth import Partner
from models.warehouse import Location
from blueprints.stockin.action import StockinAction, InvAction

from utils.flask_tools import json_response
from utils.functions import gen_query, DictNone
import settings

bp_stockin = Blueprint("stockin", __name__)





# 获取订单列表， 创建订单
@bp_stockin.route('/stockin', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def stockin_api():
    """
    创建订单
    post req: 
    [{'erp_order_code': 'erp3', 'warehouse_code': 'test', 'owner_code': 'test',
        'lines': [
            {'sku': 'sku1', 'barcode': 'sku1', 'qty': 5, 'name':'name1'}, 
            {'sku': 'sku2', 'barcode': 'sku2', 'qty': 1, 'name':'name2'}, 
            {'sku': 'sku3', 'barcode': 'sku3', 'qty': 2, 'name':'name3'}, 
        ]
    }]

    查询订单列表
    get req:
    q={filters:[{}], order_by, single, limit, offset, group_by}
    """
    if request.method == 'GET':
        # q = {filters:[{}], order_by, single, limit, offset, group_by}
        query = Stockin.query.t_query
        res = gen_query(request.args.get('q', None), query, Stockin, db=db, per_page=settings.PER_PAGE)
        return json_response(res, indent=4)

    orders = []
    if request.method == 'POST':
        data = request.json
        for d in data:
            lines = d.pop('lines', [])
            exist, order = StockinAction.create_stockin(d, g)
            if not exist:
                # order.JSON = d
                db.session.add(order)
                # lines
                for ld in lines:
                    if float(ld.get('qty', 0)) <= 0:
                        continue
                    StockinAction.create_stockin_line(ld, order)
            orders.append(order)

        db.session.commit()

    return json_response([order.as_dict for order in orders])

# 获取订单
@bp_stockin.route('/stockin/one/<order_id>', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def stockin_one_api(order_id):
    """
    查询订单
    get req:
    """
    if request.method == 'GET':
        order = Stockin.query.t_query.filter(or_(Stockin.id==order_id, Stockin.order_code==order_id)).first()
        order_data = order.as_dict

        lines_data = [line.as_dict for line in order.lines]
        partner = Partner.query.c_query.filter_by(code=order.partner_code).first()
        partner_data = partner.as_dict if partner else {}

        pay_state = u'未付款'
        if order.purchase_order_code:
            Money = db.M('Money')
            m = Money.query.o_query.filter_by(code=order.purchase_order_code, come='outcome', xtype='purchase').filter(Money.state!='cancel').first()
            if m is not None:
                if m.state == 'doing':
                    pay_state = '部分付款'
                elif m.state in ('done', 'partdone'):
                    pay_state = '已付款'
            else:
                # stockin 的自定义付款字段
                pass

        return json_response({'order': order_data, 'lines': lines_data, 'partner': partner_data, 'pay_state': pay_state}, indent=4)

    if request.method == 'PUT':
        # update Stockin
        order = Stockin.query.t_query.filter(or_(Stockin.id==order_id, Stockin.order_code==order_id)).with_for_update().first()
        if order.state != 'create':
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': u'order state is not `create`',}, indent=4)
        order_id = order.id
        order.partner_code = request.json['partner_code'] or order.partner_code
        order.partner_name = request.json.get('partner_name', order.partner_name)
        partner = Partner.query.c_query.filter_by(code=order.partner_code).first()
        if partner:
            order.partner_id = partner.id
            
        order.xtype = request.json['xtype'] or order.xtype
        for line in request.json['lines']:
            if not line.get('id',None):
                if int(line.get('qty', 0)) <= 0:
                        continue
                StockinAction.create_stockin_line(line, order)
            elif line['qty'] != '' and line.get('id',None):
                pl = StockinLine.query.filter_by(id=line['id'], stockin_id=order_id).with_for_update().first()
                pl.qty = line['qty']
                pl.price = line['price'] or pl.price
                pl.supplier_code = line['supplier_code'] or ''
                pl.spec = line['spec'] or ''
                pl.location_code = line.get('location_code', pl.location_code)

        db.session.commit()
        return json_response({'status': 'success', 'msg': u'ok',}, indent=4) 

    return ''

# 更新订单信息
@bp_stockin.route('/stockin/info', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def stockin_info_api():
    """
    更新订单头信息
    post req: 
        {}
    """
    if request.method == 'POST':
        data = request.json
        order = Stockin.query.t_query.filter_by(id=data['id']).first()
        order.sender_info = data['sender_info']
        order.receiver_info = data['receiver_info']
        order.date_planned = data['date_planned'][:10] if data.get('date_planned', '') else None
        order.remark = data['remark']

        db.session.commit()

    return json_response({'status': 'success', 'msg': u'ok'})

# 获取订单行/ 删除
@bp_stockin.route('/<int:stockin_id>/line', methods=('POST', 'DELETE'))
@bp_stockin.route('/<int:stockin_id>/line/<line_id>', methods=('POST', 'DELETE'))
@normal_perm.require()
def stockin_line_api(stockin_id, line_id=None):
    """
    获取订单行
    POST req:
    {barcode}
    resp:
    {status: , {line...}}
    """
    arg = request.json
    if request.method == 'POST':
        subq = StockinLine.query.t_query.filter_by(stockin_id=stockin_id)
        barcode = arg.get('barcode', '')
        if barcode:
            subq = subq.filter_by(barcode=barcode)
        line = subq.first()
        if line is None:
            return json_response({'status': 'fail', 'msg': u'没找到有该货品(%s)的订单行'%barcode})

        return json_response({'status': 'success', 'msg': u'ok', 'data':line.as_dict}, indent=4)

    if request.method == 'DELETE':
        stockin = Stockin.query.t_query.filter_by(id=stockin_id).with_for_update().first()
        if stockin.state == 'create':
            StockinLine.query.t_query.filter_by(id=line_id, stockin_id=stockin_id).delete()
            db.session.commit()
            return json_response({'status': 'success', 'msg': u'ok',}, indent=4) 
        else:
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': u'order state is not `create`',}, indent=4)

    return json_response({})

# 获取订单行的推荐库位
@bp_stockin.route('/<int:stockin_id>/autolocation', methods=('POST', 'DELETE'))
@bp_stockin.route('/<int:stockin_id>/autolocation/lines', methods=('POST', 'DELETE'))
@normal_perm.require()
def stockin_autolocation_api(stockin_id):
    stockin = Stockin.query.t_query.filter_by(id=stockin_id).with_for_update().first()
    action  = StockinAction()
    loc_dict = {}
    excludes = []
    ok = True
    for line in stockin.lines:
        ok, loc = action.auto_location(line, only_one=True, excludes=excludes if ok else [], order=stockin)
        loc_dict[line.id] = loc
        excludes.append(loc)

    company_id = g.user.company.id
    loc_images = {}
    for loc in Location.query.w_query.filter(Location.code.in_([v for k, v in loc_dict.items()])).all():
        loc_images[loc.code] = loc.get_barcode(str(company_id))

    return json_response({'status': 'success', 'loc_dict':loc_dict, 'loc_images':loc_images})


# 获取入库单流水
@bp_stockin.route('/trans/<stockin_id>', methods=('GET',))
@bp_stockin.route('/trans/<stockin_id>/line/<stockin_line_id>', methods=('GET',))
@normal_perm.require()
def trans_api(stockin_id, stockin_line_id=None):
    """
    查询入库单流水列表
    get req:
    q={filters:[{}], order_by, single, limit, offset, group_by}
    """
    if request.method == 'GET':
        # q = {filters:[{}], order_by, single, limit, offset, group_by}
        query = StockinLineTrans.query.filter_by(stockin_id=stockin_id)
        if stockin_line_id:
            query = query.filter_by(stockin_line_id=stockin_line_id)
        pagin = gen_query(request.args.get('q', None), query, StockinLineTrans, db=db, per_page=settings.PER_PAGE, get_objects=True)
        # 
        objects = []
        for o in pagin.items:
            obj = o.as_dict
            if not o.sku:
                inv = o.inv
                if inv:
                    obj['sku'] = inv.sku
                    obj['barcode'] = inv.barcode
                    obj['name'] = inv.name
            objects.append(obj)
        ret =  {
              "num_results": pagin.total,
              "total_pages": pagin.pages,
              "page": pagin.page,
              "per_page": pagin.per_page,
              "objects": objects,
            }
        return json_response(ret, indent=4)


# 入库， 快捷入库，直接收取到库存
@bp_stockin.route('/putin/<stockin_id>', methods=('GET', 'POST'))
@normal_perm.require()
def putin_api(stockin_id):
    """
    订单行入库
    post req: withlock
    {
        lines: [{line_id, qty, location, lpn=''}...]
        w_user_code,
        w_user_name
    }
    
    查询订单行
    get

    """
    if request.method == 'POST':
        order = Stockin.query.t_query.filter_by(id=stockin_id).with_for_update().first()
        if order.state in ('done', 'cancel'):
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': u'订单处于不可操作状态（已完成或已取消）'})
        data = request.json.pop('lines', [])# [{line_id, qty, location, lpn=''}...]
        w_user_code = request.json.pop('w_user_code', None)
        w_user_name = request.json.pop('w_user_name', None)

        action = StockinAction(order)
        is_overcharge = g.owner.is_overcharge
        for d in data:
            if d.get('qty', 0) <= 0:
                continue
            # 返回 是否允许超收，总超收数量； 0 or 负数 表示没超收; real receive qty 真实收货数量
            is_overcharge, qty_off, qty_real = action.putin(w_user_code=w_user_code, w_user_name=w_user_name, is_overcharge=is_overcharge, **d)
            d['qty_real'] = qty_real
        order.state = 'part'
        
        # 不允许超收时，收完一次后，判断单子是否入库完成; 允许超收的话，单子只能手动关闭
        # 改为: 超收也检查进行关闭
        # if not g.owner.is_overcharge:
        if True:
            finish = True
            for line in order.lines:
                if not (line.qty_real >= line.qty):
                    finish = False
            order.state = 'all' if finish else 'part'
            if order.state == 'all':
                order.finish()

        db.session.commit()
    else:
        # 获取订单行
        order = Stockin.query.t_query.filter_by(id=stockin_id).first()
        lines = [line.as_dict for line in order.lines]

        partner = Partner.query.c_query.filter_by(code=order.partner_code).first()
        partner_data = partner.as_dict if partner else {}

        pay_state = u'未付款'
        if order.purchase_order_code:
            Money = db.M('Money')
            m = Money.query.o_query.filter_by(code=order.purchase_order_code, come='outcome', xtype='purchase').filter(Money.state!='cancel').first()
            if m is not None:
                if m.state == 'doing':
                    pay_state = '部分付款'
                elif m.state in ('done', 'partdone'):
                    pay_state = '已付款'
            else:
                # stockin 的自定义付款字段
                pass

        # fetch price
        if not order.price or order.sum_price!=order.price:
            order.price = order.sum_price
            db.session.commit()
        return json_response({'lines': lines, 'order': order.as_dict, 'partner': partner_data, 'pay_state': pay_state})

    return json_response({'status': 'success', 'msg': u'ok', 'data':data})


# 入库， 快捷入库，直接收取到库存
@bp_stockin.route('/putin/rfid/<stockin_id>', methods=('GET', 'POST'))
@bp_stockin.route('/putin/rfid/<stockin_id>/overcharge', methods=('GET', 'POST'))
@normal_perm.require()
def putin_rfid_api(stockin_id):
    """
    订单行入库
    post req: withlock
    {
        lines: [{line_id, qty, location, lpn='', 
            rfid_list[rfid1, rfid2, rfid3...], 
            rfid_details{rfid1:{weight, gross_weight, qty_inner}, rfid2, rfid3...}, 
        }...]
        w_user_code,
        w_user_name
    }
    
    查询订单行
    get

    """
    if request.method == 'POST':
        is_overcharge = ('overcharge' in request.path) or g.owner.is_overcharge

        order = Stockin.query.t_query.filter_by(id=stockin_id).with_for_update().first()
        if order.state in ('done', 'cancel'):
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': u'订单处于不可操作状态（已完成或已取消）'})
        data = request.json.pop('lines', [])# [{line_id, qty, location, lpn=''}...]
        w_user_code = request.json.pop('w_user_code', None)
        w_user_name = request.json.pop('w_user_name', None)

        action = StockinAction(order)
        for d in data:
            if d.get('qty', 0) <= 0:
                continue
            # 填充, rfid有数据详情的情况
            if not d.get('rfid_list', None) and d.get('rfid_details', None):
                rfid_details = d.get('rfid_details', [])
                rfid_list = [rfid for rfid in rfid_details.keys()]
                d['rfid_list'] = rfid_list
            # 返回 是否允许超收，总超收数量； 0 or 负数 表示没超收; real receive qty 真实收货数量
            is_overcharge, qty_off, qty_real = action.putin(w_user_code=w_user_code, w_user_name=w_user_name, is_overcharge=is_overcharge, **d)
            d['qty_real'] = qty_real
        order.state = 'part'

        db.session.flush()
        finish = True
        for line in order.lines:
            if line.qty_real < line.qty: # 有单行小于预期数量的时候, 则未完成
                finish = False
        order.state = 'all' if finish else 'part'
        if order.state == 'all':
            order.finish()

        db.session.commit()
    else:
        # 获取订单行
        order = Stockin.query.t_query.filter_by(id=stockin_id).first()
        lines = [line.as_dict for line in order.lines]
        return json_response(lines)

    return json_response({'status': 'success', 'msg': u'ok', 'data':data})

# 无单入库， 快捷入库，直接收取到库存
@bp_stockin.route('/putin/rfid/no-order', methods=('GET', 'POST'))
@bp_stockin.route('/putin/rfid/no-order/overcharge', methods=('GET', 'POST'))
@normal_perm.require()
def putin_rfid_no_order_api():
    """
    无订单的情况下入库, 自动创建订单(类型为生产入库), 订单行入库
    post req: withlock
    {
        lines: [{line_id:~, qty, location, lpn='', sku,
            rfid_list[rfid1, rfid2, rfid3...], 
            rfid_details[{rfid1, weight, gross_weight, qty_inner}, {rfid2}, {rfid3}...}], 
        }...]
        w_user_code,
        w_user_name
    }
    sample:{
        lines: [
            {qty, sku, location:~, rfid_details[{rfid1, weight, gross_weight, qty_inner}, ], }
        ]
    }
    """
    if request.method == 'POST':
        is_overcharge = ('overcharge' in request.path) or g.owner.is_overcharge
        is_enable_fast_stockin_qty_inner = g.owner.is_enable_fast_stockin_qty_inner

        data = request.json.pop('lines', [])# [{line_id, qty, location, lpn=''}...]
        w_user_code = request.json.pop('w_user_code', None)
        w_user_name = request.json.pop('w_user_name', None)

        # 每次只一个RFID入库时, 判断RFID是否已经入库了.
        if len(data) == 1:
            r_details = data[0].get('rfid_details', [])
            if len(r_details) == 1:
                rfid0 = r_details[0]['rfid']
                inv0 = InvRfid.query.t_query.filter_by(rfid=rfid0).first()
                if inv0 and inv0.qty == 1:
                    return json_response({'status': 'fail', 'msg': u'已经入库过了'})

        ok, order = StockinAction.create_stockin({'xtype': 'produce'}, g)
        db.session.add(order)
        db.session.flush()

        action = StockinAction(order)
        for xd in data:
            d = DictNone(xd)
            if d.get('qty', 0) <= 0:
                continue
            # 填充, rfid有数据详情的情况
            rfid_details = {}
            if not d.get('rfid_list', None) and d.get('rfid_details', None):
                r_details = d.get('rfid_details', [])
                rfid_list = [r['rfid'] for r in r_details]
                d['rfid_list'] = rfid_list
                rfid_details = {r['rfid']:r for r in r_details}
            # ('spec','brand','unit','style','color','size','level')
            ld = DictNone()
            ld.sku = d.sku
            ld.qty = 1 if is_enable_fast_stockin_qty_inner else (d.qty or 1)
            ld.location_code = d.location or ''
            ld.batch_code = d.batch_code or ''
            ld.spec = d.spec or ''
            ld.style = d.style or ''
            ld.color = d.color or ''
            ld.size = d.size or ''
            ld.level = d.level or ''
            ld.twisted = d.twisted or ''

            line = StockinAction.create_stockin_line(ld, order, poplist=None, is_add=True)
            db.session.add(line)
            db.session.flush()
            # line_id, qty, location, lpn='', line=None
            is_overcharge, qty_off, qty_real = action.putin(line_id=None, line=line, qty=ld.qty, location=(ld.location_code or 'STAGE'), \
                rfid_list=d['rfid_list'], rfid_details=rfid_details, \
                w_user_code=w_user_code, w_user_name=w_user_name, is_overcharge=is_overcharge)
            d['qty_real'] = qty_real
        order.state = 'all'

        db.session.flush()
        finish = True
        for line in order.lines:
            if line.qty_real < line.qty: # 有单行小于预期数量的时候, 则未完成
                finish = False
            # 计重
            _ = line.weight, line.gross_weight, line.qty_inner
        # 计重
        _ = order.weight, order.gross_weight, order.qty_inner

        order.state = 'all' if finish else 'part'
        if order.state == 'all':
            order.finish()

        db.session.commit()

    return json_response({'status': 'success', 'msg': u'ok', 'data':data})

# 根据订单行推荐库位
@bp_stockin.route('/recommend/location/<stockin_line_id>')
@normal_perm.require()
def recommend_location(stockin_line_id):
    line = StockinLine.query.t_query.filter_by(id=stockin_line_id).first()
    q = request.args.get('q', None)
    locations = InvAction().recommend_location(line, q)

    return json_response(locations)

# 根据sku推荐库位
@bp_stockin.route('/recommend/location/sku/<sku>')
@bp_stockin.route('/recommend/location/sku/<sku>/<location>')
@normal_perm.require()
def recommend_location_by_sku(sku, location=None):
    q = request.args.get('q', None)
    locations = InvAction().recommend_location_by_sku(sku, location, q=q)
    return json_response(locations)


# 完成入库单, 强制完成
@bp_stockin.route('/done/<stockin_id>', methods=('GET', 'POST'))
@normal_perm.require()
def done_api(stockin_id):
    order = Stockin.query.t_query.filter_by(id=stockin_id).first()
    order.state = 'done'
    order.finish()
    db.session.commit()

    # TODO 回传

    return json_response({'status': 'success', 'msg': u'ok', 'data': order.as_dict})


# 取消入库单
@bp_stockin.route('/cancel/<stockin_id>', methods=('GET', 'POST'))
@normal_perm.require()
def cancel_api(stockin_id):
    order = Stockin.query.t_query.filter_by(id=stockin_id).with_for_update().first()
    if order.state != 'done' and order.state!='cancel':
        order.state = 'cancel'
        db.session.commit()

        return json_response({'status': 'success', 'msg': u'ok', 'data': order.as_dict})

    db.session.rollback()
    return json_response({'status': 'fail', 'msg': u'订单操作中，不能取消', 'data': order.as_dict})



# 扫码入库，复核入库单货品，一般收取到STAGE库位
@bp_stockin.route('/check', methods=('GET', 'POST'))
@normal_perm.require()
def check_api():
    """
    复核货品入库
    post req: withlock
    {
        erp_order_code,
        lines: [{
            barcode, location, lpn, qty
        },]
        w_user_code,
        w_user_name
    }
    
    """
    w_user_code = request.json.pop('w_user_code', None)
    w_user_name = request.json.pop('w_user_name', None)
    order = Stockin.query.t_query.filter_by(erp_order_code=request.json.pop('erp_order_code')) \
            .with_for_update().first()
    if order.state == 'create' or order.state == 'part':
        lines = request.json['lines']
        action = StockinAction(order)
        for line in lines:
            line['qty'] = int(line.get('qty', 0) or 0)
            if line.get('qty', 0) <= 0:
                continue
            action.check(order=order, w_user_code=w_user_code, w_user_name=w_user_name, **line)

        order.state = 'part'
        
        # 不允许超收时，收完一次后，判断单子是否入库完成; 允许超收的话，单子只能手动关闭
        if not g.owner.is_overcharge:
            finish = True
            for line in order.lines:
                if not (line.qty_real >= line.qty):
                    finish = False
            order.state = 'all' if finish else 'part'
            if order.state == 'all':
                order.finish()
        db.session.commit()

        return json_response({'status': 'success', 'msg': u'ok', 'data': order.as_dict})

    db.session.rollback()
    return json_response({'status': 'fail', 'msg': u'订单在（%s）状态中，不能再收货'%(order.state), 'data': order.as_dict})




# 入库单转移库单
@bp_stockin.route('/to_move/<stockin_id>', methods=('GET', 'POST'))
@normal_perm.require()
def to_move_api(stockin_id):
    order = Stockin.query.t_query.filter_by(id=stockin_id).first()
    if order.state == 'done':
        StockinAction.trans_to_invmove(order)
        db.session.commit()

        return json_response({'status': 'success', 'msg': u'ok', 'data': order.as_dict, 'move_order_code': order.move_order_code})

    return json_response({'status': 'fail', 'msg': u'订单未完成, 不能转移库单', 'data': order.as_dict})


# 反单
@bp_stockin.route('/reverse/<order_id>', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def stockin_reverse_api(order_id):
    from blueprints.stockout.action import StockoutAction
    stockin = Stockin.query.c_query.filter_by(id=order_id).with_for_update().first()

    action = StockoutAction()
    ok, msg, order = action.fan_order(stockin)
    db.session.commit()

    if ok:
        return json_response({'status': 'success', 'msg':msg, 'order_code': order.order_code})

    return json_response({'status': 'fail', 'msg':msg, 'order_code': ''})
