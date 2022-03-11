#coding=utf8

import json
from flask import g, session
from hashlib import sha256
from datetime import datetime, timedelta

from sqlalchemy import func, or_
from utils.base import Dict, DictNone

from extensions.database import db
from models.auth import User, Company
from models.finance import Money, MoneyLine, MoneyAccount


class FinanceAction(object):

    def __init__(self):
        pass

    # 按 月/收入支出/费用类型 进行统计
    def summary(self, month=None, xtype=None, come=None, xtype_group=True):
        query = Money.query.with_entities(
                Money.id,
                Money.xtype, 
                Money.come, 
                func.sum(Money.amount).label('amount'), 
                func.sum(Money.real).label('real'),
                func.sum(Money.bad).label('bad'),
            ).t_query
        # 统计查询的月份
        if month:
            month = datetime.strptime(month[:7], '%Y-%m')
            _next = (month + timedelta(days=32))
            nextm = datetime.strptime("%d-%02d"%(_next.year, _next.month), '%Y-%m')
            query = query.filter(Money.date_forcount >= month, Money.date_forcount < nextm)
        # 默认统计当月
        else:
            now = datetime.now()
            month = datetime.strptime("%d-%02d"%(now.year, now.month), '%Y-%m')
            query = query.filter(Money.date_forcount >= month)
        if xtype:
            query = query.filter_by(xtype=xtype)
        if come:
            query = query.filter_by(come=come)

        table = []
        month = str(month)[:7]
        # 统计收支
        if not come:
            if xtype:
                income = query.filter_by(come='income').first()
                outcome = query.filter_by(come='outcome').first()

                d = Dict()
                d.amount = income.amount or 0
                d.real = income.real or 0
                d.month_real = self.month_real(month, xtype=xtype, come=income.come)
                d.xtype = xtype
                d.month = month
                d.come = 'income'
                d.x = True
                d.id = 'xin'
                table.append(d)

                d = Dict()
                d.amount = outcome.amount or 0
                d.real = outcome.real or 0
                d.month_real = self.month_real(month, xtype=xtype, come=outcome.come)
                d.xtype = xtype
                d.month = month
                d.come = 'outcome'
                d.x = True
                d.id = 'xout'
                table.append(d)
            else:
                income = query.filter_by(come='income').group_by(Money.xtype if xtype_group else None).all()
                outcome = query.filter_by(come='outcome').group_by(Money.xtype if xtype_group else None).all()

                for o in income:
                    d = Dict()
                    d.amount = o.amount or 0
                    d.real = o.real or 0
                    d.month_real = self.month_real(month, xtype=o.xtype, come=o.come)
                    d.xtype = o.xtype
                    d.month = month
                    d.come = 'income'
                    d.x = False
                    d.id = o.id
                    table.append(d)

                for o in outcome:
                    d = Dict()
                    d.amount = o.amount or 0
                    d.real = o.real or 0
                    d.month_real = self.month_real(month, xtype=o.xtype, come=o.come)
                    d.xtype = o.xtype
                    d.month = month
                    d.come = 'outcome'
                    d.x = False
                    d.id = o.id
                    table.append(d)
                # 总计
                income2 = query.filter_by(come='income').first()
                outcome2 = query.filter_by(come='outcome').first()

                month_real1 = 0
                d = Dict()
                d.amount = income2.amount or 0
                d.real = income2.real or 0
                d.month_real = month_real1 = self.month_real(month, come=income2.come)
                d.xtype = ''
                d.month = month
                d.come = 'income'
                d.x = True
                d.id = 'xin'
                table.append(d)

                month_real2 = 0
                d = Dict()
                d.amount = outcome2.amount or 0
                d.real = outcome2.real or 0
                d.month_real = month_real2 = self.month_real(month, come=outcome2.come)
                d.xtype = ''
                d.month = month
                d.come = 'outcome'
                d.x = True
                d.id = 'xout'
                table.append(d)

                d = Dict()
                d.amount = (income2.amount or 0) - (outcome2.amount or 0)
                d.real = (income2.real or 0) - (outcome2.real or 0)
                d.month_real = float(month_real1) - float(month_real2)
                d.xtype = u'毛利'
                d.month = month
                d.come = '毛利'
                d.x = True
                d.id = 'xsum'
                table.append(d)
        # only
        else:
            if xtype:
                xcome = query.first()

                d = Dict()
                d.amount = xcome.amount or 0
                d.real = xcome.real or 0
                d.month_real = self.month_real(month, xtype=xtype, come=come)
                d.xtype = xtype
                d.month = month
                d.come = come
                d.x = True
                d.id = 'x'
                table.append(d)
            else:
                xcome = query.group_by(Money.xtype if xtype_group else None).all()

                for o in xcome:
                    d = Dict()
                    d.amount = o.amount or 0
                    d.real = o.real or 0
                    d.month_real = self.month_real(month, xtype=o.xtype, come=come)
                    d.xtype = o.xtype
                    d.month = month
                    d.come = come
                    d.x = False
                    d.id = o.id
                    table.append(d)
                # 总计
                xcome2 = query.first()

                d = Dict()
                d.amount = xcome2.amount or 0
                d.real = xcome2.real or 0
                d.month_real = self.month_real(month, come=come)
                d.xtype = ''
                d.month = month
                d.come = come
                d.x = True
                d.id = 'x'
                table.append(d)


        return table, month

    # 获取当月款项的流水统计
    def month_real(self, month, xtype=None, come=None, money_id=None):
        query = MoneyLine.query.with_entities(func.sum(MoneyLine.real).label('real')) \
                .filter(func.date_format(MoneyLine.create_time, '%Y-%m')==month) \
                .filter(Money.id==MoneyLine.money_id)
        if money_id:
            query = query.filter(MoneyLine.money_id==money_id)
        if xtype:
            query = query.filter(Money.xtype==xtype)
        if come:
            query = query.filter(Money.come==come)

        ml = query.first()
        return ml.real if ml and ml.real else 0.00

    # 款项流水, is_partdone 只付一部分钱, 后面的钱收不回来了
    def do_money_trans(self, real, money, ref_user_code=None, remark='', is_partdone=False, account_longname=''):
        if float(real or 0) >= 0:
            # incr
            money.real = (money.real or 0) + real
            # done
            if money.real >= float(money.amount):
                money.state = 'done'
                money.date_finished = db.func.current_timestamp()
            elif is_partdone:
                money.state = 'partdone'
                bad = float(money.amount) - float(money.real)
                money.bad = bad if bad > 0 else 0
            else:
                money.state = 'doing'
            # trans
            line = MoneyLine(company_code=money.company_code, warehouse_code=money.warehouse_code, owner_code=money.owner_code,
                real=real, ref_user_code=ref_user_code or money.ref_user_code, user_code=g.user.code, remark=remark)
            db.session.add(line)
            line.money = money
            line.account_longname = account_longname
            if account_longname:
                account = MoneyAccount.query.t_query.filter_by(longname=account_longname).first()
                if account:
                    line.account_id = account.id

            return True

        return False

