#coding=utf8

from sqlalchemy import func, or_, and_
from flask import g
from datetime import datetime
from random import randint
from itertools import groupby
from utils.base import fan_stock_type
from utils.functions import update_model_with_fields, m2dict, copy_and_update_model, common_poplist, json2mdict_pop, DictNone, clear_empty

from models.stockin import Stockin, StockinLine, StockinLineTrans
from blueprints.inv.action import InvAction
from models.auth import Seq, Partner
from models.inv import  Good, Inv
from models.warehouse import Location

from extensions.database import db

class StockinAction(object):

    def __init__(self, stockin=None):
        self.stockin = stockin

    # 快速入库，直接增加库存
    def putin(self, line_id, qty, location, lpn='', line=None, w_user_code=None, w_user_name=None, rfid_list=None, is_overcharge=False, rfid_details=None, **kw):
        # 订单行------------------------
        if line is None:
            line = StockinLine.query.filter_by(id=line_id, stockin_id=self.stockin.id).with_for_update().first()
        
        qty_before = line.qty_real
        qty_now = line.qty_real + qty

        # 允许超收
        if is_overcharge:
            line.qty_real = qty_now
        # 不允许超收
        else:
            # 没超收
            if qty_now <= line.qty:
                line.qty_real = qty_now
            # 超收了， 超过的数量直接不要
            else:
                line.qty_real = line.qty

        # 订单行流水--------------------- 超收时expect预期数量其实是0
        # intran = self.create_tran(line, qty, line.qty_real - qty_before, None, w_user_code=w_user_code, w_user_name=w_user_name)
        qty_expect = line.qty - qty_before
        intran = self.create_tran(line, qty_expect, line.qty_real - qty_before, None, w_user_code=w_user_code, w_user_name=w_user_name)
        
        # 库存&库存流水--------------------------
        invaction = InvAction()
        inv = invaction.add_by_stockin_tran(intran, location, lpn, withlock=True, inline=line)
        intran.inv_id = inv.id
        intran.location_code = location
        intran.lpn = lpn

        # rfid 入库
        if rfid_list:
            invaction.putin_rfid(inv.id, rfid_list, inv, stockin=self.stockin, w_user_code=w_user_code, w_user_name=w_user_name, rfid_details=rfid_details)

        # 返回 是否允许超收，总超收数量； 0 or 负数 表示没超收; real receive_qty
        return is_overcharge, qty_now - line.qty, line.qty_real - qty_before

    # 入库流水
    def create_tran(self, line, qty, qty_real, inv_id=None, w_user_code=None, w_user_name=None):
        #tran = update_model_with_fields(StockinLineTrans, line, common_poplist+['qty'], qty=qty, inv_id=inv_id, user_code=g.user.code, user_name=g.user.name)
        poplist = common_poplist + ['qty']
        tran = StockinLineTrans()
        for c in line._columns_name:
            if c in tran._columns_name and c not in poplist:
                setattr(tran, c, getattr(line, c))
        tran.stockin_line = line
        tran.price = line.price
        tran.qty = qty
        tran.qty_real = qty_real
        tran.inv_id = inv_id
        tran.user_code = g.user.code
        tran.user_name = g.user.name
        tran.w_user_code = w_user_code
        tran.w_user_name = w_user_name
        db.session.add(tran)
        return tran



    # 上架，采用移库方式来做，从暂存库位直接移动到存储库位
    def on_shelf(self, line_id, qty):
        pass

    # 复核，支持RF,PC端；同一单子不会存在不同批次的同一货品
    # 扫单号，或者选择订单列表； 扫barcode， qty可以填， 默认为1， 扫库位，默认stage库位，扫lpn，默认不填
    def check(self, barcode, qty, location, lpn='', order=None, **kw):
        line = StockinLine.query.filter_by(barcode=barcode, stockin_id=order.id).with_for_update().first()
        self.putin(line.id, qty, location, lpn, line=line, **kw)

    # 入库库位推荐
    def auto_location(self, line, only_one=False, excludes=None, order=None, pass_location_code=False, move_type=None):
        """
            1. 货品默认库区/库位
            2. 根据上一次入库位置进行分配
            3. 根据库存重量分配
            4. 根据库存数量分配
            5. 一个库位只放一种东西（同货品，没有货品则选择空库位）
            6. 放满后选择临近库位（根据index, 根据area/workarea）
            last. 最后排序, 根据库位码顺序(index, code, priority)
        """
        stockin_type_location = g.owner.stockin_type_location
        location_workarea = None
        if order:
            location_workarea = stockin_type_location.get(order.xtype, None)
        elif move_type:
            location_workarea = stockin_type_location.get(move_type, None)

        query0 = Location.query.with_entities(Location.code.label('code')).filter(
                Location.code!='PICK',
                Location.warehouse_code==g.warehouse_code, 
                Location.company_code==g.company_code)

        # 0. 只推荐stockin_type_location(入库单类型对应库位工作区)配置里设定的库位
        if location_workarea:
            query0 = query0.filter(Location.workarea_code==location_workarea)
        # 1. 行默认库位
        if not pass_location_code and line.location_code and line.location_code!='STAGE':
            return True, line.location_code if only_one else [line.location_code]
        # 1. 货品默认库区/库位
        good = line.good
        if good.location_code:
            return True, good.location_code if only_one else [good.location_code]
        elif good.area_code:
            query0 = query0.filter(Location.area_code==good.area_code)

        rules = [r.str1 for r in g.owner.auto_location_rules]
        locations = []
        locations_seq = {}

        for idx, rule in enumerate(g.owner.auto_location_rules):
            # print('stockin auto_location recommend', locations, idx, rule.str1)
            if idx == 0:
                query = query0
            elif locations:
                query = query0.filter(Location.code.in_(locations))
            else:
                query = query0
            # 2. 根据上一次入库位置进行分配
            if rule.str1 == 'last_time':
                query = query.filter(
                    StockinLineTrans.sku==line.sku,
                    StockinLineTrans.location_code==Location.code, 
                    StockinLineTrans.warehouse_code==g.warehouse_code, 
                    StockinLineTrans.company_code==g.company_code, 
                    StockinLineTrans.owner_code==g.owner_code).order_by(StockinLineTrans.id.asc())
                locations = [c.code for c in query.all()]

            # 3.1 根据库存同货品重量分配, 从少到多. 等于数量
            if rule.str1 == 'same_inv_weight':
                f_qty = func.sum(Inv.qty).label('qty')
                query = Inv.query.with_entities(Inv.location_code.label('code'), f_qty).filter(
                    Inv.sku==line.sku,
                    Inv.warehouse_code==g.warehouse_code, 
                    Inv.company_code==g.company_code, 
                    Inv.owner_code==g.owner_code,
                    Inv.location_code!='PICK').group_by(Inv.location_code).order_by(f_qty.asc())
                if idx != 0:
                    query = query.filter(Inv.location_code.in_(locations))
                locations = [inv.code for inv in query.all()]

            # 3.2 根据库存所有货品重量分配, 从少到多
            if rule.str1 == 'inv_weight':
                f_weight = func.sum(Inv.qty*Good.weight).label('weight')
                query = Inv.query.with_entities(Inv.location_code.label('code'), f_weight).filter(
                    Inv.warehouse_code==g.warehouse_code, 
                    Inv.company_code==g.company_code, 
                    Inv.owner_code==g.owner_code,
                    Inv.location_code!='PICK',
                    Good.company_code==g.company_code,
                    Good.owner_code==g.owner_code)
                if idx != 0:
                    query = query.filter(Inv.location_code.in_(locations))
                query = query.group_by(Inv.location_code).order_by(f_weight.asc())
                locations = [inv.code for inv in query.all()]

            # 4.1 根据库存同货品数量分配, 从少到多
            if rule.str1 == 'same_inv_qty':
                f_qty = func.sum(Inv.qty).label('qty')
                query = Inv.query.with_entities(Inv.location_code.label('code'), f_qty).filter(
                    Inv.sku==line.sku,
                    Inv.warehouse_code==g.warehouse_code, 
                    Inv.company_code==g.company_code, 
                    Inv.owner_code==g.owner_code,
                    Inv.location_code!='PICK')
                if idx != 0:
                    query = query.filter(Inv.location_code.in_(locations))
                query = query.group_by(Inv.location_code).order_by(f_qty.asc())
                locations = [inv.code for inv in query.all()]

            # 4.2 根据库存所有货品数量分配, 从少到多
            if rule.str1 == 'inv_qty':
                f_qty = func.sum(Inv.qty).label('qty')
                query = Inv.query.with_entities(Inv.location_code.label('code'), f_qty).filter(
                    Inv.warehouse_code==g.warehouse_code, 
                    Inv.company_code==g.company_code, 
                    Inv.owner_code==g.owner_code,
                    Inv.location_code!='PICK')
                if idx != 0:
                    query = query.filter(Inv.location_code.in_(locations))
                query = query.group_by(Inv.location_code).order_by(f_qty.asc())
                locations = [inv.code for inv in query.all()]

            # 5. 一个库位只放一种东西（同货品，没有货品则选择空库位）
            if rule.str1 == 'same_location':
                query = Inv.query.t_query.with_entities(Inv.location_code.label('code')).filter(
                    Inv.location_code!='PICK',
                    Inv.qty>0,
                    Inv.sku==line.sku).group_by(Inv.location_code)
                if idx != 0:
                    query = query.filter(Inv.location_code.in_(locations))
                locations_inv = [inv.code for inv in query.all()]

                # 同种货品的库位
                locations = locations_inv
                # 不存在, 则选择空库位
                if not locations:
                    query = Inv.query.t_query.with_entities(Inv.location_code.label('code')).filter(
                        Inv.location_code!='PICK',
                        Inv.qty>0,
                        Inv.sku!=line.sku).group_by(Inv.location_code)
                    locations_inv = [inv.code for inv in query.all()]
                    locations_all = [c.code for c in query0.all()]
                    locations = list(set(locations_all) - set(locations_inv))

            # last. 根据库位码顺序(index, code)
            if rule.str1 == 'index_asc':
                query = query.order_by(Location.index.asc())
                locations = [c.code for c in query.all()]

            if rule.str1 == 'index_desc':
                query = query.order_by(Location.index.desc())
                locations = [c.code for c in query.all()]

            if rule.str1 == 'code_asc':
                query = query.order_by(Location.code.asc())
                locations = [c.code for c in query.all()]

            if rule.str1 == 'code_desc':
                query = query.order_by(Location.code.desc())
                locations = [c.code for c in query.all()]

            if rule.str1 == 'priority_asc':
                query = query.order_by(Location.priority.asc())
                locations = [c.code for c in query.all()]

            if rule.str1 == 'priority_desc':
                query = query.order_by(Location.priority.desc())
                locations = [c.code for c in query.all()]
                
        # 6. 放满后选择临近空库位（根据index, 根据area/workarea）
        if rules and 'most_close' in rules:
            pass
        elif rules and 'most_close_empty' in rules:
            pass

        # 如果没有规则, 随机10个库位
        if not rules:
            print('stockin auto_location recommend, not rules')
            locations = [c.code for c in query0.limit(10).all()]

        ok = True
        if not locations:
            ok = False
            print('stockin auto_location recommend, not locations')
            locations = [c.code for c in query0.limit(10).all()]

        # print(ok, locations)
        # print(locations)
        # 特殊库位判断, 是否允许 QC / STAGE 库位
        if 'no_qc' in rules:
            locations = [c for c in locations if c!='QC']
        if 'no_stage' in rules:
            locations = [c for c in locations if c!='STAGE']
        if 'no_stage_qc' in rules:
            locations = [c for c in locations if c!='STAGE' and c!='QC']

        # 找到库位, 清除不需要的
        if locations:
            locations = list(set(locations) - set(excludes or []))
            if locations:
                return ok, locations[0] if only_one else locations
            # 如果还找不到, 再继续找一次
            else:
                locations = [c.code for c in query0.limit(10).all()]
                locations = list(set(locations) - set(excludes or []))
                if locations:
                    return False, locations[0] if only_one else locations
        else:
            # 没找到库位
            pass
        
        return False, 'STAGE' if only_one else ['STAGE']


    # --------------- get default ---------------

    @staticmethod
    def make_order_code(company_code):
        #return 'IN-%s-%s-%04d'%(company_code, datetime.now().strftime('%Y%m%d%H%M%S'), randint(1, 9999))
        return 'R%s-%04d'%(datetime.now().strftime('%y%m%d%H%M%S'), randint(1, 9999))

    @staticmethod
    def create_stockin(data, g=None):
        exist = True
        order = None
        # replace
        erp_order_code = data.get('erp_order_code', '')
        if erp_order_code:
            subq = Stockin.query.filter_by(
                    company_code=data.get('company_code', '') or g.company_code,
                    warehouse_code=data.get('warehouse_code','') or g.warehouse_code, 
                    owner_code=data.get('owner_code') or g.owner_code)
            subq = subq.filter_by(erp_order_code=erp_order_code)
            order = subq.first()
        # new　不传订单号，直接创建新的
        if order is None:
            exist = False
            # order = Stockin(**{k:v for k,v in data.items() if k in [c.name for c in Stockin.__table__.columns] and k not in common_poplist})
            order = Stockin(**json2mdict_pop(Stockin, clear_empty(data)))
            if g:
                order.company_code = g.company_code
                order.warehouse_code = g.warehouse_code
                order.owner_code = g.owner_code
                if not order.user_code:
                    order.user_code = g.user.code
                    order.user_name = g.user.name
                
            order.order_code = Seq.make_order_code('R', order.company_code, order.warehouse_code, order.owner_code)
            if data.get('sender_info', None):
                order.sender_info = data.get('sender_info')
            if order.partner_code and not order.sender_name:
                partner = Partner.query.c_query.filter_by(code=order.partner_code).first()
                if partner is not None:
                    order.sender_name = partner.name
                    order.sender_tel = partner.tel or partner.phone
                    order.sender_address = partner.address
                    order.partner_name = partner.name
                    order.partner_id = partner.id
            if data.get('receiver_info', None):
                order.receiver_info = data.get('receiver_info')
            if data.get('remark', None):
                order.remark = data.get('remark')
                
            if not order.erp_order_code:
                order.erp_order_code = order.order_code

        return exist, order


    @staticmethod
    def create_stockin_line(data, order, line=None, poplist=None, is_add=True):
        poplist = poplist or []
        good = Good.query.filter_by(company_code=order.company_code, owner_code=order.owner_code, code=line.sku if line else data.get('sku')).first()
        if good:
            goodd = good.as_dict
            for b in ('name', 'barcode', 'spec','brand','unit', 'weight_unit','style','color','size'):
                data[b] = goodd.get(b, '') or data.get(b, '')
        # new
        if line is not None:
            for c in StockinLine.__table__.columns:
                if c not in common_poplist+poplist:
                    setattr(line, c, getattr(data, c, None))
        else:
            # line = StockinLine(**{k:v for k,v in data.items() if (k in [c.name for c in StockinLine.__table__.columns] and k not in common_poplist+poplist)})
            line = StockinLine(**json2mdict_pop(StockinLine, clear_empty(data)))
        for one in ['company_code', 'warehouse_code', 'owner_code', 'order_code', 'middle_order_code', 'erp_order_code']:
            setattr(line, one, getattr(order, one, ''))
        # line.JSON = data
        if is_add:
            line.stockin = order

        if order.partner_code and not line.supplier_code:
            line.supplier_code = order.partner_code
            line.partner_name = order.partner_name
            line.partner_id = order.partner_id

        if good and not line.price:
            line.price = good.cost_price or good.price or 0
        elif good and line.price:
            good.last_in_price = line.price
            
        return line


    # 入库流水转移库单
    @staticmethod
    def trans_to_invmove(stockin):
        from blueprints.inv.action import InvMoveAction

        data = []
        for line in stockin.lines:
            for tran in line.trans:
                d = DictNone()
                d.sku = line.sku
                d.name = line.name
                d.barcode = line.barcode
                d.location_code = tran.location_code
                d.lpn = tran.lpn
                d.qty = tran.qty_real
                d.supplier_code = line.supplier_code
                d.spec = line.spec
                # important
                d.stockin_order_code = stockin.order_code
                d.move_type = 'onshelf'
                data.append(d)

        action = InvMoveAction()
        series_code = action.gen_series_code(stockin.company_code, stockin.warehouse_code, stockin.owner_code)
        for d in data:
            action.create(d, series_code=series_code)
        stockin.move_order_code = series_code

        return series_code


    @staticmethod
    def inner_passback(order):
        # qimen回传
        if order.is_qimen and order.is_passback==False and order.state == 'done':
            from blueprints.qimen.action import async_confirm_order
            ret = async_confirm_order.schedule([order.id, 'in'], delay=2)


    def fan_order(self, stockout):
        fan_dict = fan_stock_type
        xtype = fan_dict.get(stockout.order_type, None)
        if not xtype:
            return False, u'该订单类型不能创建反单', None
        if stockout.fan_order_code:
            return False, u'已经存在反单, 请不要重复创建', None

        data = {
            'fan_order_code': stockout.order_code,
            'xtype': xtype,
            'partner_id': stockout.partner_id,
            'partner_code': stockout.partner_code,
            'partner_name': stockout.partner_name,
            'erp_source': stockout.erp_source,
            'remark': stockout.remark,
            'sender_name': stockout.receiver_name,
            'sender_tel': stockout.receiver_tel,
            'sender_province': stockout.receiver_province,
            'sender_city': stockout.receiver_city,
            'sender_area': stockout.receiver_area,
            'sender_town': stockout.receiver_town,
            'sender_address': stockout.receiver_address,
            'receiver_name': stockout.sender_name,
            'receiver_tel': stockout.sender_tel,
            'receiver_province': stockout.sender_province,
            'receiver_city': stockout.sender_city,
            'receiver_area': stockout.sender_area,
            'receiver_town': stockout.sender_town,
            'receiver_address': stockout.sender_address,
        }
        _, stockin = StockinAction.create_stockin(data, g)

        for oline in stockout.lines:
            ld = {
                'sku': oline.sku, 
                'barcode': oline.barcode, 
                'qty': oline.qty, 
                'name': oline.name,
                'location_code': oline.location_code or '',
            }
            StockinAction.create_stockin_line(ld, stockin)

        db.session.add(stockin)
        stockout.fan_order_code = stockin.order_code

        return True, u'ok', stockin