#coding=utf8
import json
from sqlalchemy import func, or_
from pprint import pprint
from datetime import datetime, timedelta
from random import randint

from flask import Blueprint, g, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from extensions.database import db
from extensions.permissions import admin_perm, manager_perm, normal_perm

from models.inv import Inv, Good, Category, InvRfid
from models.inv import InvMove, InvAdjust, InvCount
from models.stockin import Stockin, StockinLine, StockinLineTrans
from models.stockout import Stockout, StockoutLine, StockoutLineTrans
from models.finance import Money, MoneySummary
from models.auth import User, Partner

from utils.flask_tools import json_response, gen_csv, gen_xlsx
from utils.functions import gen_query, clear_empty, json2mdict, json2mdict_pop
from utils.functions import update_model_with_fields, m2dict, copy_and_update_model, common_poplist
from utils.functions import gen_query
from utils.base import Dict, DictNone

from blueprints.finance.action import FinanceAction
import settings


bp_finance_stat = Blueprint("finance_stat", __name__)



"""
出入库统计-订单类型.
    +入库物料表
    +成品入库物料表
    +采购入库物料表
    +出库物料表
    +生产出库物料表
    +销售出库物料表

    
生产,采购,销售的统计可以通过出入库的订单类型得到, 也可以通过直接统计对应单据得到
"""

SIL = StockinLine
SI = Stockin
SIT = StockinLineTrans

SOL = StockoutLine
SO = Stockout
SOT = StockoutLineTrans


# 入库物料表
@bp_finance_stat.route('/goods/stockin', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@bp_finance_stat.route('/goods/stockin/detail', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def goods_stockin_api(money_id=None):
    """
    req json:
    {
        order_type: Stockin.xtype
        time_type: 订单创建时间 create_time, 订单完结时间 finish_time, 物料入库时间 in_time
        group_by: ['supplier_code', 'quality_type', 'spec']
        page: 1
        per_page: 20
    }
    resp:
    {
      "num_results": pagin.total,
      "total_pages": pagin.pages,
      "page": pagin.page,
      "per_page": pagin.per_page,
      "objects": objects
    }
    """
    # 有 订单创建时间 create_time, 订单完结时间 finish_time, 物料入库时间 in_time
    xargs = request.json or request.args.to_dict()

    time_type = xargs.get('time_type', 'create_time')
    order_type = xargs.get('order_type', None)
    date1 = (xargs.get('date1', None) or datetime.now().strftime('%Y-%m-01'))[:10]
    date2 = (xargs.get('date2', None) or datetime.now().strftime('%Y-%m-%d'))[:10]
    qstr = xargs.get('qstr', None)

    f_qty = func.sum(SIL.qty_real).label('qty_real')
    f_price = func.sum(SIL.qty_real*SIL.price).label('price')
    query = StockinLine.query.t_query.with_entities(
                SIL.id,
                SIL.sku, 
                SIL.barcode, 
                SIL.name, 
                SIL.supplier_code,
                SIL.quality_type,
                SIL.spec,
                func.sum(SIL.qty).label('qty'), 
                f_qty, 
                f_price,
                Stockin.create_time,
                Stockin.partner_code,
                Stockin.partner_name,
                SIL.price.label('price_one'),
                SIL.qty.label('qty_plan'),)
    query = query.filter(StockinLine.stockin_id==Stockin.id)
    query = query.filter(Stockin.state!='cancel')
    if qstr:
        query = query.filter(or_(StockinLine.sku.like('%%%s%%'%qstr), StockinLine.name.like('%%%s%%'%qstr)))


    if order_type:
        query = query.filter(Stockin.xtype==order_type)

    if time_type == 'create_time':
        if date1:
            query = query.filter(Stockin.create_time>=date1)
        if date2:
            query = query.filter(func.date_format(Stockin.create_time, '%Y-%m-%d') <= date2)

    if time_type == 'finish_time':
        if date1:
            query = query.filter(Stockin.date_finished>=date1)
        if date2:
            query = query.filter(func.date_format(Stockin.date_finished, '%Y-%m-%d') <= date2)

    if time_type == 'in_time':
        f_qty = func.sum(SIT.qty_real).label('qty_real')
        f_price = func.sum(SIT.qty_real*SIL.price).label('price')
        query = SIT.query.with_entities(
                SIL.id,
                SIL.sku, 
                SIL.barcode, 
                SIL.name, 
                SIL.supplier_code,
                SIL.quality_type,
                SIL.spec,
                func.sum(SIT.qty).label('qty'),  # 无用
                f_qty, 
                f_price)
        query = query.filter(SIT.stockin_id==Stockin.id, SIT.stockin_line_id==StockinLine.id)
        query = query.filter(SI.company_code==g.company_code, SI.warehouse_code==g.warehouse_code, SI.owner_code==g.owner_code)
        if date1:
            query = query.filter(SIT.create_time>=date1)
        if date2:
            query = query.filter(func.date_format(SIT.create_time, '%Y-%m-%d') <= date2)
        if order_type:
            query = query.filter(Stockin.xtype==order_type)


    group_by = xargs.get('group_by', None) or [] #['supplier_code', 'quality_type', 'spec']
    groups = []
    if 'supplier_code' in group_by:
        groups.append(StockinLine.supplier_code)
    if 'quality_type' in group_by:
        groups.append(StockinLine.quality_type)
    if 'spec' in group_by:
        groups.append(StockinLine.spec)
    if 'both' in group_by:
        groups.append(StockinLine.supplier_code)
        groups.append(StockinLine.spec)

    query = query.group_by(SIL.sku, *groups)
    query = query.having(f_qty > 0)

    if '/detail' in request.path:
        sku = request.args.get('sku', '')
        if sku:
            query = query.filter(SIL.sku==sku)
        detail_list = query.group_by(Stockin.id).all()
        return json_response({'objects':[d._asdict() for d in detail_list]})

    o = query.group_by(None).first()
    amount = (o.price or 0) if o else 0

    query = query.order_by(f_qty.desc())
    order_by = xargs.get('order_by', [])
    if order_by:
        orderby = DictNone(order_by[0])
        query = query.order_by(None)
        if orderby.field == 'qty_real':
            query = query.order_by(f_qty.asc() if orderby.direction == 'asc' else f_qty.desc())
        elif orderby.field == 'price':
            query = query.order_by(f_price.asc() if orderby.direction == 'asc' else f_price.desc())

    page, per_page = xargs.get('page', 1), xargs.get('per_page', settings.PER_PAGE)
    pagin = query.paginate(page, per_page=per_page)

    objects = []
    g1, g2, g3 = 'supplier_code' in group_by or 'both' in group_by, 'quality_type' in group_by, 'spec' in group_by or 'both' in group_by
    for i in pagin.items:
        if not i.id or not i.qty_real:
            continue
        o = DictNone()
        o.id = i.id
        o.sku = i.sku
        o.barcode = i.barcode
        o.name = i.name
        o.supplier_code = i.supplier_code if g1 else ''
        o.quality_type = i.quality_type if g2 else ''
        o.spec = i.spec if g3 else ''
        o.qty = i.qty
        o.qty_real = i.qty_real
        o.price = i.price
        objects.append(o)

    if xargs.get('export', None) == 'xlsx':
        title = [u'货品码', u'条码', u'名称', u'供应商', u'规格', u'入库数量', u'总价',]
        keys = 'sku,barcode,name,supplier_code,spec,qty_real,price'.split(',')
        table = [[getattr(o, k, '') for k in keys] for o in objects]
        return gen_xlsx(title, table, fname=u'入库单统计')

    ret =  {
      "num_results": pagin.total,
      "total_pages": pagin.pages,
      "page": pagin.page,
      "per_page": pagin.per_page,
      "objects": objects,
      'amount': amount,
    }

    return json_response(ret, indent=4)



# 出库物料表
@bp_finance_stat.route('/goods/stockout', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@bp_finance_stat.route('/goods/stockout/detail', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def goods_stockout_api(money_id=None):
    """
    req json:
    {
        order_type: Stockout.order_type
        time_type: 订单创建时间 create_time, 订单完结时间 finish_time, 物料出库时间 out_time
        group_by: ['supplier_code', 'quality_type', 'spec']
        page: 1
        per_page: 20
    }
    resp:
    {
      "num_results": pagin.total,
      "total_pages": pagin.pages,
      "page": pagin.page,
      "per_page": pagin.per_page,
      "objects": objects
    }
    """
    # 有 订单创建时间 create_time, 订单完结时间 finish_time, 物料出库时间 out_time
    xargs = request.json or request.args.to_dict()

    time_type = xargs.get('time_type', 'create_time')
    order_type = xargs.get('order_type', None)
    date1 = (xargs.get('date1', None) or datetime.now().strftime('%Y-%m-01'))[:10]
    date2 = (xargs.get('date2', None) or datetime.now().strftime('%Y-%m-%d'))[:10]
    qstr = xargs.get('qstr', None)

    f_qty = func.sum(SOL.qty_pick).label('qty_real')
    f_price = func.sum(SOL.qty_pick*SOL.price).label('price')
    query = StockoutLine.query.t_query.with_entities(
                SOL.id,
                SOL.sku, 
                SOL.barcode, 
                SOL.name, 
                SOL.supplier_code,
                SOL.spec,
                func.sum(SOL.qty).label('qty'), 
                f_qty, 
                f_price,
                Stockout.create_time,
                Stockout.partner_code,
                Stockout.partner_name,
                SOL.price.label('price_one'),
                SOL.qty.label('qty_plan'),)
    query = query.filter(StockoutLine.stockout_id==Stockout.id)
    query = query.filter(Stockout.state!='cancel')
    if qstr:
        query = query.filter(or_(StockoutLine.sku.like('%%%s%%'%qstr), StockoutLine.name.like('%%%s%%'%qstr)))

    if order_type:
        query = query.filter(Stockout.order_type==order_type)

    if time_type == 'create_time':
        if date1:
            query = query.filter(Stockout.create_time>=date1)
        if date2:
            query = query.filter(func.date_format(Stockout.create_time, '%Y-%m-%d') <= date2)

    if time_type == 'finish_time':
        if date1:
            query = query.filter(Stockout.date_finished>=date1)
        if date2:
            query = query.filter(func.date_format(Stockout.date_finished, '%Y-%m-%d') <= date2)

    if time_type == 'out_time':
        f_qty = func.sum(SOT.qty).label('qty_real')
        f_price = func.sum(SOT.qty*SOL.price).label('price')
        query = SOT.query.with_entities(
                SOL.id,
                SOL.sku, 
                SOL.barcode, 
                SOL.name, 
                SOL.supplier_code,
                SOL.spec,
                func.sum(SOL.qty).label('qty'), # 无用
                f_qty, 
                f_price)
        query = query.filter(SOT.stockout_id==Stockout.id, SOT.stockout_line_id==StockoutLine.id)
        query = query.filter(SO.company_code==g.company_code, SO.warehouse_code==g.warehouse_code, SO.owner_code==g.owner_code)
        if date1:
            query = query.filter(SOT.create_time>=date1)
        if date2:
            query = query.filter(func.date_format(SOT.create_time, '%Y-%m-%d') <= date2)
        query = query.filter(SOT.xtype=='pick')
        if order_type:
            query = query.filter(Stockout.order_type==order_type)


    group_by = xargs.get('group_by', None) or [] #['supplier_code', 'quality_type', 'spec']
    groups = []
    if 'supplier_code' in group_by:
        groups.append(StockoutLine.supplier_code)
    if 'spec' in group_by:
        groups.append(StockoutLine.spec)
    if 'both' in group_by:
        groups.append(StockinLine.supplier_code)
        groups.append(StockinLine.spec)

    query = query.group_by(SOL.sku, *groups)
    query = query.having(f_qty > 0)

    if '/detail' in request.path:
        sku = request.args.get('sku', '')
        if sku:
            query = query.filter(SOL.sku==sku)
        detail_list = query.group_by(Stockout.id).all()
        return json_response({'objects':[d._asdict() for d in detail_list]})

    o = query.group_by(None).first()
    amount = (o.price or 0) if o else 0

    query = query.order_by(f_qty.desc())
    order_by = xargs.get('order_by', [])
    if order_by:
        orderby = DictNone(order_by[0])
        query = query.order_by(None)
        if orderby.field == 'qty_real':
            query = query.order_by(f_qty.asc() if orderby.direction == 'asc' else f_qty.desc())
        elif orderby.field == 'price':
            query = query.order_by(f_price.asc() if orderby.direction == 'asc' else f_price.desc())

    page, per_page = xargs.get('page', 1), xargs.get('per_page', settings.PER_PAGE)
    pagin = query.paginate(page, per_page=per_page)
    # print(query.real_sql(), '=======', date1, date2)

    objects = []
    g1, g3 = 'supplier_code' in group_by or 'both' in group_by, 'spec' in group_by or 'both' in group_by
    for i in pagin.items:
        if not i.id or not i.qty_real:
            continue
        o = DictNone()
        o.id = i.id
        o.sku = i.sku
        o.barcode = i.barcode
        o.name = i.name
        o.supplier_code = i.supplier_code if g1 else ''
        o.spec = i.spec if g3 else ''
        o.qty = i.qty
        o.qty_real = i.qty_real
        o.price = i.price
        objects.append(o)

    if xargs.get('export', None) == 'xlsx':
        title = [u'货品码', u'条码', u'名称', u'供应商', u'规格', u'出库数量', u'总价',]
        keys = 'sku,barcode,name,supplier_code,spec,qty_real,price'.split(',')
        table = [[getattr(o, k, '') for k in keys] for o in objects]
        return gen_xlsx(title, table, fname=u'出库单统计')

    ret =  {
      "num_results": pagin.total,
      "total_pages": pagin.pages,
      "page": pagin.page,
      "per_page": pagin.per_page,
      "objects": objects,
      'amount':amount,
    }

    return json_response(ret, indent=4)



# 客户财务费用汇总
@bp_finance_stat.route('/partner/summary', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def partner_summary_api(year=None):
    xargs = request.args
    query = Money.query.t_query.filter(Money.state!='cancel')

    f_amount = func.sum(Money.amount).label('amount')
    f_real = func.sum(Money.real).label('real')
    f_bad = func.sum(Money.bad).label('bad')
    f_unreal = func.sum(Money.amount - Money.real).label('unreal')

    subq = query.with_entities(f_amount, f_real, f_unreal, Money.partner_code, Money.id.label('id'))
    subq = gen_query(request.args.get('q', None), subq, Money, db=db, export=True)

    data = subq.group_by(Money.partner_code).order_by(f_amount).all()
    sum_data = subq.first()
    objects = [{'amount': d.amount, 'real': d.real, 'unreal': d.unreal, 'partner_code': d.partner_code, 'id': d.id} for d in data]

    if xargs.get('export', None) == 'xlsx':
        come = xargs.get('come', 'income')
        comestr = u'客户应收统计' if come == 'income' else u'客户应付统计'
        title = [u'合作商', u'总额', u'实额', u'余额']
        keys = 'partner_code,amount,real,unreal'.split(',')
        table = [[o.get(k, '') for k in keys] for o in objects]
        table.append([u'总计', sum_data.amount, sum_data.real, sum_data.unreal])
        return gen_xlsx(title, table, fname=comestr)

    # result
    res = DictNone()
    res.objects = objects

    res.num_results = len(objects)
    res.total_pages = 1
    res.page = 1
    res.per_page = 50

    res.amount = sum_data.amount
    res.real = sum_data.real
    res.unreal = sum_data.unreal

    return  json_response(res)

