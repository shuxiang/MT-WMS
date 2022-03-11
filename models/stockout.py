#coding=utf8
__all__ = ['StockoutLineTrans', 'StockoutLine', 'Stockout', 'Alloc', 'StockoutMerge', 'BoxLine', 'Box', ]
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

class Stockout(db.Model):
    __tablename__ = 'o_stockout'
    __table_args__ = (
                      Index("ix_stockout_order_code", "order_code", "company_code"),
                      Index("ix_stockout_erp_order_code", "erp_order_code", "company_code"),
                      Index("ix_stockout_tenant", "company_code", 'warehouse_code', "owner_code",),
                      )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    company_code = db.Column(db.String(50))
    warehouse_code = db.Column(db.String(50))
    owner_code = db.Column(db.String(50))

    order_code = db.Column(db.String(50), default='')
    middle_order_code = db.Column(db.String(50), default='')
    erp_order_code = db.Column(db.String(50), default='')

    # 由于合并拣货单
    merge_order_code = db.Column(db.String(50), default='')

    # 总价
    price = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)
    # 成本, 拣货的成本, 出库完成后才有
    cost_price = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)
    # 批次库存成本, 分配的成本
    alloc_cost_price = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)

    # 出库只有生产单与销售单号
    sale_order_code = db.Column(db.String(50), default='', server_default='')
    produce_order_code = db.Column(db.String(50), default='', server_default='')
    # 采购退货单
    purchase_order_code = db.Column(db.String(50), default='', server_default='')
    # 反向单号
    fan_order_code = db.Column(db.String(50), default='', server_default='')
    # 派工单
    pm_order_code = db.Column(db.String(50), default='', server_default='')

    # 调拨入库单
    transfer_in_order_code = db.Column(db.String(50), default='', server_default='')
    # 调拨入库单状态
    transfer_in_order_state = db.Column(db.String(10), default='create', server_default='create')
    # 调拨目标仓库
    transfer_in_warehouse_code = db.Column(db.String(50), default='', server_default='')
    transfer_in_warehouse_name = db.Column(db.String(50), default='', server_default='')
    # 目标货主
    transfer_in_owner_code = db.Column(db.String(50), default='', server_default='')
    transfer_in_owner_name = db.Column(db.String(50), default='', server_default='')
    # 目标公司
    transfer_in_company_code = db.Column(db.String(50), default='', server_default='')
    transfer_in_company_name = db.Column(db.String(50), default='', server_default='')

    # 退库相关, 退款实际金额
    return_real = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)
    # 退库相关, 退款计算金额
    return_amount = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)

    # 状态信息
    state = db.Column(db.Enum('create', 'done', 'cancel', 'doing'), server_default='create')
    # 分配状态, 捡货状态, 发运状态
    state_alloc = db.Column(db.Enum('no', 'part', 'done'), server_default='no')
    state_pick = db.Column(db.Enum('no', 'part', 'done'), server_default='no')
    state_ship = db.Column(db.Enum('no', 'part', 'done'), server_default='no')

    # 面单发运状态
    waybill_state = db.Column(db.Enum('null', 'failure', 'success', 'created'), server_default='null')
    box_seq = db.Column(db.Integer, default=0, server_default='0')

    # 用于流程的类型
    xtype = db.Column(db.Enum('B2C', 'B2B', 'custom'), server_default='B2B')
    # 用于显示的订单类型, 客户自定义的订单类型 custom; sale 销售出库，produce　生产出库
    # normal 普通出库，　return 退货出库, 销售单协作出库(代工配件出库) coop , 领料 material_pick
    # 维修出库 fix, 报废出库 scrap, borrow 借用出库, transfer 转移出库, consign 交易出库
    order_type = db.Column(db.String(50), default='normal')
    # qimen
    sub_order_type = db.Column(db.String(50), default='QTCK', server_default='QTCK')

    # 合作伙伴, 客户
    partner_id = db.Column(db.Integer)
    partner_code = db.Column(db.String(50), default='', server_default='')
    partner_name = db.Column(db.String(50), default='', server_default='')
    partner_str  = db.Column(db.String(250), default='', server_default='')

    # qimen
    is_qimen = db.Column(db.Boolean(), server_default='0', default=False)
    express_code = db.Column(db.String(50), server_default='')
    express_name = db.Column(db.String(50), server_default='')
    bill_code = db.Column(db.String(50), server_default='')
    reason = db.Column(db.String(250), server_default='')

    erp_biz_code = db.Column(db.String(50))
    #订单来源
    source = db.Column(db.Enum('erp', 'custom', 'import'), server_default='erp')
    # 淘宝, 京东, PDD 等
    erp_source = db.Column(db.String(50))

    # 时间信息
    date_planned = db.Column(db.Date)
    date_finished = db.Column(db.DateTime)

    # 是否回传
    is_passback = db.Column(db.Boolean(), server_default='0', default=False)

    # custom
    custom1 = db.Column(db.String(50), server_default='')
    custom2 = db.Column(db.String(50), server_default='')
    custom3 = db.Column(db.String(50), server_default='')
    custom4 = db.Column(db.String(50), server_default='')

    custom_uuid = db.Column(db.String(50), server_default='')  # 自定义json字段，用于存放需要定制保存的字段，而不需要新增数据库字段

    # 发票信息
    invoice_info_uuid  = db.Column(db.String(50), server_default='')
    # 供应商信息
    supplier_info_uuid = db.Column(db.String(50), server_default='')
    # 快递公司/物流信息
    express_info_uuid  = db.Column(db.String(50), server_default='')

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

    # 仓库操作人信息/领料人信息
    w_user_code = db.Column(db.String(20))
    w_user_name = db.Column(db.String(20))

    # 系统操作人信息
    user_code = db.Column(db.String(20))
    user_name = db.Column(db.String(20))
    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())


    __dump_prop__ = ('has_produce_order', 'sender_info', 'receiver_info', 'date_left')

    # 批次库存成本. cost_price 是拣货后的成本, alloc_cost_price 是分配的成本, 可能 拣货<分配
    def sum_alloc_cost_price(self):
        if self.state_alloc == 'done':
            return self.alloc_cost_price
        Inv = db.M('Inv')
        Alloc = db.M('Alloc')
        o = Inv.query.t_query.with_entities(func.sum(Alloc.qty_alloc*Inv.price).label('price')).filter(Inv.id==Alloc.inv_id, 
                Inv.company_code==Alloc.company_code, Inv.warehouse_code==Alloc.warehouse_code, Inv.owner_code==Alloc.owner_code) \
            .filter(Alloc.order_code==self.order_code).first()
        if o:
            self.alloc_cost_price = float(o.price or 0)
        return self.alloc_cost_price

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
    def has_produce_order(self):
        if getattr(self, '_produce', None) is not None:
            return True
        self._produce = None
        return self._produce is not None
    

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
            big = db.M('Big').query.filter_by(code='JSON', subcode='o_stockout__json', uuid=self.custom_uuid).first()
        return json.loads(big.blob) if big else {}

    @JSON.setter
    def JSON(self, obj):
        val = json_dump(obj)
        if self.custom_uuid:
            db.M('Big').query.filter_by(code='JSON', subcode='o_stockout__json', uuid=self.custom_uuid).update({'blob':val})
        else:
            uuid = str(uuid4())
            big = db.M('Big')(company_code=self.company_code, code='JSON', subcode='o_stockout__json', blob=val, uuid=uuid)
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
            big = db.M('Big').query.filter_by(code='JSON', subcode='o_stockout__invoice_info', uuid=self.invoice_info_uuid).first()
        return json.loads(big.blob) if big else {}

    @invoice_info.setter
    def invoice_info(self, obj):
        val = json_dump(obj)
        if self.invoice_info_uuid:
            db.M('Big').query.filter_by(code='JSON', subcode='o_stockout__invoice_info', uuid=self.invoice_info_uuid).update({'blob':val})
        else:
            uuid = str(uuid4())
            big = db.M('Big')(company_code=self.company_code, code='JSON', subcode='o_stockout__invoice_info', blob=val, uuid=uuid)
            db.session.add(big)
            self.invoice_info_uuid = uuid
    # 供应商信息
    @property
    def supplier_info(self):
        big = None
        if self.supplier_info_uuid:
            big = db.M('Big').query.filter_by(code='JSON', subcode='o_stockout__supplier_info', uuid=self.supplier_info_uuid).first()
        return json.loads(big.blob) if big else {}

    @supplier_info.setter
    def supplier_info(self, obj):
        val = json_dump(obj)
        if self.supplier_info_uuid:
            db.M('Big').query.filter_by(code='JSON', subcode='o_stockout__supplier_info', uuid=self.supplier_info_uuid).update({'blob':val})
        else:
            uuid = str(uuid4())
            big = db.M('Big')(company_code=self.company_code, code='JSON', subcode='o_stockout__supplier_info', blob=val, uuid=uuid)
            db.session.add(big)
            self.supplier_info_uuid = uuid
    # 快递公司/物流信息
    @property
    def express_info(self):
        big = None
        if self.express_info_uuid:
            big = db.M('Big').query.filter_by(code='JSON', subcode='o_stockout__express_info', uuid=self.express_info_uuid).first()
        return json.loads(big.blob) if big else {}

    @express_info.setter
    def express_info(self, obj):
        val = json_dump(obj)
        if self.express_info_uuid:
            db.M('Big').query.filter_by(code='JSON', subcode='o_stockout__express_info', uuid=self.express_info_uuid).update({'blob':val})
        else:
            uuid = str(uuid4())
            big = db.M('Big')(company_code=self.company_code, code='JSON', subcode='o_stockout__express_info', blob=val, uuid=uuid)
            db.session.add(big)
            self.express_info_uuid = uuid

    def finish(self):
        self.sum_alloc_cost_price()
        
        self.date_finished = db.func.current_timestamp()
        
        if self.state_ship == 'done':
            self.state = 'done'
        elif self.state_pick == 'done' and self.owner.is_close_when_pick:
            self.state = 'done'

        if self.state == 'done':

            from blueprints.stockout.action import StockoutAction
            StockoutAction.inner_passback(self)

            StockoutAction.create_out_invtran(self)

            # 报废出库, 相关的RFID.state='off'
            if self.order_type == 'scrap':
                db.session.flush()
                InvRfid = db.M('InvRfid')
                rfids = InvRfid.query.filter_by(company_code=self.company_code, warehouse_code=self.warehouse_code, owner_code=self.owner_code) \
                    .filter_by(stockout_order_code=self.order_code).all()
                for rfid in rfids:
                    rfid.qty = 0
                    rfid.state = 'off'
            # 完成调拨入库对应字段状态
            if self.order_type == 'transfer' and self.transfer_in_order_code:
                Stockin = db.M('Stockin')
                stockin = Stockin.query.filter_by(company_code=self.transfer_in_company_code, 
                    warehouse_code=self.transfer_in_warehouse_code, 
                    owner_code=self.transfer_in_owner_code,
                    order_code=self.transfer_in_order_code).first()
                if stockin is not None:
                    stockin.transfer_out_order_state = self.state

    def cancel(self):
        ok, msg = False, ''
        # 已经分配的, 取消分配
        if self.state == 'doing':
            from blueprints.stockout.action import StockoutAction
            action = StockoutAction()
            ok, msg = action.alloc_cancel(order=self, cancel=True)
        elif self.state in ('create', 'cancel'):
            self.state = 'cancel'
            ok = True
        else:
            ok = False
            msg = u'不能取消'
        # 取消调拨入库单
        if ok and self.order_type == 'transfer' and self.transfer_in_order_code:
            Stockin = db.M('Stockin')
            stockin = Stockin.query.filter_by(
                company_code=self.transfer_in_company_code, 
                warehouse_code=self.transfer_in_warehouse_code, 
                owner_code=self.transfer_in_owner_code, 
                order_code=self.transfer_in_order_code).first()
            if stockin is not None:
                if stockin.state == 'create':
                    stockin.state = 'cancel'
        if ok:
            self.transfer_in_order_state = 'cancel'


    @cached_property
    def sum_price(self):
        if not self.price:
            price = StockoutLine.query.with_entities(func.sum(StockoutLine.price*StockoutLine.qty).label('price')).t_query.filter_by(stockout_id=self.id).first().price
            self.price = price
        return self.price


    # 码单信息
    def rfid_list(self):
        IRT = db.M('InvRfidTrans')
        IR = db.M('InvRfid')
        rfids = IR.query.t_query.filter(IRT.rfid==IR.rfid, IRT.sku==IR.sku, IRT.xtype=='out', IRT.order_code==self.order_code,
            IRT.company_code==self.company_code, IRT.owner_code==self.owner_code, IRT.warehouse_code==self.warehouse_code).all()
        return rfids


class StockoutLine(db.Model):
    __tablename__ = 'o_stockout_line'
    __table_args__ = (
                      Index("ix_stockout_line_order_code", "order_code", "company_code"),
                      Index("ix_stockout_line_erp_order_code", "erp_order_code", "company_code"),
                      Index("ix_stockout_line_tenant", "company_code", 'warehouse_code', "owner_code",),
                      Index("ix_stockout_line_sku", "company_code", 'warehouse_code', "owner_code", 'order_code', 'sku'),
                      Index("ix_stockout_line_sku2", "company_code", 'warehouse_code', "owner_code", 'stockout_id', 'sku'),
                      Index("ix_stockout_line_sku3", 'stockout_id', 'sku'),
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
    qty        = db.Column(db.Integer, server_default='0', default=0)

    # 用来缓存已经出库的库位, 方便反单入库
    location_code = db.Column(db.String(50), server_default='', default='')

    qty_alloc = db.Column(db.Integer, server_default='0', default=0)  # 实际分配数量
    qty_pick  = db.Column(db.Integer, server_default='0', default=0)  # 实际拣货数量
    qty_ship  = db.Column(db.Integer, server_default='0', default=0)  # 实际发运数量

    qty_self  = db.Column(db.Integer, server_default='0', default=0)  # 用于销售单自有库存出库, 非采购的数量

    partner_id = db.Column(db.Integer)
    partner_name = db.Column(db.String(50), server_default='')
    # 指定出库的供应商
    supplier_code = db.Column(db.String(50), server_default='')
    # 指定规格
    spec = db.Column(db.String(50), server_default='')

    # qimen, 暂时没有用
    product_date = db.Column(db.Date)
    expire_date  = db.Column(db.Date)
    batch_code   = db.Column(db.String(50), server_default='')
    quality_type = db.Column(db.Enum('ZP', 'CC', 'DJ', 'ZT', 'JS', 'XS'), server_default='ZP')

    # 款色码
    style   = db.Column(db.String(50), server_default='')
    color   = db.Column(db.String(50), server_default='')
    size    = db.Column(db.String(50), server_default='')
    unit    = db.Column(db.String(20), server_default='')
    weight_unit = db.Column(db.String(10), server_default='')

    # 本次销售出库价格
    price = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)
    # 总成本
    cost_price = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)
    # 单件
    cost_per_price = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)

    # 非标件, 统计重量
    # 非标件, 可能按重量来算
    _weight = db.Column(db.Float(asdecimal=True, precision='15,4'), name='weight', server_default='0.00', default=0.00)
    _gross_weight = db.Column(db.Float(asdecimal=True, precision='15,4'), name='gross_weight', server_default='0.00', default=0.00)
    # 非标件, 内部数量
    _qty_inner = db.Column(db.Integer, name='qty_inner', server_default='0', default=0)

    custom_uuid = db.Column(db.String(50), server_default='')  # 自定义json字段，用于存放需要定制保存的字段，而不需要新增数据库字段

    # 关联
    stockout_id = db.Column(db.Integer, db.ForeignKey("o_stockout.id"))

    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())

    stockout = db.relationship("Stockout", backref=db.backref('lines', lazy='dynamic'))

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
    def good(self):
        Good = db.M('Good')
        return Good.query.filter(and_(
            Good.code==self.sku,
            Good.owner_code==self.owner_code,
            Good.company_code==self.company_code)).first()


    @property
    def JSON(self):
        big = None
        if self.custom_uuid:
            big = db.M('Big').query.filter_by(code='JSON', subcode='o_stockout_line__json', uuid=self.custom_uuid).first()
        return json.loads(big.blob) if big else {}

    @JSON.setter
    def JSON(self, obj):
        val = json_dump(obj)
        if self.custom_uuid:
            db.M('Big').query.filter_by(code='JSON', subcode='o_stockout_line__json', uuid=self.custom_uuid).update({'blob':val})
        else:
            uuid = str(uuid4())
            big = db.M('Big')(company_code=self.company_code, code='JSON', subcode='o_stockout_line__json', blob=val, uuid=uuid)
            db.session.add(big)
            self.custom_uuid = uuid

    @property
    def weight(self):
        if self.stockout.state  == 'doing':
            InvRfid = db.M('InvRfid')
            o = InvRfid.query.with_entities(func.sum(InvRfid._weight).label('weight')) \
                .filter_by(company_code=self.company_code, owner_code=self.owner_code, warehouse_code=self.warehouse_code, \
                    stockout_order_code=self.stockout.order_code) \
                .filter(InvRfid.sku==self.sku).first()
            self._weight = o.weight
        return self._weight

    @property
    def gross_weight(self):
        if self.stockout.state  == 'doing':
            InvRfid = db.M('InvRfid')
            o = InvRfid.query.with_entities(func.sum(InvRfid._gross_weight).label('gross_weight')) \
                .filter_by(company_code=self.company_code, owner_code=self.owner_code, warehouse_code=self.warehouse_code, \
                    stockout_order_code=self.stockout.order_code) \
                .filter(InvRfid.sku==self.sku).first()
            self._gross_weight = o.gross_weight
        return self._gross_weight

    @property
    def qty_inner(self):
        if self.stockout.state  == 'doing':
            InvRfid = db.M('InvRfid')
            o = InvRfid.query.with_entities(func.sum(InvRfid._qty_inner).label('qty_inner')) \
                .filter_by(company_code=self.company_code, owner_code=self.owner_code, warehouse_code=self.warehouse_code, \
                    stockout_order_code=self.stockout.order_code) \
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


class StockoutLineTrans(db.Model):
    __tablename__ = 'o_stockout_line_trans'
    __table_args__ = (Index("ix_o_trans_order_code", "order_code",),
                      Index("ix_o_trans_erp_order_code", "erp_order_code",),
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

    # 货品信息
    qty = db.Column(db.Integer, server_default='0', default=0)
    location_code = db.Column(db.String(50), server_default='', default='')

    price = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)

    # 流水类型; 分配，拣货，发运人，　取消分配，取消拣货，领料/领货人
    xtype = db.Column(db.Enum('alloc', 'pick', 'ship', 'unalloc', 'unpick', 'receive'), default='alloc')

    # 系统操作人信息
    user_code = db.Column(db.String(20))
    user_name = db.Column(db.String(20))

    # 仓库操作人信息/领料人信息
    w_user_code = db.Column(db.String(20))
    w_user_name = db.Column(db.String(20))

    # 外键
    stockout_id = db.Column(db.Integer, db.ForeignKey("o_stockout.id"))
    stockout_line_id = db.Column(db.Integer, db.ForeignKey("o_stockout_line.id"))

    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())

    stockout = db.relationship("Stockout", backref=db.backref('line_trans', lazy='dynamic'))
    stockout_line = db.relationship("StockoutLine", backref=db.backref('trans', lazy='dynamic'))


# alloc & pick & ship
class Alloc(db.Model):
    __tablename__ = 'o_alloc'
    __table_args__ = (Index("ix_alloc_sku", "sku", "location_code", "company_code",),
                      Index("ix_alloc_tenant", "company_code", 'warehouse_code', "owner_code",),
                      Index("ix_alloc_sku2", "sku", "stockout_line_id",),
                      )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    company_code = db.Column(db.String(50))
    warehouse_code = db.Column(db.String(50))
    owner_code = db.Column(db.String(50))

    order_code = db.Column(db.String(50), default='')
    middle_order_code = db.Column(db.String(50), default='')
    erp_order_code = db.Column(db.String(50), default='')

    # 一系列可以分配多个出库单，给汇总出库预留的字段; 
    # 多次分配的单子，多次分配时，打印一次拣货，就赋予一个号， 下次的分配，赋予另一个号；目前先不做，只做一次性分配拣货发运，不做部分发运
    series_code = db.Column(db.String(50), default='')

    location_code = db.Column(db.String(50))
    lpn = db.Column(db.String(50), server_default='', default='')
    inv_id = db.Column(db.Integer, default='')

    sku        = db.Column(db.String(50), server_default='')
    name       = db.Column(db.String(50), server_default='')
    barcode    = db.Column(db.String(50), server_default='')

    style       = db.Column(db.String(50), server_default='')
    color       = db.Column(db.String(50), server_default='')
    size        = db.Column(db.String(50), server_default='')

    spec        = db.Column(db.String(50), server_default='')
    unit        = db.Column(db.String(50), server_default='')

    # 订单行需求帐户变动信息
    qty_alloc = db.Column(db.Integer, server_default='0', default=0)  # 分配数量
    qty_pick  = db.Column(db.Integer, server_default='0', default=0)  # 实际捡货数量，复核之后
    qty_ship  = db.Column(db.Integer, server_default='0', default=0)  # 发运数量

    stockout_id = db.Column(db.Integer)
    stockout_line_id = db.Column(db.Integer)

    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())


    @property
    def stockout_line(self):
        StockoutLine = db.M('StockoutLine')
        return StockoutLine.query.filter(StockoutLine.id==self.stockout_line_id).first()

    @property
    def inv(self):
        Inv = db.M('Inv')
        return Inv.query.filter(Inv.id==self.inv_id).first()

    def lock_inv(self):
        Inv = db.M('Inv')
        return Inv.query.t_query.filter(Inv.id==self.inv_id).with_for_update().first()


# 装箱单
class Box(db.Model):
    __tablename__ = 'o_box'
    __table_args__ = (
                      Index("ix_box_tenant", "company_code", 'warehouse_code', "owner_code",),
                      Index("ix_box_code", "company_code", 'warehouse_code', "owner_code", "order_code"),
                      )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    company_code = db.Column(db.String(50))
    warehouse_code = db.Column(db.String(50))
    owner_code = db.Column(db.String(50))
    # 出库单
    order_code = db.Column(db.String(50), default='')
    # 销售单
    sale_order_code = db.Column(db.String(50), default='')

    # 箱号
    box_code = db.Column(db.String(50), default='')
    # 平台单号/唯一码
    plat_code = db.Column(db.String(250), default='')
    # 面单号
    bill_code = db.Column(db.String(50), default='')
    # 子单号, 多包裹时
    sub_bill_code = db.Column(db.String(50), default='')
    # express 快递公司缩写码
    express_code = db.Column(db.String(50), default='')
    express_name = db.Column(db.String(50), default='')
    express_type = db.Column(db.String(50), default='')
    # 模板html
    tpl = db.Column(db.Text(30000), default='')

    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())


class BoxLine(db.Model):
    __tablename__ = 'o_box_line'
    __table_args__ = (
                      Index("ix_boxline_tenant", "company_code", 'warehouse_code', "owner_code",),
                      Index("ix_boxline_order_code", "company_code", 'warehouse_code', "owner_code", "order_code"),
                      Index("ix_boxline_box_code", "company_code", 'warehouse_code', "owner_code", "box_code"),
                      )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    company_code = db.Column(db.String(50))
    warehouse_code = db.Column(db.String(50))
    owner_code = db.Column(db.String(50))
    # 出库单
    order_code = db.Column(db.String(50), default='')
    # 销售单
    sale_order_code = db.Column(db.String(50), default='')

    # 箱号
    box_code = db.Column(db.String(50), default='')
    # 面单号
    bill_code = db.Column(db.String(50), default='')
    # express 快递公司缩写码
    express_code = db.Column(db.String(50), default='')
    express_name = db.Column(db.String(50), default='')

    # 货品信息
    sku        = db.Column(db.String(50), server_default='')
    name       = db.Column(db.String(200), default='')
    barcode    = db.Column(db.String(50), server_default='')
    qty        = db.Column(db.Integer, server_default='0', default=0)

    # 指定规格
    spec = db.Column(db.String(50), server_default='')
    unit    = db.Column(db.String(20), server_default='')

    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())

    # 关联
    order_id = db.Column(db.Integer, db.ForeignKey("o_box.id"))
    order = db.relationship("Box", backref=db.backref('lines', lazy='dynamic'))



# PC只有快速拣货, 支持打印拣货单
# PDA有扫码拣货, 拣货数量依次计算到不同的单据上
# 复核发运可以要按单, 支持多包发运
class StockoutMerge(db.Model):
    __tablename__ = 'o_stockout_merge'
    __table_args__ = (
                      Index("ix_stockout_m_tenant", "company_code", 'warehouse_code', "owner_code",),
                      Index("ix_stockout_m_tenant_order_code", "company_code", 'warehouse_code', "owner_code", 'order_code'),
                      )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    company_code = db.Column(db.String(50))
    warehouse_code = db.Column(db.String(50))
    owner_code = db.Column(db.String(50))

    order_code = db.Column(db.String(50), default='')
    name = db.Column(db.String(50), default='')

    state = db.Column(db.Enum('create', 'done', 'cancel', 'doing'), server_default='create')
    # 分配状态, 捡货状态, 发运状态
    state_alloc = db.Column(db.Enum('no', 'part', 'done'), server_default='no')
    state_pick = db.Column(db.Enum('no', 'part', 'done'), server_default='no')
    state_ship = db.Column(db.Enum('no', 'part', 'done'), server_default='no')

    # 系统操作人信息
    user_code = db.Column(db.String(20))
    user_name = db.Column(db.String(20))
    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())


    @property
    def orders(self):
        return Stockout.query.t_query.filter(Stockout.merge_order_code==self.order_code).all()

    @property
    def lines(self):
        return StockoutLine.query.t_query.filter(Stockout.merge_order_code==self.order_code, Stockout.id==StockoutLine.stockout_id).all()

    def lines_with_batch(self):
        OL = StockoutLine
        return StockoutLine.query.with_entities(
                func.sum(OL.qty).label('qty'),
                func.sum(OL.qty_alloc).label('qty_alloc'),
                func.sum(OL.qty_pick).label('qty_pick'),
                func.sum(OL.qty_ship).label('qty_ship'),
                OL.sku.label('sku'),
                OL.name.label('name'),
                OL.barcode.label('barcode'),
                OL.spec.label('spec'),
                OL.unit.label('unit'),
            ).t_query.filter(Stockout.merge_order_code==self.order_code, Stockout.id==OL.stockout_id) \
            .group_by(OL.sku, OL.barcode, OL.spec).all()


    def calc_state(self):
        query = Stockout.query.t_query.filter(Stockout.merge_order_code==self.order_code)
        if query.count() == 0:
            self.state = 'cancel'
            return

        if query.filter(Stockout.state!='done').count() == 0:
            self.state = 'done'
        elif query.filter(Stockout.state!='create').count() > 0:
            self.state = 'doing'

        if query.filter(Stockout.state_alloc!='done').count() == 0:
            self.state_alloc = 'done'
        elif query.filter(Stockout.state_alloc!='no').count() > 0:
            self.state_alloc = 'part'

        if query.filter(Stockout.state_pick!='done').count() == 0:
            self.state_pick = 'done'
        elif query.filter(Stockout.state_pick!='no').count() > 0:
            self.state_pick = 'part'

        if query.filter(Stockout.state_ship!='done').count() == 0:
            self.state_ship = 'done'
        elif query.filter(Stockout.state_ship!='no').count() > 0:
            self.state_ship = 'part'

    
