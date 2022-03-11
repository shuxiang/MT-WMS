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
from models.stockin import Stockin
from models.stockout import Stockout
from models.finance import Money, MoneySummary, MoneyAccount
from models.auth import Partner

from utils.flask_tools import json_response, gen_csv
from utils.functions import gen_query, clear_empty, json2mdict, json2mdict_pop
from utils.functions import update_model_with_fields, m2dict, copy_and_update_model, common_poplist
from utils.functions import gen_query
from utils.base import Dict, DictNone

from blueprints.finance.action import FinanceAction
import settings


bp_finance = Blueprint("finance", __name__)



# 获取订单统计数据-订单状态数量统计
@bp_finance.route('/money', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@bp_finance.route('/money/<int:money_id>', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def money_api(money_id=None):

    if request.method == 'GET':
        query = Money.query.t_query
        res = gen_query(request.args.get('q', None), query, Money, db=db, per_page=settings.PER_PAGE)

        subq = Money.query.with_entities(func.sum(Money.amount).label('amount'), func.sum(Money.real).label('real'), func.sum(Money.bad).label('bad')).t_query
        subq = gen_query(request.args.get('q', None), subq, Money, db=db, export=True)
        income = subq.filter_by(come='income').order_by(None).group_by(Money.come).first()
        outcome = subq.filter_by(come='outcome').order_by(None).group_by(Money.come).first()

        res['income_amount'] = income.amount if income else 0
        res['income_real']   = income.real if income else 0
        res['income_bad']    = income.bad if income else 0
        res['outcome_amount'] = outcome.amount if outcome else 0
        res['outcome_real']   = outcome.real if outcome else 0
        res['outcome_bad']    = outcome.bad if outcome else 0
        return  json_response(res)

    if request.method == 'POST':
        is_clear = request.json.pop('is_clear', False)
        date_forcount = request.json.pop('date_forcount', '')
        remark = request.json.pop('remark', '')
        m = Money(user_code=g.user.code, company_code=g.company_code, owner_code=g.owner_code, warehouse_code=g.warehouse_code, 
                **json2mdict_pop(Money, clear_empty(request.json)))
        m.code = m.code.strip()
        db.session.add(m)
        m.is_clear = is_clear
        m.date_forcount = date_forcount[:10] if  date_forcount else datetime.now().date()
        m.remark = remark
        if m.code:
            m.subcode = 'extra'
        if m.partner_code:
            _partner = Partner.query.c_query.filter_by(code=m.partner_code).first()
            if _partner:
                m.partner_str = '%s %s' % (_partner.name, _partner.tel or _partner.code)
                m.partner_name = _partner.name
                m.partner_id = _partner.id
            else:
                m.partner_str = m.partner_code
        db.session.commit()

        return json_response({'status': 'success', 'msg': 'ok', 'data': m.as_dict})

    if request.method == 'PUT':
        is_clear = request.json.pop('is_clear', False)
        date_forcount = request.json.pop('date_forcount', '')
        remark = request.json.pop('remark', '')
        request.json.pop('real', None)
        m = Money.query.t_query.filter_by(id=money_id).first()
        m.update(json2mdict_pop(Money, clear_empty(request.json, False)))
        m.code = m.code.strip()
        m.is_clear = is_clear
        m.date_forcount = date_forcount[:10] or datetime.now().date()
        m.remark = remark or m.remark
        if m.code:
            m.subcode = 'extra'
        if m.partner_code:
            _partner = Partner.query.c_query.filter_by(code=m.partner_code).first()
            if _partner:
                m.partner_str = '%s %s' % (_partner.name, _partner.tel or _partner.code)
                m.partner_name = _partner.name
                m.partner_id = _partner.id
            else:
                m.partner_str = m.partner_code
        db.session.commit()

        return json_response({'status': 'success', 'msg': 'ok',})

    if request.method == 'DELETE':
        m = Money.query.t_query.filter_by(id=money_id).with_for_update().first()
        if m.state == 'create':
            m.state = 'cancel'
        db.session.commit()

        return json_response({'status': 'success', 'msg': 'ok',})

    return ''


# 记录收款/付款流水
@bp_finance.route('/money/<action>/<int:money_id>', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def money_action_api(action, money_id=None):
    """
    post req:
        {real, money_id, ref_user_code, remark}
    """
    if request.method == 'POST':
        action = FinanceAction()

        money = Money.query.t_query.filter_by(id=money_id).first()
        # (real, money, ref_user_code=None, remark='')
        ok = action.do_money_trans(money=money, **clear_empty(request.json))
        db.session.commit()
        if ok:
            return json_response({'status': 'success', 'msg': 'ok'})
        else:
            return json_response({'status': 'fail', 'msg': u'请输入正确的数字'})

    return ''


# 记录收款/付款流水查询
@bp_finance.route('/money/trans/<int:money_id>', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def money_trans_api(money_id=None):

    m = Money.query.t_query.filter_by(id=money_id).first()
    data = [r.as_dict for r in m.lines]
    return json_response({'status': 'success', 'msg': u'ok', 'data': data})



# 获取订单统计数据-订单状态数量统计
@bp_finance.route('/money/summary', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def money_summary_api():

    if request.method == 'POST':
        month = request.json.get('month', None)
        xtype = request.json.get('xtype', None)
        come  = request.json.get('come', None)

        action = FinanceAction()
        table, month = action.summary(month=month, xtype=xtype, come=come)

        return json_response({'status': 'success', 'data': table, 'month': month, 'msg': 'ok'}, indent=4)

    return ''


# 按月份统计数据-最近12个月的数据
@bp_finance.route('/money/month/summary', methods=('GET', 'POST'))
@normal_perm.require()
def money_month_summary_api():
    action = FinanceAction()

    now = datetime.now()
    year_ago = now.date() - timedelta(days=365)

    mon = func.date_format(Money.date_forcount, '%Y-%m').label('mon')
    current_mon = now.strftime('%Y-%m')
    real = func.sum(Money.real).label('real')

    for m in Money.query.with_entities(Money.xtype, Money.come, mon).t_query.filter(Money.date_forcount > year_ago).group_by(Money.xtype, Money.come, mon).all():
        # print m.xtype, m.come, m.mon
        table1 = []
        table2 = []

        if MoneySummary.query.t_query.filter_by(xtype=m.xtype, come=m.come, month=m.mon).count() == 0:
            table1, month1 = action.summary(m.mon, m.xtype, m.come)
        if MoneySummary.query.t_query.filter_by(come=m.come, month=m.mon).count() == 0:
            table2, month2 = action.summary(m.mon, come=m.come)

        for t in table1+table2:
            if MoneySummary.query.t_query.filter_by(xtype=t.xtype, come=t.come, month=m.mon).count() == 0:
                ms = MoneySummary(company_code=g.company_code, owner_code=g.owner_code, warehouse_code=g.warehouse_code)
                # ms.real  = t.real
                ms.real  = t.month_real
                ms.amount = t.amount
                ms.xtype = t.xtype
                ms.come  = t.come
                ms.month = m.mon
                db.session.add(ms)
            # 当前月会刷新
            else:
                if m.mon == current_mon:
                    ms = MoneySummary.query.t_query.filter_by(xtype=t.xtype, come=t.come, month=m.mon).first()
                    ms.real = t.month_real
                    ms.amount = t.amount


    db.session.commit()

    data = DictNone({'in':[], 'out':[], 'in_real':[], 'out_real':[]})
    res = MoneySummary.query.t_query.filter(MoneySummary.month > year_ago.strftime('%Y-%m'), MoneySummary.xtype=='').order_by(MoneySummary.month.asc()).all()
    data.category = list(set([r.month for r in res]))
    data.category.sort()

    ind = {r.month:r for r in res if r.come == 'income'}
    outd = {r.month:r for r in res if r.come == 'outcome'}
    for c in data.category:
        d = ind.get(c, None)
        data['in'].append(d.amount if d else 0)
        data['in_real'].append(d.real if d else 0)

        d = outd.get(c, None)
        data['out'].append(d.amount if d else 0)
        data['out_real'].append(d.real if d else 0)

    return json_response(data, indent=4)


# 获取订单统计数据-订单状态数量统计
@bp_finance.route('/money/account', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@bp_finance.route('/money/account/<int:account_id>', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def money_account_api(account_id=None):

    if request.method == 'GET':
        query = MoneyAccount.query.t_query
        res = gen_query(request.args.get('q', None), query, MoneyAccount, db=db, per_page=settings.PER_PAGE)
        return  json_response(res)

    if request.method == 'POST':
        remark = request.json.pop('remark', '')
        m = MoneyAccount(company_code=g.company_code, owner_code=g.owner_code, warehouse_code=g.warehouse_code, 
                **json2mdict_pop(MoneyAccount, clear_empty(request.json)))
        db.session.add(m)
        m.remark = remark
        m.set_longname()
        db.session.commit()

        return json_response({'status': 'success', 'msg': 'ok', 'data': m.as_dict})

    if request.method == 'PUT':
        remark = request.json.pop('remark', '')
        m = MoneyAccount.query.t_query.filter_by(id=account_id).first()
        m.update(json2mdict_pop(MoneyAccount, clear_empty(request.json, False)))
        m.remark = remark or m.remark
        m.set_longname()
        db.session.commit()

        return json_response({'status': 'success', 'msg': 'ok',})

    if request.method == 'DELETE':
        m = MoneyAccount.query.t_query.filter_by(id=MoneyAccount_id).with_for_update().first()
        if m.state == 'on':
            m.state = 'off'
        db.session.commit()
        
        return json_response({'status': 'success', 'msg': 'ok',})

    return ''