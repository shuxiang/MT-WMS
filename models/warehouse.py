#coding=utf8
__all__ = ['Warehouse', 'Area', 'Workarea', 'Location']
'''
warehouse   -> area     -> location
            -> workarea
'''

import os, os.path
from utils.upload import get_oss_image, save_inv_qrcode, save_inv_barcode

from sqlalchemy.sql import text
from datetime import datetime
from sqlalchemy import Index, UniqueConstraint
from sqlalchemy import func, or_, and_

from extensions.database import db
import settings

class Warehouse(db.Model):
    __tablename__ = 'w_warehouse'
    __table_args__ = (
                      Index("ix_w_code", "company_code", "code",),
                      )

    __table_args__ = (
                      Index("ix_w_code", "company_code", "code",),
                      )

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), server_default='')

    name = db.Column(db.String(20), server_default='')
    tel = db.Column(db.String(20), server_default='')
    email = db.Column(db.String(100), server_default='')
    contact = db.Column(db.String(20), server_default='')
    address = db.Column(db.String(100), server_default='')

    company_code = db.Column(db.String(50))
    # 共享仓，共享给对方公司的公司key
    sharekey = db.Column(db.String(200), server_default='')
    # 仓库默认的快递公司
    express_code = db.Column(db.String(50), default='')
    express_name = db.Column(db.String(50), default='')

    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())

    @property
    def company(self):
        Company = db.M('Company')
        return Company.query.filter_by(code=self.company_code).first()


class Area(db.Model):
    __tablename__ = 'w_area'
    __table_args__ = (
                      Index("ix_wa_code", "company_code", "code",),
                      )

    __table_args__ = (
                      Index("ix_area_tenant", "company_code", 'warehouse_code',),
                      )

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), server_default='')
    name = db.Column(db.String(20), server_default='')

    # 存储区， 临时区， 零散区， 坏品区, 退货/退庫区， 维修区
    xtype = db.Column(db.Enum('storage', 'temp', 'piece', 'bad', 'return', 'repair'), default='storage')

    warehouse_code = db.Column(db.String(50))
    company_code   = db.Column(db.String(50))

    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())

    @property
    def company(self):
        Company = db.M('Company')
        return Company.query.filter_by(code=self.company_code).first()

    @property
    def warehouse(self):
        Warehouse = db.M('Warehouse')
        return Warehouse.query.filter(and_(
            Warehouse.code==self.warehouse_code,
            Warehouse.company_code==self.company_code)).first()


class Workarea(db.Model):
    __tablename__ = 'w_workarea'
    __table_args__ = (
                      Index("ix_wwa_code", "company_code", "code",),
                      )

    __table_args__ = (
                      Index("ix_workarea_tenant", "company_code", 'warehouse_code',),
                      )

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), server_default='')
    name = db.Column(db.String(20), server_default='')

    warehouse_code = db.Column(db.String(50))
    company_code   = db.Column(db.String(50))

    # 是否系统工作区
    is_inner = db.Column(db.Boolean, server_default='0', default=0)

    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())

    @property
    def company(self):
        Company = db.M('Company')
        return Company.query.filter_by(code=self.company_code).first()

    @property
    def warehouse(self):
        Warehouse = db.M('Warehouse')
        return Warehouse.query.filter(and_(
            Warehouse.code==self.warehouse_code,
            Warehouse.company_code==self.company_code)).first()



# 库位数据结构定义
class Location(db.Model):
    __tablename__ = 'w_location'
    __table_args__ = (
                      Index("ix_location_code", "code", "company_code",),
                      Index("ix_location_tenant", "company_code", 'warehouse_code',)
                      )

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), server_default='')

    # 关联的共享仓公司key
    sharekey = db.Column(db.String(200), server_default='')
    # 关联的共享仓仓库code
    sharecode = db.Column(db.String(50), server_default='')
    # 共享仓名称
    sharename = db.Column(db.String(50), server_default='')

    # 操作序
    index = db.Column(db.Integer, server_default='0', default=0)
    # 优先级
    priority = db.Column(db.Enum('L1', 'L2', 'L3', 'L4', 'L5'), server_default='L3')
    # 是否系统库位
    is_inner = db.Column(db.Boolean, server_default='0', default=0)


    # 扩展数据
    length = db.Column(db.String(20), server_default='')
    width =  db.Column(db.String(20), server_default='')
    height = db.Column(db.String(20), server_default='')
    # 容积
    cubage = db.Column(db.String(20), server_default='')
    weight = db.Column(db.String(20), server_default='')


    warehouse_code = db.Column(db.String(50))
    company_code   = db.Column(db.String(50))
    workarea_code  = db.Column(db.String(50))
    area_code      = db.Column(db.String(50))

    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())


    @property
    def company(self):
        Company = db.M('Company')
        return Company.query.filter_by(code=self.company_code).first()

    @property
    def warehouse(self):
        Warehouse = db.M('Warehouse')
        return Warehouse.query.filter(and_(
            Warehouse.code==self.warehouse_code,
            Warehouse.company_code==self.company_code)).first()

    @property
    def workarea(self):
        Workarea = db.M('Workarea')
        return Workarea.query.filter(and_(
            Workarea.code==self.workarea_code,
            Workarea.company_code==self.company_code,
            Workarea.warehouse_code==self.warehouse_code)).first()

    @property
    def area(self):
        Area = db.M('Area')
        return Area.query.filter(and_(
            Area.code==self.area_code,
            Area.company_code==self.company_code,
            Area.warehouse_code==self.warehouse_code)).first()

    def get_barcode(self, company_id):
        if not os.path.exists(os.path.join(settings.UPLOAD_DIR, 'barcode', company_id, self.code)):
            _, path = save_inv_barcode(settings.UPLOAD_DIR, company_id, self.code)
        else:
            path = '/static/upload/barcode/%s/%s.png'%(company_id, self.code)
        return path

    def get_qrcode(self, company_id):
        if not os.path.exists(os.path.join(settings.UPLOAD_DIR, 'qrcode', company_id, self.code)):
            _, path = save_inv_qrcode(settings.UPLOAD_DIR, company_id, self.code)
        else:
            path = '/static/upload/qrcode/%s/%s.png'%(company_id, self.code)
        return path









