#coding=utf8
import time
from datetime import datetime
from uuid import uuid4
from flask import g
from random import randint
from utils.functions import update_model_with_fields, m2dict, copy_and_update_model, common_poplist, json2mdict, json2mdict_pop, clear_empty, ubarcode, DictNone
from sqlalchemy import func, or_, and_

from models.auth import Seq
from models.inv import Inv, InvTrans, Category, Good, InvRfid, InvRfidTrans
from models.inv import InvAdjust, InvMove, InvCount
from models.warehouse import Location, Area, Workarea, Warehouse

from extensions.database import db
import settings

class InvAction(object):

    def __init__(self, inv=None):
        self.inv = None

    def ondown_good(self, sku=None, oid=None):
        query = Good.query.o_query
        if sku:
            query = query.filter(Good.sku==sku)
        if oid:
            query = query.filter(Good.id==oid)

        good = query.first()
        if good.state == 'on':
            good.state = 'down'
        else:
            good.state = 'on'
        return good

    # 通过入库单行， 获取库存行 query 对象
    def get_inv_query_by_stockin_line(self, line, i_sku=True, i_batch=True, i_style=True, is_split=False):
        subq = Inv.query.filter(Inv.location_code!='PICK').filter_by(
                owner_code=line.owner_code, 
                warehouse_code=line.warehouse_code, 
                company_code=line.company_code
            )
        # sku
        if i_sku:
            subq = subq.filter_by(sku=line.sku)

        # 批次属性过滤, 入库时间会每次创建时填充，所以，不算批次属性
        if i_batch:
            subq = subq.filter_by(
                #stockin_date=line.stockin_date,
                quality_type=line.quality_type,
                product_date=line.product_date,
                expire_date=line.expire_date,
                batch_code=line.batch_code,
                virtual_warehouse=line.virtual_warehouse,
                spec=line.spec,
            )
        if g.owner.is_enable_supplier_batch:
            subq = subq.filter_by(supplier_code=line.supplier_code)

        # 分裂内存方式
        if is_split:
            split_inv_type = g.owner.split_inv_type
            # 按入库单号分开
            if split_inv_type == 'order_code':
                subq = subq.filter_by(refin_order_code=line.order_code)
            elif split_inv_type == 'stockin_date':
                subq = subq.filter_by(stockin_date=db.func.current_date())
            elif split_inv_type == 'order_code_stockin_date':
                subq = subq.filter_by(refin_order_code=line.order_code)
                subq = subq.filter_by(stockin_date=db.func.current_date())
            elif split_inv_type == 'new':
                # 会查不到库存行, 入库只能创建新的库存
                subq = subq.filter_by(refin_order_code='new')
            else:
                # split_inv_type == 'no_split'
                pass
        # 款色码过滤
        if i_style:
            subq = subq.filter_by(
                style=line.style,
                color=line.color,
                size=line.size
            )
        return subq

    # 通过sku， 获取库存行 query 对象
    def get_inv_query_by_sku(self, sku, spec=None, supplier_code=None, not_locations=None):
        subq = Inv.query.filter(Inv.location_code!='PICK').filter_by(
                owner_code=g.owner_code, 
                warehouse_code=g.warehouse_code, 
                company_code=g.company_code
            ).filter_by(sku=sku)

        if supplier_code:
            subq = subq.filter_by(supplier_code=supplier_code)
        if spec:
            subq = subq.filter_by(spec=spec)
        if not_locations:
            subq = subq.filter(~Inv.location_code.in_(not_locations))
        return subq

    # 入库推荐库位
    def recommend_location(self, line, q=None):
        locations = []
        set_locations = set()
        subq = self.get_inv_query_by_stockin_line(line)
        subq = subq.group_by(Inv.location_code)

        for inv in subq.all():
            set_locations.add(inv.location_code)
            locations.append({'value':inv.location_code, 'qty':0, 'qty_total':0, 'label': inv.location_code})

        if len(locations) < settings.RECOMMEND_LOCATIONS:
            subq = self.get_inv_query_by_stockin_line(line, i_style=False)
            for inv in subq.all():
                if inv.location_code not in set_locations:
                    set_locations.add(inv.location_code)
                    locations.append({'value':inv.location_code, 'qty':0, 'qty_total':0, 'label': inv.location_code})

            if len(locations) < settings.RECOMMEND_LOCATIONS:
                subq = self.get_inv_query_by_stockin_line(line, i_batch=False, i_style=False)
                for inv in subq.all():
                    if inv.location_code not in set_locations:
                        set_locations.add(inv.location_code)
                        locations.append({'value':inv.location_code, 'qty':0, 'qty_total':0, 'label': inv.location_code})

                if len(locations) < settings.RECOMMEND_LOCATIONS: 
                    subq = self.get_inv_query_by_stockin_line(line, i_sku=False, i_batch=False, i_style=False)
                    for inv in subq.all():
                        if inv.location_code not in set_locations:
                            set_locations.add(inv.location_code)
                            locations.append({'value':inv.location_code, 'qty':0, 'qty_total':0, 'label': inv.location_code})

                    if len(locations) < settings.RECOMMEND_LOCATIONS:
                        # 如果库位数还不够，就推荐库存不一样的库位
                        locs = Location.query.w_query.filter(Location.code!='PICK').limit(10).all()
                        for loc in locs:
                            if loc.code not in set_locations:
                                set_locations.add(loc.code)
                                locations.append({'value':loc.code, 'qty':0, 'qty_total':0, 'label': loc.code})

        # 搜索库位 fetch 5 items
        if q:
            _locations = [{'value':l.code, 'qty':0, 'qty_total': 0, 'label':l.code} \
                    for l in Location.query.with_entities(Location.code).w_query \
                    .filter(Location.code.like('%%%s%%'%q), ~Location.code.in_([lo['value'] for lo in locations]), Location.code!='PICK').limit(5).all()]
            locations = _locations + locations

        qty_total = func.sum(Inv.qty).label('qty_total')
        for loc in locations[:10]:
            inv = Inv.query.w_query.with_entities(qty_total).filter_by(location_code=loc['value']).first()
            inv2 = Inv.query.w_query.with_entities(qty_total).filter_by(location_code=loc['value'], sku=line.sku).first()

            loc['qty_total'] = int(inv.qty_total or 0) if inv else 0
            loc['qty'] = int(inv2.qty_total or 0) if inv2 else 0
        # 库位, 库位该货品数, 库位总货品数; 控制库位总货品数
        # 只是推荐库位，方便类似的商品都放到类似的商品都放到附近；最终入库时，库存行是按库位，批次，款色码，容器号等进行明确区分的
        return locations[:10]


    # 推荐库位
    def recommend_location_by_sku(self, sku, location=None, q=None):
        locations = []
        set_locations = set()
        subq = self.get_inv_query_by_sku(sku, not_locations=[location] if location else None)
        subq = subq.group_by(Inv.location_code)

        for inv in subq.all():
            set_locations.add(inv.location_code)
            locations.append({'value':inv.location_code, 'qty':0, 'qty_total':0, 'label': inv.location_code})

        # 搜索库位 fetch 5 items
        if q:
            _locations = [{'value':l.code, 'qty':0, 'qty_total': 0, 'label':l.code} \
                    for l in Location.query.with_entities(Location.code).w_query \
                    .filter(
                        Location.code.like('%%%s%%'%q), 
                        ~Location.code.in_([lo['value'] for lo in locations]), 
                        Location.code!=location, 
                        Location.code!='PICK').limit(5).all()]
            locations = _locations + locations

        qty_total = func.sum(Inv.qty).label('qty_total')
        for loc in locations[:10]:
            inv = Inv.query.w_query.with_entities(qty_total).filter_by(location_code=loc['value']).first()
            inv2 = Inv.query.w_query.with_entities(qty_total).filter_by(location_code=loc['value'], sku=sku).first()

            loc['qty_total'] = int(inv.qty_total or 0) if inv else 0
            loc['qty'] = int(inv2.qty_total or 0) if inv2 else 0
        # 库位, 库位该货品数, 库位总货品数; 控制库位总货品数
        # 只是推荐库位，方便类似的商品都放到类似的商品都放到附近；最终入库时，库存行是按库位，批次，款色码，容器号等进行明确区分的
        if not locations:
            _locations = [{'value':l.code, 'qty':0, 'qty_total': 0, 'label':l.code} \
                    for l in Location.query.with_entities(Location.code).w_query \
                    .filter(Location.code!=location, Location.code!='PICK').limit(5).all()]
            # print locations, _locations
            locations = _locations + locations
        return locations[:10]

    # 通过入库库存行，创建库存
    def create_inv_by_stockin_line(self, line, location_code, lpn=''):
        inv = Inv()
        poplist = common_poplist+['qty', ]

        # 复制货品sku，款色码，批次等
        for c in line._columns_name:
            if c in inv._columns_name and c not in poplist:
                setattr(inv, c, getattr(line, c))
        # 改为: 入库的时候记录供应商, 但出库还是按有没有启用供应商批次来过滤出库
        if not g.owner.is_enable_supplier_batch:
            split_inv_type = g.owner.split_inv_type
            if split_inv_type.startswith('order_code') or split_inv_type == 'new':
                pass
            else:
                inv.supplier_code = ''

        inv.qty = inv.qty_able = inv.qty_alloc = 0

        # category, good
        good = Good.query.filter_by(company_code=line.company_code, owner_code=line.owner_code, code=line.sku).first()
        if good is None:
            category = InvAction.default_category()
            good = Good(code=line.sku, name=line.name, barcode=line.barcode)
            good.name_en = ubarcode(good.name)
            good.category_code = category.code
            db.session.add(good)
        inv.sku = good.code
        inv.category_code = good.category_code
        inv.brand = good.brand

        # location, lpn, area, workarea
        inv.location_code = location_code
        inv.lpn = lpn
        location = Location.query.filter_by(company_code=line.company_code, warehouse_code=line.warehouse_code, code=location_code).first()
        if location is None:
            location = Location(code=location_code, company_code=line.company_code, warehouse_code=line.warehouse_code)
            location.area_code = InvAction.default_area().code
            location.workarea_code = InvAction.default_workarea().code
            db.session.add(location)
        inv.area_code = location.area_code
        inv.workarea_code = location.workarea_code
        # split_inv_type
        inv.refin_order_code = line.order_code

        db.session.add(inv)
        db.session.flush() # flush for id
        return inv

    # 通过入库订单行 与 库位 获取库存
    def get_inv_by_stockin_line(self, line, location_code, lpn='', get_or_create=False, withlock=False):
        # 获取可以入库的库存行时，必须按照库位，批次，款色码，容器号完全过滤
        subq = self.get_inv_query_by_stockin_line(line, is_split=True)
        subq = subq.filter_by(location_code=location_code, lpn=lpn)
        if withlock:
            subq = subq.with_for_update()
        inv = subq.first()
        # print subq.real_sql(), inv

        if get_or_create and inv is None:
            inv = self.create_inv_by_stockin_line(line, location_code, lpn)
        return inv

    # 通过同一批次的特殊库位库存,查询非特殊库位库存 
    def get_inv_by_same_batch(self, inv, location_code=None, lpn='', get_or_create=False, withlock=False):
        subq = Inv.query.filter(Inv.location_code!='PICK') \
                .filter_by(company_code=inv.company_code, owner_code=inv.owner_code, warehouse_code=inv.warehouse_code) \
                .filter_by(sku=inv.sku)

        # 批次属性过滤
        subq = subq.filter_by(
            #stockin_date=inv.stockin_date,
            quality_type=inv.quality_type,
            product_date=inv.product_date,
            expire_date=inv.expire_date,
            batch_code=inv.batch_code,
            virtual_warehouse=inv.virtual_warehouse,
            spec=inv.spec,
        )
        if g.owner.is_enable_supplier_batch:
            subq = subq.filter_by(supplier_code=inv.supplier_code)
        # 款色码过滤
        subq = subq.filter_by(
            style=inv.style,
            color=inv.color,
            size=inv.size
        )
        # filter location & lpn
        if location_code:
            subq = subq.filter_by(location_code=location_code)
        if lpn:
            subq = subq.filter_by(lpn=lpn)

        if withlock:
            subq = subq.with_for_update()
        inv2 = subq.first()
        if inv2 is None and get_or_create and location_code:
            inv2 = update_model_with_fields(Inv, inv, common_poplist+['location_code', 'lpn', 'qty', 'qty_able', 'qty_alloc'], \
                    location_code=location_code, lpn=lpn)
            db.session.add(inv2)

        db.session.flush()
        return inv2

    def get_inv_qty(self, sku, location_code='', supplier_code='', spec='', company_code='', obj=False):
        subq = Inv.query.with_entities(
                func.sum(Inv.qty).label('qty'),
                func.sum(Inv.qty_able).label('qty_able'),
                func.sum(Inv.qty_alloc).label('qty_alloc'),
            ).filter(Inv.sku==sku, Inv.location_code!='PICK')
        if company_code:
            subq = subq.filter_by(company_code=company_code)
        else:
            subq = subq.t_query
        if location_code:
            subq = subq.filter_by(location_code=location_code)
        if supplier_code:
            subq = subq.filter_by(supplier_code=supplier_code)
        if spec:
            subq = subq.filter_by(spec=spec)
        o = subq.first()
        if obj:
            return o
        return int(o.qty_able or 0) if o else 0

    def mget_inv_qty(self, sku_list, location_code='', supplier_code='', spec='', company_code='', obj=False):
        subq = Inv.query.with_entities(
                Inv.sku.label('sku'),
                func.sum(Inv.qty).label('qty'),
                func.sum(Inv.qty_able).label('qty_able'),
                func.sum(Inv.qty_alloc).label('qty_alloc'),
            ).filter(Inv.sku.in_(sku_list), Inv.location_code!='PICK')
        if company_code:
            subq = subq.filter_by(company_code=company_code)
        else:
            subq = subq.t_query
        if location_code:
            subq = subq.filter_by(location_code=location_code)
        if supplier_code:
            subq = subq.filter_by(supplier_code=supplier_code)
        if spec:
            subq = subq.filter_by(spec=spec)
        ret = subq.group_by(Inv.sku).all()
        if obj:
            return ret
        return {o.sku:int(o.qty_able or 0) for o in ret}

    # --------------------------------

    # 通过入库单行流水, 库位增加库存
    def add_by_stockin_tran(self, intran, location_code, lpn='', withlock=False, inline=None):
        inline = inline or intran.stockin_line
        inv = self.get_inv_by_stockin_line(inline, location_code, lpn='', get_or_create=True, withlock=withlock)
        # 增加库存
        before_qty = inv.qty
        inv.qty += intran.qty_real
        inv.qty_able += intran.qty_real
        # inv.price = inline.price # 已经通过intran 传递给inv了
        after_qty = inv.qty
        # 库存流水
        tran = InvAction.create_tran(inv, before_qty, after_qty, intran.qty_real, intran=intran)
        return inv

    def putin_rfid(self, inv_id, rfid_list, inv=None, stockin=None, w_user_code=None, w_user_name=None, rfid_details=None):
        if inv is None:
            inv = Inv.query.get(inv_id)

        rfid_details = rfid_details or {}

        for rfid in rfid_list:
            invrfid = InvRfid.query.t_query.filter(InvRfid.rfid==rfid).first()
            if invrfid is None:
                invrfid = update_model_with_fields(InvRfid, inv, common_poplist, qty=1, rfid=rfid, inv_id=inv_id,
                        stockin_order_code=stockin.order_code,
                        in_user_code=g.user.code, in_user_name=g.user.name,
                        in_w_user_code=w_user_code, in_w_user_name=w_user_name)
                db.session.add(invrfid)
            else:
                invrfid.qty = 1
                invrfid.inv_id = inv_id
                invrfid.stockin_order_code=stockin.order_code
                invrfid.in_user_code=g.user.code
                invrfid.in_user_name=g.user.name
                invrfid.in_w_user_code=w_user_code
                invrfid.in_w_user_name=w_user_name
            
            detail = DictNone(rfid_details.get(rfid, {}))
            if detail:
                invrfid._qty_inner = detail.qty_inner or 1
                invrfid._weight = detail.weight or 0
                invrfid._gross_weight = detail.gross_weight or 0
                invrfid.batch_code = detail.batch_code or invrfid.batch_code or ''
                invrfid.color = detail.color or invrfid.color or ''
                invrfid.spec = detail.spec or invrfid.spec or ''
                invrfid.level = detail.level or invrfid.level or ''
                invrfid.twisted = detail.twisted or invrfid.twisted or ''


            # create invrfid trans
            tran = update_model_with_fields(InvRfidTrans, invrfid, common_poplist, 
                    user_code=g.user.code, user_name=g.user.name, w_user_code=w_user_code, w_user_name=w_user_name,
                    xtype='in', order_type=stockin.xtype, order_code=stockin.order_code)
            db.session.add(tran)


    # --------------------------------

    # 入库/出库流水
    @staticmethod
    def create_tran(inv, before_qty, after_qty, change_qty, intran=None, outtran=None, xtype='stockin', xtype_opt='in'):
        tran = update_model_with_fields(InvTrans, inv, common_poplist, 
            before_qty=before_qty, after_qty=after_qty, change_qty=change_qty, qty_able=(change_qty if change_qty > 0 else 0),
            inventory_id=inv.id, user_code=g.user.code, user_name=g.user.name)
        # 补充关联信息
        if intran:
            tran.order_code = intran.stockin.order_code
            tran.erp_order_code = intran.stockin.erp_order_code
            tran.price = intran.price
        elif outtran:
            tran.order_code = outtran.stockout.order_code
            tran.erp_order_code = outtran.stockout.erp_order_code
            tran.price = outtran.price
        else:
            tran.price = inv.good.cost_price or inv.good.price

        tran.xtype = xtype
        tran.xtype_opt = xtype_opt

        db.session.add(tran)
        return tran

    # --------------------------------

    # 通过出库单行， 获取库存行 query 对象
    def get_inv_query_by_stockout_line(self, line):
        subq = Inv.query.filter(Inv.location_code!='PICK').filter(
                Inv.owner_code==line.owner_code, 
                Inv.warehouse_code==line.warehouse_code, 
                Inv.company_code==line.company_code
            )
        # sku
        subq = subq.filter(Inv.sku==line.sku)
        # 供应商
        # if line.supplier_code:
        #     subq = subq.filter_by(supplier_code=line.supplier_code)
        if g.owner.is_enable_supplier_batch and line.supplier_code:
            subq = subq.filter(Inv.supplier_code==line.supplier_code)
        # 规格
        if line.spec:
            subq = subq.filter(Inv.spec==line.spec)
        # 款色码过滤
        subq = subq.filter(
                Inv.style==line.style,
                Inv.color==line.color,
                Inv.size==line.size
            )
        return subq

    # 自动出库、指定库位出库，通过出库订单行获取库存; 推荐出库库存
    def get_inv_by_stockout_line(self, line, recommend=False, withlock=False, order=None):
        subq = self.get_inv_query_by_stockout_line(line)
        subq = subq.filter(Inv.qty_able > 0)

        # 出库单类型对应库位工作区
        stockout_type_location = g.owner.stockout_type_location
        if order:
            location_workarea = stockout_type_location.get(order.order_type, None)
            if location_workarea:
                subq = subq.filter(
                    Inv.location_code==Location.code, 
                    Location.workarea_code==location_workarea,
                    Location.company_code==Inv.company_code, 
                    Location.warehouse_code==Inv.warehouse_code)

        # g.owner.alloc_location 库位过滤; 自动分配时才有效; 
        # 如果是手动指定库位推荐的话, 还是可以分配任意库位的库存; 
        if not recommend:
            alloc_location = g.owner.alloc_location
            if alloc_location == 'STAGE':
                subq = subq.filter(Inv.location_code=='STAGE')
            elif alloc_location == 'NO_STAGE':
                subq = subq.filter(Inv.location_code!='STAGE')
            elif alloc_location == 'NO_QC':
                subq = subq.filter(Inv.location_code!='QC')
            elif alloc_location == 'NO_QC_STAGE':
                subq = subq.filter(Inv.location_code!='QC', Inv.location_code!='STAGE')
            else:
                pass

        # 分配规则
        for rule in g.owner.alloc_rules:
            ## 先进先出 入库时间(stockin_date)
            if rule == 'FIFO':
                subq = subq.order_by(Inv.stockin_date.asc())
            ## 后进先出 入库时间(stockin_date)
            elif rule == 'FILO': 
                subq = subq.order_by(Inv.stockin_date.desc()) 
            ## 生产时间(product_date)
            elif rule == 'FPFO': # 先生产的后出
                subq = subq.order_by(Inv.product_date.asc())
            elif rule == 'FPLO': # 先生产的后出
                subq = subq.order_by(Inv.product_date.desc())
            ## 过期时间(expire_date)
            elif rule == 'FEFO': # 快过期的先出
                subq = subq.order_by(Inv.expire_date.asc())
            elif rule == 'FELO': # 快过期的后出
                subq = subq.order_by(Inv.expire_date.desc())
            ## 清库位库存优先 ，库位库存少的先出
            elif rule == 'clear_location':
                subq = subq.order_by(Inv.qty_able.asc())
            ## 保质期与过期时间, (Inv.expire_date - Inv.product_date).asc
            elif rule == 'FBFO': # 保质期短的先出
                subq = subq.order_by((Inv.expire_date - Inv.product_date).asc())
            elif rule == 'FBLO': # 保质期长的先出
                subq = subq.order_by((Inv.expire_date - Inv.product_date).desc())
            ## 库位优先级高先出
            elif rule == 'priority_location':
                subq = subq.filter(Inv.location_code==Location.code, Location.company_code==Inv.company_code, Location.warehouse_code==Inv.warehouse_code)
                subq = subq.order_by(Location.priority.desc())
            ## 库位完整远近优先
            elif rule == 'index_location_asc': # 库位近的优先, 库位序小的先出
                subq = subq.filter(Inv.location_code==Location.code, Location.company_code==Inv.company_code, Location.warehouse_code==Inv.warehouse_code)
                subq = subq.order_by(Location.index.asc())
            elif rule == 'index_location_desc': # 库位远的优先，库位序大的先出
                subq = subq.filter(Inv.location_code==Location.code, Location.company_code==Inv.company_code, Location.warehouse_code==Inv.warehouse_code)
                subq = subq.order_by(Location.index.desc())
            else:
                pass

        # 默认先进先出
        if not g.owner.alloc_rules:
            subq = subq.order_by(Inv.stockin_date.asc())

        if withlock:
            subq = subq.with_for_update()

        invs = subq.all()
        qty_total = sum([inv.qty_able for inv in invs])

        choice = []
        qty_select = 0
        for inv in invs:
            qty_select += inv.qty_able
            # 自动分配，分配够数量即可
            if qty_select >= line.qty and not recommend:
                choice.append(inv)
                break
            # 指定库位出库，如果库存够了，只推荐10条库存
            elif recommend and len(choice) >= 9 and qty_select >= line.qty:
                choice.append(inv)
                break
            choice.append(inv)

        # 返回总数是否满足，库存行
        # return qty_total >= line.qty, choice 
        return qty_total >= (line.qty - line.qty_alloc), choice

    # --------------------------------

    # 通过出库单行，减少库存
    def reduce_by_stockout_line(self, outline):
        pass

    # ------------- get default ------

    @staticmethod
    def default_category(code='default'):
        subq = Category.query.o_query
        if code:
            subq = subq.filter_by(code=code)
        return subq.first()

    @staticmethod
    def default_area(code='default'):
        subq = Area.query.w_query
        if code:
            subq = subq.filter_by(code=code)
        return subq.first()

    @staticmethod
    def default_workarea(code='default'):
        subq = Workarea.query.w_query
        if code:
            subq = subq.filter_by(code=code)
        return subq.first()

    @staticmethod
    def create_good(data, g=None):
        exist = True
        # replace
        subq = Good.query.filter_by(code=data['code'])
        if g:
            subq.o_query
        good = subq.first()
        # new
        if good is None:
            good = Good(**json2mdict_pop(Good, clear_empty(data)))
            good.name_en = ubarcode(good.name).replace(' ', '')
            exist = False
        if g:
            good.owner_code = g.owner_code
            good.company_code = g.company_code
        return exist, good

    @staticmethod
    def create_category(code, name=None):
        if not name:
            name = code
        cate = Category.query.o_query.filter_by(code=code).first()
        if cate is None:
            cate = Category(code=code, name=name, owner_code=g.owner_code, company_code=g.company_code)
            db.session.add(cate)
        return cate


    # ------ 调整单: 只能调整无lpn的库存行数量，可以自己生成调整单（导入）或者上游erp下发调整单; 调整的是可用数量-------
    @staticmethod
    def adjust(inv, qty_diff): 
        # 负数为盘亏, 正数为盘盈; 调整后, 总数必须大于等于0
        before_qty = inv.qty
        if inv.qty_able + qty_diff >= 0:
            inv.qty_able += qty_diff
            inv.qty = inv.qty_able + inv.qty_alloc

            # create inv-trans
            InvAction.create_tran(inv, before_qty, inv.qty, qty_diff, intran=None, outtran=None, xtype='inv_adjust', xtype_opt='in')
            return True
        else:
            return False

    @staticmethod
    def adjust_invs(invs, qty_diff): 
        qty_able = sum([inv.qty_able for inv in invs])
        _qty_diff = qty_diff
        done = False

        if qty_able + qty_diff >= 0:
            for inv in invs:
                if inv.qty_able + _qty_diff >= 0:
                    InvAction.adjust(inv, _qty_diff)
                    break
                else:
                    _qty_diff = _qty_diff+inv.qty_able
                    InvAction.adjust(inv, -inv.qty_able)
            return True

        return False


    # ------ 移库单: 从一个库位移动到另一个库位，支持不同仓库之间的移库，但不能不同货主直接移动，指定数量移动（可用数量）
    # ------ 新移库单, 移出到PICK, lpn=MOVE_id 再移入目标库位, 要设置 is_move
    @staticmethod
    def move(inv, qty, dest_w, dest_lc, dest_lpn='', is_move=False, move_type='out'):
        before_qty = inv.qty
        if inv.qty_able >= qty:
            inv2 = None
            if not is_move:
                #query inv2
                query = Inv.query.filter(Inv.location_code!='PICK') \
                    .filter_by(company_code=g.company_code, warehouse_code=dest_w, owner_code=inv.owner_code) \
                    .filter_by(location_code=dest_lc, sku=inv.sku) \
                    .filter_by(
                            #stockin_date=inv.stockin_date, 
                            #supplier_code=inv.supplier_code,
                            quality_type=inv.quality_type, product_date=inv.product_date,
                            expire_date=inv.expire_date, batch_code=inv.batch_code, virtual_warehouse=inv.virtual_warehouse, 
                            spec=inv.spec,
                        ) \
                    .filter_by(style=inv.style, color=inv.color, size=inv.size, lpn=dest_lpn)
                if g.owner.is_enable_supplier_batch:
                    query = query.filter_by(supplier_code=inv.supplier_code)
                inv2 = query.with_for_update().first()

            # create inv2
            if inv2 is None:
                inv2 = copy_and_update_model(Inv, inv, ['qty_alloc', 'qty', 'qty_able']+common_poplist, 
                        warehouse_code=dest_w, location_code=dest_lc, lpn=dest_lpn,
                        qty=qty, qty_able=qty, qty_alloc=0,
                    )
                db.session.add(inv2)
                db.session.flush()
            else:
                # update inv2
                inv2.qty += qty
                inv2.qty_able += qty

            # update inv
            inv.qty -= qty
            inv.qty_able -= qty

            # create inv-trans
            InvAction.create_tran(inv, before_qty, inv.qty, qty, intran=None, outtran=None, xtype='inv_move', xtype_opt=move_type)
        else:
            return False

        return True

    @staticmethod
    def move_invs(invs, qty, dest_w, dest_lc, dest_lpn='', is_move=False, move_type='out'):
        qty_able = sum([inv.qty_able for inv in invs])
        _qty = qty

        if qty_able >= qty:
            for inv in invs:
                if inv.qty_able >= _qty:
                    InvAction.move(inv, _qty, dest_w, dest_lc, dest_lpn, is_move, move_type)
                    break
                else:
                    _qty = _qty - inv.qty_able
                    InvAction.move(inv, inv.qty_able, dest_w, dest_lc, dest_lpn, is_move, move_type)
            return True
        return False

    # 移库，移动的是锁定的库存, 用于分配之后拣货到临时发运区特殊库位PICK
    @staticmethod
    def move_qty_alloc(inv_id, qty, dest_w, dest_lc, dest_lpn='', refid=0):
        inv = Inv.query.o_query.filter(Inv.location_code!='PICK').filter_by(id=inv_id) \
                .with_for_update().first()
        if inv is None:
            return False
        if inv.qty_alloc >= qty:
            #query inv2
            query = Inv.query.filter(Inv.location_code!='PICK') \
                .filter_by(company_code=g.company_code, warehouse_code=dest_w, owner_code=inv.owner_code) \
                .filter_by(location_code=dest_lc, sku=inv.sku) \
                .filter_by(
                        #stockin_date=inv.stockin_date, 
                        #supplier_code=inv.supplier_code,
                        quality_type=inv.quality_type, product_date=inv.product_date,
                        expire_date=inv.expire_date, batch_code=inv.batch_code, virtual_warehouse=inv.virtual_warehouse, 
                        spec=inv.spec,
                    ) \
                .filter_by(style=inv.style, color=inv.color, size=inv.size, lpn=dest_lpn, refid=refid)
            if g.owner.is_enable_supplier_batch:
                query = query.filter_by(supplier_code=inv.supplier_code)
            inv2 = query.with_for_update().first()
            # create inv2
            if inv2 is None:
                inv2 = copy_and_update_model(Inv, inv, ['qty_alloc', 'qty', 'qty_able']+common_poplist, 
                        warehouse_code=dest_w, location_code=dest_lc, lpn=dest_lpn,
                        qty=qty, qty_able=qty, qty_alloc=0, refid=refid,
                    )
                db.session.add(inv2)
                db.session.flush()
            else:
                # update inv2
                inv2.qty += qty
                inv2.qty_able += qty

            # update inv
            before_qty = inv.qty
            inv.qty -= qty
            inv.qty_alloc -= qty

            # create inv-trans
            InvAction.create_tran(inv, before_qty, inv.qty, qty, intran=None, outtran=None, xtype='stockout', xtype_opt='out')
        else:
            return False

        return True


    # qty 总数不扣除
    # 冻结批次的id, 按库位与SKU冻结, 按库位与SKU冻结数量, 按SKU冻结数量; 随机冻结
    def freeze_inv(self, sku=None, spec=None, location_code=None, area_code=None, qty=None, inv_list=None):
        # 按id冻结
        if inv_list:
            for inv in Inv.query.t_query.filter(Inv.id.in_(inv_list)).with_for_update().all():
                inv.qty_freeze = inv.qty_freeze + inv.qty_able
                inv.qty_able = 0
        # 其它冻结
        else:
            query = Inv.query.t_query.filter(Inv.sku==sku)
            if spec:
                query = query.filter(Inv.spec==spec)
            if location_code:
                query = query.filter(Inv.location_code==location_code)
            if area_code:
                query = query.filter(Inv.area_code==area_code)

            # 一次只取10条进行冻结
            if qty:
                qty_need = qty
                while qty_need > 0:
                    invs = query.filter(Inv.qty_able > 0).limit(10).all()
                    if len(invs) == 0:
                        break
                    for inv in invs:
                        # 数量已经满足
                        if inv.qty_able >= qty_need:
                            inv.qty_freeze = inv.qty_freeze + qty_need
                            inv.qty_able = inv.qty_able - qty_need
                            qty_need = 0
                            break
                        # 数量未满足
                        else:
                            inv.qty_freeze = inv.qty_freeze + inv.qty_able
                            qty_need = qty_need - inv.qty_able
                            inv.qty_able = 0

                    # 更新到库存, 取下一批新的10条
                    db.session.flush()

                if qty_need > 0:
                    return False, u'库存可用数量没有这么多, 请减少库存冻结数量'

            # 冻结所有
            else:
                for inv in query.with_for_update().all():
                    inv.qty_freeze = inv.qty_able
                    inv.qty_able = 0

        return True, 'ok'

    # 解冻
    def unfreeze_inv(self, sku=None, spec=None, location_code=None, area_code=None, qty=None, inv_list=None):
        # 按id解冻
        if inv_list:
            for inv in Inv.query.t_query.filter(Inv.id.in_(inv_list)).with_for_update().all():
                inv.qty_able = inv.qty_able + inv.qty_freeze
                inv.qty_freeze = 0
        # 其它解冻
        else:
            query = Inv.query.t_query.filter(Inv.sku==sku)
            if spec:
                query = query.filter(Inv.spec==spec)
            if location_code:
                query = query.filter(Inv.location_code==location_code)
            if area_code:
                query = query.filter(Inv.area_code==area_code)

            # 一次只取10条进行解冻
            if qty:
                qty_need = qty
                while qty_need > 0:
                    invs = query.filter(Inv.qty_freeze > 0).limit(10).all()
                    if len(invs) == 0:
                        break
                    for inv in invs:
                        # 数量已经满足
                        if inv.qty_freeze >= qty_need:
                            inv.qty_able = inv.qty_able + qty_need
                            inv.qty_freeze = inv.qty_freeze - qty_need
                            qty_need = 0
                            break
                        # 数量未满足
                        else:
                            inv.qty_able = inv.qty_able + inv.qty_freeze
                            inv.qty_freeze = 0
                            qty_need = qty_need - inv.qty_freeze

                    # 更新到库存, 取下一批新的10条
                    db.session.flush()

                if qty_need > 0:
                    return False, u'库存冻结数量没有这么多, 请减少解冻数量'

            # 解冻所有
            else:
                for inv in query.with_for_update().all():
                    inv.qty_able = inv.qty_able + inv.qty_freeze
                    inv.qty_freeze = 0

        return True, 'ok'


# 调整
class InvAdjustAction(object):

    def __int__(self, order=None):
        self.order = order

    def create(self, data):
        pass

    def adjust(self, orders):
        for o in orders:
            query = Inv.query.filter(Inv.location_code!='PICK') \
                .filter_by(company_code=g.company_code, warehouse_code=o.warehouse_code, owner_code=o.owner_code) \
                .filter_by(location_code=o.location_code, sku=o.sku) \
                .filter_by(
                        # stockin_date=o.stockin_date, 
                        #supplier_code=o.supplier_code,
                        quality_type=o.quality_type, product_date=o.product_date,
                        expire_date=o.expire_date, batch_code=o.batch_code, virtual_warehouse=o.virtual_warehouse, 
                        spec=o.spec,
                    ) \
                .filter_by(style=o.style, color=o.color, size=o.size, lpn=o.lpn)
            if g.owner.is_enable_supplier_batch:
                query = query.filter_by(supplier_code=o.supplier_code)
            # inv = query.with_for_update().first()
            # if inv:
            #     ok = InvAction.adjust(inv, o.qty_diff)
            #     if not ok:
            #         return False, u"%s 在库位%s 同批次库存不足"%(inv.sku, inv.location_code)
            invs = query.with_for_update().all()
            if invs:
                ok = InvAction.adjust_invs(invs, o.qty_diff)
                if not ok:
                    return False, u"%s 在库位%s 同批次库存不足"%(o.sku, o.location_code)
            else:
                # 创建一个空库存
                good = Good.query.filter_by(company_code=o.company_code, owner_code=o.owner_code, code=o.sku).first()
                location = Location.query.filter_by(company_code=o.company_code, warehouse_code=o.warehouse_code, code=o.location_code).first()
                inv0 = update_model_with_fields(Inv, o, common_poplist, qty=0, qty_able=0, qty_alloc=0)
                inv0.category_code = good.category_code
                inv0.area_code = location.area_code
                inv0.workarea_code = location.workarea_code
                db.session.add(inv0)
                db.session.flush()
                ok = InvAction.adjust(inv0, o.qty_diff)
                if not ok:
                    return False, u"%s 在库位%s 同批次库存不足"%(inv0.sku, inv0.location_code)
                # return False, u"找不到%s在库位%s的同批次库存"%(o.sku, o.location_code)
            # # if allow part success
            # o.state = 'done' if ok else 'fail'
            o.state = 'done'
            o.user_code = g.user.code
            o.user_name = g.user.name
        return True, None

    def cancel(self, order_id):
        o = InvAdjust.query.c_query.filter_by(id=order_id).with_for_update().first()
        o.state = 'cancel'
        return o

    @staticmethod
    def gen_series_code(company_code, warehouse_code, owner_code):
        return Seq.make_order_code(prefix='IA', company_code=company_code, warehouse_code=warehouse_code, owner_code=owner_code)


# 移库
class InvMoveAction(object):

    def __int__(self, order=None):
        self.order = order

    def create(self, data, series_code=None):
        subq = Inv.query.t_query.filter_by(sku=data['sku'], location_code=data['location_code'])
        if data.get('supplier_code',''):
            subq = subq.filter_by(supplier_code=data['supplier_code'])
        if data.get('spec', ''):
            subq = subq.filter_by(spec=data['spec'])
        if data.get('lpn', ''):
            subq = subq.filter_by(lpn=data['lpn'])
        if data.get('inv_id', None):
            subq = subq.filter_by(id=data['inv_id'])

        series_code = InvMoveAction.gen_series_code(g.company_code, g.warehouse_code, g.owner_code) if not series_code else series_code
        dest_warehouse_code = data.get('dest_warehouse_code', g.warehouse_code)
        
        inv = subq.first()
        c = update_model_with_fields(InvMove, inv, common_poplist, user_code=g.user.code, user_name=g.user.name, remark='',
                series_code=series_code, dest_warehouse_code=dest_warehouse_code, **json2mdict_pop(InvMove, clear_empty(data)))
        db.session.add(c)
        return True, series_code

    def move(self, orders, part=False):
        for o in orders:
            _qty = o.qty
            if part:
                _qty = o.qty_real2
            query = Inv.query.filter(Inv.location_code!='PICK') \
                    .filter_by(company_code=g.company_code, warehouse_code=o.warehouse_code, owner_code=o.owner_code) \
                    .filter_by(location_code=o.location_code, sku=o.sku) \
                    .filter_by(
                            # stockin_date=o.stockin_date, 
                            # supplier_code=o.supplier_code,
                            quality_type=o.quality_type, product_date=o.product_date,
                            expire_date=o.expire_date, batch_code=o.batch_code, virtual_warehouse=o.virtual_warehouse, 
                            spec=o.spec,
                        ) \
                    .filter_by(style=o.style, color=o.color, size=o.size, lpn=o.lpn) \
                    .filter(Inv.qty_able > 0)
            if g.owner.is_enable_supplier_batch:
                query = query.filter_by(supplier_code=o.supplier_code)
            # inv =  query.with_for_update().first()
            # if inv:
            #     ok = InvAction.move(inv, _qty, dest_w=o.dest_warehouse_code, dest_lc=o.dest_location_code, dest_lpn=o.dest_lpn)
            #     if not ok:
            #         return False, u"%s 在库位%s 同批次库存不足"%(inv.sku, inv.location_code)
            invs =  query.with_for_update().all()
            if invs:
                ok = InvAction.move_invs(invs, _qty, dest_w=o.dest_warehouse_code, dest_lc=o.dest_location_code, dest_lpn=o.dest_lpn)
                if not ok:
                    return False, u"%s 在库位%s 同批次库存不足"%(o.sku, o.location_code)
            else:
                return False, u"找不到%s在库位%s的同批次库存"%(o.sku, o.location_code)

            o.state = 'done' if not part else 'doing'
            if o.qty == o.qty_real:
                o.state = 'done'
            o.qty_real = _qty
            o.user_code = g.user.code
            o.user_name = g.user.name
        return True, None

    def cancel(self, series_code):
        orders = InvMove.query.c_query.filter_by(series_code=series_code).with_for_update().all()
        for o in orders:
            if o.state == 'create':
                o.state = 'cancel'
            elif o.state == 'doing':
                query = Inv.query.filter(Inv.location_code=='PICK', Inv.lpn=='MOVE_%s'%o.id)
                invs=  query.with_for_update().all()
                for inv in invs:
                    InvAction.move(inv, inv.qty_able, dest_w=o.warehouse_code, dest_lc=o.location_code, dest_lpn=o.lpn, is_move=False, move_type='in')

                o.state = 'cancel'
                o.qty_real = 0

        return True, None

    # 已经移出原库位的, 全部移入目标库位
    def done(self, series_code):
        orders = InvMove.query.c_query.filter_by(series_code=series_code).with_for_update().all()
        for o in orders:
            if o.state == 'create':
                o.state = 'done'
            elif o.state == 'doing':
                query = Inv.query.filter(Inv.location_code=='PICK', Inv.lpn=='MOVE_%s'%o.id)
                invs =  query.with_for_update().first()
                for inv in invs:
                    InvAction.move(inv, inv.qty_able, dest_w=o.dest_warehouse_code, dest_lc=o.dest_location_code, dest_lpn=o.dest_lpn, is_move=False, move_type='in')
                o.qty_real = o.qty
                o.state = 'done'

        return True, None

    def move_out(self, orders, part=False):
        for o in orders:
            _qty = o.qty
            if part:
                _qty = o.qty_real
            query = Inv.query.filter(Inv.location_code!='PICK') \
                    .filter_by(company_code=g.company_code, warehouse_code=o.warehouse_code, owner_code=o.owner_code) \
                    .filter_by(location_code=o.location_code, sku=o.sku) \
                    .filter_by(
                            # stockin_date=o.stockin_date, 
                            # supplier_code=o.supplier_code,
                            quality_type=o.quality_type, product_date=o.product_date,
                            expire_date=o.expire_date, batch_code=o.batch_code, virtual_warehouse=o.virtual_warehouse, 
                            spec=o.spec,
                        ) \
                    .filter_by(style=o.style, color=o.color, size=o.size, lpn=o.lpn) \
                    .filter(Inv.qty_able > 0)
            if g.owner.is_enable_supplier_batch:
                query = query.filter_by(supplier_code=o.supplier_code)
            # inv =  query.with_for_update().first()
            # if inv:
            #     ok = InvAction.move(inv, _qty, dest_w=o.dest_warehouse_code, dest_lc='PICK', dest_lpn='MOVE_%s'%o.id, is_move=True, move_type='out')
            #     if not ok:
            #         return False, u"%s 在库位%s 同批次库存不足"%(inv.sku, inv.location_code)
            invs =  query.with_for_update().all()
            if invs:
                ok = InvAction.move_invs(invs, _qty, dest_w=o.dest_warehouse_code, dest_lc='PICK', dest_lpn='MOVE_%s'%o.id, is_move=True, move_type='out')
                if not ok:
                    return False, u"%s 在库位%s 同批次库存不足"%(o.sku, o.location_code)
            else:
                return False, u"找不到%s在库位%s的同批次库存"%(o.sku, o.location_code)

            o.state = 'doing'
            o.user_code = g.user.code
            o.user_name = g.user.name
        return True, None

    def move_in(self, orders):
        for o in orders:
            query = Inv.query.filter(Inv.location_code=='PICK', Inv.lpn=='MOVE_%s'%o.id)
            invs =  query.with_for_update().all()
            for inv in invs:
                InvAction.move(inv, inv.qty_able, dest_w=o.dest_warehouse_code, dest_lc=o.dest_location_code, dest_lpn=o.dest_lpn, is_move=False, move_type='in')
            o.qty_real = o.qty
            o.state = 'done'
        return True, None


    @staticmethod
    def gen_series_code(company_code, warehouse_code, owner_code):
        return Seq.make_order_code(prefix='IM', company_code=company_code, warehouse_code=warehouse_code, owner_code=owner_code)


# 盘点
class InvCountAction(object):

    def __int__(self, order=None):
        self.order = order

    def create(self, data, fill=False, series_code=None):
        # {location_code, sku}
        data.pop('code', None)
        location_code = data.get('location_code', '')
        sku = data.get('sku', '')
        area = data.get('area', '')

        subq = Inv.query.t_query.filter(Inv.location_code!='PICK').filter(Inv.qty>0)
        good = None
        if location_code:
            subq = subq.filter(Inv.location_code==location_code)
        if sku:
            subq = subq.filter(Inv.sku==sku)
            good = Good.query.o_query.filter_by(code=sku).first()
        if area and area!='ALL':
            subq = subq.filter(Inv.area_code==area)

        if sku and not good:
            return False, u'找不到货品'

        series_code = InvCountAction.gen_series_code(g.company_code, g.warehouse_code, g.owner_code) if not series_code else series_code
        if not fill:
            # group_by 用于库存分裂的情况, 同一个sku, 只会产生一条盘点数据
            invaction = InvAction()
            for inv in subq.group_by(Inv.location_code, Inv.sku).all():
                o = invaction.get_inv_qty(inv.sku, inv.location_code, obj=True)
                c = update_model_with_fields(InvCount, inv, common_poplist, series_code=series_code, qty=o.qty, qty_real=o.qty, qty_alloc=o.qty_alloc)
                db.session.add(c)

            if subq.count() == 0:
                if sku and not good:
                    return False, u'找不到货品'
                elif good:
                    c = update_model_with_fields(InvCount, good, common_poplist, 
                        series_code=series_code, code='', warehouse_code=g.warehouse_code, sku=good.code, state='create', source='erp',
                        qty_real=0, qty=0, location_code=location_code or 'STAGE')
                    db.session.add(c)
                elif not sku:
                    for good in Good.query.o_query.all():
                        for loc in Location.query.w_query.all():
                            c = update_model_with_fields(InvCount, good, common_poplist, 
                            series_code=series_code, code='', warehouse_code=g.warehouse_code, sku=good.code, state='create', source='erp',
                            qty_real=0, qty=0, location_code=loc.code or 'STAGE')
                            db.session.add(c)
                else:
                    return False, u'找不到货品'
        elif good:
            c = update_model_with_fields(InvCount, good, common_poplist, user_code=g.user.code, user_name=g.user.name, remark='PDA', state='create', source='erp',
                    series_code=series_code, code='', warehouse_code=g.warehouse_code, **json2mdict_pop(InvCount, clear_empty(data)))
            db.session.add(c)

        if not fill:
            db.session.flush()

        return True, series_code

    def create_lines(self, lines):
        series_code = InvCountAction.gen_series_code(g.company_code, g.warehouse_code, g.owner_code)
        invaction = InvAction()
        for data in lines:
            # {location_code, sku}
            location_code = data.get('location_code', '')
            sku = data.get('sku', '')
            qty_real = data.get('qty_real', 0)

            good = Good.query.o_query.filter_by(code=sku).first()
            inv = invaction.get_inv_qty(sku, location_code, obj=True)

            c = update_model_with_fields(InvCount, good, common_poplist, 
                    series_code=series_code, code='', warehouse_code=g.warehouse_code, sku=good.code, state='create', source='erp',
                    qty_real=qty_real, qty=inv.qty, qty_alloc=inv.qty_alloc, location_code=location_code or 'STAGE')
            db.session.add(c)

        db.session.flush()
        return True, series_code

    def count(self):
        pass

    # 从盘点单生成调整单
    def gen_adjust(self, orders):
        series_code = InvAdjustAction.gen_series_code(g.company_code, g.warehouse_code, g.owner_code)
        adjust_list = []
        for order in orders:
            adjust = update_model_with_fields(InvAdjust, order, common_poplist)
            adjust.qty_before = order.qty
            adjust.qty_after = order.qty_real
            adjust.qty_diff = order.qty_real - order.qty
            adjust.count_code = order.code
            adjust.count_series_code = order.series_code
            adjust.state = 'create'
            adjust.code = str(uuid4())
            adjust.series_code = series_code

            adjust_list.append(adjust)
            db.session.add(adjust)

            order.state = 'done'
            order.adjust_series_code = series_code
            order.user_code = g.user.code
            order.user_name = g.user.name

        db.session.flush()
        return series_code, adjust_list


    def cancel(self, series_code):
        orders = InvCount.query.c_query.filter_by(series_code=series_code).with_for_update().all()
        for o in orders:
            if o.state == 'create':
                o.state = 'cancel'

        return True, None

    @staticmethod
    def gen_series_code(company_code, warehouse_code, owner_code):
        return Seq.make_order_code(prefix='IC', company_code=company_code, warehouse_code=warehouse_code, owner_code=owner_code)
        #return 'IC%s-%04d'%(datetime.now().strftime('%y%m%d%H'), randint(1, 9999))
    




