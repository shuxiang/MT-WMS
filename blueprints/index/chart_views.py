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
from models.finance import Money, MoneyLine, MoneySummary
from blueprints.inv.action import InvAction, InvCountAction, InvMoveAction, InvAdjustAction
from blueprints.index.action import IndexAction, ChartAction

from utils.flask_tools import json_response, gen_csv
from utils.functions import update_model_with_fields, m2dict, copy_and_update_model, common_poplist
from utils.functions import gen_query, DictNone
from utils.base import Dict
import settings

bp_chart = Blueprint("chart", __name__)



# 获取订单统计数据-订单状态数量统计
@bp_chart.route('/order/count', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def order_count_api():
    
    action = ChartAction()
    data = action.order_count(g.company_code, g.warehouse_code, g.owner_code)
    return json_response(data, indent=4)

# 获取订单统计数据-最近一年订单数量趋势
@bp_chart.route('/order/count/year', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def order_count_year_api():
    data = {'in': [], 'out': [], 'pd': [], 'pc': [], 'sale':[], 'pp':[]}
    now = datetime.now()
    week_ago = now.date() - timedelta(days=7)
    year_ago = now.date() - timedelta(days=365)

    # # SELECT DATE_FORMAT(create_time,'%Y-%m') AS t1, COUNT(1) AS num FROM i_stockin    GROUP BY  t1  

    in_query = Stockin.query.t_query
    mon = func.date_format(Stockin.create_time, '%Y-%m').label('mon')
    num = func.count(Stockin.id).label('num')
    in_data = {o.mon:o.num for o in in_query.with_entities(mon, num).filter(Stockin.create_time > year_ago).group_by(mon).all()}

    out_query = Stockout.query.t_query
    mon = func.date_format(Stockout.create_time, '%Y-%m').label('mon')
    num = func.count(Stockout.id).label('num')
    out_data = {o.mon:o.num for o in out_query.with_entities(mon, num).filter(Stockout.create_time > year_ago).group_by(mon).all()}

    keys = sorted(list(set(in_data.keys()+out_data.keys())))
    for k in keys:
        if k not in in_data:
            in_data[k] = 0
        if k not in out_data:
            out_data[k] = 0
        data['in'].append(in_data[k])
        data['out'].append(out_data[k])

    data['category'] = keys
    #pprint(data)
    return json_response(data, indent=4)

# 获取订单统计数据-最近7天订单数量趋势
@bp_chart.route('/order/count/week', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def order_count_week_api():
    data = {'in': [], 'out': [], 'pd': [], 'pc': [], 'sale':[], 'pp':[]}
    now = datetime.now()
    week_ago = now.date() - timedelta(days=8)

    # # SELECT DATE_FORMAT(create_time,'%Y-%m') AS t1, COUNT(1) AS num FROM i_stockin    GROUP BY  t1  

    in_query = Stockin.query.t_query
    mon = func.date_format(Stockin.create_time, '%Y-%m-%d').label('mon')
    num = func.count(Stockin.id).label('num')
    in_data = {o.mon:o.num for o in in_query.with_entities(mon, num).filter(Stockin.create_time > week_ago).group_by(mon).all()}

    out_query = Stockout.query.t_query
    mon = func.date_format(Stockout.create_time, '%Y-%m-%d').label('mon')
    num = func.count(Stockout.id).label('num')
    out_data = {o.mon:o.num for o in out_query.with_entities(mon, num).filter(Stockout.create_time > week_ago).group_by(mon).all()}

    keys = sorted(list(set(in_data.keys()+out_data.keys())))
    for k in keys:
        if k not in in_data:
            in_data[k] = 0
        if k not in out_data:
            out_data[k] = 0
        data['in'].append(in_data[k])
        data['out'].append(out_data[k])

    real_keys = []
    real_data = {'in': [], 'out': [],}

    x = datetime.now().date() #datetime.strptime(keys[0], '%Y-%m-%d') if keys else datetime.now().date()

    for i in range(0, 7):
        k = str(x-timedelta(days=i))[:10]
        real_keys.insert(0, k)
        if k in keys:
            idx = keys.index(k)
            real_data['in'].insert(0, data['in'][idx])
            real_data['out'].insert(0, data['out'][idx])
        else:
            real_data['in'].insert(0, 0)
            real_data['out'].insert(0, 0)

    real_data['category'] = real_keys
    #pprint(data)
    return json_response(real_data, indent=4)


# 获取按业务日期分组, 最近8条数据汇总
@bp_chart.route('/money/count', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@bp_chart.route('/money/count/<mtype>', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def money_count_api(mtype='pay'):
    query = Money.query.t_query

    query = query.with_entities(
            func.sum(Money.amount).label('amount'), 
            func.sum(Money.real).label('real'), 
            func.sum(Money.bad).label('bad'), 
            func.sum(Money.amount-Money.real).label('un'),
            Money.date_forcount.label('date'),
        )

    if mtype == 'pay':
        query = query.filter(Money.come == 'outcome')
    elif mtype == 'recv':
        query = query.filter(Money.come == 'income')

    data = query.group_by(Money.date_forcount).order_by(Money.date_forcount.desc()).limit(10).all()

    xaxis = []
    amount_list = []
    real_list = []
    un_list = []

    for d in data:
        xaxis.append(d.date)
        amount_list.append(d.amount or 0)
        real_list.append(d.real or 0)
        un_list.append(d.un or 0)

    return json_response({'xaxis': xaxis, 'amount_list': amount_list, 'real_list': real_list, 'un_list': un_list})

