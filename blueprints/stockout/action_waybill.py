#coding=utf8

import traceback
from flask import g, current_app
from datetime import datetime
from random import randint
from itertools import groupby
from sqlalchemy import and_, or_
from utils.functions import update_model_with_fields, m2dict, copy_and_update_model, common_poplist, json2mdict_pop, clear_empty

from models.stockout import Stockout, StockoutLine, StockoutLineTrans, Alloc, StockoutMerge
from blueprints.inv.action import InvAction

from extensions.database import db
from models.inv import Inv, Good, InvTrans
from models.auth import Seq, Partner

from utils.waybill.kdniao import Kdniao

class WaybillAction(object):

    def __init__(self):
        pass

    def do(self, order, box, multi=False, weight=False):
        ok, msg = True, 'ok'

        # 获取快递公司
        if not g.owner.express_code or not g.owner.express_type:
            return False, u'请先配置货主的`快递(物流)类型`与`快递(物流)公司`'

        box.express_code =  order.express_code or g.owner.express_code
        box.express_type = g.owner.express_type or 'kdniao'

        # qimen如果传过来了面单号
        if order.bill_code:
            # TODO 通过面单号获取模板
            box.bill_code = order.bill_code
            return ok, msg

        # TODO 获取面单号
        ## 快递类型: 快递鸟
        if box.express_type=='kdniao':
            try:
                ok, msg = self.do_kdniao(order, box, multi=multi, weight=weight)
            except:
                ok = False
                msg = traceback.format_exc()
        
        return ok, msg

    def do_kdniao(self, order, box, multi=False, weight=False):
        ok, msg = True, 'ok'

        order_code = order.erp_order_code or order.order_code
        if multi:
            order_code = "%s_%s"%(order_code, box.id)

        kdniao = Kdniao(bid=g.owner.express_bid, appkey=g.owner.express_appkey, debug=current_app.debug)

        goods = []
        for line in box.lines:# order.lines
            goods.append({
                    "GoodsCode": line.sku,     # O
                    "GoodsName": line.name,    # R
                    "Goodsquantity": line.qty, # O
                    # "GoodsWeight": 1.0  # O
                })

        receiver = {               # 收货人
                "Name": order.receiver_name, 
                "Mobile": order.receiver_tel, 
                "CityName": order.receiver_city, 
                "ExpAreaName": order.receiver_area, 
                "Address": order.receiver_address, 
                "ProvinceName": order.receiver_province,
            }
        if current_app.debug:
            receiver = {               # 收货人
                "Name": order.receiver_name or u'刘数据', 
                "Mobile": order.receiver_tel or u'13167077953', 
                "CityName": order.receiver_city or u'上海市', 
                "ExpAreaName": order.receiver_area or u'闵行区', 
                "Address": order.receiver_address or u'xx小区8号楼1103',
                "ProvinceName": order.receiver_province or u'上海',
            }

        data = {
            "IsReturnPrintTemplate": 1, # 返回电子面单模板：0-不需要；1-需要
            "Remark": order.remark, 
            "Sender": {                 # 发货人信息
                "Name": order.sender_name or g.owner.sender_name, 
                "Mobile": order.sender_tel or g.owner.sender_tel,
                "CityName": order.sender_city or g.owner.sender_city,
                "ExpAreaName": order.sender_area or g.owner.sender_area,
                "Address": order.sender_address or g.owner.sender_address,
                "ProvinceName": order.sender_province or g.owner.sender_province,
            }, 
            "Commodity": goods,                # 要快递的东西
            "ShipperCode": box.express_code,        # 快递公司
            "Receiver": receiver, 
            #"OtherCost": 1.0,           # 其它费用
            "Quantity": 1,              # 包裹数(最多支持30件) 一个包裹对应一个运单号，如果是大于1个包裹，返回则按照子母件的方式返回母运单号和子运单号
            "OrderCode": order_code,    # 单号, 唯一
            #"Weight": 1.0,              # 总重
            "ExpType": 1,               # 快递类型：1-标准快件 ,详细快递类型参考《快递公司快递业务类型.xlsx》    
            "PayType": 3 if g.owner.express_month_code else 1,               # 邮费支付方式:1-现付，2-到付，3-月结，4-第三方支付(仅SF支持)
            #"Volume": 0.0,              # 包裹总体积m3 当为快运的订单时必填，不填时快递鸟将根据各个快运公司要求传对应的默认值
            #"Cost": 1.0                 # 快递运费
        }

        ret = kdniao.do('waybill', data)

        if ret['Success']:
            box.bill_code = ret['Order']['LogisticCode']
            box.plat_code = ret['Order']['KDNOrderCode'] + ' / ' +ret['UniquerRequestNumber']
            box.tpl = ret['PrintTemplate']
            if not order.bill_code:
                order.bill_code = box.bill_code
                order.express_code = box.express_code
                order.express_name = box.express_name
        else:
            ok = False
            msg = 'Fetch Kdniao LogisticCode Error: code: %s msg: %s'%(ret['ResultCode'], ret['Reason'])

        return ok, msg