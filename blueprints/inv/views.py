#coding=utf8
import os
import re
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

from models.inv import Inv, Good, Category, InvRfid, GoodMap, InvRfidTrans
from models.inv import InvMove, InvAdjust, InvCount
from models.warehouse import Location

from blueprints.inv.action import InvAction, InvCountAction, InvMoveAction, InvAdjustAction

from utils.flask_tools import json_response, gen_csv, gen_xlsx
from utils.functions import update_model_with_fields, m2dict, copy_and_update_model, common_poplist
from utils.functions import gen_query, make_q
from utils.base import Dict, DictNone
import settings

bp_inv = Blueprint("inv", __name__)



# 获取库存列表
@bp_inv.route('/inv', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def inv_api():
    """
    查询库存列表
    get req:
    q={filters:[{}], order_by, single, limit, offset, group_by, without_batch}
    """
    if request.method == 'GET':
        # q = {filters:[{}], order_by, single, limit, offset, group_by}
        q = request.args.get('q', '')
        without_batch = 'without_batch' in q or (request.args.get('without_batch', 'false') == 'true')
        with_good = request.args.get('with_good', 'false') == 'true'
        without_location = request.args.get('without_location', 'false') == 'true'
        supplier_code = request.args.get('supplier_code', '')

        qd = make_q(q)
        
        if without_batch:
            query = Inv.query.t_query.with_entities(
                    func.sum(Inv.qty).label('sum_qty'), 
                    func.sum(Inv.qty_able).label('sum_qty_able'), 
                    func.sum(Inv.qty_alloc).label('sum_qty_alloc'), 
                    Inv) \
                .filter(Inv.location_code!='PICK').filter(Inv.qty>0)
            if not qd.get('order_by', None):
                query = query.order_by(Inv.sku.asc())
            if without_location:
                query = query.group_by(Inv.sku)
            else:
                query = query.group_by(Inv.location_code, Inv.sku)

            pagin = gen_query(q, query, Inv, db=db, per_page=settings.PER_PAGE, get_objects=True)

            objects = []
            for o in pagin.items:
                obj = Dict(o[-1].as_dict)
                obj.qty = int(o.sum_qty or 0)
                obj.qty_able = int(o.sum_qty_able or 0)
                obj.qty_alloc = int(o.sum_qty_alloc or 0)
                objects.append(obj)

            # 带上货品信息
            if with_good:
                good_dict = {good.code:good for good in Good.query.o_query.filter(Good.code.in_([o.sku for o in objects])).all()}
                for o in objects:
                    good = good_dict.get(o.sku)
                    o['good'] = good.as_dict

            ret =  {
                  "num_results": pagin.total,
                  "total_pages": pagin.pages,
                  "page": pagin.page,
                  "per_page": pagin.per_page,
                  "objects": objects,
                  "without_batch": without_batch,
                }
            return json_response(ret, indent=4)

        query = Inv.query.t_query.filter(Inv.location_code!='PICK').filter(Inv.qty>0)

        if not qd.get('order_by', None):
            query = query.order_by(Inv.sku.asc())
        res = gen_query(q, query, Inv, db=db, per_page=settings.PER_PAGE)
        res['without_batch'] = without_batch
        return json_response(res, indent=4)


# 查询某一个sku的库存
@bp_inv.route('/inv/<sku>', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@bp_inv.route('/inv/<sku>/<location_code>', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def inv_sku_api(sku, location_code='STAGE'):
    """
    查询库存列表
    get req:
    resp:
    {
        ...
    }
    """
    if request.method == 'GET':
        inv = Inv.query.t_query.with_entities(
                func.sum(Inv.qty).label('sum_qty'), 
                func.sum(Inv.qty_able).label('sum_qty_able'), 
                func.sum(Inv.qty_alloc).label('sum_qty_alloc'), 
                Inv) \
            .filter(Inv.location_code!='PICK', Inv.location_code==location_code, or_(Inv.sku==sku, Inv.barcode==sku)) \
            .group_by(Inv.location_code, Inv.sku).first()

        res = DictNone()
        good = Good.query.o_query.filter(or_(Good.code==sku, Good.barcode==sku)).first()
        if good is None:
            return json_response({'status': 'fail', 'data': res}, indent=4)

        if inv and inv[-1] is not None:
            res = DictNone(inv[-1].as_dict)
            res.sum_qty = inv[0]
            res.sum_qty_able = inv[1]
            res.sum_qty_alloc = inv[2]
        elif (inv and inv[-1] is None) or inv is None:
            res = DictNone(good.as_dict)
            res.sku = res.code
            res.location_code = res.location = 'STAGE'
            res.sum_qty = inv[0] if inv else 0
            res.sum_qty_able = inv[1] if inv else 0
            res.sum_qty_alloc = inv[2] if inv else 0

        return json_response({'status': 'success', 'data': res}, indent=4)

# 
@bp_inv.route('/rfid', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def rfid_api():
    """
    根据rfid查询唯一码库存
    """
    if request.method == 'GET':
        _rfid = request.args.get('rfid', None)
        sku = request.args.get('sku', None)
        if _rfid:
            rfid = InvRfid.query.t_query.filter_by(rfid=_rfid).first()
            if rfid is not None:
                if sku and rfid.sku != sku:
                    return json_response({'status': 'fail', 'msg': u'唯一码属于货品(%s/%s)'%(rfid.sku,rfid.name)}, indent=4)
                return json_response({'status': 'success', 'msg': 'ok', 'data': rfid.as_dict}, indent=4)
            else:
                return json_response({'status': 'fail', 'msg': u'系统中未找到该唯一码对应的货品'}, indent=4)
        else:
            argstr = request.args.get('q', '')
            q = json.loads(argstr) if argstr else Dict()
            
            query = InvRfid.query.t_query
            #res = gen_query(argstr, query, InvRfid, db=db, per_page=settings.PER_PAGE)

            pagin = gen_query(argstr, query, InvRfid, db=db, per_page=settings.PER_PAGE, get_objects=True)

            objects = []
            company_id = str(g.user.company_id)
            for o in pagin.items:
                d = o.as_dict
                d['qrcode_url'] = o.get_qrcode(company_id=company_id)
                objects.append(d)

            ret =  {
                  "num_results": pagin.total,
                  "total_pages": pagin.pages,
                  "page": pagin.page,
                  "per_page": pagin.per_page,
                  "objects": objects,
                }
            return json_response(ret, indent=4)

    return ''


@bp_inv.route('/rfid/history/<rfid>', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def rfid_history_api(rfid):
    """
    根据rfid查询唯一码历史
    """
    if request.method == 'GET':
        query = InvRfidTrans.query.t_query.filter(InvRfidTrans.xtype.in_(['in', 'out']), InvRfidTrans.rfid==rfid) \
            .order_by(InvRfidTrans.id.desc())
        res = gen_query(request.args.get('q', None), query, InvRfidTrans, db=db, per_page=100)
        return json_response(res, indent=4)

    return ''

# 生成唯一码/ 查询生成的历史唯一码
@bp_inv.route('/rfid/gen', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@bp_inv.route('/rfid/gen/download', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@bp_inv.route('/rfid/gen/print', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def rfid_gen_api():
    """
    GET: 

    post req: 
        {
            sku
            num
        }
    """
    if request.method == 'POST':
        sku = request.json.get('sku', '').strip()
        num = int(request.json.get('num', 0))

        product_code, cate_code, good = 'UN', 'UN', None
        if sku:
            product_code = sku.upper()
            good = Good.query.o_query.filter_by(code=sku).first()
            if good is not None:
                cate_code = (good.category_code or 'UN')[:3].upper()
        now = datetime.now()

        #rfid_list = ['%s/%s/%s-%s'%(cate_code, product_code, str(hex(int(now.strftime('%y%m%d%H%M%S'))))[2:], i) for i in xrange(1, num+1)]
        rfid_list = ['%s-%s-%s'%(product_code, str(hex(int(now.strftime('%y%m%d%H%M%S'))))[2:], i) for i in xrange(1, num+1)]
        # send to machine
        success = True
        if success:# and product_code != 'UN':
            # save to db
            warehouse_code = g.warehouse_code
            owner_code = g.owner_code
            company_code = g.company_code

            if good is not None:
                for _rfid in rfid_list:
                    rfid = update_model_with_fields(InvRfid, good, common_poplist, rfid=_rfid, qty=0, sku=good.code, warehouse_code=warehouse_code, source='custom', create_time=now)
                    rfid.weight = rfid.weight or 0
                    rfid.gross_weight = rfid.gross_weight or 0
                    db.session.add(rfid)
            else:    
                for _rfid in rfid_list:
                    rfid = InvRfid(rfid=_rfid, qty=0, warehouse_code=warehouse_code, owner_code=owner_code, company_code=company_code, source='custom', create_time=now)
                    db.session.add(rfid)
            db.session.commit()

        return json_response({'status': 'success', 'msg': 'ok', 'data': rfid_list})

    elif request.method == 'GET' and 'download' in request.url:
        id = request.args.get('id')
        rfid = InvRfid.query.get(id)
        rfid_list = InvRfid.query.t_query.filter_by(sku=rfid.sku, create_time=rfid.create_time).all()

        table = [[o.rfid] for o in rfid_list]
        return gen_csv(title=['唯一码'], table=table, fname='rfid', to_txt=True)

    elif request.method == 'GET' and 'print' in request.url:
        id = request.args.get('id')
        rfid = InvRfid.query.get(id)
        rfid_list = InvRfid.query.t_query.filter_by(sku=rfid.sku, create_time=rfid.create_time).all()
        for rfid in rfid_list:
            rfid.printed = True
        db.session.commit()

        rfid_list_data = []
        company_id = str(g.user.company.id)
        for rfid in rfid_list:
            d = rfid.as_dict
            d['qrcode_url'] = rfid.get_qrcode(company_id)
            d['barcode_url'] = rfid.get_barcode(company_id)
            rfid_list_data.append(d)

        return json_response({'status': 'success', 'msg': 'ok', 'rfid_list': rfid_list_data})

    elif request.method == 'GET':
        query = InvRfid.query.t_query.with_entities(
                    func.count(InvRfid.id).label('num'), 
                    InvRfid).filter_by(source='custom') \
                .group_by(InvRfid.sku, InvRfid.create_time)
        pagin = gen_query(request.args.get('q', None), query, InvRfid, db=db, per_page=settings.PER_PAGE, get_objects=True)

        objects = []
        for o in pagin.items:
            obj = Dict(o[-1].as_dict)
            obj.num = int(o.num)
            objects.append(obj)

        ret =  {
              "num_results": pagin.total,
              "total_pages": pagin.pages,
              "page": pagin.page,
              "per_page": pagin.per_page,
              "objects": objects,
              "with_batch": False,
            }
        return json_response(ret, indent=4)



@bp_inv.route('/good', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@bp_inv.route('/good/v2', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def good_api():
    goods = []
    if request.method == 'GET' and '/v2' in request.path:
        q = request.args.get('q', None)
        q2 = request.args.get('q2', None)
        qtype = request.args.get('qtype', None)

        query = Good.query.o_query.filter(Good.state!='delete', or_(
                Good.code.like('%%%s%%'%q2), 
                Good.barcode.like('%%%s%%'%q2), 
                Good.name.like('%%%s%%'%q2), 
                Good.spec.like('%%%s%%'%q2),
                Good.category_code.like('%s%%'%q2), 
            ))

        if qtype=='sale':
            query = query.filter(Good.state=='on')

        query = query.order_by(Good.code.asc())
        pagin = gen_query(q, query, Good, db=db, per_page=settings.PER_PAGE, get_objects=True)
        goods = pagin.items

        invaction = InvAction()
        with_inv_qty = request.args.get('with_inv_qty', '') == 'true'
        qtype = request.args.get('qtype', '')

        price_type = 2
        if qtype in ('in', 'purchase'):
            price_type = 1
        elif qtype in ('out', 'sale'):
            price_type = 0

        qty_dict = invaction.mget_inv_qty([good.code for good in goods])

        data = []
        for good in goods:
            d = good.as_dict
            d['now_price'] = d['price'] if price_type == 2 else (d['last_in_price'] if price_type == 1 else d['last_out_price'])
            data.append(d)
            if with_inv_qty:
                d['qty_able'] = qty_dict.get(good.code, 0)
        
        ret =  {
              "num_results": pagin.total,
              "total_pages": pagin.pages,
              "page": pagin.page,
              "per_page": pagin.per_page,
              "objects": data,
            }
        return json_response(ret, indent=4)

    if request.method == 'GET':
        query = Good.query.o_query

        q = request.args.get('q', None)
        qtype = request.args.get('qtype', None)

        query = Good.query.o_query
        if q:
            query = query.filter(or_(
                Good.code.like('%%%s%%'%q), 
                Good.barcode.like('%%%s%%'%q), 
                Good.name.like('%%%s%%'%q), 
                Good.name_en.like('%%%s%%'%q), 
                Good.spec.like('%%%s%%'%q),
                Good.category_code.like('%s%%'%q), 
            ))

        if qtype=='sale':
            query = query.filter(Good.state=='on')

        maincode = request.args.get('maincode', None)
        if maincode:
            query = query.filter(GoodMap.subcode==Good.code, GoodMap.company_code==Good.company_code, GoodMap.owner_code==Good.owner_code)

        limit = 20
        if g.owner.is_enable_search_good_500:
            limit = g.owner.is_enable_search_good_500
        goods = query.order_by(Good.code.asc()).limit(limit).all()

        invaction = InvAction()
        with_inv_qty = request.args.get('with_inv_qty', '') == 'true'
        qtype = request.args.get('qtype', '')

        price_type = 2
        if qtype in ('in', 'purchase'):
            price_type = 1
        elif qtype in ('out', 'sale'):
            price_type = 0

        qty_dict = invaction.mget_inv_qty([good.code for good in goods])

        data = []
        for good in goods:
            d = good.as_dict
            d['now_price'] = d['price'] if price_type == 2 else (d['last_in_price'] if price_type == 1 else d['last_out_price'])
            data.append(d)
            if with_inv_qty:
                d['qty_able'] = qty_dict.get(good.code, 0)
                #d['qty_able'] = invaction.get_inv_qty(good.code)

        return json_response(data)

    if request.method == 'POST':
        data = request.json
        for d in data:
            exist, good = InvAction.create_good(d, g)
            if not exist:
                if good.category_code:
                    category = InvAction.create_category(good.category_code)
                else:
                    category = InvAction.default_category(d.pop('category_code', None))
                good.category_code = category.code
                # good.JSON = d
                db.session.add(good)
            goods.append(good)
        db.session.commit()

        invaction = InvAction()
        with_inv_qty = request.args.get('with_inv_qty', '') == 'true'
        qtype = request.args.get('qtype', '')

        price_type = 2
        if qtype in ('in', 'purchase'):
            price_type = 1
        elif qtype in ('out', 'sale'):
            price_type = 0

        data = []
        for good in goods:
            d = good.as_dict
            d['now_price'] = d['price'] if price_type == 2 else (d['last_in_price'] if price_type == 1 else d['last_out_price'])
            data.append(d)
            if with_inv_qty:
                d['qty_able'] = invaction.get_inv_qty(good.code)

        return json_response(data)


@bp_inv.route('/good/supply_demand', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def good_supply_demand_api():
    goods = []
    if request.method == 'GET':
        query = Good.query.o_query

        q = request.args.get('q', None)
        qtype = request.args.get('qtype', None)
        is_supply_demand = True if 'supply_demand' in request.path else False

        query = Good.query.o_query

        if qtype=='sale':
            query = query.filter(Good.state=='on')

        maincode = request.args.get('maincode', None)
        if maincode:
            query = query.filter(GoodMap.subcode==Good.code, GoodMap.company_code==Good.company_code, GoodMap.owner_code==Good.owner_code)

        limit = 20
        if g.owner.is_enable_search_good_500:
            limit = g.owner.is_enable_search_good_500

        if request.args.get('export', None) == 'xlsx':
            query = gen_query(q, query, Good, db=db, per_page=settings.PER_PAGE, export=True)
            goods = query.all()
        else:
            pagin = gen_query(q, query, Good, db=db, per_page=settings.PER_PAGE, get_objects=True)
            goods = pagin.items

        invaction = InvAction()
        with_inv_qty = request.args.get('with_inv_qty', '') == 'true'
        qtype = request.args.get('qtype', '')

        price_type = 2
        if qtype in ('in', 'purchase'):
            price_type = 1
        elif qtype in ('out', 'sale'):
            price_type = 0

        qty_dict = {inv.sku:inv for inv in invaction.mget_inv_qty([good.code for good in goods], obj=True)}

        Stockout = db.M('Stockout')
        OL = db.M('StockoutLine')
        Stockin = db.M('Stockin')
        IL = db.M('StockinLine')

        data = []
        for good in goods:
            d = DictNone(good.as_dict)
            d['now_price'] = d['price'] if price_type == 2 else (d['last_in_price'] if price_type == 1 else d['last_out_price'])
            data.append(d)
            if with_inv_qty:
                inv = qty_dict.get(good.code, None)
                if inv:
                    d['qty_able'] = inv.qty_able
                    d['qty_alloc'] = inv.qty_alloc
                    d['qty'] = inv.qty
                else:
                    d['qty_able'] = d['qty_alloc'] = d['qty'] = 0
                #d['qty_able'] = invaction.get_inv_qty(good.code)
            # # 库存，销售需求，生产需求，其它需求，采购数量，到货数量，剩余需求，剩余库存
            if is_supply_demand:
                # 销售需求 已经确认的未完成的销售出库单
                o1 = OL.query.t_query.with_entities(func.sum(OL.qty).label('qty_sale')).filter(
                        ~Stockout.state.in_(['done', 'cancel']), 
                        Stockout.order_type=='sale',
                        OL.stockout_id==Stockout.id,
                        OL.sku==good.code,
                    ).first()
                d['qty_sale'] = (o1.qty_sale if o1 else 0) or 0
                o2 = OL.query.t_query.with_entities(func.sum(OL.qty).label('qty_produce')).filter(
                        ~Stockout.state.in_(['done', 'cancel']), 
                        Stockout.order_type=='produce',
                        OL.stockout_id==Stockout.id,
                        OL.sku==good.code,
                    ).first()
                d['qty_produce'] = (o2.qty_produce if o2 else 0) or 0
                o3 = OL.query.t_query.with_entities(func.sum(OL.qty).label('qty_other')).filter(
                        ~Stockout.state.in_(['done', 'cancel']), 
                        ~Stockout.order_type.in_(['produce', 'sale']),
                        OL.stockout_id==Stockout.id,
                        OL.sku==good.code,
                    ).first()
                d['qty_other'] = (o3.qty_other if o3 else 0) or 0
                d['qty_demand'] = d['qty_sale']+d['qty_produce']+d['qty_other']
                o4 = IL.query.t_query.with_entities(
                        func.sum(IL.qty).label('qty_purchase'), 
                        func.sum(IL.qty_real).label('qty_purchase_in')
                    ).filter(
                        ~Stockin.state.in_(['done', 'cancel']), 
                        Stockin.xtype=='purchase',
                        IL.stockin_id==Stockin.id,
                        IL.sku==good.code,
                    ).first()
                d['qty_purchase'] = (o4.qty_purchase if o4 else 0) or 0
                d['qty_purchase_in'] = (o4.qty_purchase_in if o4 else 0) or 0
                d['qty_purchase_notin'] = d['qty_purchase'] - d['qty_purchase_in']
                # 剩余需求，剩余库存
                d['qty_demand_left'] = d['qty_demand'] - d['qty'] - d['qty_purchase_notin']
                d['qty_left'] = d['qty'] - d['qty_demand']

        if request.args.get('export', None) == 'xlsx':
            title = [u'货品码', u'名称', u'规格', u'库存', u'销售需求', u'生产需求', u'其它需求', u'总需求', u'采购数量', u'采购到货', u'采购未到', u'剩余需求', u'剩余库存']
            keys = 'sku,name,spec,qty,qty_sale,qty_produce,qty_other,qty_demand,qty_purchase,qty_purchase_in,qty_purchase_notin,qty_demand_left,qty_left'.split(',')
            table = [[getattr(o, k, '') for k in keys] for o in data]
            return gen_xlsx(title, table, fname=u'需求与供应统计')

        ret =  {
              "num_results": pagin.total,
              "total_pages": pagin.pages,
              "page": pagin.page,
              "per_page": pagin.per_page,
              "objects": data
            }
        return json_response(ret, indent=4)


# 设置货品图片
@bp_inv.route('/good/<good_id>/image', methods=('GET', 'POST', 'PUT', 'DELETE'))
@normal_perm.require()
def good_image_api(good_id=None):
    if request.method == 'PUT':
        good = Good.query.get(good_id)
        from utils.upload import save_request_file, save_image

        msg = u'无图片'
        try:
            fname, file_path = save_request_file(settings.UPLOAD_DIR, company_id=g.user.company_id)
            # 保存图片
            fmt = os.path.splitext(fname)[1][1:]
            with open(file_path, 'rb') as f:
                blob = f.read()
            if blob:
                path, osslink = save_image(settings.UPLOAD_DIR, blob, fmt, settings.UPLOAD_IMG_TO_OSS, company_id=g.user.company_id)
                if settings.UPLOAD_IMG_TO_OSS:
                    iurl = settings.OSS_URL_PREFIX + osslink
                else:
                    iurl = '/static/upload/images/%s/%s'%(g.user.company_id, osslink)
                good.image_url = iurl
                good.images = ",".join(good.images.split(',') + [iurl])
                db.session.commit()

                return json_response({'status': 'success', 'msg': 'ok', 'image_url': good.image_url, 'images_list': good.images_list})
        except:
            msg = traceback.format_exc()
        return json_response({'status': 'fail', 'msg': msg})

    if request.method == 'POST':
        good = Good.query.get(good_id)
        from utils.upload import save_request_file, save_image

        msg = u'无图片'
        try:
            fname, file_path = save_request_file(settings.UPLOAD_DIR, company_id=g.user.company_id)
            # 保存图片
            fmt = os.path.splitext(fname)[1][1:]
            with open(file_path, 'rb') as f:
                blob = f.read()
            if blob:
                path, osslink = save_image(settings.UPLOAD_DIR, blob, fmt, settings.UPLOAD_IMG_TO_OSS, company_id=g.user.company_id)
                if settings.UPLOAD_IMG_TO_OSS:
                    iurl = settings.OSS_URL_PREFIX + osslink
                else:
                    #iurl = '/static/upload/images/'+osslink
                    iurl = '/static/upload/images/%s/%s'%(g.user.company_id, osslink)
                if good:
                    good.images = ",".join(good.images.split(',') + [iurl])
                db.session.commit()
                if good:
                    return json_response({'status': 'success', 'msg': 'ok', 'images_list': good.images_list})
                return json_response({'status': 'success', 'msg': 'ok', 'image_url': iurl})
        except:
            msg = traceback.format_exc()
        return json_response({'status': 'fail', 'msg': msg})

    if request.method == 'DELETE':
        img = request.args.get('img', None)
        good = Good.query.get(good_id)
        if img:
            name = img.split('/')[-1]
            good.images = ",".join([im for im in good.images.split(',') if not im.endswith(name)])
            if name in good.image_url:
                good.image_url = ''
            db.session.commit()
            return json_response({'status': 'success', 'msg': 'ok', 'images_list':good.images_list})
        return json_response({'status': 'fail', 'msg': 'not pass img to server'})

# 设置货品广告图片
@bp_inv.route('/good/<good_id>/ad_image', methods=('GET', 'POST', 'PUT', 'DELETE'))
@normal_perm.require()
def good_ad_image_api(good_id=None):
    if request.method == 'POST' or request.method == 'PUT':
        good = Good.query.get(good_id)
        from utils.upload import save_request_file, save_image

        msg = u'无图片'
        try:
            fname, file_path = save_request_file(settings.UPLOAD_DIR, company_id=g.user.company_id)
            # 保存图片
            fmt = os.path.splitext(fname)[1][1:]
            with open(file_path, 'rb') as f:
                blob = f.read()
            if blob:
                path, osslink = save_image(settings.UPLOAD_DIR, blob, fmt, settings.UPLOAD_IMG_TO_OSS, company_id=g.user.company_id)
                if settings.UPLOAD_IMG_TO_OSS:
                    iurl = settings.OSS_URL_PREFIX + osslink
                else:
                    #iurl = '/static/upload/images/'+osslink
                    iurl = '/static/upload/images/%s/%s'%(g.user.company_id, osslink)
                if good:
                    good.ad_images = ",".join(good.ad_images.split(',') + [iurl])
                db.session.commit()
                if good:
                    return json_response({'status': 'success', 'msg': 'ok', 'ad_images_list': good.ad_images_list})
                return json_response({'status': 'success', 'msg': 'ok', 'image_url': iurl})
        except:
            msg = traceback.format_exc()
        return json_response({'status': 'fail', 'msg': msg})

    if request.method == 'DELETE':
        img = request.args.get('img', None)
        good = Good.query.get(good_id)
        if img:
            name = img.split('/')[-1]
            good.ad_images = ",".join([im for im in good.ad_images.split(',') if not im.endswith(name)])
            db.session.commit()
            return json_response({'status': 'success', 'msg': 'ok', 'ad_images_list':good.ad_images_list})
        return json_response({'status': 'fail', 'msg': 'not pass img to server'})

# 上架下架
@bp_inv.route('/good/<good_id>/ondown', methods=('GET', 'POST', 'PUT', 'DELETE'))
@normal_perm.require()
def good_ondown_api(good_id=None):
    good = InvAction().ondown_good(oid=good_id)

    from blueprints.openapi.action import LaoaAction
    ok, msg = False, None
    try:
        if good.state == 'down':
            #action = LaoaAction(settings.LAOA_HBB_URL, settings.LAOA_HBB_APPKEY, settings.LAOA_HBB_APPSECRET)
            #ok, msg = action.remote_down_good(good)
            if ok:
                db.session.commit()
            else:
                db.session.rollback()
    except:
        db.session.rollback()
        traceback.print_exc()
        msg = '500 error'

    if ok:
        return json_response({'status': 'success', 'msg': 'ok', 'data': good.as_dict})
    return json_response({'status': 'fail', 'msg': msg, 'data': good.as_dict})


# 移库上架, 移库单api
@bp_inv.route('/move', methods=('GET', 'POST', 'PUT', 'DELETE'))
@bp_inv.route('/move/<line_id>', methods=('GET', 'POST', 'PUT', 'DELETE'))
@bp_inv.route('/move/one', methods=('GET', 'POST', 'PUT', 'DELETE'))
@normal_perm.require()
def move_api(line_id=None):
    """
    查询移库单
    get req:
        q = {filters:[{}], order_by, single, limit, offset, group_by}

    更新移库单
    put req: 
        [{...}, {...}]
    """
    if request.method == 'GET' and 'one' in request.path:
        argstr = request.args.get('q', '')
        q = json.loads(argstr) if argstr else Dict()

        query = InvMove.query.t_query.filter(InvMove.series_code==request.args.get('series_code', None))
        # print(query.real_sql())
        query = query.filter(InvMove.location_code==Location.code)

        for rule in g.owner.alloc_rules:
            ## 库位优先级高先出
            if rule == 'priority_location':
                query = query.filter(InvMove.location_code==Location.code).order_by(Location.priority.desc())
            ## 库位完整远近优先
            elif rule == 'index_location_asc': # 库位近的优先, 库位序小的先出
                query = query.filter(InvMove.location_code==Location.code).order_by(Location.index.asc())
            elif rule == 'index_location_desc': # 库位远的优先，库位序大的先出
                query = query.filter(InvMove.location_code==Location.code).order_by(Location.index.desc())
            else:
                pass

        res = gen_query(argstr, query, InvMove, db=db, per_page=settings.PER_PAGE)
        return json_response(res, indent=4)

    if request.method == 'GET':
        # q = {filters:[{}], order_by, single, limit, offset, group_by}
        argstr = request.args.get('q', '')
        q = json.loads(argstr) if argstr else Dict()
        
        query = InvMove.query.t_query
        res = gen_query(argstr, query, InvMove, db=db, per_page=settings.PER_PAGE)
        return json_response(res, indent=4)

    if request.method == 'POST':
        action = InvMoveAction()
        series_code = action.gen_series_code(g.company_code, g.warehouse_code, g.owner_code)
        for line in request.json:
            ok, series_code = action.create(line, series_code=series_code)
            print(ok, '======', line)
        if True:
            db.session.commit()
            return json_response({'status': 'success', 'msg': series_code, 'data': {'series_code': series_code}})
        else:
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': series_code, 'data': {'series_code': series_code}})
    # 更新功能暂时无效
    elif request.method == 'PUT':
        series_code = None
        nlines = []
        for o in request.json:
            if o.get('id', None):
                series_code = o['series_code']
                InvMove.query.t_query.filter_by(id=o['id'], state='create') \
                        .update({'qty': o['qty'], 'dest_location_code': o['dest_location_code'], 'dest_lpn': o['dest_lpn']})
            else:
                sku = o.get('sku', None)
                if sku:
                    good = Good.query.o_query.filter(or_(Good.code==sku, Good.barcode==sku)).first()
                    iv = InvMove(series_code=series_code, sku=good.code, barcode=good.barcode, name=good.name, spec=good.spec, **o)
                    db.session.add(iv)
                    nlines.append(iv)

        for nl in nlines:
            nl.series_code = series_code

        db.session.commit()
        return json_response({'status': 'success', 'msg': 'ok', 'lines': request.json})

    elif request.method == 'DELETE':
        InvMove.query.t_query.filter_by(id=line_id, state='create').delete()
        db.session.commit()
        return json_response({'status': 'success', 'msg': 'ok'})


# 执行移库单
@bp_inv.route('/move/exec/<series_code>', methods=('POST',))
@bp_inv.route('/move/exec/<series_code>/part', methods=('POST',))
@normal_perm.require()
def move_exec_api(series_code):
    """
    执行调整单
    post req: withlock


    """
    if request.method == 'POST' and 'part' in request.path:
        moves = []
        for line in request.json['lines']:
            qty_real = int(line['qty_real2'] or 0)
            if qty_real:
                move = InvMove.query.t_query.filter_by(series_code=series_code, id=line['id']).with_for_update().first()
                move.qty_real += qty_real
                move.qty_real2 = qty_real
                moves.append(move)
                print(move.sku, move.qty_real2)
        db.session.flush()

        action = InvMoveAction()
        ok, err = action.move(moves, part=True)
        if not ok:
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': err})
        db.session.commit()
        return json_response({'status': 'success', 'msg': 'ok'})

    elif request.method == 'POST':
        orders = InvMove.query.t_query.filter_by(series_code=series_code, state='create').with_for_update().all()
        action = InvMoveAction()
        ok, err = action.move(orders)
        if not ok:
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': err})
        db.session.commit()
        return json_response({'status': 'success', 'msg': 'ok'})

# 取消移库单
@bp_inv.route('/move/cancel/<series_code>', methods=('GET', 'POST',))
@normal_perm.require()
def move_cancel_api(series_code):
    """
    执行调整单
    post req: withlock


    """
    action = InvMoveAction()
    ok, err = action.cancel(series_code)
    if not ok:
        db.session.rollback()
        return json_response({'status': 'fail', 'msg': err})
    db.session.commit()
    return json_response({'status': 'success', 'msg': 'ok'})

# 完成移库单
@bp_inv.route('/move/done/<series_code>', methods=('GET', 'POST',))
@normal_perm.require()
def move_done_api(series_code):
    """
    执行调整单
    post req: withlock


    """
    action = InvMoveAction()
    ok, err = action.done(series_code)
    if not ok:
        db.session.rollback()
        return json_response({'status': 'fail', 'msg': err})
    db.session.commit()
    return json_response({'status': 'success', 'msg': 'ok'})

# 执行移库单-移出
@bp_inv.route('/move/exec_out/<series_code>', methods=('POST',))
@normal_perm.require()
def move_exec_out_api(series_code):
    """
    执行调整单
    post req: withlock


    """
    if request.method == 'POST':
        orders = InvMove.query.t_query.filter_by(series_code=series_code, state='create').with_for_update().all()
        action = InvMoveAction()
        ok, err = action.move_out(orders)
        if not ok:
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': err})
        db.session.commit()
        return json_response({'status': 'success', 'msg': 'ok'})


# 执行移库单-移入
@bp_inv.route('/move/exec_in/<series_code>', methods=('POST',))
@normal_perm.require()
def move_exec_in_api(series_code):
    """
    执行调整单
    post req: withlock


    """
    if request.method == 'POST':
        orders = InvMove.query.t_query.filter_by(series_code=series_code, state='doing').with_for_update().all()
        action = InvMoveAction()
        ok, err = action.move_in(orders)
        if not ok:
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': err})
        db.session.commit()
        return json_response({'status': 'success', 'msg': 'ok'})


# 获取订单行的推荐库位
@bp_inv.route('/move/autolocation', methods=('POST', 'DELETE'))
@bp_inv.route('/move/autolocation/lines', methods=('POST', 'DELETE'))
@normal_perm.require()
def move_autolocation_api():
    from blueprints.stockin.action import StockinAction
    action  = StockinAction()
    lines = request.json

    loc_dict = {}
    ok = True
    # 移入库存/移出库存
    move_type = request.args.get('type', 'movein_inv')

    for idx, linedata in enumerate(lines):
        line = DictNone(linedata)
        excludes = [line.location_code]
        line.good = Good.query.o_query.filter(Good.code==line.sku).first()
        
        ok, loc = action.auto_location(line, only_one=True, excludes=excludes, pass_location_code=True, move_type=move_type)
        loc_dict[idx] = loc
        excludes.append(loc)
    return json_response({'status': 'success', 'loc_dict':loc_dict})


# 调整单api
@bp_inv.route('/adjust', methods=('GET', 'POST', 'PUT', 'DELETE'))
@bp_inv.route('/adjust/<line_id>', methods=('GET', 'POST', 'PUT', 'DELETE'))
@normal_perm.require()
def adjust_api(line_id=None):
    """
    查询调整单
    get req:
        q = {filters:[{}], order_by, single, limit, offset, group_by}

    更新调整单
    put req:
    """
    if request.method == 'GET':
        # q = {filters:[{}], order_by, single, limit, offset, group_by}
        argstr = request.args.get('q', '')
        q = json.loads(argstr) if argstr else Dict()
        
        query = InvAdjust.query.t_query
        res = gen_query(argstr, query, InvAdjust, db=db, per_page=settings.PER_PAGE)
        return json_response(res, indent=4)

    elif request.method == 'PUT':
        series_code = None
        nlines = []
        for o in request.json:
            if o.get('id', None):
                InvAdjust.query.t_query.filter_by(id=o['id'], state='create').update({'qty_diff': o['qty_diff']})
                series_code = o['series_code']
            else:
                sku = o.get('sku', None)
                if sku:
                    good = Good.query.o_query.filter(or_(Good.code==sku, Good.barcode==sku)).first()
                    ia = InvAdjust(series_code=series_code, sku=good.code, barcode=good.barcode, name=good.name, spec=good.spec, **o)
                    db.session.add(ia)
                    nlines.append(ia)

        for nl in nlines:
            nl.series_code = series_code

        db.session.commit()
        return json_response({'status': 'success', 'msg': 'ok', 'lines': request.json})

    elif request.method == 'DELETE':
        InvAdjust.query.t_query.filter_by(id=line_id, state='create').delete()
        db.session.commit()
        return json_response({'status': 'success', 'msg': 'ok'})


# 执行调整单
@bp_inv.route('/adjust/exec/<series_code>', methods=('POST',))
@normal_perm.require()
def adjust_exec_api(series_code):
    """
    执行调整单
    post req: withlock


    """
    if request.method == 'POST':
        orders = InvAdjust.query.t_query.filter_by(series_code=series_code, state='create').with_for_update().all()
        action = InvAdjustAction()
        ok, err = action.adjust(orders)
        if not ok:
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': err})
        db.session.commit()
        return json_response({'status': 'success', 'msg': 'ok'})


# 盘点单api
@bp_inv.route('/count', methods=('GET', 'POST', 'PUT', 'DELETE'))
@bp_inv.route('/count/create_lines', methods=('GET', 'POST', 'PUT', 'DELETE'))
@bp_inv.route('/count/<line_id>', methods=('GET', 'POST', 'PUT', 'DELETE'))
@bp_inv.route('/count/pda', methods=('GET', 'POST', 'PUT', 'DELETE'))
@normal_perm.require()
def count_api(line_id=None):
    """
    查询盘点单
    get req:
        q = {filters:[{}], order_by, single, limit, offset, group_by}

    更新盘点单
    put req:
        [{...},]

    创建盘点单
    post req:
        {location_code, sku}
    """
    if request.method == 'GET':
        # q = {filters:[{}], order_by, single, limit, offset, group_by}
        argstr = request.args.get('q', '')
        q = json.loads(argstr) if argstr else Dict()
        
        query = InvCount.query.t_query
        res = gen_query(argstr, query, InvCount, db=db, per_page=settings.PER_PAGE)
        return json_response(res, indent=4)

    elif request.method == 'PUT':
        series_code = request.args.get('series_code', None)
        for o in request.json:
            if o.get('id', None) and o['id'] > 0:
                InvCount.query.t_query.filter_by(id=o['id'], state='create').update({'qty_real': o['qty_real']})
            else:
                sku = o.get('sku', None)
                o.pop('id', None)
                if sku:
                    good = Good.query.o_query.filter(or_(Good.code==sku, Good.barcode==sku)).first()
                    ic = InvCount(company_code=g.company_code, owner_code=g.owner_code, warehouse_code=g.warehouse_code, series_code=series_code, spec=good.spec, **o)
                    ic.name = good.name
                    ic.barcode = good.barcode
                    db.session.add(ic)

        db.session.commit()
        return json_response({'status': 'success', 'msg': 'ok', 'lines': request.json})

    elif request.method == 'POST' and 'pda' in request.path:
        action = InvCountAction()
        series_code = InvCountAction.gen_series_code(g.company_code, g.warehouse_code, g.owner_code)
        for data in request.json['lines']:
            action.create(data, fill=True, series_code=series_code)
        if True:
            db.session.commit()
        else:
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': series_code, 'data': {'series_code': series_code}})

        return json_response({'status': 'success', 'msg': 'ok', 'data': {'series_code': series_code}})

    elif request.method == 'POST' and request.path.endswith('/create_lines'):
        action = InvCountAction()
        ok, series_code = action.create_lines(request.json['lines'])
        if ok:
            db.session.commit()
        else:
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': series_code, 'data': {'series_code': series_code}})

        return json_response({'status': 'success', 'msg': 'ok', 'data': {'series_code': series_code}})

    elif request.method == 'POST':
        action = InvCountAction()
        ok, series_code = action.create(request.json)
        if ok:
            db.session.commit()
        else:
            db.session.rollback()
            return json_response({'status': 'fail', 'msg': series_code, 'data': {'series_code': series_code}})

        return json_response({'status': 'success', 'msg': 'ok', 'data': {'series_code': series_code}})

    elif request.method == 'DELETE':
        InvCount.query.t_query.filter_by(id=line_id, state='create').delete()
        db.session.commit()
        return json_response({'status': 'success', 'msg': 'ok'})


# 盘点单生成调整单
@bp_inv.route('/count/to_adjust/<series_code>', methods=('POST',))
@bp_inv.route('/count/to_adjust/<series_code>/exec', methods=('POST',))
@normal_perm.require()
def count_to_adjust_api(series_code):
    """
    盘点单生成调整单
    post req: withlock
    """
    if request.method == 'POST':
        orders = InvCount.query.t_query.filter_by(series_code=series_code, state='create').with_for_update().all()
        action = InvCountAction()
        adjust_series_code, adj_orders = action.gen_adjust(orders)

        if 'exec' in request.path:
            action2 = InvAdjustAction()
            ok, err = action2.adjust(adj_orders)
            if not ok:
                db.session.rollback()
                return json_response({'status': 'fail', 'msg': err})

        db.session.commit()
        return json_response({'status': 'success', 'msg': 'ok', 'adjust_series_code': adjust_series_code})


# 取消盘点
@bp_inv.route('/count/cancel/<series_code>', methods=('GET', 'POST',))
@normal_perm.require()
def count_cancel_api(series_code):
    """
    执行调整单
    post req: withlock


    """
    action = InvCountAction()
    ok, err = action.cancel(series_code)
    if not ok:
        db.session.rollback()
        return json_response({'status': 'fail', 'msg': err})
    db.session.commit()
    return json_response({'status': 'success', 'msg': 'ok'})


# 库存告警-高库存告警
@bp_inv.route('/warn/high', methods=('GET', 'POST',))
@normal_perm.require()
def warn_high_api():
    """
    高库存告警
    get req: 
    """
    qty_real = func.sum(Inv.qty_able).label('qty_real')
    argstr = request.args.get('q', '')
    q = make_q(argstr)
    subq = gen_query(argstr, Good.query.o_query, Good, db=db, export=True)

    subq0 = Inv.query.with_entities(Inv.sku.label('sku'), Inv.qty_able.label('qty_able')).t_query.filter(Inv.location_code!='PICK').group_by(Inv.sku).subquery()
    subq = subq.outerjoin(subq0, subq0.c.sku==Good.code).with_entities(Good.code, Good.barcode, Good.name, Good.max_qty, subq0.c.qty_able) \
            .filter(Good.max_qty>0) \
            .group_by(Good.code).having(subq0.c.qty_able>Good.max_qty).order_by(None)
    # print(subq.real_sql())
    pagin = subq.paginate(q.page, per_page=(q.per_page or settings.PER_PAGE))

    table = []
    for line in pagin.items:
        d = DictNone()
        d.sku = line.code
        d.barcode = line.barcode
        d.name = line.name
        d.qty_real = line.qty_able or 0
        d.qty_warn = line.max_qty
        table.append(d)

    ret =  {
          "num_results": pagin.total,
          "total_pages": pagin.pages,
          "page": pagin.page,
          "per_page": pagin.per_page,
          "objects": table,
        }
    return json_response(ret, indent=4)


# 库存告警-低库存告警
@bp_inv.route('/warn/low', methods=('GET', 'POST',))
@normal_perm.require()
def warn_low_api():
    """
    高库存告警
    get req: 
    """
    qty_real = func.sum(Inv.qty_able).label('qty_real')
    argstr = request.args.get('q', '')
    q = make_q(argstr)
    subq = gen_query(argstr, Good.query.o_query, Good, db=db, export=True)
    # subq = subq.with_entities(Good, Good.min_qty, qty_real) \
    #         .filter(Inv.location_code!='PICK') \
    #         .filter(Inv.sku==Good.code, Inv.company_code==Good.company_code, Inv.owner_code==Good.owner_code, Inv.warehouse_code==g.warehouse_code) \
    #         .filter(Good.min_qty > 0).group_by(Inv.sku).having(qty_real<Good.min_qty).order_by(None)
    

    subq0 = Inv.query.with_entities(Inv.sku.label('sku'), Inv.qty_able.label('qty_able')).t_query.filter(Inv.location_code!='PICK').group_by(Inv.sku).subquery()
    subq = subq.outerjoin(subq0, subq0.c.sku==Good.code).with_entities(Good.code, Good.barcode, Good.name, Good.min_qty, subq0.c.qty_able) \
            .filter(Good.min_qty>0) \
            .group_by(Good.code).having(or_(subq0.c.qty_able<Good.min_qty, subq0.c.qty_able==None)).order_by(None)
    # print(subq.real_sql())
    pagin = subq.paginate(q.page, per_page=(q.per_page or settings.PER_PAGE))

    table = []
    #for inv, mq, wq in pagin.items:
    #    d = inv.as_dict
    #    d['qty_real'] = wq
    #    d['qty_warn'] = mq
    for line in pagin.items:
        d = DictNone()
        d.sku = line.code
        d.barcode = line.barcode
        d.name = line.name
        d.qty_real = line.qty_able or 0
        d.qty_warn = line.min_qty
        table.append(d)

    ret =  {
          "num_results": pagin.total,
          "total_pages": pagin.pages,
          "page": pagin.page,
          "per_page": pagin.per_page,
          "objects": table,
        }
    return json_response(ret, indent=4)


@bp_inv.route('/asset', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def inv_asset_api():
    """
    查询库存列表
    get req:
    q={filters:[{}], order_by, single, limit, offset, group_by, without_batch}
    """
    if request.method == 'GET':
        xargs = request.args
        q = xargs.get('q', '')
        query = Good.query.o_query
        pagin = gen_query(q, query, Good, db=db, per_page=settings.PER_PAGE, get_objects=True)

        objects = []
        action  = InvAction()

        sku_list = [o.code for o in pagin.items]
        qty_dict = {om.sku: om for om in action.mget_inv_qty(sku_list, obj=True)}

        rfid_dict = {}
        for rfid in InvRfid.query.t_query.filter(InvRfid.sku.in_(sku_list), InvRfid.state=='on', InvRfid.qty==0).all():
            if rfid.sku not in rfid_dict:
                rfid_dict[rfid.sku] = 0
            rfid_dict[rfid.sku] += 1

        for o in pagin.items:
            obj = DictNone(o.as_dict)
            inv = qty_dict.get(o.code, None)
            qty_use = rfid_dict.get(o.code, 0)
            if inv:
                obj.qty = inv.qty or 0
                obj.qty_alloc = inv.qty_alloc or 0
                obj.qty_able = inv.qty_able or 0
            obj.qty_use = qty_use
            obj.qty_total = obj.qty_use + (obj.qty or 0)

            objects.append(obj)

        if xargs.get('export', None) == 'xlsx':
            title = [u'货品码', u'条码', u'名称', u'资产总数', u'领用总数', u'库存数量', '锁定数', u'可用数', '货类码']
            keys = 'code,barcode,name,qty_total,qty_use,qty,qty_alloc,qty_able,category_code'.split(',')
            table = [[getattr(o, k, '') for k in keys] for o in objects]
            return gen_xlsx(title, table, fname=u'资产统计')

        ret =  {
              "num_results": pagin.total,
              "total_pages": pagin.pages,
              "page": pagin.page,
              "per_page": pagin.per_page,
              "objects": objects,
            }
        return json_response(ret, indent=4)