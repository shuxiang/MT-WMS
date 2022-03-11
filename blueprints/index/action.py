#coding=utf8

import json
from flask import g, session
from hashlib import sha256
from datetime import datetime, timedelta

from sqlalchemy import func, or_
from utils.base import Dict, DictNone
from utils.functions import gen_query

from extensions.database import db
#from extensions.cacheext import cache

from models.auth import User, Company
from models.finance import Money, MoneyLine
from models.inv import Inv, Good, Category, InvRfid, GoodMap
from models.inv import InvMove, InvAdjust, InvCount
from models.warehouse import Location
from models.stockin import Stockin
from models.stockout import Stockout

import settings


class IndexAction(object):

    def __init__(self):
        pass


class ChartAction(object):

    def __init__(self):
        pass

    # 统计各种订单的统计数据
    # @cache.memoize(60*10), windows cython 不支持这种用法
    def order_count(self, company_code, warehouse_code, owner_code):
        data = {'in': {}, 'out': {},}
        week_ago = datetime.now().date() - timedelta(days=7)

        in_query = Stockin.query.t_query
        data['in']['create'] = in_query.filter_by(state='create').count()
        data['in']['cancel'] = in_query.filter_by(state='cancel').count()
        data['in']['doing'] = in_query.filter(Stockin.state.in_(['part', 'all'])).count()
        data['in']['done'] = in_query.filter(Stockin.state=='done').count()
        data['in']['all'] = in_query.count()
        data['in']['week'] = in_query.filter(Stockin.create_time > week_ago).count()

        out_query = Stockout.query.t_query
        data['out']['create'] = out_query.filter_by(state='create').count()
        data['out']['cancel'] = out_query.filter_by(state='cancel').count()
        data['out']['doing'] = out_query.filter(Stockout.state=='doing').count()
        data['out']['done'] = out_query.filter(Stockout.state=='done').count()
        data['out']['all'] = out_query.count()
        data['out']['week'] = out_query.filter(Stockout.create_time > week_ago).count()

        # +收款统计
        # +付款统计
        data['pay'] = {}
        data['recv'] = {}

        pay_query = Money.query.t_query.filter(Money.come=='outcome')
        data['pay']['create'] = pay_query.filter_by(state='create').count()
        data['pay']['doing'] = pay_query.filter_by(state='doing').count()
        data['pay']['done'] = pay_query.filter_by(state='done').count()
        data['pay']['partdone'] = pay_query.filter_by(state='partdone').count()
        data['pay']['cancel'] = pay_query.filter_by(state='cancel').count()
        data['pay']['amount'] = pay_query.with_entities(func.sum(Money.amount).label('amount')).first().amount
        data['pay']['real']   = pay_query.with_entities(func.sum(Money.real).label('real')).first().real
        data['pay']['bad']    = pay_query.with_entities(func.sum(Money.bad).label('bad')).first().bad
        # TODO 应该减掉烂帐与取消的
        data['pay']['diff']   = (data['pay']['amount'] or 0) - (data['pay']['real'] or 0)

        recv_query = Money.query.t_query.filter(Money.come=='income')
        data['recv']['create'] = recv_query.filter_by(state='create').count()
        data['recv']['doing'] = recv_query.filter_by(state='doing').count()
        data['recv']['done'] = recv_query.filter_by(state='done').count()
        data['recv']['partdone'] = recv_query.filter_by(state='partdone').count()
        data['recv']['cancel'] = recv_query.filter_by(state='cancel').count()
        data['recv']['amount'] = recv_query.with_entities(func.sum(Money.amount).label('amount')).first().amount
        data['recv']['real']   = recv_query.with_entities(func.sum(Money.real).label('real')).first().real
        data['recv']['bad']    = recv_query.with_entities(func.sum(Money.bad).label('bad')).first().bad
        # TODO 应该减掉烂帐与取消的
        data['recv']['diff']   = (data['recv']['amount'] or 0) - (data['recv']['real'] or 0)

        # +库存
        # +/库存告警
        data['inv'] = {}
        inv_query = Inv.query.t_query.filter(Inv.location_code!='PICK')
        qty_real = func.sum(Inv.qty_able).label('qty_real')
        data['inv']['all']  = inv_query.with_entities(func.sum(Inv.qty_able).label('all')).filter(Inv.qty_able>0).first().all or 0
        data['inv']['high'] = inv_query.with_entities(Inv.id, Good.max_qty, qty_real).filter(Inv.sku==Good.code, Inv.company_code==Good.company_code, Inv.owner_code==Good.owner_code) \
                .filter(Good.max_qty > 0).group_by(Inv.sku).having(qty_real>Good.max_qty).count()
        data['inv']['low']  = inv_query.with_entities(Inv.id, Good.min_qty, qty_real).filter(Inv.sku==Good.code, Inv.company_code==Good.company_code, Inv.owner_code==Good.owner_code) \
                .filter(Good.min_qty > 0).group_by(Inv.sku).having(qty_real<Good.min_qty).count()

        # +/库位
        # +主件统计配料统计
        # +导入导出, 功能移到历史里
        data['stock'] = {}
        data['stock']['loc']  = Location.query.w_query.count()
        data['stock']['good'] = Good.query.o_query.group_by(Good.code).count()
        data['stock']['mgood'] = GoodMap.query.o_query.group_by(GoodMap.code).count()
        data['stock']['subgood'] = GoodMap.query.o_query.group_by(GoodMap.subcode).count()

        return data