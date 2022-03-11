#coding=utf8
__all__ = ['Company', 'User', 'Partner', 'Big', 'Config', 'Seq', 'Did', 'Contact']
'''
company     -> user
            -> partner(owner)
'''
import os
from hashlib import sha256
from flask_login import UserMixin
from sqlalchemy.sql import text
from datetime import datetime
import base64
from uuid import uuid4
from hashlib import sha256
from sqlalchemy import Index, UniqueConstraint
from werkzeug.utils import cached_property

from extensions.database import db
from extensions.permissions import ROLES_PERM, VROLES
from utils.upload import get_oss_image

import settings


# 基础登录表， 以后可能独立一个数据库 ----------------------

class Company(db.Model):
    __bind_key__ = 'auth'
    __tablename__ = 'u_company'
    __table_args__ = (Index("ix_u_comp", "code",),
        )

    __table_args__ = (
                      Index("ix_company_code", "code",),
                      Index("ix_company_uniquekey", "uniquekey"),
                      )

    id = db.Column(db.Integer(), primary_key=True)
    code = db.Column(db.String(50), server_default=u'', unique=True)
    # 对外接口key
    apikey = db.Column(db.String(200), default='')
    # 共享仓key/公司唯一性key 用于给合作伙伴分享
    uniquekey = db.Column(db.String(200), default='')
    # deploy host for openresty reverse proxy
    host = db.Column(db.String(250), server_default='')

    name = db.Column(db.String(250), server_default='')
    tel = db.Column(db.String(250), server_default='')
    email = db.Column(db.String(250), server_default='')
    contact = db.Column(db.String(250), server_default='')
    address = db.Column(db.String(250), server_default='')

    # 集团/组织, 可以多个, 逗号(,)隔开
    group = db.Column(db.String(255), server_default=u'')

    max_users = db.Column(db.Integer, default=0, server_default='0')

    # 图片
    image_url = db.Column(db.String(255), server_default='')
    # 是否已经初始化过了
    is_init = db.Column(db.Boolean, default=False, server_default='0')
    # 该公司单独的服务器地址
    server_url = db.Column(db.String(255), server_default='')
    # 代理商, 谁创建的
    agent = db.Column(db.String(20), server_default='admin')

    remark = db.Column(db.String(250), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())

    __dump_prop__ = ('image_path', )

    def __init__(self, *arg, **kw):
        self.uniquekey = str(uuid4()).upper()
        self.apikey = base64.urlsafe_b64encode(bytes(sha256((self.uniquekey+'-AddSomeSaltItsGood!').encode()).hexdigest(), 'utf8'))
        super(Company, self).__init__(*arg, **kw)

    @property
    def is_match_ow(self):
        return self.match_ow=='on'
    
    @property
    def users(self):
        return User.query.filter_by(company_code=self.code).all()

    @property
    def partners(self):
        return Partner.query.filter_by(company_code=self.code).all()

    @property
    def image_path(self):
        if self.image_url:
            get_oss_image(settings.UPLOAD_DIR, self.image_url, company_id=self.id)
        return self.image_url

    # 公司开通CRM/ERP, 并且用户也开通操作权才能进入系统
    @property
    def enable_crm(self):
        c = Config.query.filter_by(code='enable_crm', company_code=self.code).first()
        if c is None:
            return False
        return True if c and c.bool1 else False

    @property
    def enable_erp(self):
        c = Config.query.filter_by(code='enable_erp', company_code=self.code).first()
        if c is None:
            return False
        return True if c and c.bool1 else False
    
class User(db.Model, UserMixin):
    __bind_key__ = 'auth'
    __tablename__ = 'u_user'
    __table_args__ = (Index("ix_u_user", "company_code", 'code'),
        )

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), server_default='')
    password = db.Column(db.String(128), server_default='')

    xtype = db.Column(db.String(20), server_default='user')

    # 对外接口key
    _apikey = db.Column(db.String(200), name='apikey', default='')

    # 部门
    department = db.Column(db.String(250), server_default='')
    # +工号
    jobno = db.Column(db.String(250), server_default='')
    # +岗位
    post = db.Column(db.String(250), server_default='')
    
    name = db.Column(db.String(250), server_default='')
    tel = db.Column(db.String(250), server_default='')
    qq = db.Column(db.String(20), server_default='')
    wx = db.Column(db.String(20), server_default='')
    email = db.Column(db.String(250), server_default='')
    contact = db.Column(db.String(250), server_default='')
    address = db.Column(db.String(250), server_default='')
    state = db.Column(db.Enum('ban', 'delete', 'on'), server_default='on')
    # perms
    roles = db.Column(db.String(250), server_default='normal', default='normal')
    # view roles 视图角色, 控制页面功能是否显示, 不同于权限perms; 
    # 老板boss 管理员manager 财务finance 仓库stock 销售sale 采购purchase
    vroles = db.Column(db.String(250), server_default='stock', default='stock')
    # 菜单权限
    menus = db.Column(db.String(2000), server_default='', default='')

    # 特殊用户, xtype=client, 所属的partner
    partner_id = db.Column(db.Integer)
    partner_code = db.Column(db.String(50), default='')
    partner_name = db.Column(db.String(50), default='')

    receiver_name    = db.Column(db.String(50), server_default='')
    receiver_tel     = db.Column(db.String(50), server_default='')
    receiver_province = db.Column(db.String(250), server_default='')
    receiver_city     = db.Column(db.String(250), server_default='')
    receiver_area     = db.Column(db.String(250), server_default='')
    receiver_town     = db.Column(db.String(250), server_default='')
    receiver_address = db.Column(db.String(250), server_default='')

    # 能管理的货主和仓库
    owners = db.Column(db.String(255), server_default='')
    warehouses = db.Column(db.String(255), server_default='')
    factories = db.Column(db.String(255), server_default='')

    company_code = db.Column(db.String(50))

    remark = db.Column(db.String(250), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())


    __dump_prop__ = ('is_employee', 'is_manager', 'is_admin', 'is_agent', 'is_monitor', 'is_bank', 'is_park', 'is_client',)


    def __init__(self, *arg, **kw):
        self.apikey
        super(User, self).__init__(*arg, **kw)

    @cached_property
    def company_id(self):
        return self.company.id

    @property
    def apikey(self):
        if not self._apikey:
            k = str(uuid4()).upper()
            self._apikey = base64.urlsafe_b64encode(bytes(sha256((k+'-AddSomeSaltItsGood!').encode()).hexdigest(), 'utf8'))
        return self._apikey

    @apikey.setter
    def apikey(self, v):
        self._apikey = v

    @property
    def company(self):
        return Company.query.filter_by(code=self.company_code).first()

    @property
    def get_owners(self):
        owners = self.owners.split(',') if self.owners else ['default']
        M = db.M('Partner')
        return M.query.filter_by(company_code=self.company_code).filter(M.code.in_(owners)).all()

    @property
    def get_warehouses(self):
        whs = self.warehouses.split(',') if self.warehouses else ['default']
        M = db.M('Warehouse')
        return M.query.filter_by(company_code=self.company_code).filter(M.code.in_(whs)).all()

    @property
    def get_factories(self):
        whs = self.factories.split(',') if self.factories else ['default']
        return []

    @property
    def get_perms(self):
        return self.roles.split(',')

    def set_perm(self, perm):
        self.roles = ",".join(ROLES_PERM.get(perm, ['normal']))

    def del_perm(self, perm):
        perms = set(self.get_perms)
        perms.remove(perm)
        self.roles = ",".join(perms)

    @property
    def get_vroles(self):
        return self.vroles.split(',') if self.vroles else []

    def set_vrole(self, role):
        tmp = role
        if type(role) is not list:
            tmp = [role]
        self.vroles = ",".join([i for i in set(self.get_vroles + tmp) if i])

    def del_vrole(self, role):
        vroles = set(self.get_vroles)
        vroles.remove(role)
        self.vroles = ",".join(vroles)

    @property
    def get_menus(self):
        return self.menus.split(',') if self.menus else []

    def set_menu(self, menu):
        tmp = menu
        if type(menu) is not list:
            tmp = [menu]
        self.menus = ",".join(set(self.get_menus + tmp))

    def del_menus(self, menu):
        menus = set(self.get_menus)
        menus.remove(menu)
        self.menus = ",".join(menus)

    @property
    def is_manager(self):
        return self.roles and ('manager' in self.roles)

    @property
    def is_admin(self):
        return self.roles and ('admin' in self.roles)

    @property
    def is_employee(self):
        return self.roles and ('employee' in self.roles)

    @property
    def is_agent(self):
        return 'agent' in self.roles

    @property
    def is_monitor(self):
        return self.xtype == 'monitor'

    @property
    def is_bank(self):
        return self.xtype == 'bank'

    @property
    def is_park(self):
        return self.xtype == 'park'

    @property
    def is_client(self):
        return self.xtype == 'client'

    def set_password(self, password):
        self.password = sha256((password+'+SomeSaltToFoodIsDelicious!').encode()).hexdigest()

    @property
    def need_change_pwd(self):
        return self.password == sha256((self.code+'+SomeSaltToFoodIsDelicious!').encode()).hexdigest()


# 常用用户数据关联表，可能按公司进行分库/或者按公司+仓库进行分库 --------------------

class Partner(db.Model):
    __tablename__ = 'u_partner'
    __table_args__ = (Index("ix_u_partner_company", "company_code",),
                      Index("ix_u_partner_code", "company_code", "code",),
                      )

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), server_default='')
    
    name = db.Column(db.String(250), server_default='')
    # 手机
    tel = db.Column(db.String(250), server_default='')
    # 电话
    phone = db.Column(db.String(250), server_default='')
    email = db.Column(db.String(250), server_default='')
    # 联系人
    contact = db.Column(db.String(250), server_default='')
    # 联系人地址
    address = db.Column(db.String(250), server_default='')
    # 公司名称, 用于个人客户对方手动填写, laoa
    company_name = db.Column(db.String(250), server_default='')

    # 是否启用电子面单 on/off
    express_on = db.Column(db.String(50), server_default='off', default='off')
    # 默认物流类型 kdniao/jd/cainiao/pdd
    express_type = db.Column(db.String(50), server_default='')
    # 默认物流公司
    express_code = db.Column(db.String(250), server_default='')
    express_name = db.Column(db.String(250), server_default='')
    express_month_code = db.Column(db.String(250), server_default='')
    express_bid = db.Column(db.String(250), server_default='')
    express_appkey = db.Column(db.String(250), server_default='')
    express_secret = db.Column(db.String(250), server_default='')
    express_passwd = db.Column(db.String(250), server_default='')

    sender_name    = db.Column(db.String(50), server_default='')
    sender_tel     = db.Column(db.String(50), server_default='')
    sender_province = db.Column(db.String(250), server_default='')
    sender_city     = db.Column(db.String(250), server_default='')
    sender_area     = db.Column(db.String(250), server_default='')
    sender_town     = db.Column(db.String(250), server_default='')
    sender_address = db.Column(db.String(250), server_default='')

    receiver_name    = db.Column(db.String(50), server_default='')
    receiver_tel     = db.Column(db.String(50), server_default='')
    receiver_province = db.Column(db.String(250), server_default='')
    receiver_city     = db.Column(db.String(250), server_default='')
    receiver_area     = db.Column(db.String(250), server_default='')
    receiver_town     = db.Column(db.String(250), server_default='')
    receiver_address = db.Column(db.String(250), server_default='')

    # qimen
    qimen_type       = db.Column(db.String(250), server_default='json', default='json')
    qimen_url        = db.Column(db.String(250), server_default='')
    qimen_customerid = db.Column(db.String(250), server_default='')
    qimen_secret     = db.Column(db.String(250), server_default='')

    # 'owner', 'express', 'client', 'supplier', 'client_supplier'
    xtype = db.Column(db.String(50), default='owner')
    # inner / purchase 内采/外采
    stype = db.Column(db.String(50), server_default='purchase', default='purchase')

    company_code = db.Column(db.String(50))
    # 协同生产商的公司唯一识别码uniquekey
    coopkey = db.Column(db.String(200), default='')

    remark = db.Column(db.String(250), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())


    @property
    def company(self):
        return Company.query.filter_by(code=self.company_code).first()

    # 是否启用同步方式下载文件, 默认不启用
    @property
    def is_sync_downfile(self):
        c = Config.query.filter_by(code='sync_downfile', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return False
        return True if c and c.bool1 else False
    

    # 货主级别的超收设置
    @property
    def is_overcharge(self):
        c = Config.query.filter_by(code='overcharge', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return True
        return True if c and c.bool1 else False

    # 分开库存方式: 入库单号 order_code/入库日期 stockin_date/入库单号+日期 order_code_stockin_date/不分开 no_split /全新,完全分裂 new
    @property
    def split_inv_type(self):
        c = Config.query.filter_by(code='split_inv_type', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return 'new'
        return c.str1 if c and c.str1 else 'new'

    # 货主级别的部分分配设置, 默认可以部分分配
    @property
    def is_partalloc(self):
        c = Config.query.filter_by(code='partalloc', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return True
        return True if c and c.bool1 else False

    # 货主级别的拣货后直接关闭订单无发运流程配置, 默认直接关闭
    @property
    def is_close_when_pick(self):
        c = Config.query.filter_by(code='close_when_pick', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return True
        return True if c and c.bool1 else False

    # 货主级别的启用快速移库, 默认不启用
    @property
    def is_enable_fast_invmove(self):
        c = Config.query.filter_by(code='enable_fast_invmove', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return False
        return True if c and c.bool1 else False

    # 货主级别的启用财务, 默认不启用
    @property
    def is_enable_finance(self):
        c = Config.query.filter_by(code='enable_finance', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return False
        return True if c and c.bool1 else False

    # 货主级别的分配优先设置
    @property
    def auto_location_rules(self):
        # 规则顺序 int1, 规则名称 str1
        cs = Config.query.filter_by(code='auto_location_rules', owner_code=self.code, company_code=self.company_code) \
            .order_by(Config.int1.asc()).all()
        return cs

    # 货主级别的分配优先设置
    @property
    def alloc_rules(self):
        cs = Config.query.filter_by(code='alloc_rule', owner_code=self.code, company_code=self.company_code) \
            .order_by(Config.int1.asc()).all()
        return [c.str1 for c in cs]

    # 分配的库位, 所有 ALL,  临时 STAGE,  非临时 NO_STAGE , 非QC NO_QC, 非临时非QC NO_QC_STAGE
    @property
    def alloc_location(self):
        c = Config.query.filter_by(code='alloc_location', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return 'ALL'
        return c.str1

    # 推荐库位时, 不同订单类型, 推荐的库位所在的工作区
    @property
    def stockin_type_location(self):
        cs = Config.query.filter_by(code='stockin_type_location', owner_code=self.code, company_code=self.company_code) \
            .order_by(Config.index.asc()).all()
        return {c.str1: c.str2 for c in cs}

    # 指定出库时, 不同订单类型所操作的工作区
    @property
    def stockout_type_location(self):
        cs = Config.query.filter_by(code='stockout_type_location', owner_code=self.code, company_code=self.company_code) \
            .order_by(Config.index.asc()).all()
        return {c.str1: c.str2 for c in cs}

    # 出库单取消时, 已经拣货的库存处理方式
    @property
    def stockout_cancel_pick_inv_handle_type(self):
        # to_stage 放到stage库位； to_stockin 放到退库入库单; to_origin 原路归还,操作人员放回去
        c = Config.query.filter_by(code='stockout_cancel_pick_inv_handle_type', owner_code=self.code, company_code=self.company_code).first()
        return c.str1 if c else 'to_origin'

    # 拣货单打印排序 index_asc index_desc code_asc code_desc; default=code_asc
    @property
    def print_rule(self):
        c = Config.query.filter_by(code='print_rule', owner_code=self.code, company_code=self.company_code).first()
        return c.str1 if c else 'desc'

    @property
    def coop_sale_type(self):
        c = Config.query.filter_by(code='coop_sale_type', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return 'origin'
        return c.str1 if c else 'origin'

    # 是否启用逐个扫条码入库, 默认开启
    @property
    def is_scan_each_barcode(self):
        c = Config.query.filter_by(code='scan_each_barcode', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return True
        return True if c and c.bool1 else False

    # 是否启用非逐个扫条码入库, 默认不开启
    @property
    def is_scan_batch_barcode(self):
        c = Config.query.filter_by(code='scan_batch_barcode', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return False
        return True if c and c.bool1 else False

    # 是否使用扫描RFID入库
    @property
    def is_scan_rfid(self):
        c = Config.query.filter_by(code='scan_rfid', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return True
        return True if c and c.bool1 else False

    # 是否启用快速入库, 默认开启
    @property
    def is_enable_quick_in(self):
        c = Config.query.filter_by(code='enable_quick_in', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return True
        return True if c and c.bool1 else False

    @property
    def is_enable_fast_stockin_qty_inner(self):
        c = Config.query.filter_by(code='enable_fast_stockin_qty_inner', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return True
        return True if c and c.bool1 else False
    

    # 是否启用快速拣货, 默认开启
    @property
    def is_enable_quick_pick(self):
        c = Config.query.filter_by(code='enable_quick_pick', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return True
        return True if c and c.bool1 else False

    # 是否启用出库扫条码
    @property
    def is_enable_out_barcode(self):
        c = Config.query.filter_by(code='enable_out_barcode', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return False
        return True if c and c.bool1 else False

    # 是否启用出库逐个扫条码
    @property
    def is_enable_out_each_barcode(self):
        c = Config.query.filter_by(code='enable_out_each_barcode', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return True
        return True if c and c.bool1 else False

    # 是否启用出库逐个扫条码
    @property
    def is_enable_out_rfid(self):
        c = Config.query.filter_by(code='enable_out_rfid', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return True
        return True if c and c.bool1 else False

    # 是否启用快速拣货, 默认开启
    @property
    def is_enable_part_pick(self):
        c = Config.query.filter_by(code='enable_part_pick', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return True
        return True if c and c.bool1 else False

    # 是否启用库存告警, 默认关闭
    @property
    def is_enable_inv_warn(self):
        c = Config.query.filter_by(code='enable_inv_warn', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return True
        return True if c and c.bool1 else False

    # 是否启用库存冻结, 默认不开启
    @property
    def is_enable_inv_freeze(self):
        c = Config.query.filter_by(code='enable_inv_freeze', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return False
        return True if c and c.bool1 else False

    # 是否启用库存解冻, 默认关闭
    @property
    def is_enable_inv_unfreeze(self):
        c = Config.query.filter_by(code='enable_inv_unfreeze', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return False
        return True if c and c.bool1 else False

    # 是否启用容器, 主要是方便PDA的操作, 默认关闭
    @property
    def is_enable_lpn(self):
        c = Config.query.filter_by(code='enable_lpn', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return False
        return True if c and c.bool1 else False

    # 是否启用供应商作为批次
    @property
    def is_enable_supplier_batch(self):
        c = Config.query.filter_by(code='enable_supplier_batch', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return False
        return True if c and c.bool1 else False

    # 是否启用老菜单布局
    @property
    def is_enable_setting(self):
        c = Config.query.filter_by(code='enable_setting', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return True
        return True if c and c.bool1 else False

    # 启用搜索条
    @property
    def is_enable_search_bar(self):
        c = Config.query.filter_by(code='enable_search_bar', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return True
        return True if c and c.bool1 else False

    # 启用简洁模式
    @property
    def is_enable_simple_mode(self):
        c = Config.query.filter_by(code='enable_simple_mode', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return True
        return True if c and c.bool1 else False

    # 启用合单拣货
    @property
    def is_enable_stockout_merge(self):
        c = Config.query.filter_by(code='enable_stockout_merge', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return False
        return True if c and c.bool1 else False

    # 启用货品搜索返回大量数据
    @property
    def is_enable_search_good_500(self):
        c = Config.query.filter_by(code='enable_search_good_500', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return False
        return (c.int1 or 500) if c else False

    # 是否启用码单
    @property
    def is_enable_madan(self):
        c = Config.query.filter_by(code='enable_madan', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return False
        return True if c and c.bool1 else False
    
    # 码单计价, 单件价(箱价box_price), 内部件价(inner_qty_price), 重量价(box_weight)
    @property
    def rfid_price_type(self):
        c = Config.query.filter_by(code='rfid_price_type', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return 'box_weight'
        return c.str1 if c else False

    @property
    def async2oss(self):
        c = Config.query.filter_by(code='async2oss', owner_code=self.code, company_code=self.company_code).first()
        if c is None:
            return False
        return True if c and c.bool1 else False
    

    @property
    def conf(self):
        return {
            'express_on': self.express_on, #
            'is_overcharge': self.is_overcharge, 
            'is_partalloc': self.is_partalloc, 
            'is_close_when_pick': self.is_close_when_pick,
            'alloc_rules': self.alloc_rules,
            'alloc_location': self.alloc_location,
            'print_rule': self.print_rule,
            'is_enable_finance': self.is_enable_finance,
            'is_scan_each_barcode': self.is_scan_each_barcode,
            'is_scan_batch_barcode': self.is_scan_batch_barcode,
            'is_scan_rfid': self.is_scan_rfid,
            'is_enable_quick_in': self.is_enable_quick_in,
            'is_enable_part_pick': self.is_enable_part_pick,
            'is_enable_quick_pick': self.is_enable_quick_pick,
            'is_enable_out_barcode': self.is_enable_out_barcode,
            'is_enable_out_each_barcode': self.is_enable_out_each_barcode,
            'is_enable_out_rfid': self.is_enable_out_rfid,
            'is_enable_inv_warn': self.is_enable_inv_warn,
            'is_enable_inv_freeze': self.is_enable_inv_freeze,
            'is_enable_inv_unfreeze': self.is_enable_inv_unfreeze,
            'is_enable_lpn': self.is_enable_lpn,
            'is_enable_supplier_batch': self.is_enable_supplier_batch,
            'is_enable_setting': self.is_enable_setting,
            'is_sync_downfile': self.is_sync_downfile,
            'is_enable_fast_invmove': self.is_enable_fast_invmove,
            'is_enable_search_bar': self.is_enable_search_bar,
            'is_enable_simple_mode': self.is_enable_simple_mode,
            'is_enable_stockout_merge': self.is_enable_stockout_merge,
            'is_enable_search_good_500': self.is_enable_search_good_500,
            'is_enable_madan': self.is_enable_madan,
            'rfid_price_type': self.rfid_price_type,
            'stockout_cancel_pick_inv_handle_type': self.stockout_cancel_pick_inv_handle_type,
            'async2oss': self.async2oss,
            }

# 大字段储存
class Big(db.Model):
    __tablename__ = 's_big'
    __table_args__ = (
                      Index("ix_s_big_code", "code",),
                      Index("ix_s_big_uuid", "uuid"),
                      )

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(50), server_default='')
    code = db.Column(db.String(100), server_default='')
    subcode = db.Column(db.String(100), server_default='')
    
    company_code = db.Column(db.String(50))

    blob = db.Column(db.BLOB)

    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())

# 配置
class Config(db.Model):
    __tablename__ = 's_config'
    __table_args__ = (Index("ix_s_config_code", "company_code", "code"),
                      Index("ix_s_config_tenant", "company_code", 'warehouse_code', "owner_code",),
                      )

    id = db.Column(db.Integer, primary_key=True)

    company_code = db.Column(db.String(50), server_default='')
    warehouse_code = db.Column(db.String(50), server_default='')
    owner_code = db.Column(db.String(50), server_default='')

    code = db.Column(db.String(100), server_default='')
    subcode = db.Column(db.String(100), server_default='')

    # extra
    label = db.Column(db.String(100), server_default='')
    xtype = db.Column(db.String(20), server_default='bool')
    multi = db.Column(db.Boolean, server_default='0')
    index = db.Column(db.Integer, server_default='0', default=0)
    # 一次配置多个数据项
    options_multi = db.Column(db.Boolean, server_default='0')

    str1 = db.Column(db.String(255), server_default='')
    str2 = db.Column(db.String(255), server_default='')
    str3 = db.Column(db.String(255), server_default='')

    int1 = db.Column(db.Integer, server_default='0', default=0)
    int2 = db.Column(db.Integer, server_default='0', default=0)
    int3 = db.Column(db.Integer, server_default='0', default=0)

    bool1 = db.Column(db.Boolean, server_default='0', default=False)
    bool2 = db.Column(db.Boolean, server_default='0', default=False)
    bool3 = db.Column(db.Boolean, server_default='0', default=False)

    float1 = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.0', default=0)
    float2 = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.0', default=0)
    float3 = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.0', default=0)

    remark = db.Column(db.String(1000), default='')

    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())

# 递增序列号, 用来生成单号
class Seq(db.Model):
    __tablename__ = 's_seq'
    __table_args__ = (Index("ix_s_config_code", "company_code", "code"),
                      Index("ix_s_config_tenant", "company_code", 'warehouse_code', "owner_code",),
                      )

    id = db.Column(db.Integer, primary_key=True)

    company_code = db.Column(db.String(50), server_default='')
    warehouse_code = db.Column(db.String(50), server_default='')
    owner_code = db.Column(db.String(50), server_default='')

    # 入库/R/in 出库/C/out 生产/S/produce 销售/X/sale 销售出库/CX/saleout 采购/G/purchase 采购入库/RG/purchasein 生产成品入库/RS/producein 生产配件出库/CS/produceout
    code = db.Column(db.String(100), server_default='')
    seq  = db.Column(db.Integer, default=0, server_default='0')
    month = db.Column(db.String(20), default='', server_default='')

    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())


    @staticmethod
    def make_order_code(prefix='R', company_code=None, warehouse_code='', owner_code=''):
        month = ''
        query = Seq.query.filter_by(company_code=company_code)
        if warehouse_code:
            query = query.filter_by(warehouse_code=warehouse_code)
        if owner_code:
            query = query.filter_by(owner_code=owner_code)
        if prefix:
            query = query.filter_by(code=prefix)
        if settings.SEQ_MONTH:
            month = datetime.now().strftime('%y%m')
            query = query.filter_by(month=month)
        else:
            query = query.filter_by(month='')

        owner = ''
        if settings.SEQ_OWNER:
            p = Partner.query.with_entities(Partner.id.label('id')).filter_by(company_code=company_code, code=owner_code).first()
            if p and p.id:
                owner = '%s-'%p.id

        o = query.with_for_update().first()
        if o is None:
            o = Seq(company_code=company_code, warehouse_code=warehouse_code, owner_code=owner_code, code=prefix, month=month, seq=0)
            db.session.add(o)
        o.seq += 1
        db.session.flush()

        return '%s%s%s-%03d'%(o.code, owner, o.month or '', o.seq)

# 动作表, 记录用户操作
class Did(db.Model):
    __tablename__ = 's_did'
    __table_args__ = (Index("ix_s_did_code", "company_code", "code"),
                      Index("ix_s_did_tenant", "company_code", 'warehouse_code', "owner_code",),
                      )

    id = db.Column(db.Integer, primary_key=True)
    user_code = db.Column(db.String(20))

    # 动作
    code = db.Column(db.String(100), server_default='')
    # 动作子码, 可以关联单号
    subcode = db.Column(db.String(100), server_default='')
    # 操作的字段
    col =  db.Column(db.String(100), server_default='')
    # 操作前, 操作后
    str1 = db.Column(db.String(255), server_default='')
    str2 = db.Column(db.String(255), server_default='')

    int1 = db.Column(db.Integer, server_default='0', default=0)
    int2 = db.Column(db.Integer, server_default='0', default=0)

    bool1 = db.Column(db.Boolean, server_default='0', default=False)
    bool2 = db.Column(db.Boolean, server_default='0', default=False)

    float1 = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.0', default=0)
    float2 = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.0', default=0)

    company_code = db.Column(db.String(50))
    warehouse_code = db.Column(db.String(50))
    owner_code = db.Column(db.String(50))

    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())

# 记录来自官网咨询的客户
class Contact(db.Model):
    __tablename__ = 'ext_contact'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(50))
    tel = db.Column(db.String(50))
    email = db.Column(db.String(50))

    content = db.Column(db.String(2000), server_default='')

    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())