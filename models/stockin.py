#coding=utf8
__all__ = ['StockinLineTrans', 'StockinLine', 'Stockin', ]
import json
from flask import g
from uuid import uuid4
from sqlalchemy.sql import text
from datetime import datetime
from sqlalchemy import Index, UniqueConstraint
from sqlalchemy import func, or_, and_
from werkzeug.utils import cached_property

from extensions.database import db
from utils.flask_tools import json_dump

class Stockin(db.Model):
    __tablename__ = 'i_stockin'
    __table_args__ = (
                      Index("ix_stockin_order_code", "company_code", 'order_code'),
                      Index("ix_stockin_erp_order_code", "company_code", 'erp_order_code'),
                      Index("ix_stockin_tenant", "company_code", 'warehouse_code', "owner_code"),
                      )


    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    company_code = db.Column(db.String(50))
    warehouse_code = db.Column(db.String(50))
    owner_code = db.Column(db.String(50))

    order_code = db.Column(db.String(50), default='')
    erp_order_code = db.Column(db.String(50), default='')
    # 如果是return, 出库单拣货对应的退库入库单
    middle_order_code = db.Column(db.String(50), default='')

    # 入库有生产单与采购单号, 并关联采购单号
    sale_order_code = db.Column(db.String(50), default='', server_default='')
    purchase_order_code = db.Column(db.String(50), default='', server_default='')
    produce_order_code = db.Column(db.String(50), default='', server_default='')
    # 反向单号
    fan_order_code = db.Column(db.String(50), default='', server_default='')
    # 派工单
    pm_order_code = db.Column(db.String(50), default='', server_default='')
    pm_order_code_pick = db.Column(db.String(50), default='', server_default='')

    # 入库单转移库单
    move_order_code = db.Column(db.String(50), default='', server_default='')

    # 拆解单单号
    disassemble_order_code = db.Column(db.String(50), default='', server_default='')

    # 调拨出库单
    transfer_out_order_code = db.Column(db.String(50), default='', server_default='')
    # 调拨出库单状态
    transfer_out_order_state = db.Column(db.String(10), default='create', server_default='create')
    # 调拨目标仓库
    transfer_out_warehouse_code = db.Column(db.String(50), default='', server_default='')
    transfer_out_warehouse_name = db.Column(db.String(50), default='', server_default='')
    # 目标货主
    transfer_out_owner_code = db.Column(db.String(50), default='', server_default='')
    transfer_out_owner_name = db.Column(db.String(50), default='', server_default='')
    # 目标公司
    transfer_out_company_code = db.Column(db.String(50), default='', server_default='')
    transfer_out_company_name = db.Column(db.String(50), default='', server_default='')

    # 总价
    price = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)

    # 非标件, 统计重量
    # 非标件, 可能按重量来算
    _weight = db.Column(db.Float(asdecimal=True, precision='15,4'), name='weight', server_default='0.00', default=0.00)
    _gross_weight = db.Column(db.Float(asdecimal=True, precision='15,4'), name='gross_weight', server_default='0.00', default=0.00)
    # 非标件, 内部数量
    _qty_inner = db.Column(db.Integer, name='qty_inner', server_default='0', default=0)

    # 退库相关, 退款实际金额
    return_real = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)
    # 退库相关, 退款计算金额
    return_amount = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)

    # 采购单 purchase，退货单 return，转移/调拨单 transfer，交易单 consign, 生产成品入库单 produce, 
    # 自定义 custom, 退料 material_return, 维修入库 fix
    # borrow 借用归还入库, normal 普通入库, coop 协作退还入库 , produce_return 生产配料退回
    # xtype = db.Column(db.Enum('purchase', 'return', 'transfer', 'consign', 'custom', 'produce', 'material_return'), default='consign')
    xtype = db.Column(db.String(50), default='consign')
    # qimen
    order_type = db.Column(db.String(50), default='QTRK', server_default='QTRK')

    # 合作伙伴, 供应商
    partner_id = db.Column(db.Integer)
    partner_code = db.Column(db.String(50), default='', server_default='')
    partner_name = db.Column(db.String(50), default='', server_default='')
    partner_str  = db.Column(db.String(250), default='', server_default='')

    # 预期到货
    date_planned = db.Column(db.Date)
    # 最晚到货
    date_planned_end = db.Column(db.Date)
    date_finished = db.Column(db.DateTime)

    # 创建，部分收货，全部收货，等待上架，完成，取消; 等待上架状态未使用，暂时保留
    state = db.Column(db.Enum('create', 'part', 'all', 'done', 'cancel'), server_default='create')

    erp_biz_code = db.Column(db.String(50))
    #订单来源
    source = db.Column(db.Enum('erp', 'custom', 'import'), server_default='erp')
    # 淘宝, 京东, PDD 等
    erp_source = db.Column(db.String(50))

    # 是否回传
    is_passback = db.Column(db.Boolean(), server_default='0', default=False)

    # custom
    custom1 = db.Column(db.String(50), server_default='')
    custom2 = db.Column(db.String(50), server_default='')
    custom3 = db.Column(db.String(50), server_default='')
    custom4 = db.Column(db.String(50), server_default='')

    custom_uuid = db.Column(db.String(50))  # 自定义json字段，用于存放需要定制保存的字段，而不需要新增数据库字段

    # 发票信息
    invoice_info_uuid  = db.Column(db.String(50), server_default='')
    # 供应商信息
    supplier_info_uuid = db.Column(db.String(50), server_default='')
    # 快递公司/物流信息
    express_info_uuid  = db.Column(db.String(50), server_default='')

    # qimen
    is_qimen = db.Column(db.Boolean(), server_default='0', default=False)
    express_code = db.Column(db.String(50), server_default='')
    express_name = db.Column(db.String(50), server_default='')
    bill_code = db.Column(db.String(50), server_default='')
    reason = db.Column(db.String(250), server_default='')

    # 发件人信息，对应奇门 senderInfo部分
    # sender_info_uuid   = db.Column(db.String(50), server_default='')
    sender_name    = db.Column(db.String(50), server_default='')
    sender_tel     = db.Column(db.String(50), server_default='')
    sender_province = db.Column(db.String(250), server_default='')
    sender_city     = db.Column(db.String(250), server_default='')
    sender_area     = db.Column(db.String(250), server_default='')
    sender_town     = db.Column(db.String(250), server_default='')
    sender_address = db.Column(db.String(250), server_default='')
    # 收件人信息
    # receiver_info_uuid = db.Column(db.String(50), server_default='')
    receiver_name    = db.Column(db.String(50), server_default='')
    receiver_tel     = db.Column(db.String(50), server_default='')
    receiver_province = db.Column(db.String(250), server_default='')
    receiver_city     = db.Column(db.String(250), server_default='')
    receiver_area     = db.Column(db.String(250), server_default='')
    receiver_town     = db.Column(db.String(250), server_default='')
    receiver_address = db.Column(db.String(250), server_default='')

    # 系统操作人信息
    user_code = db.Column(db.String(20))
    user_name = db.Column(db.String(20))
    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())

    __dump_prop__ = ('sender_info', 'receiver_info', 'rate', 'date_left')


    @property
    def date_left(self):
        if self.date_planned:
            return (self.date_planned - datetime.now().date()).days
        return ''


    def find_line(self, sku, supplier_code='', spec=''):
        subq = self.lines.filter_by(sku=sku)
        if supplier_code:
            subq = subq.filter_by(supplier_code=supplier_code)
        if spec:
            subq = subq.filter_by(spec=spec)
        return subq.first()

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
    def owner(self):
        Partner = db.M('Partner')
        return Partner.query.filter(and_(
            Partner.code==self.owner_code,
            Partner.company_code==self.company_code)).first()


    @property
    def JSON(self):
        big = None
        if self.custom_uuid:
            big = db.M('Big').query.filter_by(code='JSON', subcode='i_stockin__json', uuid=self.custom_uuid).first()
        return json.loads(big.blob) if big else {}

    @JSON.setter
    def JSON(self, obj):
        val = json_dump(obj)
        if self.custom_uuid:
            db.M('Big').query.filter_by(code='JSON', subcode='i_stockin__json', uuid=self.custom_uuid).update({'blob':val})
        else:
            uuid = str(uuid4())
            big = db.M('Big')(company_code=self.company_code, code='JSON', subcode='i_stockin__json', blob=val, uuid=uuid)
            db.session.add(big)
            self.custom_uuid = uuid

    @property
    def sender_info(self):
        return {'name':self.sender_name, 'tel':self.sender_tel, 'address':self.sender_address, 'province': self.sender_province, 'city': self.sender_city, 'area':self.sender_area, 'town': self.sender_town}

    @sender_info.setter
    def sender_info(self, obj):
        if not obj:
            return
        self.sender_name = obj['name']
        self.sender_tel  = obj['tel']
        self.sender_address = obj['address']
        self.sender_province = obj['province']
        self.sender_city = obj['city']
        self.sender_area = obj.get('area', '')
        self.sender_town = obj.get('town', '')

    # 收件人信息
    @property
    def receiver_info(self):
        return {'name':self.receiver_name, 'tel':self.receiver_tel, 'address':self.receiver_address, 'province': self.receiver_province, 'city': self.receiver_city, 'area':self.receiver_area, 'town': self.receiver_town}

    @receiver_info.setter
    def receiver_info(self, obj):
        if not obj:
            return
        self.receiver_name = obj['name']
        self.receiver_tel  = obj['tel']
        self.receiver_address = obj['address']
        self.receiver_province = obj['province']
        self.receiver_city = obj['city']
        self.receiver_area = obj.get('area', '')
        self.receiver_town = obj.get('town', '')

    # 发票信息
    @property
    def invoice_info(self):
        big = None
        if self.invoice_info_uuid:
            big = db.M('Big').query.filter_by(code='JSON', subcode='i_stockin__invoice_info', uuid=self.invoice_info_uuid).first()
        return json.loads(big.blob) if big else {}

    @invoice_info.setter
    def invoice_info(self, obj):
        val = json_dump(obj)
        if self.invoice_info_uuid:
            db.M('Big').query.filter_by(code='JSON', subcode='i_stockin__invoice_info', uuid=self.invoice_info_uuid).update({'blob':val})
        else:
            uuid = str(uuid4())
            big = db.M('Big')(company_code=self.company_code, code='JSON', subcode='i_stockin__invoice_info', blob=val, uuid=uuid)
            db.session.add(big)
            self.invoice_info_uuid = uuid
    # 供应商信息
    @property
    def supplier_info(self):
        big = None
        if self.supplier_info_uuid:
            big = db.M('Big').query.filter_by(code='JSON', subcode='i_stockin__supplier_info', uuid=self.supplier_info_uuid).first()
        return json.loads(big.blob) if big else {}

    @supplier_info.setter
    def supplier_info(self, obj):
        val = json_dump(obj)
        if self.supplier_info_uuid:
            db.M('Big').query.filter_by(code='JSON', subcode='i_stockin__supplier_info', uuid=self.supplier_info_uuid).update({'blob':val})
        else:
            uuid = str(uuid4())
            big = db.M('Big')(company_code=self.company_code, code='JSON', subcode='i_stockin__supplier_info', blob=val, uuid=uuid)
            db.session.add(big)
            self.supplier_info_uuid = uuid
    # 快递公司信息
    @property
    def express_info(self):
        big = None
        if self.express_info_uuid:
            big = db.M('Big').query.filter_by(code='JSON', subcode='i_stockin__express_info', uuid=self.express_info_uuid).first()
        return json.loads(big.blob) if big else {}

    @express_info.setter
    def express_info(self, obj):
        val = json_dump(obj)
        if self.express_info_uuid:
            db.M('Big').query.filter_by(code='JSON', subcode='i_stockin__express_info', uuid=self.express_info_uuid).update({'blob':val})
        else:
            uuid = str(uuid4())
            big = db.M('Big')(company_code=self.company_code, code='JSON', subcode='i_stockin__express_info', blob=val, uuid=uuid)
            db.session.add(big)
            self.express_info_uuid = uuid


    def finish(self):
        self.date_finished = db.func.current_timestamp()

        if self.state == 'all' or self.state == 'done':
            self.state = 'done'

        if self.state == 'done':
            from blueprints.stockin.action import StockinAction
            StockinAction.inner_passback(self)
            # 完成调拨出库对应字段状态
            if self.xtype == 'transfer' and self.transfer_out_order_code:
                Stockout = db.M('Stockout')
                out = Stockout.query.filter_by(company_code=self.transfer_out_company_code, 
                    warehouse_code=self.transfer_out_warehouse_code, 
                    owner_code=self.transfer_out_owner_code,
                    order_code=self.transfer_out_order_code).first()
                if out is not None:
                    out.transfer_in_order_state = self.state
            elif self.xtype == 'return' and self.disassemble_order_code:
                dis = Disassemble.query.filter_by(company_code=self.company_code, owner_code=self.owner_code, warehouse_code=self.warehouse_code) \
                    .filter_by(order_code=self.disassemble_order_code).first()
                if dis is not None:
                    dis.state = 'done'


    @property
    def rate(self):
        o = StockinLine.query.with_entities(
                func.sum(StockinLine.qty).label('qty_total'), 
                func.sum(StockinLine.qty_real).label('qty_real')
            ).filter_by(stockin_id=self.id).first()
        qty_total  = float(o.qty_total or 0)
        qty_real   = float(o.qty_real or 0)
        p = '%0.2f%%'%(qty_real*100./qty_total) if qty_total else '0.00%'
        return p

    @cached_property
    def sum_price(self):
        if not self.price:
            price = StockinLine.query.with_entities(func.sum(StockinLine.price*StockinLine.qty).label('price')).t_query.filter_by(stockin_id=self.id).first().price
            self.price = price
        return self.price

    @property
    def weight(self):
        if self.state  in ('part', 'all'):
            InvRfid = db.M('InvRfid')
            o = InvRfid.query.with_entities(func.sum(InvRfid._weight).label('weight')) \
                .filter_by(company_code=self.company_code, owner_code=self.owner_code, warehouse_code=self.warehouse_code, \
                    stockin_order_code=self.order_code).first()
            self._weight = o.weight
        return self._weight

    @property
    def gross_weight(self):
        if self.state  in ('part', 'all'):
            InvRfid = db.M('InvRfid')
            o = InvRfid.query.with_entities(func.sum(InvRfid._gross_weight).label('gross_weight')) \
                .filter_by(company_code=self.company_code, owner_code=self.owner_code, warehouse_code=self.warehouse_code, \
                    stockin_order_code=self.order_code).first()
            self._gross_weight = o.gross_weight
        return self._gross_weight

    @property
    def qty_inner(self):
        if self.state  in ('part', 'all'):
            InvRfid = db.M('InvRfid')
            o = InvRfid.query.with_entities(func.sum(InvRfid._qty_inner).label('qty_inner')) \
                .filter_by(company_code=self.company_code, owner_code=self.owner_code, warehouse_code=self.warehouse_code, \
                    stockin_order_code=self.order_code).first()
            self._qty_inner = o.qty_inner
        return self._qty_inner

    @weight.setter
    def weight(self, v):
        self._weight = v

    @gross_weight.setter
    def gross_weight(self, v):
        self._gross_weight = v

    @qty_inner.setter
    def qty_inner(self, v):
        self._qty_inner = v



class StockinLine(db.Model):
    __tablename__ = 'i_stockin_line'
    __table_args__ = (
                      Index("ix_stockin_line_order_code", "order_code", "company_code"),
                      Index("ix_stockin_line_erp_order_code", "erp_order_code", "company_code"),
                      Index("ix_stockin_line_tenant", "company_code", 'warehouse_code', "owner_code",),
                      Index("ix_stockin_line_sku", "company_code", 'warehouse_code', "owner_code", 'order_code', 'sku'),
                      Index("ix_stockin_line_sku2", "company_code", 'warehouse_code', "owner_code", 'stockin_id', 'sku'),
                      Index("ix_stockin_line_sku3", 'stockin_id', 'sku'),
                      )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    company_code = db.Column(db.String(50))
    warehouse_code = db.Column(db.String(50))
    owner_code = db.Column(db.String(50))

    order_code = db.Column(db.String(50), default='')
    middle_order_code = db.Column(db.String(50), default='')
    erp_order_code = db.Column(db.String(50), default='')
    # 行号, qimen
    lineno = db.Column(db.String(20), server_default='')
    
    # 货品信息
    sku        = db.Column(db.String(50), server_default='')
    name       = db.Column(db.String(200), default='')
    barcode    = db.Column(db.String(50), server_default='')
    middle_sku = db.Column(db.String(50), server_default='')
    # 计划数量
    qty        = db.Column(db.Integer, server_default='0', default=0)
    # 实收数量
    qty_real   = db.Column(db.Integer, server_default='0', default=0)
    # 预收库位
    location_code = db.Column(db.String(50), server_default='', default='')

    stockin_date = db.Column(db.Date)

    partner_id = db.Column(db.Integer)
    partner_name = db.Column(db.String(50), server_default='')
    # 批次属性
    supplier_code = db.Column(db.String(50), server_default='')
    quality_type = db.Column(db.Enum('ZP', 'CC', 'DJ', 'ZT', 'JS', 'XS'), server_default='ZP')
    product_date = db.Column(db.Date)
    expire_date  = db.Column(db.Date)
    batch_code   = db.Column(db.String(50), server_default='')
    virtual_warehouse = db.Column(db.String(50), server_default='')
    spec = db.Column(db.String(50), server_default='')

    # 款色码
    style   = db.Column(db.String(50), server_default='')
    color   = db.Column(db.String(50), server_default='')
    size    = db.Column(db.String(50), server_default='')

    # 单位
    unit    = db.Column(db.String(20), server_default='')
    weight_unit = db.Column(db.String(10), server_default='')

    # 本次采购入库价格
    price = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)

    # 非标件, 统计重量
    # 非标件, 可能按重量来算
    _weight = db.Column(db.Float(asdecimal=True, precision='15,4'), name='weight', server_default='0.00', default=0.00)
    _gross_weight = db.Column(db.Float(asdecimal=True, precision='15,4'), name='gross_weight', server_default='0.00', default=0.00)
    # 非标件, 内部数量
    _qty_inner = db.Column(db.Integer, name='qty_inner', server_default='0', default=0)

    custom_uuid = db.Column(db.String(50), server_default='')  # 自定义json字段，用于存放需要定制保存的字段，而不需要新增数据库字段

    # 外键
    stockin_id = db.Column(db.Integer, db.ForeignKey("i_stockin.id"))

    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())


    stockin = db.relationship("Stockin", backref=db.backref('lines', lazy='dynamic'))

    __dump_prop__ = ('rate',)

    @property
    def company(self):
        Company = db.M('Company')
        return Company.query.filter(Company.code==self.company_code).first()

    @property
    def owner(self):
        Partner = db.M('Partner')
        return Partner.query.filter(and_(
            Partner.code==self.owner_code,
            Partner.company_code==self.company_code)).first()

    @property
    def warehouse(self):
        Warehouse = db.M('Warehouse')
        return Warehouse.query.filter(and_(
            Warehouse.code==self.warehouse_code,
            Warehouse.company_code==self.company_code)).first()

    @property
    def JSON(self):
        big = None
        if self.custom_uuid:
            big = db.M('Big').query.filter_by(code='JSON', subcode='i_stockin_line__json', uuid=self.custom_uuid).first()
        return json.loads(big.blob) if big else {}

    @JSON.setter
    def JSON(self, obj):
        val = json_dump(obj)
        if self.custom_uuid:
            db.M('Big').query.filter_by(code='JSON', subcode='i_stockin_line__json', uuid=self.custom_uuid).update({'blob':val})
        else:
            uuid = str(uuid4())
            big = db.M('Big')(company_code=self.company_code, code='JSON', subcode='i_stockin_line__json', blob=val, uuid=uuid)
            db.session.add(big)
            self.custom_uuid = uuid

    # 进度
    @property
    def rate(self):
        return '%0.2f%%'%(self.qty_real*100./self.qty) if self.qty else '0.00%'

    @property
    def good(self):
        Good = db.M('Good')
        return Good.query.filter(and_(
            Good.code==self.sku,
            Good.owner_code==self.owner_code,
            Good.company_code==self.company_code)).first()

    @property
    def weight(self):
        if self.stockin.state  in ('part', 'all'):
            InvRfid = db.M('InvRfid')
            o = InvRfid.query.with_entities(func.sum(InvRfid._weight).label('weight')) \
                .filter_by(company_code=self.company_code, owner_code=self.owner_code, warehouse_code=self.warehouse_code, \
                    stockin_order_code=self.stockin.order_code) \
                .filter(InvRfid.sku==self.sku).first()
            self._weight = o.weight
        return self._weight

    @property
    def gross_weight(self):
        if self.stockin.state  in ('part', 'all'):
            InvRfid = db.M('InvRfid')
            o = InvRfid.query.with_entities(func.sum(InvRfid._gross_weight).label('gross_weight')) \
                .filter_by(company_code=self.company_code, owner_code=self.owner_code, warehouse_code=self.warehouse_code, \
                    stockin_order_code=self.stockin.order_code) \
                .filter(InvRfid.sku==self.sku).first()
            self._gross_weight = o.gross_weight
        return self._gross_weight

    @property
    def qty_inner(self):
        if self.stockin.state  in ('part', 'all'):
            InvRfid = db.M('InvRfid')
            o = InvRfid.query.with_entities(func.sum(InvRfid._qty_inner).label('qty_inner')) \
                .filter_by(company_code=self.company_code, owner_code=self.owner_code, warehouse_code=self.warehouse_code, \
                    stockin_order_code=self.stockin.order_code) \
                .filter(InvRfid.sku==self.sku).first()
            self._qty_inner = o.qty_inner
        return self._qty_inner

    @weight.setter
    def weight(self, v):
        self._weight = v

    @gross_weight.setter
    def gross_weight(self, v):
        self._gross_weight = v

    @qty_inner.setter
    def qty_inner(self, v):
        self._qty_inner = v
    



class StockinLineTrans(db.Model):
    __tablename__ = 'i_stockin_line_trans'
    __table_args__ = (Index("ix_i_trans_order_code", "order_code",),
                      Index("ix_i_trans_erp_order_code", "erp_order_code",),
                      )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    company_code = db.Column(db.String(50))
    warehouse_code = db.Column(db.String(50))
    owner_code = db.Column(db.String(50))
    
    order_code = db.Column(db.String(50), default='')
    middle_order_code = db.Column(db.String(50), default='')
    erp_order_code = db.Column(db.String(50), default='')

    sku        = db.Column(db.String(50), server_default='')
    name       = db.Column(db.String(200), default='')
    barcode    = db.Column(db.String(50), server_default='')

    # 本次要收条数
    qty = db.Column(db.Integer, server_default='0', default=0)
    # 货品实收/操作数量
    qty_real = db.Column(db.Integer, server_default='0', default=0)
    # 本次入库价格
    price = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)
    # 收放库存
    inv_id = db.Column(db.Integer)
    location_code = db.Column(db.String(50), server_default='', default='')
    lpn = db.Column(db.String(50), server_default='', default='')

    # 系统操作人信息
    user_code = db.Column(db.String(20))
    user_name = db.Column(db.String(20))

    # 仓库操作人信息
    w_user_code = db.Column(db.String(20))
    w_user_name = db.Column(db.String(20))

    # 外键
    stockin_id = db.Column(db.Integer, db.ForeignKey("i_stockin.id"))
    stockin_line_id = db.Column(db.Integer, db.ForeignKey("i_stockin_line.id"))

    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())


    stockin = db.relationship("Stockin", backref=db.backref('line_trans', lazy='dynamic'))
    stockin_line = db.relationship("StockinLine", backref=db.backref('trans', lazy='dynamic'))


    @property
    def inv(self):
        Inv = db.M('Inv')
        return Inv.query.filter(Inv.id==self.inv_id).first()


class Disassemble(db.Model):
    __tablename__ = 'i_disassemble'
    __table_args__ = (
                      Index("ix_dis_tenant", "company_code", 'warehouse_code', "owner_code",),
                      Index("ix_dis_code", "company_code", 'warehouse_code', "owner_code", 'order_code'),
                      )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    owner_code = db.Column(db.String(50))
    company_code = db.Column(db.String(50))
    warehouse_code = db.Column(db.String(50))

    order_code = db.Column(db.String(50), default='')
    # db.Enum('create', 'check', 'doing', 'done', 'cancel')
    # check: 已拆解,  doing: 入库中
    state = db.Column(db.String(20), server_default='create')

    date_finished = db.Column(db.DateTime)

    # 合作伙伴, 客户
    partner_code = db.Column(db.String(50), default='', server_default='')
    partner_str  = db.Column(db.String(250), default='', server_default='')
    partner_name = db.Column(db.String(50), default='', server_default='')

    # 外键
    stockin_id = db.Column(db.Integer)
    stockin_order_code = db.Column(db.String(50), default='')

    # 处理人
    user_code = db.Column(db.String(20))
    user_name = db.Column(db.String(20))

    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())

    __dump_prop__ = ('has_stockin',)


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
    def owner(self):
        Partner = db.M('Partner')
        return Partner.query.filter(and_(
            Partner.code==self.owner_code,
            Partner.company_code==self.company_code)).first()


    def finish(self):
        self.state = 'done'
        self.date_finished = db.func.current_timestamp()

    @property
    def has_stockin(self):
        if getattr(self, '_stockin', None) is not None:
            return True
        # 已经有成品入库单
        Stockin = db.M('Stockin')
        stockin = Stockin.query.filter_by(company_code=self.company_code, warehouse_code=self.warehouse_code, owner_code=self.owner_code) \
                .filter_by(xtype="return", disassemble_order_code=self.order_code) \
                .filter(Stockin.state!='cancel').first() #.count() > 0
        if stockin is not None:
            self._stockin = stockin
        return stockin is not None

    def cancel(self):
        self.state = 'cancel'
        if self.has_stockin:
            if self._stockin.state == 'create':
                self._stockin.state = 'cancel'


    @property
    def items(self):
        return DisassembleItem.query.t_query.filter_by(order_id=self.id).all()


# 退货拆解入库
class DisassembleLine(db.Model):
    __tablename__ = 'i_disassemble_line'
    __table_args__ = (
                      Index("i_dis_line_tenant", "company_code", 'warehouse_code', "owner_code",),
                      Index("i_dis_line_sku", "company_code", 'warehouse_code', "owner_code", 'sku'),
                      )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    company_code = db.Column(db.String(50))
    warehouse_code = db.Column(db.String(50))
    owner_code = db.Column(db.String(50))

    order_code = db.Column(db.String(50), default='')
    
    # 货品信息
    sku        = db.Column(db.String(50), server_default='')
    name       = db.Column(db.String(200), default='')
    barcode    = db.Column(db.String(50), server_default='')
    # 退回数量
    qty        = db.Column(db.Integer, server_default='0', default=0)
    # 拆解数量
    qty_apart  = db.Column(db.Integer, server_default='0', default=0)
    # 退库数量
    qty_in     = db.Column(db.Integer, server_default='0', default=0)
    # 报废数量
    qty_scrap  = db.Column(db.Integer, server_default='0', default=0)

    spec = db.Column(db.String(50), server_default='')

    # 款色码
    style   = db.Column(db.String(50), server_default='')
    color   = db.Column(db.String(50), server_default='')
    size    = db.Column(db.String(50), server_default='')
    # laoa 字段
    # 等级
    level = db.Column(db.String(50), server_default='')
    # 捻向
    twisted = db.Column(db.String(50), server_default='')

    # 单位
    unit    = db.Column(db.String(20), server_default='')
    weight_unit = db.Column(db.String(10), server_default='')

    order_id = db.Column(db.Integer, db.ForeignKey("i_disassemble.id"))

    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())

    order = db.relationship("Disassemble", backref=db.backref('lines', lazy='dynamic'))


    @property
    def company(self):
        Company = db.M('Company')
        return Company.query.filter(Company.code==self.company_code).first()

    @property
    def owner(self):
        Partner = db.M('Partner')
        return Partner.query.filter(and_(
            Partner.code==self.owner_code,
            Partner.company_code==self.company_code)).first()

    @property
    def warehouse(self):
        Warehouse = db.M('Warehouse')
        return Warehouse.query.filter(and_(
            Warehouse.code==self.warehouse_code,
            Warehouse.company_code==self.company_code)).first()

    @property
    def good(self):
        Good = db.M('Good')
        return Good.query.filter(and_(
            Good.code==self.sku,
            Good.owner_code==self.owner_code,
            Good.company_code==self.company_code)).first()


# 退货拆解入库
class DisassembleItem(db.Model):
    __tablename__ = 'i_disassemble_item'
    __table_args__ = (
                      Index("i_dis_item_tenant", "company_code", 'warehouse_code', "owner_code",),
                      Index("i_dis_item_sku", "company_code", 'warehouse_code', "owner_code", 'sku'),
                      )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    company_code = db.Column(db.String(50))
    warehouse_code = db.Column(db.String(50))
    owner_code = db.Column(db.String(50))

    order_code = db.Column(db.String(50), default='')

    # 合作伙伴, 客户
    partner_code = db.Column(db.String(50), default='', server_default='')
    partner_str  = db.Column(db.String(250), default='', server_default='')
    partner_name = db.Column(db.String(50), default='', server_default='')
    
    # 货品信息
    sku        = db.Column(db.String(50), server_default='')
    name       = db.Column(db.String(200), default='')
    barcode    = db.Column(db.String(50), server_default='')
    # 拆解数量
    qty_apart  = db.Column(db.Integer, server_default='0', default=0)
    # 退库数量
    qty_in     = db.Column(db.Integer, server_default='0', default=0)
    # 报废数量
    qty_scrap  = db.Column(db.Integer, server_default='0', default=0)
    # 退货数量, 退回给供应商
    qty_return = db.Column(db.Integer, server_default='0', default=0)
    # 预收库位
    location_code = db.Column(db.String(50), server_default='', default='')

    spec = db.Column(db.String(50), server_default='')

    # 款色码
    style   = db.Column(db.String(50), server_default='')
    color   = db.Column(db.String(50), server_default='')
    size    = db.Column(db.String(50), server_default='')
    # laoa 字段
    # 等级
    level = db.Column(db.String(50), server_default='')
    # 捻向
    twisted = db.Column(db.String(50), server_default='')

    # 单位
    unit    = db.Column(db.String(20), server_default='')
    weight_unit = db.Column(db.String(10), server_default='')

    order_id = db.Column(db.Integer)

    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())

    @property
    def good(self):
        Good = db.M('Good')
        return Good.query.filter(and_(
            Good.code==self.sku,
            Good.owner_code==self.owner_code,
            Good.company_code==self.company_code)).first()







