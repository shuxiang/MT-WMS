#coding=utf8
__all__ = ['MoneyLine', 'Money', 'MoneySummary', ]
import os
from hashlib import sha256
from flask_login import UserMixin
from sqlalchemy.sql import text
from sqlalchemy import func, or_
from datetime import datetime
import base64
from uuid import uuid4
from hashlib import sha256
from sqlalchemy import Index, UniqueConstraint

from flask import g

from extensions.database import db
from extensions.permissions import ROLES_PERM

import settings


# 费用
class Money(db.Model):
    __tablename__ = 'f_money'
    __table_args__ = (
            Index("ix_f_code", "company_code", 'warehouse_code', 'owner_code', 'code'),
            Index("ix_f_tenant", "company_code", 'warehouse_code', 'owner_code'),
        )

    __table_args__ = (
                      Index("ix_money_tenant", "company_code", 'warehouse_code', "owner_code",),
                      )

    id = db.Column(db.Integer(), primary_key=True)
    # 公司
    owner_code = db.Column(db.String(50))
    company_code = db.Column(db.String(50))
    warehouse_code = db.Column(db.String(50))

    # 收款方式
    pay_type = db.Column(db.String(50), default='', server_default='')
    
    # 单号
    code = db.Column(db.String(100), server_default='')
    # 副单号
    subcode = db.Column(db.String(100), server_default='')

    # 客户
    partner_id = db.Column(db.Integer)
    partner_code = db.Column(db.String(50))
    partner_str  = db.Column(db.String(50))
    partner_name = db.Column(db.String(50), default='', server_default='')

    contact_name = db.Column(db.String(20))
    contact_tel  = db.Column(db.String(20))
    # 销售单/in sale 生产单/out produce 采购单/out purchase 入库单/inout stockin 出库单/inout stockout 物流快递/out express 
    # 工资/out salary 吃饭/out eat 住宿/out live 差旅/out trip 打车/out car 其它/inout other 发票/inout invoice 
    # 退销单pay/out salereturn 退采单recv/in purchasereturn
    xtype = db.Column(db.String(20))
    # 总额
    amount = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0.00)
    # 烂账金额
    bad = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0.00)
    # 实收/实付
    real = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0.00)
    # 经手/相关人, 发工资/报销等用
    ref_user_code = db.Column(db.String(20))
    # 收入income/支出outcome
    come = db.Column(db.String(20), server_default='income')
    # 支票/发票地址(图片地址)
    invoice_type = db.Column(db.String(50), default="VAT") # 增值税发票VAT, 多种类型
    invoice_no   = db.Column(db.String(50)) # 发票号, 
    invoice_url  = db.Column(db.String(50)) # 发票图片地址
    # 确认状态, 创建可修改create, 进行中doing, 确认完成done, 取消cancel, 只付一部分钱后面的钱收不回来了=> partdone
    state = db.Column(db.String(20), server_default='create', default='create')
    # 付清时间/完结时间
    date_finished = db.Column(db.DateTime)
    # 记账日, 帐目算到那一天的
    date_forcount = db.Column(db.Date, default=db.default_datetime())

    # 操作人/审核人
    user_code = db.Column(db.String(20))
    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())

    __dump_prop__ = ('is_clear', )

    @property
    def company(self):
        Company = db.M('Company')
        return Company.query.filter_by(code=self.company_code).first()

    # 该月的实收数目
    def month_real(self, month):
        ml = MoneyLine.query.with_entities(func.sum(MoneyLine.real).label('real')) \
                .filter(MoneyLine.money_id==self.id, func.date_format(MoneyLine.create_time, '%Y-%m')==month).first()
        return ml.real if ml and ml.real else 0.00

    @property
    def is_clear(self):
        if self.state=='done' or self.amount == self.real:
            return True
        return False

    @is_clear.setter
    def is_clear(self, val):
        # 一次性结清, 无流水
        if val:
            real = float(self.amount) - float(self.real or 0)
            # self.real = self.amount
            # self.state = 'done'
            # self.date_finished = db.func.current_timestamp()# self.date_forcount or db.func.current_timestamp()

            from blueprints.finance.action import FinanceAction
            action = FinanceAction()

            # (real, money, ref_user_code=None, remark='')
            ok = action.do_money_trans(real, self, ref_user_code=(g.user.code if g.user else self.user_code), remark='pay clear')
            return ok

        return False



# 费用流水
class MoneyLine(db.Model):
    __tablename__ = 'f_money_line'
    __table_args__ = (
            Index("ix_fl_tenant", "company_code", 'warehouse_code', 'owner_code'),
        )

    __table_args__ = (
                      Index("ix_money_line_tenant", "company_code", 'warehouse_code', "owner_code",),
                      )

    id = db.Column(db.Integer(), primary_key=True)
    # 公司
    owner_code = db.Column(db.String(50))
    company_code = db.Column(db.String(50))
    warehouse_code = db.Column(db.String(50))
    
    money_id = db.Column(db.Integer, db.ForeignKey("f_money.id"))
    # 实收/实付
    real = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0.00)
    # 相关人, 发工资/报销等用
    ref_user_code = db.Column(db.String(20))

    account_id = db.Column(db.Integer, server_default='0')
    account_longname = db.Column(db.String(255), server_default='')

    # 操作人/审核人
    user_code = db.Column(db.String(20))
    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())

    money = db.relationship("Money", backref=db.backref('lines', lazy='dynamic'))

    @property
    def company(self):
        Company = db.M('Company')
        return Company.query.filter_by(code=self.company_code).first()


# 费用统计
class MoneySummary(db.Model):
    __tablename__ = 'f_money_summary'
    __table_args__ = (
            Index("ix_fs_tenant", "company_code", 'warehouse_code', 'owner_code'),
        )

    __table_args__ = (
                      Index("ix_money_summary_tenant", "company_code", 'warehouse_code', "owner_code",),
                      )

    id = db.Column(db.Integer(), primary_key=True)
    # 公司
    owner_code = db.Column(db.String(50))
    company_code = db.Column(db.String(50))
    warehouse_code = db.Column(db.String(50))
    
    xtype = db.Column(db.String(20))
    # 总额
    amount = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)
    # 实收/实付
    real = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)
    # 收入income/支出outcome
    come = db.Column(db.String(20), server_default='income')
    # 月份
    month = db.Column(db.String(20), server_default='')

    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())


    @property
    def company(self):
        Company = db.M('Company')
        return Company.query.filter_by(code=self.company_code).first()


# 费用账户
class MoneyAccount(db.Model):
    __tablename__ = 'f_money_account'
    __table_args__ = (
            Index("ix_fa_tenant", "company_code", 'warehouse_code', 'owner_code'),
        )

    id = db.Column(db.Integer(), primary_key=True)
    # 公司
    owner_code = db.Column(db.String(50))
    company_code = db.Column(db.String(50))
    warehouse_code = db.Column(db.String(50))
    
    # 开户机构
    organ = db.Column(db.String(100))
    name = db.Column(db.String(100))
    account = db.Column(db.String(100))

    longname = db.Column(db.String(255))
    # #on/off
    state = db.Column(db.String(10), server_default='on')

    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())


    @property
    def company(self):
        Company = db.M('Company')
        return Company.query.filter_by(code=self.company_code).first()

    def set_longname(self):
        self.longname = "/".join([self.organ, self.name, self.account])
        return self.longname

    