# -*- coding: utf-8 -*-

import os
import requests
import time
import json
import base64
import hashlib
from pprint import pprint

"""
doc: http://www.kdniao.com/api-eorder
"""

_actions = {
    # 生成请求数据

    # 电子面单 1007
    "waybill": '1007',
    # 电子面单取消 1147
    "waybill_cancel": '1147',
    # 物流跟踪 1008
    "express_trace": '1008',
    # 即时查询 1002
    "realtime_query": '1002',
    # 单号余量查询 1127 
    "orders_left": '1127',
}

KDNIAO_WAYBILL_URL = os.environ.get('KDNIAO_WAYBILL_URL', 'https://api.kdniao.com/api/EOrderService')

class Kdniao(object):
    def __init__(self, url=None, bid=None, appkey=None, debug=True):
        # 快递鸟接口
        if debug:
            self.url = url or "http://sandboxapi.kdniao.com:8080/kdniaosandbox/gateway/exterfaceInvoke.json"
        else:
            self.url = KDNIAO_WAYBILL_URL
        # kdniaoEbusinessId
        self.bid = bid or "test1598586"
        # 快递鸟appkey
        self.appkey = appkey or "6144940e-5b52-4abd-a2a6-b28876d3c79c"

    def get_curtime(self):
        # 获取当前日期和时间
        return (time.strftime("%Y%m%d"), time.strftime("%H%M%S"))

    def encrypt(self, origin_data):
        # origin_data 由字典转换后的字符串
        # appKey 在快递鸟官网申请的api_key(字符串)
        # 数据内容签名：把(请求内容(未编码)+AppKey)进行MD5加密，然后Base64编码
        m = hashlib.md5()
        m.update((origin_data + self.appkey).encode("utf8"))
        encodestr = m.hexdigest()
        base64_text = base64.b64encode(encodestr.encode(encoding='utf-8'))
        return base64_text

    def set_params(self, req_type, data):
        str_data = json.dumps(data, sort_keys=True)
        data_sign = self.encrypt(str_data)

        params = {
            "RequestData": str_data,
            "EBusinessID": self.bid,
            "RequestType": req_type,
            "DataSign": data_sign.decode(),
            "DataType": "2",
        }

        return params

    def send(self, data):
        # data 请求的数据(字典dict) set_arams的返回值
        """发送post请求"""
        headers = {'content-type': 'application/x-www-form-urlencoded','content-Encoding': 'charset=utf-8'}
        resp = requests.post(self.url, data=data, headers=headers)
        return json.loads(resp.text)

    def do(self, req_type, data):
        req_type = _actions.get(req_type)
        return self.send(self.set_params(req_type, data))


if __name__ == '__main__':
    data= {
            "IsReturnPrintTemplate": 1, # 返回电子面单模板：0-不需要；1-需要
            "Remark": u"小心轻放", 
            "Sender": {                 # 发货人信息
                "Name": "Taylor", 
                "Mobile": "15018442396", 
                "Company": "LV", 
                "CityName": u"上海", 
                "ExpAreaName": u"青浦区", 
                "Address": u"明珠路73号", 
                "ProvinceName": u"上海"
            }, 
            "Commodity": [              # 要快递的东西
                {
                    "GoodsName": u"鞋子",    # R
                    "Goodsquantity": 2, # O
                    "GoodsWeight": 1.0  # O
                }
            ], 
            "ShipperCode": "SF",        # 快递公司
            "Receiver": {               # 收货人谢谢
                "Name": "Yann", 
                "Mobile": "15018442396", 
                "Company": "GCCUI", 
                "CityName": u"北京", 
                "ExpAreaName": u"朝阳区", 
                "Address": u"三里屯街道雅秀大厦", 
                "ProvinceName": u"北京"
            }, 
            "OtherCost": 1.0,           # 其它费用
            "Quantity": 2,              # 包裹数(最多支持30件) 一个包裹对应一个运单号，如果是大于1个包裹，返回则按照子母件的方式返回母运单号和子运单号
            "OrderCode": "012657700387",# 单号, 唯一
            "Weight": 1.0,              # 总重
            "ExpType": 1,               # 快递类型：1-标准快件 ,详细快递类型参考《快递公司快递业务类型.xlsx》    
            "PayType": 1,               # 邮费支付方式:1-现付，2-到付，3-月结，4-第三方支付(仅SF支持)
            "Volume": 0.0,              # 包裹总体积m3 当为快运的订单时必填，不填时快递鸟将根据各个快运公司要求传对应的默认值
            "Cost": 1.0                 # 快递运费
        }

    kdniao = Kdniao()
    ret = kdniao.do('waybill', data)
    # pprint(ret)
    # print(json.dumps(data, ensure_ascii=False, indent=4))
    ret['PrintTemplate'] = "<html></html>"
    print(json.dumps(ret, ensure_ascii=False, indent=4))
    """
    ## 获取面单号 resp
    {
        "Success": true,
        "Order": {
            "ShipperInfo": "{\"Details\":[{\"Detail\":{\"CodingMapping\":\"V12\",\"DestCityCode\":\"020\",\"DestDeptCode\":\"020BC\",\"DestDeptCodeMapping\":\"020WD\",\"DestRouteLabel\":\"020WD-020BC\",\"DestTransferCode\":\"020WD\",\"LogisticCode\":\"252314540522\",\"OriginCityCode\":\"755\",\"OriginDeptCode\":\"755U\",\"OriginTeamCode\":\"105\",\"OriginTransferCode\":\"755WF\",\"PrintFlag\":\"000000000\",\"PrintIcon\":\"00000100\",\"ProCode\":\"T6\",\"TwoDimensionCode\":\"MMM={'k1':'020WD','k2':'020BC','k3':'','k4':'T6','k5':'252314540522','k6':''}\",\"XbFlag\":\"0\"}}]}", 
            "OrderCode": "012657700387",            # 原始单号
            "ShipperCode": "SF", 
            "KDNOrderCode": "KDN20201109093402",    # 快递鸟单号
            "LogisticCode": "252314540522",         # 快递单号
            "OriginCode": "755", 
            "DestinatioCode": "020"
        }, 
        "Reason": "成功", 
        "ResultCode": "100", 
        "EBusinessID": "test1598586", 
        "PrintTemplate": "<html></html>", 
        "UniquerRequestNumber": "d5d4dcea-6ebd-45e6-8c51-d4857adbc87a" # 唯一标识
        "SubOrders": [              # 如果是多包裹, 子单单号
            "547547316150"
        ],
        "SubPrintTemplates": [],    # 如果是多包裹, 子单模板
        "SubCount": 2               # 如果是多包裹, 子单数量
    }

    Order.ShipperInfo:
    {
        "Details": [
            {
                "Detail": {
                    "DestTransferCode": "020WD", 
                    "XbFlag": "0", 
                    "OriginDeptCode": "755U", 
                    "ProCode": "T6", 
                    "OriginTransferCode": "755WF", 
                    "DestCityCode": "020", 
                    "PrintIcon": "00000100", 
                    "CodingMapping": "V12", 
                    "DestDeptCodeMapping": "020WD", 
                    "OriginTeamCode": "105", 
                    "LogisticCode": "252314540522",
                    "OriginCityCode": "755", 
                    "DestRouteLabel": "020WD-020BC", 
                    "DestDeptCode": "020BC", 
                    "PrintFlag": "000000000", 
                    "TwoDimensionCode": "MMM={'k1':'020WD','k2':'020BC','k3':'','k4':'T6','k5':'252314540522','k6':''}"
                }
            }
        ]
    }

    ## 取消面单 req
    {
        ShipperCode String  快递公司编码  R
        OrderCode   String  订单编号    R
        ExpNo   String  快递单号 R
    }

    ## 单号余量 req
    {
        ShipperCode String  快递公司编码  R
        CustomerName    String  电子面单客户号 O
        CustomerPwd String  电子面单密码  O
        StationCode String  网点编码    R
        StationName String  网点名称    R
    }
    ## 单号余量 resp
    {
        EBusinessID String  用户ID    R
        Success Bool    成功与否(true/false)    R
        Reason  String  失败原因    O
        ResultCode  String  返回编码    R
        TotalNum    Int(10) 累计充值数量，电子面单总量(包含已使用/未使用)    O
        AvailableNum    SInt(10)    剩余可用量   O
    }
    { # resp
      "EBusinessID": "1237100",
      "Success": true,
      "Reason": "",
      "ResultCode": "100",
      "EorderBalance": {
        "AvailableNum": 0,
        "TotalNum": 0
      }
    }
    """

