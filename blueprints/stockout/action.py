#coding=utf8

import traceback
from flask import g
from datetime import datetime
from random import randint
from itertools import groupby
from sqlalchemy import and_, or_, func
from utils.base import fan_stock_type
from utils.functions import update_model_with_fields, m2dict, copy_and_update_model, common_poplist, json2mdict_pop, clear_empty

from models.stockout import Stockout, StockoutLine, StockoutLineTrans, Alloc
from blueprints.inv.action import InvAction

from extensions.database import db
from models.inv import Inv, Good, InvTrans
from models.auth import Seq, Partner, User

class StockoutAction(object):

    def __init__(self, stockout=None):
        self.stockout = stockout

    # 分配订单行
    def alloc_line(self, line_id, line=None, order=None):
        #line = StockoutLine.query.get(line_id)
        if line is None:
            line = StockoutLine.query.c_query.filter_by(id=line_id, stockout_id=self.stockout.id).with_for_update().first()

        invaction = InvAction()
        is_enough, invs = invaction.get_inv_by_stockout_line(line, withlock=True, order=order)

        qty_total = 0
        alloc_list = []
        # 一个订单行分配多个库存行时，前面的库存行直接扣减，最后一个库存行处理不足或者多余的情况
        for inv in invs[:-1]:
            alloc = update_model_with_fields(Alloc, line, common_poplist+['qty', 'qty_alloc', 'qty_pick', 'qty_ship'])
            alloc.stockout_id = line.stockout.id
            alloc.stockout_line_id = line_id

            alloc.qty_alloc = inv.qty_able
            alloc.lpn = inv.lpn
            alloc.inv_id = inv.id
            alloc.location_code = inv.location_code

            # 更新库存 # qty = qty_alloc + qty_able;
            inv.qty_able = 0
            inv.qty_alloc += alloc.qty_alloc
            inv.qty = inv.qty_able + inv.qty_alloc

            qty_total += alloc.qty_alloc

            # 更新订单行
            line.qty_alloc += alloc.qty_alloc
            if not line.location_code:
                line.location_code = inv.location_code

            # 增加订单行流水
            outtran = self.create_tran(line, alloc.qty_alloc, 'alloc', location_code=alloc.location_code)

            # 增加库存行流水
            InvAction.create_tran(inv, inv.qty, inv.qty, change_qty=alloc.qty_alloc, outtran=outtran, xtype='stockout', xtype_opt='alloc')

            alloc_list.append(alloc)
            db.session.add(alloc)

            if alloc.qty_alloc < 0:
                print('alloc_line nagative inv, order_line-qty_able-inv', line_id, alloc.qty_alloc, inv.id)
                raise Exception('nagative alloc, inv')

        # 库存不足或足够的情况
        if len(invs) > 0:
            inv = invs[-1]

            alloc = update_model_with_fields(Alloc, line, common_poplist+['qty', 'qty_alloc', 'qty_pick', 'qty_ship'])
            alloc.stockout_id = line.stockout.id
            alloc.stockout_line_id = line_id

            alloc.qty_alloc = (line.qty - line.qty_alloc) if is_enough else inv.qty_able
            alloc.lpn = inv.lpn
            alloc.inv_id = inv.id
            alloc.location_code = inv.location_code

            # 更新库存 # qty = qty_alloc + qty_able;
            inv.qty_able = inv.qty_able - alloc.qty_alloc
            inv.qty_alloc += alloc.qty_alloc
            inv.qty = inv.qty_able + inv.qty_alloc

            qty_total += alloc.qty_alloc

            # 更新订单行
            line.qty_alloc += alloc.qty_alloc

            # 增加订单行流水
            outtran = self.create_tran(line, alloc.qty_alloc, 'alloc', location_code=alloc.location_code)

            # 增加库存行流水
            InvAction.create_tran(inv, inv.qty, inv.qty, change_qty=alloc.qty_alloc, outtran=outtran, xtype='stockout', xtype_opt='alloc')

            alloc_list.append(alloc)
            db.session.add(alloc)

            if alloc.qty_alloc < 0:
                print('alloc_line nagative inv, order_line-qty_able-inv', line_id, inv.qty_able, inv.id)
                raise Exception('nagative alloc, inv')

        line.qty_total = qty_total
        return is_enough, line, alloc_list


    # 分配订单行--指定库位
    def alloc_line_by_inv(self, order, line_id, invqty):
        # {line_id: [{inv_id, qty}...]}
        line = StockoutLine.query.w_query.filter_by(id=line_id, stockout_id=order.id).with_for_update().first()
        # 超量分配了
        if sum([x['qty'] for x in invqty]) > (line.qty - line.qty_alloc):
            return False, line, [], None

        # 分配
        invaction = InvAction()
        alloc_list = []
        for x in invqty:
            inv = Inv.query.w_query.filter_by(id=x['inv_id']).with_for_update().first()
            if inv.qty_able >= x['qty']:
                alloc = update_model_with_fields(Alloc, line, common_poplist+['qty', 'qty_alloc', 'qty_pick', 'qty_ship'])
                alloc.stockout_id = line.stockout.id
                alloc.stockout_line_id = line_id

                # 更新库存
                alloc.qty_alloc = x['qty']
                alloc.lpn = inv.lpn
                alloc.inv_id = inv.id
                alloc.location_code = inv.location_code

                inv.qty_able = inv.qty_able - alloc.qty_alloc
                inv.qty_alloc += alloc.qty_alloc
                inv.qty = inv.qty_able + inv.qty_alloc

                # 更新订单行
                line.qty_alloc += alloc.qty_alloc

                # 增加订单行流水
                outtran = self.create_tran(line, alloc.qty_alloc, 'alloc', location_code=alloc.location_code)

                # 增加库存行流水
                InvAction.create_tran(inv, inv.qty, inv.qty, change_qty=alloc.qty_alloc, outtran=outtran, xtype='stockout', xtype_opt='alloc')

                alloc_list.append(alloc)
                db.session.add(alloc)

                if alloc.qty_alloc < 0:
                    print('alloc_line_by_inv nagative inv, order_line invqty', line_id, invqty )
                    return False, line, [], inv
            else:
                return False, line, [], inv

        return True, line, alloc_list, None


    # 分配订单
    def alloc(self, order_id, order=None, is_partalloc=False):
        if order is None:
            order = Stockout.query.w_query.filter_by(id=order_id).with_for_update().first()
        self.stockout = order
        # # 库存不足时允许不允许部分分配
        is_partalloc = is_partalloc or g.owner.is_partalloc
        finish = True

        current_line = None
        alloc_dict = {}
        has_alloc = False
        self.lack_line = None
        for line in order.lines:
            is_enough, current_line, alloc_list = self.alloc_line(line.id, line, order=order)
            alloc_dict[current_line.id] = alloc_list
            if not is_enough:
                self.lack_line = current_line
            if alloc_list:
                has_alloc = True
            # 不允许部分分配, 不足时, 中断
            if not is_partalloc and not is_enough:
                finish = False
                break
            # 允许部分分配, 不足时, 不中断
            if is_partalloc and not is_enough:
                finish = False
            # # 完全分配
            # if not is_enough:
            #     finish = False
            #     break
        # 不允许部分分配，库存又不足；则分配无法完成
        # 变更状态
        if finish:
            order.state_alloc = 'done'
            order.state = 'doing'
        elif has_alloc and is_partalloc:
            order.state_alloc = 'part'
            order.state = 'doing'

        return finish, is_partalloc, current_line, alloc_dict

    def alloc_cancel(self, order_id=None, line_id=None, company_code=None, warehouse_code=None, owner_code=None, cancel=False, order=None):
        order = order or Stockout.query.filter_by(id=order_id, company_code=company_code).with_for_update().first()
        order_id = order.id
        if order.state_alloc in ('part', 'done') and order.state not in ('cancel',) and order.state_ship == 'no':
            if line_id:
                lines = [StockoutLine.query.get(line_id)]
            else:
                lines = order.lines

            stockout_cancel_pick_inv_handle_type = g.owner.stockout_cancel_pick_inv_handle_type
            invaction = InvAction()

            from blueprints.stockin.action import StockinAction
            _, stockin = StockinAction.create_stockin({
                    'warehouse_code': order.warehouse_code,
                    'owner_code': order.owner_code,
                    'middle_order_code': order.order_code,
                    'remark': order.order_code,
                    'xtype': 'return',
                }, g)
            stockin_lines_count = 0

            for line in lines:
                # 未开始发运的行可以取消
                if line.qty_ship == 0:

                    stockin_line =  StockinAction.create_stockin_line(line.as_dict, stockin, poplist=['order_code', 'middle_order_code', 'erp_order_code'], is_add=False)
                    stockin_line.qty = 0
                    stockin_line.qty_real = 0

                    # 已经拣货的货品，由PICK库位进行上架到stage即可，不做其它处理==>改为已经拣货的，做退库单
                    for alloc in Alloc.query.filter_by(stockout_line_id=line.id).with_for_update().all():
                        # # 已经分配而且已经拣货的上架到stage库位==已经拣货的做退库单==已经拣货的原路退回
                        if stockout_cancel_pick_inv_handle_type == 'to_stage':
                            inv_stage = None
                            for inv_pick in Inv.query.filter_by(lpn='ALLOC_%s'%alloc.id, location_code='PICK').with_for_update().all():
                                # 上架到stage/移库合并到stage库位, 查询库位不一样，但sku，批次一样的库存，然后合并、创建
                                if not inv_stage:
                                    inv_stage = invaction.get_inv_by_same_batch(inv_pick, location_code='STAGE', lpn='', get_or_create=True, withlock=True)
                                # 增加stage库位的数量
                                inv_stage.qty += inv_pick.qty
                                inv_stage.qty_able += inv_pick.qty_able
                                
                                self.create_tran(alloc.stockout_line, inv_pick.qty_able, 'unpick', location_code=alloc.location_code, user_code='system', user_name='system')
                                # 删除 inv pick
                                db.session.delete(inv_pick)

                        if stockout_cancel_pick_inv_handle_type == 'to_stockin':
                            for inv_pick in Inv.query.filter_by( \
                                        company_code=company_code or order.company_code, \
                                        warehouse_code=warehouse_code or order.warehouse_code, \
                                        owner_code=owner_code or order.owner_code) \
                                    .filter_by(lpn='ALLOC_%s'%alloc.id, location_code='PICK').with_for_update().all():
                                stockin_line.qty += inv_pick.qty_able
                                # 预收库位
                                stockin_line.location_code = alloc.location_code
                                # create trans
                                self.create_tran(alloc.stockout_line, inv_pick.qty_able, 'unpick', location_code=alloc.location_code, user_code='system', user_name='system')
                                # 删除 inv pick
                                db.session.delete(inv_pick)

                        if stockout_cancel_pick_inv_handle_type == 'to_origin':
                            # 已经分配但已经拣货的，归还原库位
                            inv = alloc.lock_inv()
                            qty_can = alloc.qty_pick
                            if qty_can:
                                inv.qty_alloc = inv.qty_alloc - qty_can
                                inv.qty_able  = inv.qty_able + qty_can
                                inv.qty = inv.qty_alloc + inv.qty_able

                            for inv_pick in Inv.query.filter_by(lpn='ALLOC_%s'%alloc.id, location_code='PICK').with_for_update().all():
                                self.create_tran(alloc.stockout_line, inv_pick.qty_able, 'unpick', location_code=alloc.location_code, user_code='system', user_name='system')
                                # 删除 inv pick
                                db.session.delete(inv_pick)


                        # 已经分配但未拣的，归还原库位
                        inv = alloc.lock_inv()
                        qty_can = alloc.qty_alloc - alloc.qty_pick
                        if inv is not None and qty_can:
                            inv.qty_alloc = inv.qty_alloc - qty_can
                            inv.qty_able  = inv.qty_able + qty_can
                            inv.qty = inv.qty_alloc + inv.qty_able

                            self.create_tran(alloc.stockout_line, qty_can, 'unalloc', location_code=alloc.location_code, user_code='system', user_name='system')
                        # 删除alloc
                        db.session.delete(alloc)

                    if stockin_line.qty > 0:
                        stockin_lines_count += 1
                        stockin_line.stockin = stockin

                    # 清空订单行
                    line.qty_alloc = 0
                    line.qty_pick  = 0

            # add 退库单
            if stockin_lines_count > 0:
                db.session.add(stockin)

            if cancel:
                order.state = 'cancel'
                return True, 'cancel ok'

            db.session.flush()
            # 修改订单状态
            if StockoutLine.query.filter_by(stockout_id=order_id).filter(StockoutLine.qty_alloc > 0).count():
                order.state_alloc = 'part'
            else:
                order.state_alloc = 'no'

            if StockoutLine.query.filter_by(stockout_id=order_id).filter(StockoutLine.qty_pick > 0).count():
                order.state_pick = 'part'
            else:
                order.state_pick = 'no'

            if StockoutLine.query.filter_by(stockout_id=order_id).filter(StockoutLine.qty_ship > 0).count():
                order.state_ship = 'part'
            else:
                order.state_ship = 'no'

            if order.state_alloc == 'no' and order.state_pick == 'no' and order.state_ship == 'no':
                order.state = 'create'
            else:
                order.state = 'doing'

            order.finish()
            return True, 'ok'

        return False, u'订单在状态（alloc:%s, ship:%s, order:%s）下，不能取消分配'%(order.state_alloc, order.state_ship, order.state)


    # 出库流水
    def create_tran(self, line, qty, xtype, w_user_code=None, w_user_name=None, location_code='', user_code=None, user_name=None):
        tran = update_model_with_fields(StockoutLineTrans, line, common_poplist+['qty'], 
            qty=qty, xtype=xtype, user_code=user_code or g.user.code, user_name=user_name or g.user.name, location_code=location_code)
        tran.price = line.price
        tran.stockout_line = line
        tran.stockout = line.stockout
        tran.w_user_code = w_user_code
        tran.w_user_name = w_user_name
        db.session.add(tran)
        return tran

    @staticmethod
    def create_out_invtran(order):
        # 所有分配行, 进行出库扣除
        allocs = Alloc.query.t_query.filter_by(stockout_id=order.id).all()

        outlines = StockoutLine.query.t_query.with_entities(
                StockoutLine.sku.label('sku'), 
                StockoutLine.price.label('price'), 
                StockoutLine.qty_pick.label('qty_pick')
            ).filter(StockoutLine.stockout_id==Alloc.stockout_id, Alloc.stockout_id==order.id).all()
        price_dict = {o.sku:o.price for o in outlines}

        inv_dict = {o.id:o for o in Inv.query.t_query.filter(Inv.id==Alloc.inv_id, Alloc.stockout_id==order.id).all()}

        for alloc in allocs:
            inv = inv_dict.get(alloc.inv_id)
            if inv:
                tran = InvAction.create_tran(inv, inv.qty, inv.qty, change_qty=alloc.qty_pick, outtran=None, xtype='stockout', xtype_opt='out')
                tran.price = price_dict.get(alloc.sku)
                tran.order_code = order.order_code
                tran.erp_order_code = order.erp_order_code

        o = Inv.query.t_query.with_entities(func.sum(Inv.price*Inv.qty_able).label('cost_price')).filter_by(location_code='PICK', refid=order.id).first()
        order.cost_price = float(o.cost_price if o else 0)

    # ------------------------
    # 快速拣货
    def pick(self, order):
        if order.state_alloc == 'done' and order.state_pick in ('no', 'part') and order.state not in ('done', 'cancel'):
            # 拣货即移动到发货区库位（PICK）
            # 获取所有alloc行，对alloc进行移库操作
            for alloc in Alloc.query.filter_by(stockout_id=order.id).with_for_update().all():
                if alloc.qty_alloc - alloc.qty_pick <= 0:
                    continue
                # 移库到发货区
                qty_can = alloc.qty_alloc - alloc.qty_pick
                ok = InvAction.move_qty_alloc(alloc.inv_id, qty_can, alloc.warehouse_code, 'PICK', 'ALLOC_%s'%alloc.id, refid=order.id)
                if ok:
                    # 拣货复核数量
                    alloc.qty_pick += qty_can
                    # 订单行数量
                    alloc.stockout_line.qty_pick += qty_can

                    # 创建订单行流水
                    self.create_tran(alloc.stockout_line, qty_can, 'pick', w_user_code=g.user.code, w_user_name=g.user.name, location_code=alloc.location_code)
                    self.create_tran(alloc.stockout_line, qty_can, 'receive', w_user_code=g.user.code, w_user_name=g.user.name, location_code=alloc.location_code)
                else:
                    db.session.rollback()
                    return False

            # 修改订单状态
            order.state_pick = 'done'
            order.finish()

            return True
        return False

    # 发运； 考虑对接菜鸟，奇门，京东发运面单系统
    def ship(self):
        pass

    # 回传; 异步回传功能
    def passback(self):
        pass


    # --------------- get default ---------------

    @staticmethod
    def make_order_code(company_code):
        #return 'OUT-%s-%s-%04d'%(company_code, datetime.now().strftime('%Y%m%d%H%M%S'), randint(1, 9999))
        return 'C%s-%04d'%(datetime.now().strftime('%y%m%d%H%M%S'), randint(1, 9999))

    @staticmethod
    def create_stockout(data, g=None):
        exist = True
        order = None
        # replace
        erp_order_code = data.get('erp_order_code', '')
        if erp_order_code:
            subq = Stockout.query.filter_by(
                    company_code=data.get('company_code', '') or g.company_code,
                    warehouse_code=data.get('warehouse_code','') or g.warehouse_code, 
                    owner_code=data.get('owner_code', '') or g.owner_code)
            subq = subq.filter_by(erp_order_code=erp_order_code)

            order = subq.first()
        # new 不传订单号，直接创建新的
        if order is None:
            exist = False
            # order = Stockout(**{k:v for k,v in data.items() if k in [c.name for c in Stockout.__table__.columns] and k not in common_poplist})
            order = Stockout(**json2mdict_pop(Stockout, clear_empty(data)))
            if g:
                order.company_code = g.company_code
                order.warehouse_code = g.warehouse_code
                order.owner_code = g.owner_code
                if not order.user_code:
                    order.user_code = g.user.code
                    order.user_name = g.user.name

            if order.order_type == 'sale':
                order.order_code = Seq.make_order_code('CX', order.company_code, order.warehouse_code, order.owner_code)
            else:
                order.order_code = Seq.make_order_code('C', order.company_code, order.warehouse_code, order.owner_code)

            if data.get('sender_info', None):
                order.sender_info = data.get('sender_info')
            if data.get('receiver_info', None):
                order.receiver_info = data.get('receiver_info')
            if order.partner_code and not order.receiver_name:
                partner = Partner.query.c_query.filter_by(code=order.partner_code).first()
                if partner is not None:
                    order.receiver_name = partner.name
                    order.receiver_tel = partner.tel or partner.phone
                    order.receiver_address = partner.address
                    order.partner_name = partner.name
                    order.partner_id = partner.id
            if data.get('remark', None):
                order.remark = data.get('remark')
            if order.w_user_code:
                u = User.query.c_query.filter_by(code=order.w_user_code).first()
                if u:
                    order.w_user_name = u.name
                
            if not order.erp_order_code:
                order.erp_order_code = order.order_code

        return exist, order


    @staticmethod
    def create_stockout_line(data, order):
        good = Good.query.filter_by(company_code=order.company_code, owner_code=order.owner_code, code=data.get('sku')).first()
        # new
        if good:
            goodd = good.as_dict
            for b in ('spec','brand','unit','weight_unit','style','color','size'):
                data[b] = goodd.get(b, '')
        # line = StockoutLine(**{k:v for k,v in data.items() if k in [c.name for c in StockoutLine.__table__.columns] and k not in common_poplist})
        line = StockoutLine(**json2mdict_pop(StockoutLine, clear_empty(data)))
        for one in ['company_code', 'warehouse_code', 'owner_code', 'order_code', 'middle_order_code', 'erp_order_code']:
            setattr(line, one, getattr(order, one, ''))
        # line.JSON = data
        line.stockout = order

        if order.partner_code and not line.supplier_code:
            line.supplier_code = order.partner_code
            line.partner_name = order.partner_name
            line.partner_id = order.partner_id

        if good and line.price:
            good.last_out_price = line.price

        return line

    @staticmethod
    def create_transfer_stockin(order):
        if not order.transfer_in_order_code and order.order_type == 'transfer':
            db.session.flush()
            from blueprints.stockin.action import StockinAction
            data = {
                'company_code': order.transfer_in_company_code or order.company_code,
                'warehouse_code': order.transfer_in_warehouse_code or order.warehouse_code,
                'owner_code': order.transfer_in_owner_code or order.owner_code,
                'transfer_out_order_code': order.order_code,
                'transfer_out_order_state': order.state,
                'transfer_out_company_code': order.company_code,
                'transfer_out_company_name': g.user.company.name,
                'transfer_out_warehouse_code': order.warehouse_code,
                'transfer_out_warehouse_name': g.warehouse.name,
                'transfer_out_owner_code': order.owner_code,
                'transfer_out_owner_name': g.owner.name,
                'remark': order.remark,
                'receiver_info': order.sender_info,
                'sender_info': order.receiver_info,
                'xtype': 'transfer',
            }
            _, stockin = StockinAction.create_stockin(data)
            for line in order.lines:
                # 先判断有没有货品信息, 没有则添加
                good = Good.query.filter_by(
                    company_code=order.transfer_in_company_code, 
                    owner_code=order.transfer_in_owner_code,
                    code=line.sku).first()
                if good is None:
                    good = update_model_with_fields(Good, line.good, common_poplist, 
                        company_code=order.transfer_in_company_code, owner_code=order.transfer_in_owner_code)
                    db.session.add(good)
            db.session.flush()

            for line in order.lines:
                # {'sku': 'sku1', 'barcode': 'sku1', 'qty': 5, 'name':'name1'},
                linedata = {
                    'sku':line.sku,
                    'barcode': line.barcode,
                    'name': line.name,
                    'qty': line.qty,
                }
                StockinAction.create_stockin_line(linedata, stockin)
            db.session.add(stockin)
            order.transfer_in_order_code = stockin.order_code
            return stockin
        return None


    @staticmethod
    def inner_passback(order):
        # qimen回传
        if order.is_qimen and order.is_passback==False and order.state == 'done' and order.state_ship=='done':
            from blueprints.qimen.action import async_confirm_order
            ret = async_confirm_order.schedule([order.id, 'out'], delay=2)


    def fan_order(self, stockin):
        fan_dict = {v:k for k, v in fan_stock_type.items()}
        xtype = fan_dict.get(stockin.xtype, None)
        if not xtype:
            return False, u'该订单类型不能创建反单', None
        if stockin.fan_order_code:
            return False, u'已经存在反单, 请不要重复创建', None

        data = {
            'fan_order_code': stockin.order_code,
            'order_type': xtype,
            'partner_id': stockin.partner_id,
            'partner_code': stockin.partner_code,
            'partner_name': stockin.partner_name,
            'erp_source': stockin.erp_source,
            'remark': stockin.remark,
            'sender_name': stockin.receiver_name,
            'sender_tel': stockin.receiver_tel,
            'sender_province': stockin.receiver_province,
            'sender_city': stockin.receiver_city,
            'sender_area': stockin.receiver_area,
            'sender_town': stockin.receiver_town,
            'sender_address': stockin.receiver_address,
            'receiver_name': stockin.sender_name,
            'receiver_tel': stockin.sender_tel,
            'receiver_province': stockin.sender_province,
            'receiver_city': stockin.sender_city,
            'receiver_area': stockin.sender_area,
            'receiver_town': stockin.sender_town,
            'receiver_address': stockin.sender_address,
        }
        _, stockout = StockoutAction.create_stockout(data, g)

        for oline in stockin.lines:
            ld = {
                'sku': oline.sku, 
                'barcode': oline.barcode, 
                'qty': oline.qty, 
                'name': oline.name,
                'location_code':oline.location_code or '',
            }
            StockoutAction.create_stockout_line(ld, stockout)

        db.session.add(stockout)
        stockin.fan_order_code = stockout.order_code

        return True, u'ok', stockout
