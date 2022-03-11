#coding=utf8

import os
import xmltodict
import requests
import traceback
from flask import g
from datetime import datetime
from random import randint
from itertools import groupby
from hashlib import md5, sha256
#from urllib import urlencode
from urllib.parse import urlencode
from utils.functions import update_model_with_fields, m2dict, copy_and_update_model, common_poplist, \
        json2mdict_pop, clear_empty, DictNone, ubarcode
from sqlalchemy import and_, or_, func

from extensions.hueyext import hueyapp
from extensions.database import db

from models.inv import Inv, Good, Category
from models.auth import Seq, Partner, Company
from models.stockin import Stockin, StockinLine
from models.stockout import Stockout, StockoutLine


QIMEN_URL = os.environ.get('QIMEN_URL', 'http://qimenapi.tbsandbox.com/router/qimen/service')

QIMEN_SUPPORT_API_LIST = [
    "singleitem.synchronize", 
    "entryorder.create", 
    "stockout.create", 
    "deliveryorder.create", 
    "order.cancel",
    "returnorder.create", 
    "inventory.query",
]

class QimenAction(object):

    def __init__(self, company_code=''):
        self.api_list = QIMEN_SUPPORT_API_LIST
        self.company_code = company_code

    def sign(self, method='', customerid='', secret='', timestamp='', body='', app_key='MT-WMS', format='json', sign_method='md5', v='2.0'):
        # method  必须  方法名
        # timestamp   必须  时间戳，格式为yyyy-MM-dd HH:mm:ss
        # format  必须  仓储仅支持xml
        # app_key 必须  您的应用名
        # sign    必须  签名字符串
        # sign_method 必须  签名算法，支持md5和hmac-sha256
        # customerid  必须  货主id
        # v   必须  目前仅支持2.0

        # // 第一步：检查参数是否已经排序
        # // 第二步：把所有参数名和参数值串在一起
        # // 第三步：把请求主体拼接在参数后面
        # // 第四步：使用MD5/HMAC加密
        # // 第五步：把二进制转化为大写的十六进制

        kw = DictNone()
        kw.method = method
        kw.format = format
        kw.customerid = customerid
        kw.app_key = app_key
        kw.sign_method = sign_method
        kw.v = v
        kw.timestamp = timestamp#datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        kw_list = []
        kw_list.append(secret)
        keys = kw.keys()
        keys.sort()
        for k in keys:
            kw_list.append(k)
            kw_list.append(kw[k])
        kw_list.append(body)

        sign = md5("".join(kw_list)).hexdigest()
        kw.sign = sign
        return sign, kw

    def check_sign(self, args, body=''):
        kw = DictNone(args.to_dict())
        secret = ''

        owner = Partner.query.filter_by(qimen_customerid=kw.customerid).first()
        if owner is not None:
            company = owner.company
            
        else:
            company = Company.query.filter_by(code=kw.customerid).first()

        if company is None:
            return False
        else:
            secret = company.apikey

        sign = kw.pop('sign')
        sign2, _= self.sign(secret=secret, body=body, **kw)
        if sign == sign2:
            self.company_code = company.code
            return True
        return False


    def do(self, method, args, reqdata):
        func_name = 'api_' + method.replace('.', '_')
        func = getattr(self, func_name)

        return func(args, reqdata)


    def api_singleitem_synchronize(self, args, reqdata):
        sku = reqdata['request']['item']['itemCode']

        ok, msg = True, ''

        req = reqdata['request']
        item = DictNone(req.pop('item', {}))
        req = DictNone(req)

        warehouse_code = 'default' if req.warehouseCode == 'OTHER' else req.warehouseCode
        owner_code = req.ownerCode or 'default'
        actionType = req.actionType or 'add'

        good = Good.query.filter_by(code=sku, owner_code=owner_code, company_code=self.company_code).first()

        if actionType == 'add':
            if good is not None:
                pass
            else:
                good = Good(owner_code=owner_code, code=sku, company_code=self.company_code)
                db.session.add(good)

        if good:
            good.name = item.itemName
            good.name_en = ubarcode(good.name).replace(' ', '')
            # TODO 多条码, 暂时不支持
            good.barcode = (item.barCode or '').split(';')[0] or sku
            good.spec = item.skuProperty or ''
            good.unit = item.stockUnit or ''

            good.length = item.length or ''
            good.width = item.width or ''
            good.height = item.height or ''
            good.volume = item.volume or ''
            good.weight = item.weight or ''
            good.gross_weight = item.grossWeight or ''

            good.color = item.color or ''
            good.size = item.size or ''

            good.category_code = item.categoryId or 'default'
            cate = Category.query.filter_by(code=good.category_code, owner_code=owner_code, company_code=self.company_code).first()
            if cate is None:
                cate = Category(code=good.category_code, name=item.categoryName, owner_code=owner_code, company_code=self.company_code)
                db.session.add(cate)

            good.min_qty = item.safetyStock or 0
            good.item_type = item.itemType or 'ZC'
            good.price = item.retailPrice or 0
            good.cost_price = item.costPrice or 0
            good.brand = '%s / %s'%(item.brandCode, item.brandName) if item.brandCode else ''
            good.is_shelf_life = 'on' if item.isShelfLifeMgmt=='Y' else 'off'
            good.remark = item.remark or ''

        else:
            ok = False
            msg = u'goods can not find'


        fail_ret = {
            "response":{
                "flag":"failure",
                "code":"2",
                "message":msg,
                "itemId":sku,
            }
        }

        success_ret = {
            "error_response":{
                "flag":"success",
                "code":"0",
                "message":msg,
                "itemId":sku,
            }
        }

        if not ok:
            return ok, fail_ret
        return ok, success_ret


    def api_entryorder_create(self, args, reqdata):
        erp_order_code = reqdata['request']['entryOrder']['entryOrderCode']

        ok, msg = True, 'ok'

        req = reqdata['request']
        item = DictNone(req.pop('entryOrder', {}))
        itemlines = [DictNone(line) for line in req.pop('orderLines', [])]

        warehouse_code = 'default' if item.warehouseCode == 'OTHER' else item.warehouseCode
        owner_code = item.ownerCode

        stockin = Stockin.query.filter_by(erp_order_code=erp_order_code, warehouse_code=warehouse_code, owner_code=owner_code, company_code=self.company_code).first()
        if not stockin:
            stockin = Stockin(erp_order_code=erp_order_code, warehouse_code=warehouse_code, owner_code=owner_code, company_code=self.company_code)
            stockin.is_qimen = True
            stockin.order_code = erp_order_code
            stockin.xtype = 'custom'
            stockin.order_type = item.orderType or 'CGRK'
            stockin.remark = item.remark or ''
            # stockin.create_time = item.orderCreateTime or db.func.current_timestamp()
            stockin.date_planned = item.expectStartTime or None
            stockin.date_planned_end = item.expectEndTime or None
            stockin.express_code = item.logisticsCode or ''
            stockin.express_name = item.logisticsName or ''
            stockin.bill_code = item.expressCode or ''
            # 开启 is_enable_supplier_batch 库存才会有供应商
            stockin.partner_code = item.supplierCode or ''
            stockin.partner_name = item.supplierName or ''
            partner = Partner.query.filter_by(company_code=self.company_code, code=stockin.partner_code).first()
            if partner is None:
                partner = Partner(company_code=self.company_code, code=stockin.partner_code, name=stockin.partner_name)
                db.session.add(partner)
                db.session.flush()
            else:
                stockin.partner_id = partner.id
            # stockin.user_code = item.operatorCode
            # stockin.user_name = item.operatorName

            sender = DictNone(item.senderInfo or {})
            receiver = DictNone(item.receiverInfo or {})

            stockin.sender_name = sender.name or ''
            stockin.sender_tel = sender.mobile or sender.tel or ''
            stockin.sender_province = sender.province or ''
            stockin.sender_city = sender.city or ''
            stockin.sender_area = sender.area or ''
            stockin.sender_town = sender.town or ''
            stockin.sender_address = sender.detailAddress or ''

            stockin.receiver_name = receiver.name or ''
            stockin.receiver_tel = receiver.mobile or receiver.tel or ''
            stockin.receiver_province = receiver.province or ''
            stockin.receiver_city = receiver.city or ''
            stockin.receiver_area = receiver.area or ''
            stockin.receiver_town = receiver.town or ''
            stockin.receiver_address = receiver.detailAddress or ''

            for it in itemlines:
                line = StockinLine(company_code=self.company_code, owner_code=owner_code, warehouse_code=warehouse_code, 
                        order_code=stockin.order_code, erp_order_code=stockin.erp_order_code)
                line.lineno = it.orderLineNo or ''
                line.sku = it.itemCode
                line.name = it.itemName
                line.barcode = it.barCode or it.itemCode
                line.unit = it.unit or ''
                line.qty = it.planQty
                line.price = it.purchasePrice or 0
                line.spec = it.skuProperty or ''
                line.quality_type = it.inventoryType or 'ZP'
                line.product_date = it.productDate or None
                line.expire_date = it.expireDate or None
                line.batch_code = it.batchCode or ''
                line.stockin = stockin
                
                line.partner_id = stockin.partner_id
                line.partner_name = stockin.partner_name
                line.supplier_code = stockin.partner_code

                db.session.add(line)

            db.session.add(stockin)

        return ok, {
            "response":{
                "flag":"success",
                "code":"0",
                "message": msg,
                "entryOrderId":stockin.order_code
            }
        }


    def api_returnorder_create(self, args, reqdata):
        erp_order_code = reqdata['request']['returnOrder']['returnOrderCode']

        ok, msg = True, 'ok'

        req = reqdata['request']
        item = DictNone(req.pop('returnOrder', {}))
        itemlines = [DictNone(line) for line in req.pop('orderLines', [])]

        warehouse_code = 'default' if item.warehouseCode == 'OTHER' else item.warehouseCode
        owner_code = item.ownerCode

        stockin = Stockin.query.filter_by(erp_order_code=erp_order_code, warehouse_code=warehouse_code, owner_code=owner_code, company_code=self.company_code).first()
        if not stockin:
            stockin = Stockin(erp_order_code=erp_order_code, warehouse_code=warehouse_code, owner_code=owner_code, company_code=self.company_code)
            stockin.is_qimen = True
            stockin.order_code = erp_order_code
            stockin.xtype = 'custom'
            stockin.order_type = item.orderType or 'THRK'
            stockin.remark = item.remark or ''
            # stockin.create_time = item.orderCreateTime or db.func.current_timestamp()
            stockin.date_planned = item.expectStartTime or None
            stockin.date_planned_end = item.expectEndTime or None
            stockin.express_code = item.logisticsCode or ''
            stockin.express_name = item.logisticsName or ''
            stockin.bill_code = item.expressCode or ''

            sender = DictNone(item.senderInfo or {})
            receiver = DictNone(item.receiverInfo or {})

            stockin.sender_name = sender.name or ''
            stockin.sender_tel = sender.mobile or sender.tel or ''
            stockin.sender_province = sender.province or ''
            stockin.sender_city = sender.city or ''
            stockin.sender_area = sender.area or ''
            stockin.sender_town = sender.town or ''
            stockin.sender_address = sender.detailAddress or ''

            stockin.receiver_name = receiver.name or ''
            stockin.receiver_tel = receiver.mobile or receiver.tel or ''
            stockin.receiver_province = receiver.province or ''
            stockin.receiver_city = receiver.city or ''
            stockin.receiver_area = receiver.area or ''
            stockin.receiver_town = receiver.town or ''
            stockin.receiver_address = receiver.detailAddress or ''

            for it in itemlines:
                line = StockinLine(company_code=self.company_code, owner_code=owner_code, warehouse_code=warehouse_code, 
                        order_code=stockin.order_code, erp_order_code=stockin.erp_order_code)
                line.lineno = it.orderLineNo or ''
                line.sku = it.itemCode
                line.name = it.itemName
                line.barcode = it.barCode or it.itemCode
                line.unit = it.unit or ''
                line.qty = it.planQty
                line.spec = it.skuProperty or ''
                line.quality_type = it.inventoryType or 'ZP'
                line.product_date = it.productDate or None
                line.expire_date = it.expireDate or None
                line.batch_code = it.batchCode or ''
                line.stockin = stockin
                db.session.add(line)

            db.session.add(stockin)

        return ok, {
            "response":{
                "flag":"success",
                "code":"0",
                "message": msg,
                "returnOrderId":stockin.order_code
            }
        }

    # B2B
    def api_stockout_create(self, args, reqdata):
        erp_order_code = reqdata['request']['deliveryOrder']['deliveryOrderCode']

        ok, msg = True, 'ok'

        req = reqdata['request']
        item = DictNone(req.pop('deliveryOrder', {}))
        itemlines = [DictNone(line) for line in req.pop('orderLines', [])]

        warehouse_code = 'default' if item.warehouseCode == 'OTHER' else item.warehouseCode
        owner_code = item.ownerCode

        stockout = Stockout.query.filter_by(erp_order_code=erp_order_code, warehouse_code=warehouse_code, owner_code=owner_code, company_code=self.company_code).first()
        if not stockout:
            stockout = Stockout(erp_order_code=erp_order_code, warehouse_code=warehouse_code, owner_code=owner_code, company_code=self.company_code)
            stockout.is_qimen = True
            stockout.order_code = erp_order_code
            stockout.order_type = 'custom'
            stockout.sub_order_type = item.orderType or 'PTCK'
            stockout.xtype = 'B2B'
            stockout.remark = item.remark or ''
            # stockout.create_time = item.orderCreateTime or db.func.current_timestamp()
            stockout.date_planned = item.scheduleDate or None
            stockout.express_code = item.logisticsCode or ''
            stockout.express_name = item.logisticsName or ''
            stockout.bill_code = item.expressCode or ''
            stockout.erp_source = item.orderSourceType or ''
            # 开启 is_enable_supplier_batch 库存才会有供应商
            stockout.partner_code = item.supplierCode or ''
            stockout.partner_name = item.supplierName or ''
            partner = Partner.query.filter_by(company_code=self.company_code, code=stockout.partner_code).first()
            if partner is None:
                partner = Partner(company_code=self.company_code, code=stockout.partner_code, name=stockout.partner_name)
                db.session.add(partner)
                db.session.flush()
            else:
                stockout.partner_id = partner.id
            # stockout.user_code = item.operatorCode
            # stockout.user_name = item.operatorName

            sender = DictNone(item.senderInfo or {})
            receiver = DictNone(item.receiverInfo or {})

            stockout.sender_name = sender.name or ''
            stockout.sender_tel = sender.mobile or sender.tel or ''
            stockout.sender_province = sender.province or ''
            stockout.sender_city = sender.city or ''
            stockout.sender_area = sender.area or ''
            stockout.sender_town = sender.town or ''
            stockout.sender_address = sender.detailAddress or ''

            stockout.receiver_name = receiver.name or ''
            stockout.receiver_tel = receiver.mobile or receiver.tel or ''
            stockout.receiver_province = receiver.province or ''
            stockout.receiver_city = receiver.city or ''
            stockout.receiver_area = receiver.area or ''
            stockout.receiver_town = receiver.town or ''
            stockout.receiver_address = receiver.detailAddress or ''

            for it in itemlines:
                line = StockoutLine(company_code=self.company_code, owner_code=owner_code, warehouse_code=warehouse_code, 
                        order_code=stockout.order_code, erp_order_code=stockout.erp_order_code)
                line.lineno = it.orderLineNo
                line.sku = it.itemCode
                line.name = it.itemName
                line.barcode = it.barCode or it.itemCode
                line.unit = it.unit or ''
                line.qty = it.planQty
                line.spec = it.skuProperty or ''
                line.quality_type = it.inventoryType or 'ZP'
                line.product_date = it.productDate or None
                line.expire_date = it.expireDate or None
                line.batch_code = it.batchCode or ''
                line.stockout = stockout

                line.partner_id = stockout.partner_id
                line.partner_name = stockout.partner_name
                line.supplier_code = stockout.partner_code

                db.session.add(line)

            db.session.add(stockout)

        return ok, {
            "response":{
                "flag":"success",
                "code":"0",
                "message": msg,
                "createTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "deliveryOrderId":stockout.order_code
            }
        }

    # B2C 
    def api_deliveryorder_create(self, args, reqdata):
        erp_order_code = reqdata['request']['deliveryOrder']['deliveryOrderCode']

        ok, msg = True, 'ok'

        req = reqdata['request']
        item = DictNone(req.pop('deliveryOrder', {}))
        itemlines = [DictNone(line) for line in req.pop('orderLines', [])]

        warehouse_code = 'default' if item.warehouseCode == 'OTHER' else item.warehouseCode
        owner_code = item.ownerCode

        stockout = Stockout.query.filter_by(erp_order_code=erp_order_code, warehouse_code=warehouse_code, owner_code=owner_code, company_code=self.company_code).first()
        if not stockout:
            stockout = Stockout(erp_order_code=erp_order_code, warehouse_code=warehouse_code, owner_code=owner_code, company_code=self.company_code)
            stockout.is_qimen = True
            stockout.order_code = erp_order_code
            stockout.order_type = 'custom'
            stockout.sub_order_type = item.orderType or 'JYCK'
            stockout.xtype = 'B2C'
            stockout.remark = item.remark or ''
            # stockout.create_time = item.orderCreateTime or db.func.current_timestamp()
            stockout.express_code = item.logisticsCode or ''
            stockout.express_name = item.logisticsName or ''
            stockout.bill_code = item.expressCode or ''
            stockout.erp_source = item.sourcePlatformCode or ''
            # stockout.user_code = item.operatorCode
            # stockout.user_name = item.operatorName

            sender = DictNone(item.senderInfo or {})
            receiver = DictNone(item.receiverInfo or {})

            stockout.sender_name = sender.name or ''
            stockout.sender_tel = sender.mobile or sender.tel or ''
            stockout.sender_province = sender.province or ''
            stockout.sender_city = sender.city or ''
            stockout.sender_area = sender.area or ''
            stockout.sender_town = sender.town or ''
            stockout.sender_address = sender.detailAddress or ''

            stockout.receiver_name = receiver.name or ''
            stockout.receiver_tel = receiver.mobile or receiver.tel or ''
            stockout.receiver_province = receiver.province or ''
            stockout.receiver_city = receiver.city or ''
            stockout.receiver_area = receiver.area or ''
            stockout.receiver_town = receiver.town or ''
            stockout.receiver_address = receiver.detailAddress or ''

            for it in itemlines:
                line = StockoutLine(company_code=self.company_code, owner_code=owner_code, warehouse_code=warehouse_code, 
                        order_code=stockout.order_code, erp_order_code=stockout.erp_order_code)
                line.lineno = it.orderLineNo
                line.sku = it.itemCode
                line.name = it.itemName
                line.barcode = it.barCode or it.itemCode
                line.unit = it.unit or ''
                line.qty = it.planQty
                line.spec = it.skuProperty or ''
                line.price = it.actualPrice or 0
                line.quality_type = it.inventoryType or 'ZP'
                line.product_date = it.productDate or None
                line.expire_date = it.expireDate or None
                line.batch_code = it.batchCode or ''
                line.stockout = stockout
                db.session.add(line)

            db.session.add(stockout)

        return ok, {
            "response":{
                "flag":"success",
                "code":"0",
                "message": msg,
                "createTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "deliveryOrderId":stockout.order_code
            }
        }


    def api_order_cancel(self, args, reqdata):
        erp_order_code = reqdata['request']['orderCode']

        ok, msg = True, 'ok'

        req = DictNone(reqdata['request'])
        warehouse_code = 'default' if req.warehouseCode == 'OTHER' else (req.warehouseCode or 'default')
        owner_code = 'default' if req.ownerCode == 'OTHER' else (req.ownerCode or 'default')

        stockin = Stockin.query.filter_by(erp_order_code=erp_order_code, warehouse_code=warehouse_code, owner_code=owner_code, company_code=self.company_code).with_for_update().first()
        if stockin and stockin.state == 'create':
            stockin.state = 'cancel'
            stockin.reason = req.cancelReason

        stockout = Stockout.query.filter_by(erp_order_code=erp_order_code, warehouse_code=warehouse_code, owner_code=owner_code, company_code=self.company_code).with_for_update().first()
        if stockout:
            if stockout.state == 'create':
                stockout.state = 'cancel'
                stockout.reason = req.cancelReason
            elif stockout.state == 'doing' and stockout.state_ship == 'no':
                from blueprints.stockout.action import StockoutAction
                action = StockoutAction()
                ok, msg = action.alloc_cancel(stockout.id, order=stockout, cancel=True, company_code=self.company_code, owner_code=owner_code, warehouse_code=warehouse_code)

        if not ok:
            return ok, {
                "error_response":{
                    "flag":"failure",
                    "code":"2",
                    "message":"order is shipping, can not cancel"
                },
                # "response":{
                #     "flag":"failure",
                #     "code":"2",
                #     "message":"order is shipping, can not cancel"
                # }
            }

        return ok, {
            "response":{
                "flag":"success",
                "code":"0",
                "message":"ok"
            }
        }


    def api_inventory_query(self, args, reqdata):
        ok, msg = True, 'ok'

        data = []
        lines = [DictNone(line) for line in reqdata['request']['criteriaList']]

        for line in lines:
            warehouse_code = 'default' if line.warehouseCode == 'OTHER' else line.warehouseCode
            owner_code = line.ownerCode

            inv = Inv.query.with_entities(
                    func.sum(Inv.qty_able).label('qty_able'), 
                    func.sum(Inv.qty).label('qty'), 
                    Inv.sku.label('sku'), 
                    Inv.quality_type.label('quality_type'),
                ).filter_by(company_code=self.company_code, warehouse_code=warehouse_code, owner_code=owner_code) \
                .filter_by(sku=line.itemCode).group_by(Inv.sku, Inv.quality_type).first()

            d = {
                    "warehouseCode": warehouse_code,
                    "itemCode":inv.sku,
                    "itemId":inv.sku,
                    "inventoryType":inv.quality_type,
                    "quantity": inv.qty_able,
                    "lockQuantity": inv.qty - inv.qty_able,
                    #"batchCode":'',
                    #"productDate":None,
                    #"expireDate":None,
                }
            data.append(d)

        return ok, {
            "response":{
                "flag":"success",
                "code":"0",
                "message":"ok",
                "items":{
                    "item": data
                }
            }
        }

    # ---- confirm -----

    def do_confirm(self, order, inout='in'):
        ok, msg = True, 'ok'

        # 跳过已经回传的
        if not order.is_passback and order.is_qimen:
            pass
        else:
            return ok, msg

        data = None
        method = ''
        if inout == 'in':
            if order.order_type in ('THRK', 'HHRK'):
                data = self.api_returnorder_confirm(order)
                method = 'returnorder.confirm'
            else:
                data = self.api_entryorder_confirm(order)
                method = 'entryorder.confirm'
        if inout == 'out':
            if order.sub_order_type  in ('JYCK', 'HHCK', 'BFCK', 'QTCK'):
                data = self.api_deliveryorder_confirm(order)
                method = 'deliveryorder.confirm'
            else:
                data = self.api_stockout_confirm(order)
                method = 'stockout.confirm'
        # sign
        qimen_url = g.owner.qimen_url or QIMEN_URL
        qimen_customerid = g.owner.qimen_customerid or order.company_code
        qimen_secret = g.owner.qimen_secret or order.company.apikey
        qimen_type = g.owner.qimen_type or 'json'
        is_xml = qimen_type == 'xml'
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        body = xmltodict.unparse(data, pretty=True) if is_xml else ''
        sign, kw = self.sign(method=method, customerid=qimen_customerid, secret=qimen_secret, timestamp=timestamp, body=body)
        print('QIMEN CONFIRM==>', qimen_url, kw, '\n', data)
        try:
            if is_xml:
                resp = requests.post(qimen_url+'?'+urlencode(kw), data=body, timeout=30, headers={'content-type': 'application/xml'})
                ret = xmltodict.parse(resp.content)
            else:
                resp = requests.post(qimen_url+'?'+urlencode(kw), json=data, timeout=30)
                ret = resp.json()
            print(ret)
            if ret['response']['flag'] == 'success':
                order.is_passback = True
                return ok, msg
            else:
                ok = False
                msg = ret['error_response']['message']
                order.is_passback = False
                return ok, msg
        except:
            ok = False
            msg = traceback.format_exc()
            return ok, msg


    def api_entryorder_confirm(self, order):
        entryOrder = DictNone()
        orderLines = []

        entryOrder.entryOrderCode = order.erp_order_code
        entryOrder.ownerCode = order.owner_code
        entryOrder.warehouseCode = order.warehouse_code
        entryOrder.outBizCode = '%s-%s'%(order.order_code, randint(100, 999))
        entryOrder.status = 'CLOSED'
        entryOrder.orderType = order.order_type
        # shopCode/shopNick = g.owner.shop_code/g.owner.shop_name

        for line in order.lines:
            ld = DictNone()
            ld.ownerCode = order.owner_code
            ld.itemCode = line.sku
            ld.itemName = line.name
            ld.planQty = line.qty
            ld.quality_type = line.quality_type
            ld.actualQty = line.qty_real

            orderLines.append(ld)

        return True, {
            'response': {'entryOrder': entryOrder, 'orderLines': orderLines}
        }

    def api_returnorder_confirm(self, order):
        entryOrder = DictNone()
        orderLines = []

        entryOrder.returnOrderCode = order.erp_order_code
        entryOrder.ownerCode = order.owner_code
        entryOrder.warehouseCode = order.warehouse_code
        entryOrder.outBizCode = '%s-%s'%(order.order_code, randint(100, 999))
        entryOrder.status = 'CLOSED'
        entryOrder.logisticsCode = order.express_code
        entryOrder.expressCode = order.bill_code
        entryOrder.orderType = order.order_type
        # shopCode/shopNick = g.owner.shop_code/g.owner.shop_name

        for line in order.lines:
            ld = DictNone()
            ld.ownerCode = order.owner_code
            ld.itemCode = line.sku
            ld.itemName = line.name
            ld.planQty = line.qty
            ld.inventoryType = line.quality_type
            ld.actualQty = line.qty_real

            orderLines.append(ld)

        return True, {
            'response': {'returnOrder': entryOrder, 'orderLines': orderLines}
        }

    def api_stockout_confirm(self, order):
        deliveryOrder = DictNone()
        orderLines = []

        deliveryOrder.deliveryOrderCode = order.erp_order_code
        deliveryOrder.ownerCode = order.owner_code
        deliveryOrder.warehouseCode = order.warehouse_code
        deliveryOrder.outBizCode = '%s-%s'%(order.order_code, randint(100, 999))
        deliveryOrder.status = 'CLOSED'
        deliveryOrder.logisticsCode = order.express_code
        deliveryOrder.expressCode = order.bill_code
        deliveryOrder.orderType = order.sub_order_type
        # shopCode/shopNick = g.owner.shop_code/g.owner.shop_name

        for line in order.lines:
            ld = DictNone()
            ld.ownerCode = order.owner_code
            ld.itemCode = line.sku
            ld.itemName = line.name
            ld.planQty = line.qty
            ld.inventoryType = line.quality_type
            ld.actualQty = line.qty_ship

            orderLines.append(ld)

        return True, {
            'response': {'deliveryOrder': deliveryOrder, 'orderLines': orderLines}
        }

    def api_deliveryorder_confirm(self, order):
        deliveryOrder = DictNone()
        orderLines = []

        deliveryOrder.deliveryOrderCode = order.erp_order_code
        deliveryOrder.ownerCode = order.owner_code
        deliveryOrder.warehouseCode = order.warehouse_code
        deliveryOrder.outBizCode = '%s-%s'%(order.order_code, randint(100, 999))
        deliveryOrder.status = 'CLOSED'
        deliveryOrder.logisticsCode = order.express_code
        deliveryOrder.expressCode = order.bill_code
        deliveryOrder.orderType = order.sub_order_type
        # shopCode/shopNick = g.owner.shop_code/g.owner.shop_name

        for line in order.lines:
            ld = DictNone()
            ld.ownerCode = order.owner_code
            ld.itemCode = line.sku
            ld.itemName = line.name
            ld.planQty = line.qty
            ld.inventoryType = line.quality_type
            ld.actualQty = line.qty_ship

            orderLines.append(ld)

        return True, {
            'response': {'deliveryOrder': deliveryOrder, 'orderLines': orderLines}
        }


def confirm_order(order_id, inout):
    ok, msg = True, 'ok'
    if inout == 'in':
        order = Stockin.query.with_for_update().get(order_id)
    else:
        order = Stockout.query.with_for_update().get(order_id)

    action = QimenAction(order.company_code)
    try:
        ok, msg = action.do_confirm(order, inout)
    except:
        ok = False
        msg = traceback.format_exc()
    if ok:
        print('confirm order %s ok'%order.order_code)
        db.session.commit()
    else:
        print('confirm order %s error %s'%(order.order_code, msg))
        db.session.rollback()

    return ok, msg

@hueyapp.task()
def async_confirm_order(order_id, inout):
    return confirm_order(order_id, inout)
