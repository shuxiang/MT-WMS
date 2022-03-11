#coding=utf8
__all__ = ['Inv', 'InvRfid', 'InvRfidTrans', 'InvTrans', 
    'Category', 'Good', 'GoodMap', 
    'InvAdjust', 'InvMove', 'InvCount', 'InvWarn']

import os.path
import json
from sqlalchemy.sql import text
from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy import Index, UniqueConstraint
from sqlalchemy import func, or_, and_
from werkzeug.utils import cached_property
from utils.upload import get_oss_image, save_inv_qrcode, save_inv_barcode
from utils.flask_tools import json_dump

from extensions.database import db
import settings

class Inv(db.Model):
    __tablename__ = 'inv'
    __table_args__ = (
                      Index("ix_inv_sku", "sku", "location_code", "company_code"),
                      Index("ix_inv_barcode", "barcode", "location_code", "company_code"),
                      Index("ix_inv_tenant", "company_code", 'warehouse_code', "owner_code",),
                      )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # # 可用库存, 不可用库存, 限制库存
    # state = db.Column(db.Enum('Y', 'N', 'L'), default='Y')

    owner_code = db.Column(db.String(50))
    company_code = db.Column(db.String(50))
    warehouse_code = db.Column(db.String(50))

    # 库位信息
    location_code = db.Column(db.String(50))
    area_code = db.Column(db.String(50))
    workarea_code = db.Column(db.String(50))

    # 货品信息
    category_code = db.Column(db.String(50), default='')
    sku         = db.Column(db.String(50), server_default='')
    name        = db.Column(db.String(200), default='')
    name_en = db.Column(db.String(200), default='')
    barcode     = db.Column(db.String(50), server_default='')

    brand = db.Column(db.String(20), server_default='')
    
    # qty = qty_alloc + qty_able;
    qty             = db.Column(db.Integer, server_default='0', default=0)
    qty_alloc       = db.Column(db.Integer, server_default='0', default=0)
    qty_able        = db.Column(db.Integer, server_default='0', default=0)
    # 冻结数量
    qty_freeze      = db.Column(db.Integer, server_default='0', default=0)

    stockin_date = db.Column(db.Date, default=db.func.current_date())
    
    partner_name = db.Column(db.String(50), server_default='')
    # 批次属性
    supplier_code = db.Column(db.String(50), server_default='')
    # 库存类型(ZP=正品;CC=残次;JS=机损;XS= 箱损;ZT=在途库存;DJ=冻结;)
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

    # 容器
    lpn = db.Column(db.String(50), server_default='', default='')

    # 出库单PICK关联的stockout_id
    refid = db.Column(db.Integer, default=0)
    refin_order_code = db.Column(db.String(50), server_default='', default='')

    # 分裂库存模式, split by `order_code` 的时候有效
    price = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)

    remark = db.Column(db.String(200), server_default='', default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())


    @property
    def location(self):
        Location = db.M('Location')
        return Location.filter(and_(
            Location.code==self.location_code,
            Location.company_code==self.company_code,
            Location.warehouse_code==self.warehouse_code)).first()
    

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
    def area(self):
        Area = db.M('Area')
        return Area.query.filter(and_(
            Area.code==self.area_code,
            Area.company_code==self.company_code,
            Area.warehouse_code==self.warehouse_code)).first()

    @property
    def workarea(self):
        Workarea = db.M('Workarea')
        return Workarea.query.filter(and_(
            Workarea.code==self.workarea_code,
            Workarea.company_code==self.company_code,
            Workarea.warehouse_code==self.warehouse_code)).first()

    @property
    def category(self):
        Category = db.M('Category')
        return Category.query.filter(and_(
            Category.code==self.category_code,
            Category.owner_code==self.owner_code,
            Category.company_code==self.company_code)).first()

    @property
    def good(self):
        if getattr(self, '_good', None) is None:
            Good = db.M('Good')
            self._good = Good.query.filter(and_(
                Good.code==self.sku,
                Good.company_code==self.company_code,
                Good.owner_code==self.owner_code)).first()
        return self._good


class InvRfid(db.Model):
    __tablename__ = 'inv_rfid'
    __table_args__ = (
                      Index("ix_invrfid_sku", "sku", "location_code", "company_code"),
                      Index("ix_invrfid_rfid", "rfid", "location_code", "company_code"),
                      Index("ix_invrfid_tenant", "company_code", 'warehouse_code', "owner_code",),
                      )


    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    owner_code = db.Column(db.String(50))
    company_code = db.Column(db.String(50))
    warehouse_code = db.Column(db.String(50))

    inv_id = db.Column(db.Integer)
    qty    = db.Column(db.Integer, server_default='0', default=0)
    rfid   = db.Column(db.String(255), server_default='', default='')

    # 非标件, 可能按重量来算
    _weight = db.Column(db.Float(asdecimal=True, precision='15,4'), name='weight', server_default='0.00', default=0.00)
    _gross_weight = db.Column(db.Float(asdecimal=True, precision='15,4'), name='gross_weight', server_default='0.00', default=0.00)
    # 非标件, 内部数量
    _qty_inner = db.Column(db.Integer, name='qty_inner', server_default='1', default=1)

    # 上游传入的/系统自动产生的, 用户生成的, 用户导入的
    source = db.Column(db.String(50), server_default='erp')
    printed = db.Column(db.Boolean, default=False, server_default='0')

    # 在用 on / 废弃 off
    state  = db.Column(db.String(10), default='on', server_default='on')

    # 库位信息
    location_code = db.Column(db.String(50))
    area_code = db.Column(db.String(50))
    workarea_code = db.Column(db.String(50))

    # 货品信息
    category_code = db.Column(db.String(50), default='')
    sku         = db.Column(db.String(50), server_default='')
    name        = db.Column(db.String(200), default='')
    name_en = db.Column(db.String(200), default='')
    barcode     = db.Column(db.String(50), server_default='')

    brand = db.Column(db.String(20), server_default='')

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

    # 容器
    lpn = db.Column(db.String(50), server_default='', default='')


    # 入库信息----------
    stockin_order_code = db.Column(db.String(50)) # erp_order_code
    stockin_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    # 系统操作人信息
    in_user_code = db.Column(db.String(20))
    in_user_name = db.Column(db.String(20))

    # 仓库操作人信息/领料人信息
    in_w_user_code = db.Column(db.String(20))
    in_w_user_name = db.Column(db.String(20))

    # end 入库信息----------

    # 出库信息 ----------
    stockout_order_code = db.Column(db.String(50)) # erp_order_code
    stockout_date = db.Column(db.DateTime)

    # 系统操作人信息
    out_user_code = db.Column(db.String(20))
    out_user_name = db.Column(db.String(20))

    # 仓库操作人信息/领料人信息
    out_w_user_code = db.Column(db.String(20))
    out_w_user_name = db.Column(db.String(20))

    # end 出库信息 ----------

    remark = db.Column(db.String(200), server_default='', default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())

    __dump_prop__ = ('weight', 'gross_weight', 'qty_inner', )


    @property
    def inv(self):
        return Inv.query.filter(Inv.id==self.inv_id).first()

    @property
    def weight(self):
        return self._weight

    @property
    def gross_weight(self):
        return self._gross_weight

    @property
    def qty_inner(self):
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

    def get_barcode(self, company_id):
        if not os.path.exists(os.path.join(settings.UPLOAD_DIR, 'barcode', company_id, self.barcode)):
            _, path = save_inv_barcode(settings.UPLOAD_DIR, company_id, self.barcode)
        else:
            path = '/static/upload/barcode/%s/%s.png'%(company_id, self.barcode)
        return path

    def get_qrcode(self, company_id):
        if not os.path.exists(os.path.join(settings.UPLOAD_DIR, 'qrcode', company_id, self.rfid)):
            _, path = save_inv_qrcode(settings.UPLOAD_DIR, company_id, self.rfid)
        else:
            path = '/static/upload/qrcode/%s/%s.png'%(company_id, self.rfid)
        return path


# 唯一码流水只记录进出库信息
class InvRfidTrans(db.Model):
    __tablename__ = 'inv_rfid_trans'
    __table_args__ = (
                      Index("ix_invrfid_rfid", "company_code", 'warehouse_code', "owner_code", "rfid"),
                      Index("ix_invrfid_tenant", "company_code", 'warehouse_code', "owner_code",),
                      )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    owner_code = db.Column(db.String(50))
    company_code = db.Column(db.String(50))
    warehouse_code = db.Column(db.String(50))

    rfid   = db.Column(db.String(255), server_default='', default='')
    sku    = db.Column(db.String(50), server_default='')
    name    = db.Column(db.String(200), server_default='')
    barcode = db.Column(db.String(50), server_default='')

    # 系统操作人信息
    user_code = db.Column(db.String(20))
    user_name = db.Column(db.String(20))

    # 仓库操作人信息/领料人信息
    w_user_code = db.Column(db.String(20))
    w_user_name = db.Column(db.String(20))

    xtype = db.Column(db.String(20), default='in') # in/out
    order_type = db.Column(db.String(20), default='produce') # in.xtype/out.order_type
    order_code = db.Column(db.String(50), default='')

    remark = db.Column(db.String(200), server_default='', default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())


# 库存流水
class InvTrans(db.Model):
    __tablename__ = 'inv_trans'
    __table_args__ = (Index("ix_inv_trans_sku", "sku", "location_code", "company_code",),
                      Index("ix_inv_trans_tenant", "company_code", 'warehouse_code', "owner_code",),
                      )


    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    owner_code = db.Column(db.String(50))
    company_code = db.Column(db.String(50))
    warehouse_code = db.Column(db.String(50))

    # 库位信息
    location_code = db.Column(db.String(50))
    area_code = db.Column(db.String(50))

    # 货品信息
    category_code = db.Column(db.String(50), server_default='')
    sku = db.Column(db.String(50), server_default='')
    name = db.Column(db.String(200), server_default='')
    barcode = db.Column(db.String(50), server_default='')

    before_qty = db.Column(db.Integer, server_default='0', default=0)
    change_qty = db.Column(db.Integer, server_default='0', default=0)
    after_qty  = db.Column(db.Integer, server_default='0', default=0)

    price = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)
    qty_able = db.Column(db.Integer, server_default='0', default=0)

    # 入库单， 出库单， 移库单， 调整单， 转换单
    # stockin stockout inv_move inv_adjust inv_transfer
    xtype = db.Column(db.Enum('stockin', 'stockout', 'inv_move', 'inv_adjust', 'inv_transfer'), server_default='stockout')
    # 操作过程
    xtype_opt = db.Column(db.Enum('alloc', 'pick', 'cancel', 'in', 'out'), default='in')

    # 操作信息
    order_code = db.Column(db.String(50))
    erp_order_code = db.Column(db.String(50))

    # 系统操作人信息
    user_code = db.Column(db.String(20), default='')
    user_name = db.Column(db.String(20), default='')

    # 外键
    inventory_id = db.Column(db.Integer)

    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())


# 货类数据库结构定义
class Category(db.Model):
    __tablename__ = 'inv_category'
    __table_args__ = (Index("ix_inv_category_code", 'code', "company_code",),
                      Index("ix_inv_category_tenant", 'owner_code', "company_code",),
                      )

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), default='')
    name = db.Column(db.String(50), default='')

    owner_code = db.Column(db.String(50))
    company_code = db.Column(db.String(50))

    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())

    @property
    def company(self):
        Company = db.M('Company')
        return Company.query.filter_by(code=self.company_code).first()

    @property
    def owner(self):
        Partner = db.M('Partner')
        return Partner.query.filter(and_(
            Partner.code==self.owner_code,
            Partner.company_code==self.company_code)).first()


# 货品数据结构定义
class Good(db.Model):
    __tablename__ = 'inv_good'
    __table_args__ = (Index("ix_inv_good_code", "code", "company_code",),
                      Index("ix_inv_good_tenant", 'owner_code', "company_code",),
                      )

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), default='')

    name = db.Column(db.String(200), default='')
    name_en = db.Column(db.String(200), default='')
    barcode = db.Column(db.String(50), default='')

    middle_code = db.Column(db.String(50), default='')

    # 需要生产的, 会生成 生产单, 不需要生产的, 会生成 采购单
    is_produce = db.Column(db.Boolean, default=False)

    # is_main
    has_subs = db.Column(db.Boolean, default=False)

    # 规格
    spec   = db.Column(db.String(100), default='', server_default='')
    # 上架/下架 on/down, 删除delete
    state  = db.Column(db.String(100), default='on', server_default='on')

    # 长、款、高、体积（奇门发来的是double类型，这里需要string转换）
    length = db.Column(db.String(50), default='')
    width  = db.Column(db.String(50), default='')
    height = db.Column(db.String(50), default='')
    volume = db.Column(db.String(50), default='')
    # 净重
    weight = db.Column(db.String(50), default='0', server_default='0')
    # 毛重
    gross_weight = db.Column(db.String(50), default='0', server_default='0')
    # 重量单位 kg/g
    weight_unit = db.Column(db.String(10), default='')

    index = db.Column(db.Integer, default=0, server_default='0')

    # 预警: 最高库存, 最低库存
    min_qty = db.Column(db.Integer, default=0, server_default='0')
    max_qty = db.Column(db.Integer, default=0, server_default='0')

    # 价格，先选择零售价
    price = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)
    # 生产成本
    cost_price = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)
    # 最近一次价格
    last_in_price = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)
    last_out_price = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)

    # 来源 erp, import, other:上游公司码
    source = db.Column(db.String(50), server_default='erp')

    # laoa fields; 
    # app这边的good id
    appid = db.Column(db.String(50), server_default='')
    # 质保期限
    quality_month = db.Column(db.Integer, server_default='0', default=0)
    # 开模分摊费
    model_price = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)
    # 运费
    express_price = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)
    # 分级经销商价
    lv1_price = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)
    lv2_price = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)
    lv3_price = db.Column(db.Float(asdecimal=True, precision='15,4'), server_default='0.00', default=0)

    # 是否同步
    is_sync   = db.Column(db.String(1), server_default='0')

    # 图片
    image_url = db.Column(db.String(255), server_default='')
    # images
    images = db.Column(db.String(1500), server_default='')
    ad_images = db.Column(db.String(1500), server_default='')

    # 默认存放的库区/库位
    area_code = db.Column(db.String(50), server_default='')
    location_code = db.Column(db.String(50), server_default='')
    
    # 款色码
    style   = db.Column(db.String(50), server_default='')
    color   = db.Column(db.String(50), server_default='')
    size    = db.Column(db.String(50), server_default='')
    unit    = db.Column(db.String(20), server_default='')

    # 产品参数
    args = db.Column(db.String(500), server_default='')

    # qimen 类型 ZC=正常商品;FX=分销商品;ZH=组合商品;ZP=赠品;BC=包材;HC=耗材;FL=辅料;XN=虚拟品;FS=附属品;CC=残次品; OTHER=其它;
    item_type = db.Column(db.String(20), server_default='ZC', default='ZC')

    brand = db.Column(db.String(20), server_default='')
    category_code = db.Column(db.String(50), default='')

    # 是否使用保质期管理 on/off
    is_shelf_life = db.Column(db.String(20), server_default='off', default='off')

    owner_code = db.Column(db.String(50))
    company_code = db.Column(db.String(50))

    custom_uuid = db.Column(db.String(50), server_default='')
    version = db.Column(db.Integer)

    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())


    __dump_prop__ = ('sku', 'is_main', 'images_list', 'ad_images_list', 'args_list',)

    @property
    def sku(self):
        return self.code

    @cached_property
    def company_id(self):
        return db.M('Company').query.filter_by(code=self.company_code).first().id

    @property
    def images_list(self):
        if self.images:
            if self.image_url:
                return [img for img in self.images.split(',') if img]
            return [img for img in self.images.split(',') if img]
        return []

    @property
    def ad_images_list(self):
        if self.ad_images:
            return [img for img in self.ad_images.split(',') if img]
        return []

    @property
    def args_list(self):
        return [a for a in self.args.split('\n') if a]
    

    @property
    def company(self):
        Company = db.M('Company')
        return Company.query.filter_by(code=self.company_code).first()

    @property
    def owner(self):
        Partner = db.M('Partner')
        return Partner.query.filter(and_(
            Partner.code==self.owner_code,
            Partner.company_code==self.company_code)).first()

    @property
    def category(self):
        Category = db.M('Category')
        return Category.query.filter(and_(
            Category.code==self.category_code,
            Category.owner_code==self.owner_code,
            Category.company_code==self.company_code)).first()

    # 是否主件
    @property
    def is_main(self):
        return self.has_subs
        # self.has_subs = GoodMap.query.filter(GoodMap.code==self.code, GoodMap.owner_code==self.owner_code, GoodMap.company_code==self.company_code).count() > 0
        # return self.has_subs

    # 需要生产
    @property
    def need_produce(self):
        return self.is_produce or self.is_main

    # 是否配件
    @property
    def is_sub(self):
        return GoodMap.query.filter(GoodMap.subcode==self.code, GoodMap.owner_code==self.owner_code, GoodMap.company_code==self.company_code).count()
    
    # 配件列表
    @property
    def sub_goods(self):
        gm = GoodMap.query.filter(GoodMap.code==self.code, GoodMap.owner_code==self.owner_code, GoodMap.company_code==self.company_code).first()
        if gm:
            return gm.sub_goods
        return []

    @property
    def JSON(self):
        big = None
        if self.custom_uuid:
            big = db.M('Big').query.filter_by(code='JSON', subcode='inv_good__json', uuid=self.custom_uuid).first()
        return json.loads(big.blob) if big else {}

    @JSON.setter
    def JSON(self, obj):
        val = json_dump(obj)
        if self.custom_uuid:
            db.M('Big').query.filter_by(code='JSON', subcode='inv_good__json', uuid=self.custom_uuid).update({'blob':val})
        else:
            uuid = str(uuid4())
            big = db.M('Big')(company_code=self.company_code, code='JSON', subcode='inv_good__json', blob=val, uuid=uuid)
            db.session.add(big)
            self.custom_uuid = uuid

    # 计算配件成本价-- 子件
    def calc_cost_price(self):
        return self.cost_price

    def calc_main_cost_price(self):
        gm = GoodMap.query.o_query.filter_by(code=self.code).first()
        if gm:
            self.cost_price = gm.main_cost_price
        return self.cost_price

    def get_barcode(self, company_id):
        if not os.path.exists(os.path.join(settings.UPLOAD_DIR, 'barcode', company_id, self.barcode)):
            _, path = save_inv_barcode(settings.UPLOAD_DIR, company_id, self.barcode)
        else:
            path = '/static/upload/barcode/%s/%s.png'%(company_id, self.barcode)
        return path

    def get_qrcode(self, company_id):
        if not os.path.exists(os.path.join(settings.UPLOAD_DIR, 'qrcode', company_id, self.sku)):
            _, path = save_inv_qrcode(settings.UPLOAD_DIR, company_id, self.sku)
        else:
            path = '/static/upload/qrcode/%s/%s.png'%(company_id, self.sku)
        return path


class GoodMap(db.Model):
    __tablename__ = 'inv_good_map'
    __table_args__ = (Index("ix_inv_good_map_code", "code", 'subcode', "company_code",),
                      Index("ix_inv_good_map_tenant", 'owner_code', "company_code",),
                      )
    # 导入时要删除主配件关系，再新增新的
    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.String(50), default='')
    name = db.Column(db.String(200), default='')
    name_en = db.Column(db.String(200), default='')
    barcode = db.Column(db.String(50), default='')

    subcode = db.Column(db.String(50), default='')
    subname = db.Column(db.String(200), default='')
    subbarcode = db.Column(db.String(50), default='')

    qty = db.Column(db.Integer, server_default='1', default=1)

    owner_code = db.Column(db.String(50))
    company_code = db.Column(db.String(50))

    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())

    @property
    def company(self):
        Company = db.M('Company')
        return Company.query.filter_by(code=self.company_code).first()

    @property
    def owner(self):
        Partner = db.M('Partner')
        return Partner.query.filter(and_(
            Partner.code==self.owner_code,
            Partner.company_code==self.company_code)).first()

    @property
    def good(self):
        return Good.query.filter_by(code=self.code, owner_code=self.owner_code, company_code=self.company_code).first()

    @property
    def sub_good(self):
        return Good.query.filter_by(code=self.subcode, owner_code=self.owner_code, company_code=self.company_code).first()

    @property
    def sub_goods(self):
        return Good.query.filter(
            Good.owner_code==self.owner_code, 
            Good.company_code==self.company_code,
            Good.code==GoodMap.subcode,
            GoodMap.code==self.code, 
            GoodMap.owner_code==self.owner_code, 
            GoodMap.company_code==self.company_code).all()

    @property
    def main_cost_price(self):
        o = GoodMap.query.with_entities(func.sum(Good.cost_price*GoodMap.qty).label('cost_price')).filter(
            Good.owner_code==self.owner_code, 
            Good.company_code==self.company_code,
            Good.code==GoodMap.subcode,
            GoodMap.code==self.code, 
            GoodMap.owner_code==self.owner_code, 
            GoodMap.company_code==self.company_code).first()
        return float(o.cost_price or 0) if o else 0
    

    @property
    def map_goods(self):
        return GoodMap.query.filter_by(code=self.code, owner_code=self.owner_code, company_code=self.company_code).all()
    
    



class InvAdjust(db.Model):
    __tablename__ = 'inv_adjust'
    __table_args__ = (
                      Index("ix_inv_adjust_series", "company_code", "series_code"),
                      Index("ix_inv_adjust_tenant", "company_code", 'warehouse_code', "owner_code",),
                      )

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), default='')
    count_code = db.Column(db.String(50), default='')

    owner_code = db.Column(db.String(50))
    warehouse_code = db.Column(db.String(50))
    company_code = db.Column(db.String(50))

    location_code = db.Column(db.String(50))

    sku = db.Column(db.String(50), server_default='')
    name        = db.Column(db.String(200), default='')
    barcode = db.Column(db.String(50), server_default='')

    qty_before = db.Column(db.Integer, default=0) # 调整前数量
    qty_after = db.Column(db.Integer, default=0) # 调整后数量
    qty_diff = db.Column(db.Integer, default=0) # 前后差值; qty_after - qty_before; qty_real - qty

    # 一系列可以下发多个调整单
    series_code = db.Column(db.String(50), default='')
    # 盘点单号
    count_series_code = db.Column(db.String(50), default='')

    stockin_date = db.Column(db.Date)
    source = db.Column(db.String(50), server_default='erp')

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

    # 容器
    lpn = db.Column(db.String(50), server_default='', default='')

    state = db.Column(db.Enum('create', 'done', 'cancel'), server_default='create')

    user_code = db.Column(db.String(20), default='')
    user_name = db.Column(db.String(20), default='')

    remark = db.Column(db.String(200), server_default='', default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())


    @property
    def inv_count(self):
        InvCount = db.M('InvCount')
        return InvCount.query.filter(and_(
            InvCount.code==self.count_code,
            InvCount.company_code==self.company_code,
            InvCount.owner_code==self.owner_code,
            InvCount.warehouse_code==self.warehouse_code)).first()


class InvCount(db.Model):
    __tablename__ = 'inv_count'
    __table_args__ = (
                      Index("ix_inv_count_series", "company_code", "series_code"),
                      Index("ix_inv_count_tenant", "company_code", 'warehouse_code', "owner_code",),
                      )

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), default='')

    owner_code = db.Column(db.String(50))
    warehouse_code = db.Column(db.String(50))
    company_code = db.Column(db.String(50))

    location_code = db.Column(db.String(50))

    sku = db.Column(db.String(50), server_default='')
    name        = db.Column(db.String(200), default='')
    barcode = db.Column(db.String(50), server_default='')

    qty = db.Column(db.Integer, default=0) # 系统数量
    qty_real = db.Column(db.Integer, default=0) # 盘点数量
    qty_alloc = db.Column(db.Integer, default=0) # 锁定数量

    # 一系列可以下发多个盘点单
    series_code = db.Column(db.String(50), default='')
    adjust_series_code = db.Column(db.String(50), default='')

    stockin_date = db.Column(db.Date)
    source = db.Column(db.String(50), server_default='erp')

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

    # 容器
    lpn = db.Column(db.String(50), server_default='', default='')

    state = db.Column(db.Enum('create', 'done', 'cancel'), server_default='create')

    user_code = db.Column(db.String(20), default='')
    user_name = db.Column(db.String(20), default='')

    remark = db.Column(db.String(200), server_default='', default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())


class InvMove(db.Model):
    __tablename__ = 'inv_move'
    __table_args__ = (
                      Index("ix_inv_move_series", "company_code", "series_code"),
                      Index("ix_inv_move_tenant", "company_code", 'warehouse_code', "owner_code",),
                      )

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), default='')

    # 入库单转移库单
    stockin_order_code = db.Column(db.String(50), default='', server_default='')

    owner_code = db.Column(db.String(50))
    warehouse_code = db.Column(db.String(50))
    dest_warehouse_code = db.Column(db.String(50))
    company_code = db.Column(db.String(50))

    location_code = db.Column(db.String(50))
    dest_location_code = db.Column(db.String(50))

    sku = db.Column(db.String(50), server_default='')
    name        = db.Column(db.String(200), default='')
    barcode = db.Column(db.String(50), server_default='')

    qty = db.Column(db.Integer, default=0)
    # 实际移库数量
    qty_real = db.Column(db.Integer, default=0, server_default='0')

    # 一系列可以下发多个移库单
    series_code = db.Column(db.String(50), default='')
    # 系统生成的移库单（可以移库，也可以拣货）system，还是用户生成的移库单 user, 捕获移库 replenish, 上架 onshelf
    move_type = db.Column(db.String(20), default='user')

    stockin_date = db.Column(db.Date)
    # 'erp', 'custom', 'import'
    source = db.Column(db.String(50), server_default='erp')

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

    # 容器
    lpn = db.Column(db.String(50), server_default='', default='')
    dest_lpn = db.Column(db.String(50), server_default='', default='')

    state = db.Column(db.Enum('create', 'done', 'doing', 'cancel'), server_default='create')

    user_code = db.Column(db.String(20), default='')
    user_name = db.Column(db.String(20), default='')

    remark = db.Column(db.String(200), server_default='', default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())


# 库位库存预警
class InvWarn(db.Model):
    __tablename__ = 'inv_warn'
    __table_args__ = (
                      Index("ix_inv_warn_tenant", "company_code", 'warehouse_code', "owner_code",),
                      )

    id = db.Column(db.Integer, primary_key=True)

    owner_code = db.Column(db.String(50))
    warehouse_code = db.Column(db.String(50))
    company_code = db.Column(db.String(50))

    location_code = db.Column(db.String(50))

    sku = db.Column(db.String(50), server_default='')
    name = db.Column(db.String(200), default='')
    barcode = db.Column(db.String(50), server_default='')

    min_qty = db.Column(db.Integer, default=0) # 预警数量
    max_qty = db.Column(db.Integer, default=0) # 最高补货数量

    # 批次属性
    supplier_code = db.Column(db.String(50), server_default='')
    spec = db.Column(db.String(50), server_default='')

    remark = db.Column(db.String(200), server_default='', default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())
