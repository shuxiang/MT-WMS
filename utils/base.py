#coding=utf8


class Dict(dict):
    """A dict that allows for object-like property access syntax."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, val):
        self[name] = val


class DictNone(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            return None

    def __setattr__(self, name, val):
        self[name] = val

# 反向订单类型 出库=>入库
fan_stock_type = {
    # 客户自定义的订单类型 custom; sale 销售出库， produce  生产出库
    # normal 普通出库，　return 退货出库, 销售单协作出库(代工配件出库) coop , 领料 material_pick
    # 维修出库 fix, 报废出库 scrap, borrow 借用出库 , 转移单 transfer 交易单 consign

    # 采购单 purchase ，退货单 return ，转移单 transfer ，交易单 consign, 生产成品入库单 produce, 
    # 自定义 custom, 退料 material_return, 维修入库 fix
    # borrow 借用归还入库, normal 普通入库 , produce_return 生产配料退回
    'custom': 'custom',
    'sale': 'return',
    'normal': 'normal',
    'produce': 'produce_return',
    'return': 'purchase',
    'coop': 'coop',
    'material_pick': 'material_return',
    'fix': 'fix',
    #'scrap': None,
    'borrow': 'borrow',
    'transfer': 'transfer',
    'consign': 'consign',
}


stockin_type = [
    ("SCRK", u"生产入库"), 
    ("LYRK", u"领用入库"), 
    ("CCRK", u"残次品入库"), 
    ("CGRK", u"采购入库"), 
    ("DBRK", u"调拨入库"), 
    ("QTRK", u"其他入库"), 
    ("B2BRK", u"B2B入库"), 
    ("XNRK", u"虚拟入库"),
]
returnin_type = [
    ("THRK", u"退货入库"), 
    ("HHRK", u"换货入库"),
]
stockout_type = [
    ("PTCK", u"普通出库"),
    ("DBCK", u"调拨出库"), 
    ("B2BCK", u"B2B出库"), 
    ("QTCK", u"其他出库"), 
    ("CGTH", u"采购退货出库"), 
    ("XNCK", u"虚拟出库"), 
    ("JITCK", u"唯品出库"),
]
deliveryout_type = [
    ("JYCK", u"交易出库"), 
    ("HHCK", u"换货出库"), 
    ("BFCK", u"补发出库"), 
    ("QTCK", u"其他出库"),
]

in_type = stockin_type+returnin_type
out_type = stockout_type+deliveryout_type

## 物流公司
taobao = [
    ("SF",u"顺丰"),
    ("EMS",u"标准快递"),
    ("EYB",u"经济快件"),
    ("ZJS",u"宅急送"),
    ("YTO",u"圆通 "),
    ("ZTO",u"中通(ZTO)"),
    ("HTKY",u"百世汇通"),
    ("UC",u"优速"),
    ("STO",u"申通"),
    ("TTKDEX",u"天天快递"),
    ("QFKD",u"全峰"),
    ("FAST",u"快捷"),
    ("POSTB",u"邮政小包"),
    ("GTO",u"国通"),
    ("YUNDA",u"韵达"),
    ("JD",u"京东配送"),
    ("DD",u"当当宅配"),
    ("AMAZON",u"亚马逊物流"),
    ("OTHER",u"其他"),
]
kdniao = [
    ("SF",u"顺丰"),
    ("EMS",u"EMS"),
    ("YZPY",u"邮政快递包裹"),  ##
    ("ZTKY",u"中铁快运"),  ##
    ("YZBK",u"邮政国内标快"), ##
    ("UAPEX",u"全一快递"), ##
    ("UC",u"优速"),  
    ("YD",u"韵达"),  #
    ("YTO",u"圆通"),  
    ("YCWL",u"远成"),  ##
    ("ANE",u"安能"),  ##
    ("HTKY",u"百世快递"), 
    ("ZTO",u"中通"),  
    ("STO",u"申通"),  
    ("DBL",u"德邦"),  ##
    ("JD",u"京东"),  
    ("XFEX",u"信丰"),  ##
    ("GTO",u"国通"),  
    ("HHTT",u"天天快递"),  ##
    ("SURE",u"速尔快递"),  ##
    ("PJ",u"品骏快递"), ##
    ("JDKY",u"京东快运"), ##
    ("ANEKY",u"安能快运"), ##
    ("DBLKY",u"德邦快运"),  ##
    ("LB",u"龙邦快运"), ##
    ("ZJS",u"宅急送"),  
]

express_type = [('kdniao', u'快递鸟'), ('taobao', u'淘宝天猫'), ('jd', u'京东'), ('pdd', u'拼多多'), ('other', u'其他')]


ssq = [{
    "value": u"北京市", "label": u"北京市",
    "children": [{
        "value": u"北京市", "label": u"北京市",
        "children": [{
            "value": u"东城区", "label": u"东城区",
        }, {
            "value": u"西城区", "label": u"西城区",
        }, {
            "value": u"朝阳区", "label": u"朝阳区",
        }, {
            "value": u"丰台区", "label": u"丰台区",
        }, {
            "value": u"石景山区", "label": u"石景山区",
        }, {
            "value": u"海淀区", "label": u"海淀区",
        }, {
            "value": u"门头沟区", "label": u"门头沟区",
        }, {
            "value": u"房山区", "label": u"房山区",
        }, {
            "value": u"通州区", "label": u"通州区",
        }, {
            "value": u"顺义区", "label": u"顺义区",
        }, {
            "value": u"昌平区", "label": u"昌平区",
        }, {
            "value": u"大兴区", "label": u"大兴区",
        }, {
            "value": u"怀柔区", "label": u"怀柔区",
        }, {
            "value": u"平谷区", "label": u"平谷区",
        }, {
            "value": u"密云区", "label": u"密云区",
        }, {
            "value": u"延庆区", "label": u"延庆区",
        }]
    }]
    }, {
    "value": u"天津市", "label": u"天津市",
    "children": [{
        "value": u"天津市", "label": u"天津市",
        "children": [{
            "value": u"和平区", "label": u"和平区",
        }, {
            "value": u"河东区", "label": u"河东区",
        }, {
            "value": u"河西区", "label": u"河西区",
        }, {
            "value": u"南开区", "label": u"南开区",
        }, {
            "value": u"河北区", "label": u"河北区",
        }, {
            "value": u"红桥区", "label": u"红桥区",
        }, {
            "value": u"东丽区", "label": u"东丽区",
        }, {
            "value": u"西青区", "label": u"西青区",
        }, {
            "value": u"津南区", "label": u"津南区",
        }, {
            "value": u"北辰区", "label": u"北辰区",
        }, {
            "value": u"武清区", "label": u"武清区",
        }, {
            "value": u"宝坻区", "label": u"宝坻区",
        }, {
            "value": u"滨海新区", "label": u"滨海新区",
        }, {
            "value": u"宁河区", "label": u"宁河区",
        }, {
            "value": u"静海区", "label": u"静海区",
        }, {
            "value": u"蓟州区", "label": u"蓟州区",
        }]
    }]
    }, {
    "value": u"河北省", "label": u"河北省",
    "children": [{
        "value": u"石家庄市", "label": u"石家庄市",
        "children": [{
            "value": u"长安区", "label": u"长安区",
        }, {
            "value": u"桥西区", "label": u"桥西区",
        }, {
            "value": u"新华区", "label": u"新华区",
        }, {
            "value": u"井陉矿区", "label": u"井陉矿区",
        }, {
            "value": u"裕华区", "label": u"裕华区",
        }, {
            "value": u"藁城区", "label": u"藁城区",
        }, {
            "value": u"鹿泉区", "label": u"鹿泉区",
        }, {
            "value": u"栾城区", "label": u"栾城区",
        }, {
            "value": u"井陉县", "label": u"井陉县",
        }, {
            "value": u"正定县", "label": u"正定县",
        }, {
            "value": u"行唐县", "label": u"行唐县",
        }, {
            "value": u"灵寿县", "label": u"灵寿县",
        }, {
            "value": u"高邑县", "label": u"高邑县",
        }, {
            "value": u"深泽县", "label": u"深泽县",
        }, {
            "value": u"赞皇县", "label": u"赞皇县",
        }, {
            "value": u"无极县", "label": u"无极县",
        }, {
            "value": u"平山县", "label": u"平山县",
        }, {
            "value": u"元氏县", "label": u"元氏县",
        }, {
            "value": u"赵县", "label": u"赵县",
        }, {
            "value": u"辛集市", "label": u"辛集市",
        }, {
            "value": u"晋州市", "label": u"晋州市",
        }, {
            "value": u"新乐市", "label": u"新乐市",
        }]
    }, {
        "value": u"唐山市", "label": u"唐山市",
        "children": [{
            "value": u"路南区", "label": u"路南区",
        }, {
            "value": u"路北区", "label": u"路北区",
        }, {
            "value": u"古冶区", "label": u"古冶区",
        }, {
            "value": u"开平区", "label": u"开平区",
        }, {
            "value": u"丰南区", "label": u"丰南区",
        }, {
            "value": u"丰润区", "label": u"丰润区",
        }, {
            "value": u"曹妃甸区", "label": u"曹妃甸区",
        }, {
            "value": u"滦南县", "label": u"滦南县",
        }, {
            "value": u"乐亭县", "label": u"乐亭县",
        }, {
            "value": u"迁西县", "label": u"迁西县",
        }, {
            "value": u"玉田县", "label": u"玉田县",
        }, {
            "value": u"遵化市", "label": u"遵化市",
        }, {
            "value": u"迁安市", "label": u"迁安市",
        }, {
            "value": u"滦州市", "label": u"滦州市",
        }]
    }, {
        "value": u"秦皇岛市", "label": u"秦皇岛市",
        "children": [{
            "value": u"海港区", "label": u"海港区",
        }, {
            "value": u"山海关区", "label": u"山海关区",
        }, {
            "value": u"北戴河区", "label": u"北戴河区",
        }, {
            "value": u"抚宁区", "label": u"抚宁区",
        }, {
            "value": u"青龙满族自治县", "label": u"青龙满族自治县",
        }, {
            "value": u"昌黎县", "label": u"昌黎县",
        }, {
            "value": u"卢龙县", "label": u"卢龙县",
        }, {
            "value": u"经济技术开发区", "label": u"经济技术开发区",
        }]
    }, {
        "value": u"邯郸市", "label": u"邯郸市",
        "children": [{
            "value": u"邯山区", "label": u"邯山区",
        }, {
            "value": u"丛台区", "label": u"丛台区",
        }, {
            "value": u"复兴区", "label": u"复兴区",
        }, {
            "value": u"峰峰矿区", "label": u"峰峰矿区",
        }, {
            "value": u"肥乡区", "label": u"肥乡区",
        }, {
            "value": u"永年区", "label": u"永年区",
        }, {
            "value": u"临漳县", "label": u"临漳县",
        }, {
            "value": u"成安县", "label": u"成安县",
        }, {
            "value": u"大名县", "label": u"大名县",
        }, {
            "value": u"涉县", "label": u"涉县",
        }, {
            "value": u"磁县", "label": u"磁县",
        }, {
            "value": u"邱县", "label": u"邱县",
        }, {
            "value": u"鸡泽县", "label": u"鸡泽县",
        }, {
            "value": u"广平县", "label": u"广平县",
        }, {
            "value": u"馆陶县", "label": u"馆陶县",
        }, {
            "value": u"魏县", "label": u"魏县",
        }, {
            "value": u"曲周县", "label": u"曲周县",
        }, {
            "value": u"武安市", "label": u"武安市",
        }]
    }, {
        "value": u"邢台市", "label": u"邢台市",
        "children": [{
            "value": u"桥东区", "label": u"桥东区",
        }, {
            "value": u"桥西区", "label": u"桥西区",
        }, {
            "value": u"邢台县", "label": u"邢台县",
        }, {
            "value": u"临城县", "label": u"临城县",
        }, {
            "value": u"内丘县", "label": u"内丘县",
        }, {
            "value": u"柏乡县", "label": u"柏乡县",
        }, {
            "value": u"隆尧县", "label": u"隆尧县",
        }, {
            "value": u"任县", "label": u"任县",
        }, {
            "value": u"南和县", "label": u"南和县",
        }, {
            "value": u"宁晋县", "label": u"宁晋县",
        }, {
            "value": u"巨鹿县", "label": u"巨鹿县",
        }, {
            "value": u"新河县", "label": u"新河县",
        }, {
            "value": u"广宗县", "label": u"广宗县",
        }, {
            "value": u"平乡县", "label": u"平乡县",
        }, {
            "value": u"威县", "label": u"威县",
        }, {
            "value": u"清河县", "label": u"清河县",
        }, {
            "value": u"临西县", "label": u"临西县",
        }, {
            "value": u"南宫市", "label": u"南宫市",
        }, {
            "value": u"沙河市", "label": u"沙河市",
        }]
    }, {
        "value": u"保定市", "label": u"保定市",
        "children": [{
            "value": u"竞秀区", "label": u"竞秀区",
        }, {
            "value": u"莲池区", "label": u"莲池区",
        }, {
            "value": u"满城区", "label": u"满城区",
        }, {
            "value": u"清苑区", "label": u"清苑区",
        }, {
            "value": u"徐水区", "label": u"徐水区",
        }, {
            "value": u"涞水县", "label": u"涞水县",
        }, {
            "value": u"阜平县", "label": u"阜平县",
        }, {
            "value": u"定兴县", "label": u"定兴县",
        }, {
            "value": u"唐县", "label": u"唐县",
        }, {
            "value": u"高阳县", "label": u"高阳县",
        }, {
            "value": u"容城县", "label": u"容城县",
        }, {
            "value": u"涞源县", "label": u"涞源县",
        }, {
            "value": u"望都县", "label": u"望都县",
        }, {
            "value": u"安新县", "label": u"安新县",
        }, {
            "value": u"易县", "label": u"易县",
        }, {
            "value": u"曲阳县", "label": u"曲阳县",
        }, {
            "value": u"蠡县", "label": u"蠡县",
        }, {
            "value": u"顺平县", "label": u"顺平县",
        }, {
            "value": u"博野县", "label": u"博野县",
        }, {
            "value": u"雄县", "label": u"雄县",
        }, {
            "value": u"涿州市", "label": u"涿州市",
        }, {
            "value": u"定州市", "label": u"定州市",
        }, {
            "value": u"安国市", "label": u"安国市",
        }, {
            "value": u"高碑店市", "label": u"高碑店市",
        }]
    }, {
        "value": u"张家口市", "label": u"张家口市",
        "children": [{
            "value": u"桥东区", "label": u"桥东区",
        }, {
            "value": u"桥西区", "label": u"桥西区",
        }, {
            "value": u"宣化区", "label": u"宣化区",
        }, {
            "value": u"下花园区", "label": u"下花园区",
        }, {
            "value": u"万全区", "label": u"万全区",
        }, {
            "value": u"崇礼区", "label": u"崇礼区",
        }, {
            "value": u"张北县", "label": u"张北县",
        }, {
            "value": u"康保县", "label": u"康保县",
        }, {
            "value": u"沽源县", "label": u"沽源县",
        }, {
            "value": u"尚义县", "label": u"尚义县",
        }, {
            "value": u"蔚县", "label": u"蔚县",
        }, {
            "value": u"阳原县", "label": u"阳原县",
        }, {
            "value": u"怀安县", "label": u"怀安县",
        }, {
            "value": u"怀来县", "label": u"怀来县",
        }, {
            "value": u"涿鹿县", "label": u"涿鹿县",
        }, {
            "value": u"赤城县", "label": u"赤城县",
        }]
    }, {
        "value": u"承德市", "label": u"承德市",
        "children": [{
            "value": u"双桥区", "label": u"双桥区",
        }, {
            "value": u"双滦区", "label": u"双滦区",
        }, {
            "value": u"鹰手营子矿区", "label": u"鹰手营子矿区",
        }, {
            "value": u"承德县", "label": u"承德县",
        }, {
            "value": u"兴隆县", "label": u"兴隆县",
        }, {
            "value": u"滦平县", "label": u"滦平县",
        }, {
            "value": u"隆化县", "label": u"隆化县",
        }, {
            "value": u"丰宁满族自治县", "label": u"丰宁满族自治县",
        }, {
            "value": u"宽城满族自治县", "label": u"宽城满族自治县",
        }, {
            "value": u"围场满族蒙古族自治县", "label": u"围场满族蒙古族自治县",
        }, {
            "value": u"平泉市", "label": u"平泉市",
        }]
    }, {
        "value": u"沧州市", "label": u"沧州市",
        "children": [{
            "value": u"新华区", "label": u"新华区",
        }, {
            "value": u"运河区", "label": u"运河区",
        }, {
            "value": u"沧县", "label": u"沧县",
        }, {
            "value": u"青县", "label": u"青县",
        }, {
            "value": u"东光县", "label": u"东光县",
        }, {
            "value": u"海兴县", "label": u"海兴县",
        }, {
            "value": u"盐山县", "label": u"盐山县",
        }, {
            "value": u"肃宁县", "label": u"肃宁县",
        }, {
            "value": u"南皮县", "label": u"南皮县",
        }, {
            "value": u"吴桥县", "label": u"吴桥县",
        }, {
            "value": u"献县", "label": u"献县",
        }, {
            "value": u"孟村回族自治县", "label": u"孟村回族自治县",
        }, {
            "value": u"泊头市", "label": u"泊头市",
        }, {
            "value": u"任丘市", "label": u"任丘市",
        }, {
            "value": u"黄骅市", "label": u"黄骅市",
        }, {
            "value": u"河间市", "label": u"河间市",
        }]
    }, {
        "value": u"廊坊市", "label": u"廊坊市",
        "children": [{
            "value": u"安次区", "label": u"安次区",
        }, {
            "value": u"广阳区", "label": u"广阳区",
        }, {
            "value": u"固安县", "label": u"固安县",
        }, {
            "value": u"永清县", "label": u"永清县",
        }, {
            "value": u"香河县", "label": u"香河县",
        }, {
            "value": u"大城县", "label": u"大城县",
        }, {
            "value": u"文安县", "label": u"文安县",
        }, {
            "value": u"大厂回族自治县", "label": u"大厂回族自治县",
        }, {
            "value": u"霸州市", "label": u"霸州市",
        }, {
            "value": u"三河市", "label": u"三河市",
        }, {
            "value": u"开发区", "label": u"开发区",
        }]
    }, {
        "value": u"衡水市", "label": u"衡水市",
        "children": [{
            "value": u"桃城区", "label": u"桃城区",
        }, {
            "value": u"冀州区", "label": u"冀州区",
        }, {
            "value": u"枣强县", "label": u"枣强县",
        }, {
            "value": u"武邑县", "label": u"武邑县",
        }, {
            "value": u"武强县", "label": u"武强县",
        }, {
            "value": u"饶阳县", "label": u"饶阳县",
        }, {
            "value": u"安平县", "label": u"安平县",
        }, {
            "value": u"故城县", "label": u"故城县",
        }, {
            "value": u"景县", "label": u"景县",
        }, {
            "value": u"阜城县", "label": u"阜城县",
        }, {
            "value": u"深州市", "label": u"深州市",
        }]
    }]
    }, {
    "value": u"山西省", "label": u"山西省",
    "children": [{
        "value": u"太原市", "label": u"太原市",
        "children": [{
            "value": u"小店区", "label": u"小店区",
        }, {
            "value": u"迎泽区", "label": u"迎泽区",
        }, {
            "value": u"杏花岭区", "label": u"杏花岭区",
        }, {
            "value": u"尖草坪区", "label": u"尖草坪区",
        }, {
            "value": u"万柏林区", "label": u"万柏林区",
        }, {
            "value": u"晋源区", "label": u"晋源区",
        }, {
            "value": u"清徐县", "label": u"清徐县",
        }, {
            "value": u"阳曲县", "label": u"阳曲县",
        }, {
            "value": u"娄烦县", "label": u"娄烦县",
        }, {
            "value": u"古交市", "label": u"古交市",
        }]
    }, {
        "value": u"大同市", "label": u"大同市",
        "children": [{
            "value": u"新荣区", "label": u"新荣区",
        }, {
            "value": u"平城区", "label": u"平城区",
        }, {
            "value": u"云冈区", "label": u"云冈区",
        }, {
            "value": u"云州区", "label": u"云州区",
        }, {
            "value": u"阳高县", "label": u"阳高县",
        }, {
            "value": u"天镇县", "label": u"天镇县",
        }, {
            "value": u"广灵县", "label": u"广灵县",
        }, {
            "value": u"灵丘县", "label": u"灵丘县",
        }, {
            "value": u"浑源县", "label": u"浑源县",
        }, {
            "value": u"左云县", "label": u"左云县",
        }]
    }, {
        "value": u"阳泉市", "label": u"阳泉市",
        "children": [{
            "value": u"城区", "label": u"城区",
        }, {
            "value": u"矿区", "label": u"矿区",
        }, {
            "value": u"郊区", "label": u"郊区",
        }, {
            "value": u"平定县", "label": u"平定县",
        }, {
            "value": u"盂县", "label": u"盂县",
        }]
    }, {
        "value": u"长治市", "label": u"长治市",
        "children": [{
            "value": u"潞州区", "label": u"潞州区",
        }, {
            "value": u"上党区", "label": u"上党区",
        }, {
            "value": u"屯留区", "label": u"屯留区",
        }, {
            "value": u"潞城区", "label": u"潞城区",
        }, {
            "value": u"襄垣县", "label": u"襄垣县",
        }, {
            "value": u"平顺县", "label": u"平顺县",
        }, {
            "value": u"黎城县", "label": u"黎城县",
        }, {
            "value": u"壶关县", "label": u"壶关县",
        }, {
            "value": u"长子县", "label": u"长子县",
        }, {
            "value": u"武乡县", "label": u"武乡县",
        }, {
            "value": u"沁县", "label": u"沁县",
        }, {
            "value": u"沁源县", "label": u"沁源县",
        }]
    }, {
        "value": u"晋城市", "label": u"晋城市",
        "children": [{
            "value": u"城区", "label": u"城区",
        }, {
            "value": u"沁水县", "label": u"沁水县",
        }, {
            "value": u"阳城县", "label": u"阳城县",
        }, {
            "value": u"陵川县", "label": u"陵川县",
        }, {
            "value": u"泽州县", "label": u"泽州县",
        }, {
            "value": u"高平市", "label": u"高平市",
        }]
    }, {
        "value": u"朔州市", "label": u"朔州市",
        "children": [{
            "value": u"朔城区", "label": u"朔城区",
        }, {
            "value": u"平鲁区", "label": u"平鲁区",
        }, {
            "value": u"山阴县", "label": u"山阴县",
        }, {
            "value": u"应县", "label": u"应县",
        }, {
            "value": u"右玉县", "label": u"右玉县",
        }, {
            "value": u"怀仁市", "label": u"怀仁市",
        }]
    }, {
        "value": u"晋中市", "label": u"晋中市",
        "children": [{
            "value": u"榆次区", "label": u"榆次区",
        }, {
            "value": u"榆社县", "label": u"榆社县",
        }, {
            "value": u"左权县", "label": u"左权县",
        }, {
            "value": u"和顺县", "label": u"和顺县",
        }, {
            "value": u"昔阳县", "label": u"昔阳县",
        }, {
            "value": u"寿阳县", "label": u"寿阳县",
        }, {
            "value": u"太谷县", "label": u"太谷县",
        }, {
            "value": u"祁县", "label": u"祁县",
        }, {
            "value": u"平遥县", "label": u"平遥县",
        }, {
            "value": u"灵石县", "label": u"灵石县",
        }, {
            "value": u"介休市", "label": u"介休市",
        }]
    }, {
        "value": u"运城市", "label": u"运城市",
        "children": [{
            "value": u"盐湖区", "label": u"盐湖区",
        }, {
            "value": u"临猗县", "label": u"临猗县",
        }, {
            "value": u"万荣县", "label": u"万荣县",
        }, {
            "value": u"闻喜县", "label": u"闻喜县",
        }, {
            "value": u"稷山县", "label": u"稷山县",
        }, {
            "value": u"新绛县", "label": u"新绛县",
        }, {
            "value": u"绛县", "label": u"绛县",
        }, {
            "value": u"垣曲县", "label": u"垣曲县",
        }, {
            "value": u"夏县", "label": u"夏县",
        }, {
            "value": u"平陆县", "label": u"平陆县",
        }, {
            "value": u"芮城县", "label": u"芮城县",
        }, {
            "value": u"永济市", "label": u"永济市",
        }, {
            "value": u"河津市", "label": u"河津市",
        }]
    }, {
        "value": u"忻州市", "label": u"忻州市",
        "children": [{
            "value": u"忻府区", "label": u"忻府区",
        }, {
            "value": u"定襄县", "label": u"定襄县",
        }, {
            "value": u"五台县", "label": u"五台县",
        }, {
            "value": u"代县", "label": u"代县",
        }, {
            "value": u"繁峙县", "label": u"繁峙县",
        }, {
            "value": u"宁武县", "label": u"宁武县",
        }, {
            "value": u"静乐县", "label": u"静乐县",
        }, {
            "value": u"神池县", "label": u"神池县",
        }, {
            "value": u"五寨县", "label": u"五寨县",
        }, {
            "value": u"岢岚县", "label": u"岢岚县",
        }, {
            "value": u"河曲县", "label": u"河曲县",
        }, {
            "value": u"保德县", "label": u"保德县",
        }, {
            "value": u"偏关县", "label": u"偏关县",
        }, {
            "value": u"原平市", "label": u"原平市",
        }]
    }, {
        "value": u"临汾市", "label": u"临汾市",
        "children": [{
            "value": u"尧都区", "label": u"尧都区",
        }, {
            "value": u"曲沃县", "label": u"曲沃县",
        }, {
            "value": u"翼城县", "label": u"翼城县",
        }, {
            "value": u"襄汾县", "label": u"襄汾县",
        }, {
            "value": u"洪洞县", "label": u"洪洞县",
        }, {
            "value": u"古县", "label": u"古县",
        }, {
            "value": u"安泽县", "label": u"安泽县",
        }, {
            "value": u"浮山县", "label": u"浮山县",
        }, {
            "value": u"吉县", "label": u"吉县",
        }, {
            "value": u"乡宁县", "label": u"乡宁县",
        }, {
            "value": u"大宁县", "label": u"大宁县",
        }, {
            "value": u"隰县", "label": u"隰县",
        }, {
            "value": u"永和县", "label": u"永和县",
        }, {
            "value": u"蒲县", "label": u"蒲县",
        }, {
            "value": u"汾西县", "label": u"汾西县",
        }, {
            "value": u"侯马市", "label": u"侯马市",
        }, {
            "value": u"霍州市", "label": u"霍州市",
        }]
    }, {
        "value": u"吕梁市", "label": u"吕梁市",
        "children": [{
            "value": u"离石区", "label": u"离石区",
        }, {
            "value": u"文水县", "label": u"文水县",
        }, {
            "value": u"交城县", "label": u"交城县",
        }, {
            "value": u"兴县", "label": u"兴县",
        }, {
            "value": u"临县", "label": u"临县",
        }, {
            "value": u"柳林县", "label": u"柳林县",
        }, {
            "value": u"石楼县", "label": u"石楼县",
        }, {
            "value": u"岚县", "label": u"岚县",
        }, {
            "value": u"方山县", "label": u"方山县",
        }, {
            "value": u"中阳县", "label": u"中阳县",
        }, {
            "value": u"交口县", "label": u"交口县",
        }, {
            "value": u"孝义市", "label": u"孝义市",
        }, {
            "value": u"汾阳市", "label": u"汾阳市",
        }]
    }]
    }, {
    "value": u"内蒙古自治区", "label": u"内蒙古自治区",
    "children": [{
        "value": u"呼和浩特市", "label": u"呼和浩特市",
        "children": [{
            "value": u"新城区", "label": u"新城区",
        }, {
            "value": u"回民区", "label": u"回民区",
        }, {
            "value": u"玉泉区", "label": u"玉泉区",
        }, {
            "value": u"赛罕区", "label": u"赛罕区",
        }, {
            "value": u"土默特左旗", "label": u"土默特左旗",
        }, {
            "value": u"托克托县", "label": u"托克托县",
        }, {
            "value": u"和林格尔县", "label": u"和林格尔县",
        }, {
            "value": u"清水河县", "label": u"清水河县",
        }, {
            "value": u"武川县", "label": u"武川县",
        }]
    }, {
        "value": u"包头市", "label": u"包头市",
        "children": [{
            "value": u"东河区", "label": u"东河区",
        }, {
            "value": u"昆都仑区", "label": u"昆都仑区",
        }, {
            "value": u"青山区", "label": u"青山区",
        }, {
            "value": u"石拐区", "label": u"石拐区",
        }, {
            "value": u"白云鄂博矿区", "label": u"白云鄂博矿区",
        }, {
            "value": u"九原区", "label": u"九原区",
        }, {
            "value": u"土默特右旗", "label": u"土默特右旗",
        }, {
            "value": u"固阳县", "label": u"固阳县",
        }, {
            "value": u"达尔罕茂明安联合旗", "label": u"达尔罕茂明安联合旗",
        }]
    }, {
        "value": u"乌海市", "label": u"乌海市",
        "children": [{
            "value": u"海勃湾区", "label": u"海勃湾区",
        }, {
            "value": u"海南区", "label": u"海南区",
        }, {
            "value": u"乌达区", "label": u"乌达区",
        }]
    }, {
        "value": u"赤峰市", "label": u"赤峰市",
        "children": [{
            "value": u"红山区", "label": u"红山区",
        }, {
            "value": u"元宝山区", "label": u"元宝山区",
        }, {
            "value": u"松山区", "label": u"松山区",
        }, {
            "value": u"阿鲁科尔沁旗", "label": u"阿鲁科尔沁旗",
        }, {
            "value": u"巴林左旗", "label": u"巴林左旗",
        }, {
            "value": u"巴林右旗", "label": u"巴林右旗",
        }, {
            "value": u"林西县", "label": u"林西县",
        }, {
            "value": u"克什克腾旗", "label": u"克什克腾旗",
        }, {
            "value": u"翁牛特旗", "label": u"翁牛特旗",
        }, {
            "value": u"喀喇沁旗", "label": u"喀喇沁旗",
        }, {
            "value": u"宁城县", "label": u"宁城县",
        }, {
            "value": u"敖汉旗", "label": u"敖汉旗",
        }]
    }, {
        "value": u"通辽市", "label": u"通辽市",
        "children": [{
            "value": u"科尔沁区", "label": u"科尔沁区",
        }, {
            "value": u"科尔沁左翼中旗", "label": u"科尔沁左翼中旗",
        }, {
            "value": u"科尔沁左翼后旗", "label": u"科尔沁左翼后旗",
        }, {
            "value": u"开鲁县", "label": u"开鲁县",
        }, {
            "value": u"库伦旗", "label": u"库伦旗",
        }, {
            "value": u"奈曼旗", "label": u"奈曼旗",
        }, {
            "value": u"扎鲁特旗", "label": u"扎鲁特旗",
        }, {
            "value": u"霍林郭勒市", "label": u"霍林郭勒市",
        }]
    }, {
        "value": u"鄂尔多斯市", "label": u"鄂尔多斯市",
        "children": [{
            "value": u"东胜区", "label": u"东胜区",
        }, {
            "value": u"康巴什区", "label": u"康巴什区",
        }, {
            "value": u"达拉特旗", "label": u"达拉特旗",
        }, {
            "value": u"准格尔旗", "label": u"准格尔旗",
        }, {
            "value": u"鄂托克前旗", "label": u"鄂托克前旗",
        }, {
            "value": u"鄂托克旗", "label": u"鄂托克旗",
        }, {
            "value": u"杭锦旗", "label": u"杭锦旗",
        }, {
            "value": u"乌审旗", "label": u"乌审旗",
        }, {
            "value": u"伊金霍洛旗", "label": u"伊金霍洛旗",
        }]
    }, {
        "value": u"呼伦贝尔市", "label": u"呼伦贝尔市",
        "children": [{
            "value": u"海拉尔区", "label": u"海拉尔区",
        }, {
            "value": u"扎赉诺尔区", "label": u"扎赉诺尔区",
        }, {
            "value": u"阿荣旗", "label": u"阿荣旗",
        }, {
            "value": u"莫力达瓦达斡尔族自治旗", "label": u"莫力达瓦达斡尔族自治旗",
        }, {
            "value": u"鄂伦春自治旗", "label": u"鄂伦春自治旗",
        }, {
            "value": u"鄂温克族自治旗", "label": u"鄂温克族自治旗",
        }, {
            "value": u"陈巴尔虎旗", "label": u"陈巴尔虎旗",
        }, {
            "value": u"新巴尔虎左旗", "label": u"新巴尔虎左旗",
        }, {
            "value": u"新巴尔虎右旗", "label": u"新巴尔虎右旗",
        }, {
            "value": u"满洲里市", "label": u"满洲里市",
        }, {
            "value": u"牙克石市", "label": u"牙克石市",
        }, {
            "value": u"扎兰屯市", "label": u"扎兰屯市",
        }, {
            "value": u"额尔古纳市", "label": u"额尔古纳市",
        }, {
            "value": u"根河市", "label": u"根河市",
        }]
    }, {
        "value": u"巴彦淖尔市", "label": u"巴彦淖尔市",
        "children": [{
            "value": u"临河区", "label": u"临河区",
        }, {
            "value": u"五原县", "label": u"五原县",
        }, {
            "value": u"磴口县", "label": u"磴口县",
        }, {
            "value": u"乌拉特前旗", "label": u"乌拉特前旗",
        }, {
            "value": u"乌拉特中旗", "label": u"乌拉特中旗",
        }, {
            "value": u"乌拉特后旗", "label": u"乌拉特后旗",
        }, {
            "value": u"杭锦后旗", "label": u"杭锦后旗",
        }]
    }, {
        "value": u"乌兰察布市", "label": u"乌兰察布市",
        "children": [{
            "value": u"集宁区", "label": u"集宁区",
        }, {
            "value": u"卓资县", "label": u"卓资县",
        }, {
            "value": u"化德县", "label": u"化德县",
        }, {
            "value": u"商都县", "label": u"商都县",
        }, {
            "value": u"兴和县", "label": u"兴和县",
        }, {
            "value": u"凉城县", "label": u"凉城县",
        }, {
            "value": u"察哈尔右翼前旗", "label": u"察哈尔右翼前旗",
        }, {
            "value": u"察哈尔右翼中旗", "label": u"察哈尔右翼中旗",
        }, {
            "value": u"察哈尔右翼后旗", "label": u"察哈尔右翼后旗",
        }, {
            "value": u"四子王旗", "label": u"四子王旗",
        }, {
            "value": u"丰镇市", "label": u"丰镇市",
        }]
    }, {
        "value": u"兴安盟", "label": u"兴安盟",
        "children": [{
            "value": u"乌兰浩特市", "label": u"乌兰浩特市",
        }, {
            "value": u"阿尔山市", "label": u"阿尔山市",
        }, {
            "value": u"科尔沁右翼前旗", "label": u"科尔沁右翼前旗",
        }, {
            "value": u"科尔沁右翼中旗", "label": u"科尔沁右翼中旗",
        }, {
            "value": u"扎赉特旗", "label": u"扎赉特旗",
        }, {
            "value": u"突泉县", "label": u"突泉县",
        }]
    }, {
        "value": u"锡林郭勒盟", "label": u"锡林郭勒盟",
        "children": [{
            "value": u"二连浩特市", "label": u"二连浩特市",
        }, {
            "value": u"锡林浩特市", "label": u"锡林浩特市",
        }, {
            "value": u"阿巴嘎旗", "label": u"阿巴嘎旗",
        }, {
            "value": u"苏尼特左旗", "label": u"苏尼特左旗",
        }, {
            "value": u"苏尼特右旗", "label": u"苏尼特右旗",
        }, {
            "value": u"东乌珠穆沁旗", "label": u"东乌珠穆沁旗",
        }, {
            "value": u"西乌珠穆沁旗", "label": u"西乌珠穆沁旗",
        }, {
            "value": u"太仆寺旗", "label": u"太仆寺旗",
        }, {
            "value": u"镶黄旗", "label": u"镶黄旗",
        }, {
            "value": u"正镶白旗", "label": u"正镶白旗",
        }, {
            "value": u"正蓝旗", "label": u"正蓝旗",
        }, {
            "value": u"多伦县", "label": u"多伦县",
        }]
    }, {
        "value": u"阿拉善盟", "label": u"阿拉善盟",
        "children": [{
            "value": u"阿拉善左旗", "label": u"阿拉善左旗",
        }, {
            "value": u"阿拉善右旗", "label": u"阿拉善右旗",
        }, {
            "value": u"额济纳旗", "label": u"额济纳旗",
        }]
    }]
    }, {
    "value": u"辽宁省", "label": u"辽宁省",
    "children": [{
        "value": u"沈阳市", "label": u"沈阳市",
        "children": [{
            "value": u"和平区", "label": u"和平区",
        }, {
            "value": u"沈河区", "label": u"沈河区",
        }, {
            "value": u"大东区", "label": u"大东区",
        }, {
            "value": u"皇姑区", "label": u"皇姑区",
        }, {
            "value": u"铁西区", "label": u"铁西区",
        }, {
            "value": u"苏家屯区", "label": u"苏家屯区",
        }, {
            "value": u"浑南区", "label": u"浑南区",
        }, {
            "value": u"沈北新区", "label": u"沈北新区",
        }, {
            "value": u"于洪区", "label": u"于洪区",
        }, {
            "value": u"辽中区", "label": u"辽中区",
        }, {
            "value": u"康平县", "label": u"康平县",
        }, {
            "value": u"法库县", "label": u"法库县",
        }, {
            "value": u"新民市", "label": u"新民市",
        }, {
            "value": u"经济技术开发区", "label": u"经济技术开发区",
        }]
    }, {
        "value": u"大连市", "label": u"大连市",
        "children": [{
            "value": u"中山区", "label": u"中山区",
        }, {
            "value": u"西岗区", "label": u"西岗区",
        }, {
            "value": u"沙河口区", "label": u"沙河口区",
        }, {
            "value": u"甘井子区", "label": u"甘井子区",
        }, {
            "value": u"旅顺口区", "label": u"旅顺口区",
        }, {
            "value": u"金州区", "label": u"金州区",
        }, {
            "value": u"普兰店区", "label": u"普兰店区",
        }, {
            "value": u"长海县", "label": u"长海县",
        }, {
            "value": u"瓦房店市", "label": u"瓦房店市",
        }, {
            "value": u"庄河市", "label": u"庄河市",
        }]
    }, {
        "value": u"鞍山市", "label": u"鞍山市",
        "children": [{
            "value": u"铁东区", "label": u"铁东区",
        }, {
            "value": u"铁西区", "label": u"铁西区",
        }, {
            "value": u"立山区", "label": u"立山区",
        }, {
            "value": u"千山区", "label": u"千山区",
        }, {
            "value": u"台安县", "label": u"台安县",
        }, {
            "value": u"岫岩满族自治县", "label": u"岫岩满族自治县",
        }, {
            "value": u"海城市", "label": u"海城市",
        }, {
            "value": u"高新区", "label": u"高新区",
        }]
    }, {
        "value": u"抚顺市", "label": u"抚顺市",
        "children": [{
            "value": u"新抚区", "label": u"新抚区",
        }, {
            "value": u"东洲区", "label": u"东洲区",
        }, {
            "value": u"望花区", "label": u"望花区",
        }, {
            "value": u"顺城区", "label": u"顺城区",
        }, {
            "value": u"抚顺县", "label": u"抚顺县",
        }, {
            "value": u"新宾满族自治县", "label": u"新宾满族自治县",
        }, {
            "value": u"清原满族自治县", "label": u"清原满族自治县",
        }]
    }, {
        "value": u"本溪市", "label": u"本溪市",
        "children": [{
            "value": u"平山区", "label": u"平山区",
        }, {
            "value": u"溪湖区", "label": u"溪湖区",
        }, {
            "value": u"明山区", "label": u"明山区",
        }, {
            "value": u"南芬区", "label": u"南芬区",
        }, {
            "value": u"本溪满族自治县", "label": u"本溪满族自治县",
        }, {
            "value": u"桓仁满族自治县", "label": u"桓仁满族自治县",
        }]
    }, {
        "value": u"丹东市", "label": u"丹东市",
        "children": [{
            "value": u"元宝区", "label": u"元宝区",
        }, {
            "value": u"振兴区", "label": u"振兴区",
        }, {
            "value": u"振安区", "label": u"振安区",
        }, {
            "value": u"宽甸满族自治县", "label": u"宽甸满族自治县",
        }, {
            "value": u"东港市", "label": u"东港市",
        }, {
            "value": u"凤城市", "label": u"凤城市",
        }]
    }, {
        "value": u"锦州市", "label": u"锦州市",
        "children": [{
            "value": u"古塔区", "label": u"古塔区",
        }, {
            "value": u"凌河区", "label": u"凌河区",
        }, {
            "value": u"太和区", "label": u"太和区",
        }, {
            "value": u"黑山县", "label": u"黑山县",
        }, {
            "value": u"义县", "label": u"义县",
        }, {
            "value": u"凌海市", "label": u"凌海市",
        }, {
            "value": u"北镇市", "label": u"北镇市",
        }, {
            "value": u"经济技术开发区", "label": u"经济技术开发区",
        }]
    }, {
        "value": u"营口市", "label": u"营口市",
        "children": [{
            "value": u"站前区", "label": u"站前区",
        }, {
            "value": u"西市区", "label": u"西市区",
        }, {
            "value": u"鲅鱼圈区", "label": u"鲅鱼圈区",
        }, {
            "value": u"老边区", "label": u"老边区",
        }, {
            "value": u"盖州市", "label": u"盖州市",
        }, {
            "value": u"大石桥市", "label": u"大石桥市",
        }]
    }, {
        "value": u"阜新市", "label": u"阜新市",
        "children": [{
            "value": u"海州区", "label": u"海州区",
        }, {
            "value": u"新邱区", "label": u"新邱区",
        }, {
            "value": u"太平区", "label": u"太平区",
        }, {
            "value": u"清河门区", "label": u"清河门区",
        }, {
            "value": u"细河区", "label": u"细河区",
        }, {
            "value": u"阜新蒙古族自治县", "label": u"阜新蒙古族自治县",
        }, {
            "value": u"彰武县", "label": u"彰武县",
        }]
    }, {
        "value": u"辽阳市", "label": u"辽阳市",
        "children": [{
            "value": u"白塔区", "label": u"白塔区",
        }, {
            "value": u"文圣区", "label": u"文圣区",
        }, {
            "value": u"宏伟区", "label": u"宏伟区",
        }, {
            "value": u"弓长岭区", "label": u"弓长岭区",
        }, {
            "value": u"太子河区", "label": u"太子河区",
        }, {
            "value": u"辽阳县", "label": u"辽阳县",
        }, {
            "value": u"灯塔市", "label": u"灯塔市",
        }]
    }, {
        "value": u"盘锦市", "label": u"盘锦市",
        "children": [{
            "value": u"双台子区", "label": u"双台子区",
        }, {
            "value": u"兴隆台区", "label": u"兴隆台区",
        }, {
            "value": u"大洼区", "label": u"大洼区",
        }, {
            "value": u"盘山县", "label": u"盘山县",
        }]
    }, {
        "value": u"铁岭市", "label": u"铁岭市",
        "children": [{
            "value": u"银州区", "label": u"银州区",
        }, {
            "value": u"清河区", "label": u"清河区",
        }, {
            "value": u"铁岭县", "label": u"铁岭县",
        }, {
            "value": u"西丰县", "label": u"西丰县",
        }, {
            "value": u"昌图县", "label": u"昌图县",
        }, {
            "value": u"调兵山市", "label": u"调兵山市",
        }, {
            "value": u"开原市", "label": u"开原市",
        }]
    }, {
        "value": u"朝阳市", "label": u"朝阳市",
        "children": [{
            "value": u"双塔区", "label": u"双塔区",
        }, {
            "value": u"龙城区", "label": u"龙城区",
        }, {
            "value": u"朝阳县", "label": u"朝阳县",
        }, {
            "value": u"建平县", "label": u"建平县",
        }, {
            "value": u"喀喇沁左翼蒙古族自治县", "label": u"喀喇沁左翼蒙古族自治县",
        }, {
            "value": u"北票市", "label": u"北票市",
        }, {
            "value": u"凌源市", "label": u"凌源市",
        }]
    }, {
        "value": u"葫芦岛市", "label": u"葫芦岛市",
        "children": [{
            "value": u"连山区", "label": u"连山区",
        }, {
            "value": u"龙港区", "label": u"龙港区",
        }, {
            "value": u"南票区", "label": u"南票区",
        }, {
            "value": u"绥中县", "label": u"绥中县",
        }, {
            "value": u"建昌县", "label": u"建昌县",
        }, {
            "value": u"兴城市", "label": u"兴城市",
        }]
    }]
    }, {
    "value": u"吉林省", "label": u"吉林省",
    "children": [{
        "value": u"长春市", "label": u"长春市",
        "children": [{
            "value": u"南关区", "label": u"南关区",
        }, {
            "value": u"宽城区", "label": u"宽城区",
        }, {
            "value": u"朝阳区", "label": u"朝阳区",
        }, {
            "value": u"二道区", "label": u"二道区",
        }, {
            "value": u"绿园区", "label": u"绿园区",
        }, {
            "value": u"双阳区", "label": u"双阳区",
        }, {
            "value": u"九台区", "label": u"九台区",
        }, {
            "value": u"农安县", "label": u"农安县",
        }, {
            "value": u"榆树市", "label": u"榆树市",
        }, {
            "value": u"德惠市", "label": u"德惠市",
        }, {
            "value": u"经济技术开发区", "label": u"经济技术开发区",
        }]
    }, {
        "value": u"吉林市", "label": u"吉林市",
        "children": [{
            "value": u"昌邑区", "label": u"昌邑区",
        }, {
            "value": u"龙潭区", "label": u"龙潭区",
        }, {
            "value": u"船营区", "label": u"船营区",
        }, {
            "value": u"丰满区", "label": u"丰满区",
        }, {
            "value": u"永吉县", "label": u"永吉县",
        }, {
            "value": u"蛟河市", "label": u"蛟河市",
        }, {
            "value": u"桦甸市", "label": u"桦甸市",
        }, {
            "value": u"舒兰市", "label": u"舒兰市",
        }, {
            "value": u"磐石市", "label": u"磐石市",
        }]
    }, {
        "value": u"四平市", "label": u"四平市",
        "children": [{
            "value": u"铁西区", "label": u"铁西区",
        }, {
            "value": u"铁东区", "label": u"铁东区",
        }, {
            "value": u"梨树县", "label": u"梨树县",
        }, {
            "value": u"伊通满族自治县", "label": u"伊通满族自治县",
        }, {
            "value": u"公主岭市", "label": u"公主岭市",
        }, {
            "value": u"双辽市", "label": u"双辽市",
        }]
    }, {
        "value": u"辽源市", "label": u"辽源市",
        "children": [{
            "value": u"龙山区", "label": u"龙山区",
        }, {
            "value": u"西安区", "label": u"西安区",
        }, {
            "value": u"东丰县", "label": u"东丰县",
        }, {
            "value": u"东辽县", "label": u"东辽县",
        }]
    }, {
        "value": u"通化市", "label": u"通化市",
        "children": [{
            "value": u"东昌区", "label": u"东昌区",
        }, {
            "value": u"二道江区", "label": u"二道江区",
        }, {
            "value": u"通化县", "label": u"通化县",
        }, {
            "value": u"辉南县", "label": u"辉南县",
        }, {
            "value": u"柳河县", "label": u"柳河县",
        }, {
            "value": u"梅河口市", "label": u"梅河口市",
        }, {
            "value": u"集安市", "label": u"集安市",
        }]
    }, {
        "value": u"白山市", "label": u"白山市",
        "children": [{
            "value": u"浑江区", "label": u"浑江区",
        }, {
            "value": u"江源区", "label": u"江源区",
        }, {
            "value": u"抚松县", "label": u"抚松县",
        }, {
            "value": u"靖宇县", "label": u"靖宇县",
        }, {
            "value": u"长白朝鲜族自治县", "label": u"长白朝鲜族自治县",
        }, {
            "value": u"临江市", "label": u"临江市",
        }]
    }, {
        "value": u"松原市", "label": u"松原市",
        "children": [{
            "value": u"宁江区", "label": u"宁江区",
        }, {
            "value": u"前郭尔罗斯蒙古族自治县", "label": u"前郭尔罗斯蒙古族自治县",
        }, {
            "value": u"长岭县", "label": u"长岭县",
        }, {
            "value": u"乾安县", "label": u"乾安县",
        }, {
            "value": u"扶余市", "label": u"扶余市",
        }]
    }, {
        "value": u"白城市", "label": u"白城市",
        "children": [{
            "value": u"洮北区", "label": u"洮北区",
        }, {
            "value": u"镇赉县", "label": u"镇赉县",
        }, {
            "value": u"通榆县", "label": u"通榆县",
        }, {
            "value": u"洮南市", "label": u"洮南市",
        }, {
            "value": u"大安市", "label": u"大安市",
        }]
    }, {
        "value": u"延边朝鲜族自治州", "label": u"延边朝鲜族自治州",
        "children": [{
            "value": u"延吉市", "label": u"延吉市",
        }, {
            "value": u"图们市", "label": u"图们市",
        }, {
            "value": u"敦化市", "label": u"敦化市",
        }, {
            "value": u"珲春市", "label": u"珲春市",
        }, {
            "value": u"龙井市", "label": u"龙井市",
        }, {
            "value": u"和龙市", "label": u"和龙市",
        }, {
            "value": u"汪清县", "label": u"汪清县",
        }, {
            "value": u"安图县", "label": u"安图县",
        }]
    }]
    }, {
    "value": u"黑龙江省", "label": u"黑龙江省",
    "children": [{
        "value": u"哈尔滨市", "label": u"哈尔滨市",
        "children": [{
            "value": u"道里区", "label": u"道里区",
        }, {
            "value": u"南岗区", "label": u"南岗区",
        }, {
            "value": u"道外区", "label": u"道外区",
        }, {
            "value": u"平房区", "label": u"平房区",
        }, {
            "value": u"松北区", "label": u"松北区",
        }, {
            "value": u"香坊区", "label": u"香坊区",
        }, {
            "value": u"呼兰区", "label": u"呼兰区",
        }, {
            "value": u"阿城区", "label": u"阿城区",
        }, {
            "value": u"双城区", "label": u"双城区",
        }, {
            "value": u"依兰县", "label": u"依兰县",
        }, {
            "value": u"方正县", "label": u"方正县",
        }, {
            "value": u"宾县", "label": u"宾县",
        }, {
            "value": u"巴彦县", "label": u"巴彦县",
        }, {
            "value": u"木兰县", "label": u"木兰县",
        }, {
            "value": u"通河县", "label": u"通河县",
        }, {
            "value": u"延寿县", "label": u"延寿县",
        }, {
            "value": u"尚志市", "label": u"尚志市",
        }, {
            "value": u"五常市", "label": u"五常市",
        }]
    }, {
        "value": u"齐齐哈尔市", "label": u"齐齐哈尔市",
        "children": [{
            "value": u"龙沙区", "label": u"龙沙区",
        }, {
            "value": u"建华区", "label": u"建华区",
        }, {
            "value": u"铁锋区", "label": u"铁锋区",
        }, {
            "value": u"昂昂溪区", "label": u"昂昂溪区",
        }, {
            "value": u"富拉尔基区", "label": u"富拉尔基区",
        }, {
            "value": u"碾子山区", "label": u"碾子山区",
        }, {
            "value": u"梅里斯达斡尔族区", "label": u"梅里斯达斡尔族区",
        }, {
            "value": u"龙江县", "label": u"龙江县",
        }, {
            "value": u"依安县", "label": u"依安县",
        }, {
            "value": u"泰来县", "label": u"泰来县",
        }, {
            "value": u"甘南县", "label": u"甘南县",
        }, {
            "value": u"富裕县", "label": u"富裕县",
        }, {
            "value": u"克山县", "label": u"克山县",
        }, {
            "value": u"克东县", "label": u"克东县",
        }, {
            "value": u"拜泉县", "label": u"拜泉县",
        }, {
            "value": u"讷河市", "label": u"讷河市",
        }]
    }, {
        "value": u"鸡西市", "label": u"鸡西市",
        "children": [{
            "value": u"鸡冠区", "label": u"鸡冠区",
        }, {
            "value": u"恒山区", "label": u"恒山区",
        }, {
            "value": u"滴道区", "label": u"滴道区",
        }, {
            "value": u"梨树区", "label": u"梨树区",
        }, {
            "value": u"城子河区", "label": u"城子河区",
        }, {
            "value": u"麻山区", "label": u"麻山区",
        }, {
            "value": u"鸡东县", "label": u"鸡东县",
        }, {
            "value": u"虎林市", "label": u"虎林市",
        }, {
            "value": u"密山市", "label": u"密山市",
        }]
    }, {
        "value": u"鹤岗市", "label": u"鹤岗市",
        "children": [{
            "value": u"向阳区", "label": u"向阳区",
        }, {
            "value": u"工农区", "label": u"工农区",
        }, {
            "value": u"南山区", "label": u"南山区",
        }, {
            "value": u"兴安区", "label": u"兴安区",
        }, {
            "value": u"东山区", "label": u"东山区",
        }, {
            "value": u"兴山区", "label": u"兴山区",
        }, {
            "value": u"萝北县", "label": u"萝北县",
        }, {
            "value": u"绥滨县", "label": u"绥滨县",
        }]
    }, {
        "value": u"双鸭山市", "label": u"双鸭山市",
        "children": [{
            "value": u"尖山区", "label": u"尖山区",
        }, {
            "value": u"岭东区", "label": u"岭东区",
        }, {
            "value": u"四方台区", "label": u"四方台区",
        }, {
            "value": u"宝山区", "label": u"宝山区",
        }, {
            "value": u"集贤县", "label": u"集贤县",
        }, {
            "value": u"友谊县", "label": u"友谊县",
        }, {
            "value": u"宝清县", "label": u"宝清县",
        }, {
            "value": u"饶河县", "label": u"饶河县",
        }]
    }, {
        "value": u"大庆市", "label": u"大庆市",
        "children": [{
            "value": u"萨尔图区", "label": u"萨尔图区",
        }, {
            "value": u"龙凤区", "label": u"龙凤区",
        }, {
            "value": u"让胡路区", "label": u"让胡路区",
        }, {
            "value": u"红岗区", "label": u"红岗区",
        }, {
            "value": u"大同区", "label": u"大同区",
        }, {
            "value": u"肇州县", "label": u"肇州县",
        }, {
            "value": u"肇源县", "label": u"肇源县",
        }, {
            "value": u"林甸县", "label": u"林甸县",
        }, {
            "value": u"杜尔伯特蒙古族自治县", "label": u"杜尔伯特蒙古族自治县",
        }]
    }, {
        "value": u"伊春市", "label": u"伊春市",
        "children": [{
            "value": u"伊春区", "label": u"伊春区",
        }, {
            "value": u"南岔区", "label": u"南岔区",
        }, {
            "value": u"友好区", "label": u"友好区",
        }, {
            "value": u"西林区", "label": u"西林区",
        }, {
            "value": u"翠峦区", "label": u"翠峦区",
        }, {
            "value": u"新青区", "label": u"新青区",
        }, {
            "value": u"美溪区", "label": u"美溪区",
        }, {
            "value": u"金山屯区", "label": u"金山屯区",
        }, {
            "value": u"五营区", "label": u"五营区",
        }, {
            "value": u"乌马河区", "label": u"乌马河区",
        }, {
            "value": u"汤旺河区", "label": u"汤旺河区",
        }, {
            "value": u"带岭区", "label": u"带岭区",
        }, {
            "value": u"乌伊岭区", "label": u"乌伊岭区",
        }, {
            "value": u"红星区", "label": u"红星区",
        }, {
            "value": u"上甘岭区", "label": u"上甘岭区",
        }, {
            "value": u"嘉荫县", "label": u"嘉荫县",
        }, {
            "value": u"铁力市", "label": u"铁力市",
        }]
    }, {
        "value": u"佳木斯市", "label": u"佳木斯市",
        "children": [{
            "value": u"向阳区", "label": u"向阳区",
        }, {
            "value": u"前进区", "label": u"前进区",
        }, {
            "value": u"东风区", "label": u"东风区",
        }, {
            "value": u"郊区", "label": u"郊区",
        }, {
            "value": u"桦南县", "label": u"桦南县",
        }, {
            "value": u"桦川县", "label": u"桦川县",
        }, {
            "value": u"汤原县", "label": u"汤原县",
        }, {
            "value": u"同江市", "label": u"同江市",
        }, {
            "value": u"富锦市", "label": u"富锦市",
        }, {
            "value": u"抚远市", "label": u"抚远市",
        }]
    }, {
        "value": u"七台河市", "label": u"七台河市",
        "children": [{
            "value": u"新兴区", "label": u"新兴区",
        }, {
            "value": u"桃山区", "label": u"桃山区",
        }, {
            "value": u"茄子河区", "label": u"茄子河区",
        }, {
            "value": u"勃利县", "label": u"勃利县",
        }]
    }, {
        "value": u"牡丹江市", "label": u"牡丹江市",
        "children": [{
            "value": u"东安区", "label": u"东安区",
        }, {
            "value": u"阳明区", "label": u"阳明区",
        }, {
            "value": u"爱民区", "label": u"爱民区",
        }, {
            "value": u"西安区", "label": u"西安区",
        }, {
            "value": u"林口县", "label": u"林口县",
        }, {
            "value": u"绥芬河市", "label": u"绥芬河市",
        }, {
            "value": u"海林市", "label": u"海林市",
        }, {
            "value": u"宁安市", "label": u"宁安市",
        }, {
            "value": u"穆棱市", "label": u"穆棱市",
        }, {
            "value": u"东宁市", "label": u"东宁市",
        }]
    }, {
        "value": u"黑河市", "label": u"黑河市",
        "children": [{
            "value": u"爱辉区", "label": u"爱辉区",
        }, {
            "value": u"嫩江县", "label": u"嫩江县",
        }, {
            "value": u"逊克县", "label": u"逊克县",
        }, {
            "value": u"孙吴县", "label": u"孙吴县",
        }, {
            "value": u"北安市", "label": u"北安市",
        }, {
            "value": u"五大连池市", "label": u"五大连池市",
        }]
    }, {
        "value": u"绥化市", "label": u"绥化市",
        "children": [{
            "value": u"北林区", "label": u"北林区",
        }, {
            "value": u"望奎县", "label": u"望奎县",
        }, {
            "value": u"兰西县", "label": u"兰西县",
        }, {
            "value": u"青冈县", "label": u"青冈县",
        }, {
            "value": u"庆安县", "label": u"庆安县",
        }, {
            "value": u"明水县", "label": u"明水县",
        }, {
            "value": u"绥棱县", "label": u"绥棱县",
        }, {
            "value": u"安达市", "label": u"安达市",
        }, {
            "value": u"肇东市", "label": u"肇东市",
        }, {
            "value": u"海伦市", "label": u"海伦市",
        }]
    }, {
        "value": u"大兴安岭地区", "label": u"大兴安岭地区",
        "children": [{
            "value": u"漠河市", "label": u"漠河市",
        }, {
            "value": u"呼玛县", "label": u"呼玛县",
        }, {
            "value": u"塔河县", "label": u"塔河县",
        }, {
            "value": u"松岭区", "label": u"松岭区",
        }, {
            "value": u"呼中区", "label": u"呼中区",
        }, {
            "value": u"加格达奇区", "label": u"加格达奇区",
        }, {
            "value": u"新林区", "label": u"新林区",
        }]
    }]
    }, {
    "value": u"上海市", "label": u"上海市",
    "children": [{
        "value": u"上海市", "label": u"上海市",
        "children": [{
            "value": u"黄浦区", "label": u"黄浦区",
        }, {
            "value": u"徐汇区", "label": u"徐汇区",
        }, {
            "value": u"长宁区", "label": u"长宁区",
        }, {
            "value": u"静安区", "label": u"静安区",
        }, {
            "value": u"普陀区", "label": u"普陀区",
        }, {
            "value": u"虹口区", "label": u"虹口区",
        }, {
            "value": u"杨浦区", "label": u"杨浦区",
        }, {
            "value": u"闵行区", "label": u"闵行区",
        }, {
            "value": u"宝山区", "label": u"宝山区",
        }, {
            "value": u"嘉定区", "label": u"嘉定区",
        }, {
            "value": u"浦东新区", "label": u"浦东新区",
        }, {
            "value": u"金山区", "label": u"金山区",
        }, {
            "value": u"松江区", "label": u"松江区",
        }, {
            "value": u"青浦区", "label": u"青浦区",
        }, {
            "value": u"奉贤区", "label": u"奉贤区",
        }, {
            "value": u"崇明区", "label": u"崇明区",
        }]
    }]
    }, {
    "value": u"江苏省", "label": u"江苏省",
    "children": [{
        "value": u"南京市", "label": u"南京市",
        "children": [{
            "value": u"玄武区", "label": u"玄武区",
        }, {
            "value": u"秦淮区", "label": u"秦淮区",
        }, {
            "value": u"建邺区", "label": u"建邺区",
        }, {
            "value": u"鼓楼区", "label": u"鼓楼区",
        }, {
            "value": u"浦口区", "label": u"浦口区",
        }, {
            "value": u"栖霞区", "label": u"栖霞区",
        }, {
            "value": u"雨花台区", "label": u"雨花台区",
        }, {
            "value": u"江宁区", "label": u"江宁区",
        }, {
            "value": u"六合区", "label": u"六合区",
        }, {
            "value": u"溧水区", "label": u"溧水区",
        }, {
            "value": u"高淳区", "label": u"高淳区",
        }]
    }, {
        "value": u"无锡市", "label": u"无锡市",
        "children": [{
            "value": u"锡山区", "label": u"锡山区",
        }, {
            "value": u"惠山区", "label": u"惠山区",
        }, {
            "value": u"滨湖区", "label": u"滨湖区",
        }, {
            "value": u"梁溪区", "label": u"梁溪区",
        }, {
            "value": u"新吴区", "label": u"新吴区",
        }, {
            "value": u"江阴市", "label": u"江阴市",
        }, {
            "value": u"宜兴市", "label": u"宜兴市",
        }]
    }, {
        "value": u"徐州市", "label": u"徐州市",
        "children": [{
            "value": u"鼓楼区", "label": u"鼓楼区",
        }, {
            "value": u"云龙区", "label": u"云龙区",
        }, {
            "value": u"贾汪区", "label": u"贾汪区",
        }, {
            "value": u"泉山区", "label": u"泉山区",
        }, {
            "value": u"铜山区", "label": u"铜山区",
        }, {
            "value": u"丰县", "label": u"丰县",
        }, {
            "value": u"沛县", "label": u"沛县",
        }, {
            "value": u"睢宁县", "label": u"睢宁县",
        }, {
            "value": u"新沂市", "label": u"新沂市",
        }, {
            "value": u"邳州市", "label": u"邳州市",
        }, {
            "value": u"工业园区", "label": u"工业园区",
        }]
    }, {
        "value": u"常州市", "label": u"常州市",
        "children": [{
            "value": u"天宁区", "label": u"天宁区",
        }, {
            "value": u"钟楼区", "label": u"钟楼区",
        }, {
            "value": u"新北区", "label": u"新北区",
        }, {
            "value": u"武进区", "label": u"武进区",
        }, {
            "value": u"金坛区", "label": u"金坛区",
        }, {
            "value": u"溧阳市", "label": u"溧阳市",
        }]
    }, {
        "value": u"苏州市", "label": u"苏州市",
        "children": [{
            "value": u"虎丘区", "label": u"虎丘区",
        }, {
            "value": u"吴中区", "label": u"吴中区",
        }, {
            "value": u"相城区", "label": u"相城区",
        }, {
            "value": u"姑苏区", "label": u"姑苏区",
        }, {
            "value": u"吴江区", "label": u"吴江区",
        }, {
            "value": u"常熟市", "label": u"常熟市",
        }, {
            "value": u"张家港市", "label": u"张家港市",
        }, {
            "value": u"昆山市", "label": u"昆山市",
        }, {
            "value": u"太仓市", "label": u"太仓市",
        }, {
            "value": u"工业园区", "label": u"工业园区",
        }, {
            "value": u"高新区", "label": u"高新区",
        }]
    }, {
        "value": u"南通市", "label": u"南通市",
        "children": [{
            "value": u"崇川区", "label": u"崇川区",
        }, {
            "value": u"港闸区", "label": u"港闸区",
        }, {
            "value": u"通州区", "label": u"通州区",
        }, {
            "value": u"如东县", "label": u"如东县",
        }, {
            "value": u"启东市", "label": u"启东市",
        }, {
            "value": u"如皋市", "label": u"如皋市",
        }, {
            "value": u"海门市", "label": u"海门市",
        }, {
            "value": u"海安市", "label": u"海安市",
        }, {
            "value": u"高新区", "label": u"高新区",
        }]
    }, {
        "value": u"连云港市", "label": u"连云港市",
        "children": [{
            "value": u"连云区", "label": u"连云区",
        }, {
            "value": u"海州区", "label": u"海州区",
        }, {
            "value": u"赣榆区", "label": u"赣榆区",
        }, {
            "value": u"东海县", "label": u"东海县",
        }, {
            "value": u"灌云县", "label": u"灌云县",
        }, {
            "value": u"灌南县", "label": u"灌南县",
        }]
    }, {
        "value": u"淮安市", "label": u"淮安市",
        "children": [{
            "value": u"淮安区", "label": u"淮安区",
        }, {
            "value": u"淮阴区", "label": u"淮阴区",
        }, {
            "value": u"清江浦区", "label": u"清江浦区",
        }, {
            "value": u"洪泽区", "label": u"洪泽区",
        }, {
            "value": u"涟水县", "label": u"涟水县",
        }, {
            "value": u"盱眙县", "label": u"盱眙县",
        }, {
            "value": u"金湖县", "label": u"金湖县",
        }, {
            "value": u"经济开发区", "label": u"经济开发区",
        }]
    }, {
        "value": u"盐城市", "label": u"盐城市",
        "children": [{
            "value": u"亭湖区", "label": u"亭湖区",
        }, {
            "value": u"盐都区", "label": u"盐都区",
        }, {
            "value": u"大丰区", "label": u"大丰区",
        }, {
            "value": u"响水县", "label": u"响水县",
        }, {
            "value": u"滨海县", "label": u"滨海县",
        }, {
            "value": u"阜宁县", "label": u"阜宁县",
        }, {
            "value": u"射阳县", "label": u"射阳县",
        }, {
            "value": u"建湖县", "label": u"建湖县",
        }, {
            "value": u"东台市", "label": u"东台市",
        }]
    }, {
        "value": u"扬州市", "label": u"扬州市",
        "children": [{
            "value": u"广陵区", "label": u"广陵区",
        }, {
            "value": u"邗江区", "label": u"邗江区",
        }, {
            "value": u"江都区", "label": u"江都区",
        }, {
            "value": u"宝应县", "label": u"宝应县",
        }, {
            "value": u"仪征市", "label": u"仪征市",
        }, {
            "value": u"高邮市", "label": u"高邮市",
        }, {
            "value": u"经济开发区", "label": u"经济开发区",
        }]
    }, {
        "value": u"镇江市", "label": u"镇江市",
        "children": [{
            "value": u"京口区", "label": u"京口区",
        }, {
            "value": u"润州区", "label": u"润州区",
        }, {
            "value": u"丹徒区", "label": u"丹徒区",
        }, {
            "value": u"丹阳市", "label": u"丹阳市",
        }, {
            "value": u"扬中市", "label": u"扬中市",
        }, {
            "value": u"句容市", "label": u"句容市",
        }]
    }, {
        "value": u"泰州市", "label": u"泰州市",
        "children": [{
            "value": u"海陵区", "label": u"海陵区",
        }, {
            "value": u"高港区", "label": u"高港区",
        }, {
            "value": u"姜堰区", "label": u"姜堰区",
        }, {
            "value": u"兴化市", "label": u"兴化市",
        }, {
            "value": u"靖江市", "label": u"靖江市",
        }, {
            "value": u"泰兴市", "label": u"泰兴市",
        }]
    }, {
        "value": u"宿迁市", "label": u"宿迁市",
        "children": [{
            "value": u"宿城区", "label": u"宿城区",
        }, {
            "value": u"宿豫区", "label": u"宿豫区",
        }, {
            "value": u"沭阳县", "label": u"沭阳县",
        }, {
            "value": u"泗阳县", "label": u"泗阳县",
        }, {
            "value": u"泗洪县", "label": u"泗洪县",
        }]
    }]
    }, {
    "value": u"浙江省", "label": u"浙江省",
    "children": [{
        "value": u"杭州市", "label": u"杭州市",
        "children": [{
            "value": u"上城区", "label": u"上城区",
        }, {
            "value": u"下城区", "label": u"下城区",
        }, {
            "value": u"江干区", "label": u"江干区",
        }, {
            "value": u"拱墅区", "label": u"拱墅区",
        }, {
            "value": u"西湖区", "label": u"西湖区",
        }, {
            "value": u"滨江区", "label": u"滨江区",
        }, {
            "value": u"萧山区", "label": u"萧山区",
        }, {
            "value": u"余杭区", "label": u"余杭区",
        }, {
            "value": u"富阳区", "label": u"富阳区",
        }, {
            "value": u"临安区", "label": u"临安区",
        }, {
            "value": u"桐庐县", "label": u"桐庐县",
        }, {
            "value": u"淳安县", "label": u"淳安县",
        }, {
            "value": u"建德市", "label": u"建德市",
        }]
    }, {
        "value": u"宁波市", "label": u"宁波市",
        "children": [{
            "value": u"海曙区", "label": u"海曙区",
        }, {
            "value": u"江北区", "label": u"江北区",
        }, {
            "value": u"北仑区", "label": u"北仑区",
        }, {
            "value": u"镇海区", "label": u"镇海区",
        }, {
            "value": u"鄞州区", "label": u"鄞州区",
        }, {
            "value": u"奉化区", "label": u"奉化区",
        }, {
            "value": u"象山县", "label": u"象山县",
        }, {
            "value": u"宁海县", "label": u"宁海县",
        }, {
            "value": u"余姚市", "label": u"余姚市",
        }, {
            "value": u"慈溪市", "label": u"慈溪市",
        }]
    }, {
        "value": u"温州市", "label": u"温州市",
        "children": [{
            "value": u"鹿城区", "label": u"鹿城区",
        }, {
            "value": u"龙湾区", "label": u"龙湾区",
        }, {
            "value": u"瓯海区", "label": u"瓯海区",
        }, {
            "value": u"洞头区", "label": u"洞头区",
        }, {
            "value": u"永嘉县", "label": u"永嘉县",
        }, {
            "value": u"平阳县", "label": u"平阳县",
        }, {
            "value": u"苍南县", "label": u"苍南县",
        }, {
            "value": u"文成县", "label": u"文成县",
        }, {
            "value": u"泰顺县", "label": u"泰顺县",
        }, {
            "value": u"瑞安市", "label": u"瑞安市",
        }, {
            "value": u"乐清市", "label": u"乐清市",
        }]
    }, {
        "value": u"嘉兴市", "label": u"嘉兴市",
        "children": [{
            "value": u"南湖区", "label": u"南湖区",
        }, {
            "value": u"秀洲区", "label": u"秀洲区",
        }, {
            "value": u"嘉善县", "label": u"嘉善县",
        }, {
            "value": u"海盐县", "label": u"海盐县",
        }, {
            "value": u"海宁市", "label": u"海宁市",
        }, {
            "value": u"平湖市", "label": u"平湖市",
        }, {
            "value": u"桐乡市", "label": u"桐乡市",
        }]
    }, {
        "value": u"湖州市", "label": u"湖州市",
        "children": [{
            "value": u"吴兴区", "label": u"吴兴区",
        }, {
            "value": u"南浔区", "label": u"南浔区",
        }, {
            "value": u"德清县", "label": u"德清县",
        }, {
            "value": u"长兴县", "label": u"长兴县",
        }, {
            "value": u"安吉县", "label": u"安吉县",
        }]
    }, {
        "value": u"绍兴市", "label": u"绍兴市",
        "children": [{
            "value": u"越城区", "label": u"越城区",
        }, {
            "value": u"柯桥区", "label": u"柯桥区",
        }, {
            "value": u"上虞区", "label": u"上虞区",
        }, {
            "value": u"新昌县", "label": u"新昌县",
        }, {
            "value": u"诸暨市", "label": u"诸暨市",
        }, {
            "value": u"嵊州市", "label": u"嵊州市",
        }]
    }, {
        "value": u"金华市", "label": u"金华市",
        "children": [{
            "value": u"婺城区", "label": u"婺城区",
        }, {
            "value": u"金东区", "label": u"金东区",
        }, {
            "value": u"武义县", "label": u"武义县",
        }, {
            "value": u"浦江县", "label": u"浦江县",
        }, {
            "value": u"磐安县", "label": u"磐安县",
        }, {
            "value": u"兰溪市", "label": u"兰溪市",
        }, {
            "value": u"义乌市", "label": u"义乌市",
        }, {
            "value": u"东阳市", "label": u"东阳市",
        }, {
            "value": u"永康市", "label": u"永康市",
        }]
    }, {
        "value": u"衢州市", "label": u"衢州市",
        "children": [{
            "value": u"柯城区", "label": u"柯城区",
        }, {
            "value": u"衢江区", "label": u"衢江区",
        }, {
            "value": u"常山县", "label": u"常山县",
        }, {
            "value": u"开化县", "label": u"开化县",
        }, {
            "value": u"龙游县", "label": u"龙游县",
        }, {
            "value": u"江山市", "label": u"江山市",
        }]
    }, {
        "value": u"舟山市", "label": u"舟山市",
        "children": [{
            "value": u"定海区", "label": u"定海区",
        }, {
            "value": u"普陀区", "label": u"普陀区",
        }, {
            "value": u"岱山县", "label": u"岱山县",
        }, {
            "value": u"嵊泗县", "label": u"嵊泗县",
        }]
    }, {
        "value": u"台州市", "label": u"台州市",
        "children": [{
            "value": u"椒江区", "label": u"椒江区",
        }, {
            "value": u"黄岩区", "label": u"黄岩区",
        }, {
            "value": u"路桥区", "label": u"路桥区",
        }, {
            "value": u"三门县", "label": u"三门县",
        }, {
            "value": u"天台县", "label": u"天台县",
        }, {
            "value": u"仙居县", "label": u"仙居县",
        }, {
            "value": u"温岭市", "label": u"温岭市",
        }, {
            "value": u"临海市", "label": u"临海市",
        }, {
            "value": u"玉环市", "label": u"玉环市",
        }]
    }, {
        "value": u"丽水市", "label": u"丽水市",
        "children": [{
            "value": u"莲都区", "label": u"莲都区",
        }, {
            "value": u"青田县", "label": u"青田县",
        }, {
            "value": u"缙云县", "label": u"缙云县",
        }, {
            "value": u"遂昌县", "label": u"遂昌县",
        }, {
            "value": u"松阳县", "label": u"松阳县",
        }, {
            "value": u"云和县", "label": u"云和县",
        }, {
            "value": u"庆元县", "label": u"庆元县",
        }, {
            "value": u"景宁畲族自治县", "label": u"景宁畲族自治县",
        }, {
            "value": u"龙泉市", "label": u"龙泉市",
        }]
    }]
    }, {
    "value": u"安徽省", "label": u"安徽省",
    "children": [{
        "value": u"合肥市", "label": u"合肥市",
        "children": [{
            "value": u"瑶海区", "label": u"瑶海区",
        }, {
            "value": u"庐阳区", "label": u"庐阳区",
        }, {
            "value": u"蜀山区", "label": u"蜀山区",
        }, {
            "value": u"包河区", "label": u"包河区",
        }, {
            "value": u"长丰县", "label": u"长丰县",
        }, {
            "value": u"肥东县", "label": u"肥东县",
        }, {
            "value": u"肥西县", "label": u"肥西县",
        }, {
            "value": u"庐江县", "label": u"庐江县",
        }, {
            "value": u"巢湖市", "label": u"巢湖市",
        }, {
            "value": u"高新技术开发区", "label": u"高新技术开发区",
        }, {
            "value": u"经济技术开发区", "label": u"经济技术开发区",
        }]
    }, {
        "value": u"芜湖市", "label": u"芜湖市",
        "children": [{
            "value": u"镜湖区", "label": u"镜湖区",
        }, {
            "value": u"弋江区", "label": u"弋江区",
        }, {
            "value": u"鸠江区", "label": u"鸠江区",
        }, {
            "value": u"三山区", "label": u"三山区",
        }, {
            "value": u"芜湖县", "label": u"芜湖县",
        }, {
            "value": u"繁昌县", "label": u"繁昌县",
        }, {
            "value": u"南陵县", "label": u"南陵县",
        }, {
            "value": u"无为县", "label": u"无为县",
        }]
    }, {
        "value": u"蚌埠市", "label": u"蚌埠市",
        "children": [{
            "value": u"龙子湖区", "label": u"龙子湖区",
        }, {
            "value": u"蚌山区", "label": u"蚌山区",
        }, {
            "value": u"禹会区", "label": u"禹会区",
        }, {
            "value": u"淮上区", "label": u"淮上区",
        }, {
            "value": u"怀远县", "label": u"怀远县",
        }, {
            "value": u"五河县", "label": u"五河县",
        }, {
            "value": u"固镇县", "label": u"固镇县",
        }]
    }, {
        "value": u"淮南市", "label": u"淮南市",
        "children": [{
            "value": u"大通区", "label": u"大通区",
        }, {
            "value": u"田家庵区", "label": u"田家庵区",
        }, {
            "value": u"谢家集区", "label": u"谢家集区",
        }, {
            "value": u"八公山区", "label": u"八公山区",
        }, {
            "value": u"潘集区", "label": u"潘集区",
        }, {
            "value": u"凤台县", "label": u"凤台县",
        }, {
            "value": u"寿县", "label": u"寿县",
        }]
    }, {
        "value": u"马鞍山市", "label": u"马鞍山市",
        "children": [{
            "value": u"花山区", "label": u"花山区",
        }, {
            "value": u"雨山区", "label": u"雨山区",
        }, {
            "value": u"博望区", "label": u"博望区",
        }, {
            "value": u"当涂县", "label": u"当涂县",
        }, {
            "value": u"含山县", "label": u"含山县",
        }, {
            "value": u"和县", "label": u"和县",
        }]
    }, {
        "value": u"淮北市", "label": u"淮北市",
        "children": [{
            "value": u"杜集区", "label": u"杜集区",
        }, {
            "value": u"相山区", "label": u"相山区",
        }, {
            "value": u"烈山区", "label": u"烈山区",
        }, {
            "value": u"濉溪县", "label": u"濉溪县",
        }]
    }, {
        "value": u"铜陵市", "label": u"铜陵市",
        "children": [{
            "value": u"铜官区", "label": u"铜官区",
        }, {
            "value": u"义安区", "label": u"义安区",
        }, {
            "value": u"郊区", "label": u"郊区",
        }, {
            "value": u"枞阳县", "label": u"枞阳县",
        }]
    }, {
        "value": u"安庆市", "label": u"安庆市",
        "children": [{
            "value": u"迎江区", "label": u"迎江区",
        }, {
            "value": u"大观区", "label": u"大观区",
        }, {
            "value": u"宜秀区", "label": u"宜秀区",
        }, {
            "value": u"怀宁县", "label": u"怀宁县",
        }, {
            "value": u"潜山县", "label": u"潜山县",
        }, {
            "value": u"太湖县", "label": u"太湖县",
        }, {
            "value": u"宿松县", "label": u"宿松县",
        }, {
            "value": u"望江县", "label": u"望江县",
        }, {
            "value": u"岳西县", "label": u"岳西县",
        }, {
            "value": u"桐城市", "label": u"桐城市",
        }]
    }, {
        "value": u"黄山市", "label": u"黄山市",
        "children": [{
            "value": u"屯溪区", "label": u"屯溪区",
        }, {
            "value": u"黄山区", "label": u"黄山区",
        }, {
            "value": u"徽州区", "label": u"徽州区",
        }, {
            "value": u"歙县", "label": u"歙县",
        }, {
            "value": u"休宁县", "label": u"休宁县",
        }, {
            "value": u"黟县", "label": u"黟县",
        }, {
            "value": u"祁门县", "label": u"祁门县",
        }]
    }, {
        "value": u"滁州市", "label": u"滁州市",
        "children": [{
            "value": u"琅琊区", "label": u"琅琊区",
        }, {
            "value": u"南谯区", "label": u"南谯区",
        }, {
            "value": u"来安县", "label": u"来安县",
        }, {
            "value": u"全椒县", "label": u"全椒县",
        }, {
            "value": u"定远县", "label": u"定远县",
        }, {
            "value": u"凤阳县", "label": u"凤阳县",
        }, {
            "value": u"天长市", "label": u"天长市",
        }, {
            "value": u"明光市", "label": u"明光市",
        }]
    }, {
        "value": u"阜阳市", "label": u"阜阳市",
        "children": [{
            "value": u"颍州区", "label": u"颍州区",
        }, {
            "value": u"颍东区", "label": u"颍东区",
        }, {
            "value": u"颍泉区", "label": u"颍泉区",
        }, {
            "value": u"临泉县", "label": u"临泉县",
        }, {
            "value": u"太和县", "label": u"太和县",
        }, {
            "value": u"阜南县", "label": u"阜南县",
        }, {
            "value": u"颍上县", "label": u"颍上县",
        }, {
            "value": u"界首市", "label": u"界首市",
        }]
    }, {
        "value": u"宿州市", "label": u"宿州市",
        "children": [{
            "value": u"埇桥区", "label": u"埇桥区",
        }, {
            "value": u"砀山县", "label": u"砀山县",
        }, {
            "value": u"萧县", "label": u"萧县",
        }, {
            "value": u"灵璧县", "label": u"灵璧县",
        }, {
            "value": u"泗县", "label": u"泗县",
        }, {
            "value": u"经济开发区", "label": u"经济开发区",
        }]
    }, {
        "value": u"六安市", "label": u"六安市",
        "children": [{
            "value": u"金安区", "label": u"金安区",
        }, {
            "value": u"裕安区", "label": u"裕安区",
        }, {
            "value": u"叶集区", "label": u"叶集区",
        }, {
            "value": u"霍邱县", "label": u"霍邱县",
        }, {
            "value": u"舒城县", "label": u"舒城县",
        }, {
            "value": u"金寨县", "label": u"金寨县",
        }, {
            "value": u"霍山县", "label": u"霍山县",
        }]
    }, {
        "value": u"亳州市", "label": u"亳州市",
        "children": [{
            "value": u"谯城区", "label": u"谯城区",
        }, {
            "value": u"涡阳县", "label": u"涡阳县",
        }, {
            "value": u"蒙城县", "label": u"蒙城县",
        }, {
            "value": u"利辛县", "label": u"利辛县",
        }]
    }, {
        "value": u"池州市", "label": u"池州市",
        "children": [{
            "value": u"贵池区", "label": u"贵池区",
        }, {
            "value": u"东至县", "label": u"东至县",
        }, {
            "value": u"石台县", "label": u"石台县",
        }, {
            "value": u"青阳县", "label": u"青阳县",
        }]
    }, {
        "value": u"宣城市", "label": u"宣城市",
        "children": [{
            "value": u"宣州区", "label": u"宣州区",
        }, {
            "value": u"郎溪县", "label": u"郎溪县",
        }, {
            "value": u"广德县", "label": u"广德县",
        }, {
            "value": u"泾县", "label": u"泾县",
        }, {
            "value": u"绩溪县", "label": u"绩溪县",
        }, {
            "value": u"旌德县", "label": u"旌德县",
        }, {
            "value": u"宁国市", "label": u"宁国市",
        }]
    }]
    }, {
    "value": u"福建省", "label": u"福建省",
    "children": [{
        "value": u"福州市", "label": u"福州市",
        "children": [{
            "value": u"鼓楼区", "label": u"鼓楼区",
        }, {
            "value": u"台江区", "label": u"台江区",
        }, {
            "value": u"仓山区", "label": u"仓山区",
        }, {
            "value": u"马尾区", "label": u"马尾区",
        }, {
            "value": u"晋安区", "label": u"晋安区",
        }, {
            "value": u"长乐区", "label": u"长乐区",
        }, {
            "value": u"闽侯县", "label": u"闽侯县",
        }, {
            "value": u"连江县", "label": u"连江县",
        }, {
            "value": u"罗源县", "label": u"罗源县",
        }, {
            "value": u"闽清县", "label": u"闽清县",
        }, {
            "value": u"永泰县", "label": u"永泰县",
        }, {
            "value": u"平潭县", "label": u"平潭县",
        }, {
            "value": u"福清市", "label": u"福清市",
        }]
    }, {
        "value": u"厦门市", "label": u"厦门市",
        "children": [{
            "value": u"思明区", "label": u"思明区",
        }, {
            "value": u"海沧区", "label": u"海沧区",
        }, {
            "value": u"湖里区", "label": u"湖里区",
        }, {
            "value": u"集美区", "label": u"集美区",
        }, {
            "value": u"同安区", "label": u"同安区",
        }, {
            "value": u"翔安区", "label": u"翔安区",
        }]
    }, {
        "value": u"莆田市", "label": u"莆田市",
        "children": [{
            "value": u"城厢区", "label": u"城厢区",
        }, {
            "value": u"涵江区", "label": u"涵江区",
        }, {
            "value": u"荔城区", "label": u"荔城区",
        }, {
            "value": u"秀屿区", "label": u"秀屿区",
        }, {
            "value": u"仙游县", "label": u"仙游县",
        }]
    }, {
        "value": u"三明市", "label": u"三明市",
        "children": [{
            "value": u"梅列区", "label": u"梅列区",
        }, {
            "value": u"三元区", "label": u"三元区",
        }, {
            "value": u"明溪县", "label": u"明溪县",
        }, {
            "value": u"清流县", "label": u"清流县",
        }, {
            "value": u"宁化县", "label": u"宁化县",
        }, {
            "value": u"大田县", "label": u"大田县",
        }, {
            "value": u"尤溪县", "label": u"尤溪县",
        }, {
            "value": u"沙县", "label": u"沙县",
        }, {
            "value": u"将乐县", "label": u"将乐县",
        }, {
            "value": u"泰宁县", "label": u"泰宁县",
        }, {
            "value": u"建宁县", "label": u"建宁县",
        }, {
            "value": u"永安市", "label": u"永安市",
        }]
    }, {
        "value": u"泉州市", "label": u"泉州市",
        "children": [{
            "value": u"鲤城区", "label": u"鲤城区",
        }, {
            "value": u"丰泽区", "label": u"丰泽区",
        }, {
            "value": u"洛江区", "label": u"洛江区",
        }, {
            "value": u"泉港区", "label": u"泉港区",
        }, {
            "value": u"惠安县", "label": u"惠安县",
        }, {
            "value": u"安溪县", "label": u"安溪县",
        }, {
            "value": u"永春县", "label": u"永春县",
        }, {
            "value": u"德化县", "label": u"德化县",
        }, {
            "value": u"金门县", "label": u"金门县",
        }, {
            "value": u"石狮市", "label": u"石狮市",
        }, {
            "value": u"晋江市", "label": u"晋江市",
        }, {
            "value": u"南安市", "label": u"南安市",
        }]
    }, {
        "value": u"漳州市", "label": u"漳州市",
        "children": [{
            "value": u"芗城区", "label": u"芗城区",
        }, {
            "value": u"龙文区", "label": u"龙文区",
        }, {
            "value": u"云霄县", "label": u"云霄县",
        }, {
            "value": u"漳浦县", "label": u"漳浦县",
        }, {
            "value": u"诏安县", "label": u"诏安县",
        }, {
            "value": u"长泰县", "label": u"长泰县",
        }, {
            "value": u"东山县", "label": u"东山县",
        }, {
            "value": u"南靖县", "label": u"南靖县",
        }, {
            "value": u"平和县", "label": u"平和县",
        }, {
            "value": u"华安县", "label": u"华安县",
        }, {
            "value": u"龙海市", "label": u"龙海市",
        }]
    }, {
        "value": u"南平市", "label": u"南平市",
        "children": [{
            "value": u"延平区", "label": u"延平区",
        }, {
            "value": u"建阳区", "label": u"建阳区",
        }, {
            "value": u"顺昌县", "label": u"顺昌县",
        }, {
            "value": u"浦城县", "label": u"浦城县",
        }, {
            "value": u"光泽县", "label": u"光泽县",
        }, {
            "value": u"松溪县", "label": u"松溪县",
        }, {
            "value": u"政和县", "label": u"政和县",
        }, {
            "value": u"邵武市", "label": u"邵武市",
        }, {
            "value": u"武夷山市", "label": u"武夷山市",
        }, {
            "value": u"建瓯市", "label": u"建瓯市",
        }]
    }, {
        "value": u"龙岩市", "label": u"龙岩市",
        "children": [{
            "value": u"新罗区", "label": u"新罗区",
        }, {
            "value": u"永定区", "label": u"永定区",
        }, {
            "value": u"长汀县", "label": u"长汀县",
        }, {
            "value": u"上杭县", "label": u"上杭县",
        }, {
            "value": u"武平县", "label": u"武平县",
        }, {
            "value": u"连城县", "label": u"连城县",
        }, {
            "value": u"漳平市", "label": u"漳平市",
        }]
    }, {
        "value": u"宁德市", "label": u"宁德市",
        "children": [{
            "value": u"蕉城区", "label": u"蕉城区",
        }, {
            "value": u"霞浦县", "label": u"霞浦县",
        }, {
            "value": u"古田县", "label": u"古田县",
        }, {
            "value": u"屏南县", "label": u"屏南县",
        }, {
            "value": u"寿宁县", "label": u"寿宁县",
        }, {
            "value": u"周宁县", "label": u"周宁县",
        }, {
            "value": u"柘荣县", "label": u"柘荣县",
        }, {
            "value": u"福安市", "label": u"福安市",
        }, {
            "value": u"福鼎市", "label": u"福鼎市",
        }]
    }]
    }, {
    "value": u"江西省", "label": u"江西省",
    "children": [{
        "value": u"南昌市", "label": u"南昌市",
        "children": [{
            "value": u"东湖区", "label": u"东湖区",
        }, {
            "value": u"西湖区", "label": u"西湖区",
        }, {
            "value": u"青云谱区", "label": u"青云谱区",
        }, {
            "value": u"湾里区", "label": u"湾里区",
        }, {
            "value": u"青山湖区", "label": u"青山湖区",
        }, {
            "value": u"新建区", "label": u"新建区",
        }, {
            "value": u"南昌县", "label": u"南昌县",
        }, {
            "value": u"安义县", "label": u"安义县",
        }, {
            "value": u"进贤县", "label": u"进贤县",
        }, {
            "value": u"经济技术开发区", "label": u"经济技术开发区",
        }, {
            "value": u"高新区", "label": u"高新区",
        }]
    }, {
        "value": u"景德镇市", "label": u"景德镇市",
        "children": [{
            "value": u"昌江区", "label": u"昌江区",
        }, {
            "value": u"珠山区", "label": u"珠山区",
        }, {
            "value": u"浮梁县", "label": u"浮梁县",
        }, {
            "value": u"乐平市", "label": u"乐平市",
        }]
    }, {
        "value": u"萍乡市", "label": u"萍乡市",
        "children": [{
            "value": u"安源区", "label": u"安源区",
        }, {
            "value": u"湘东区", "label": u"湘东区",
        }, {
            "value": u"莲花县", "label": u"莲花县",
        }, {
            "value": u"上栗县", "label": u"上栗县",
        }, {
            "value": u"芦溪县", "label": u"芦溪县",
        }]
    }, {
        "value": u"九江市", "label": u"九江市",
        "children": [{
            "value": u"濂溪区", "label": u"濂溪区",
        }, {
            "value": u"浔阳区", "label": u"浔阳区",
        }, {
            "value": u"柴桑区", "label": u"柴桑区",
        }, {
            "value": u"武宁县", "label": u"武宁县",
        }, {
            "value": u"修水县", "label": u"修水县",
        }, {
            "value": u"永修县", "label": u"永修县",
        }, {
            "value": u"德安县", "label": u"德安县",
        }, {
            "value": u"都昌县", "label": u"都昌县",
        }, {
            "value": u"湖口县", "label": u"湖口县",
        }, {
            "value": u"彭泽县", "label": u"彭泽县",
        }, {
            "value": u"瑞昌市", "label": u"瑞昌市",
        }, {
            "value": u"共青城市", "label": u"共青城市",
        }, {
            "value": u"庐山市", "label": u"庐山市",
        }, {
            "value": u"经济技术开发区", "label": u"经济技术开发区",
        }]
    }, {
        "value": u"新余市", "label": u"新余市",
        "children": [{
            "value": u"渝水区", "label": u"渝水区",
        }, {
            "value": u"分宜县", "label": u"分宜县",
        }]
    }, {
        "value": u"鹰潭市", "label": u"鹰潭市",
        "children": [{
            "value": u"月湖区", "label": u"月湖区",
        }, {
            "value": u"余江区", "label": u"余江区",
        }, {
            "value": u"贵溪市", "label": u"贵溪市",
        }]
    }, {
        "value": u"赣州市", "label": u"赣州市",
        "children": [{
            "value": u"章贡区", "label": u"章贡区",
        }, {
            "value": u"南康区", "label": u"南康区",
        }, {
            "value": u"赣县区", "label": u"赣县区",
        }, {
            "value": u"信丰县", "label": u"信丰县",
        }, {
            "value": u"大余县", "label": u"大余县",
        }, {
            "value": u"上犹县", "label": u"上犹县",
        }, {
            "value": u"崇义县", "label": u"崇义县",
        }, {
            "value": u"安远县", "label": u"安远县",
        }, {
            "value": u"龙南县", "label": u"龙南县",
        }, {
            "value": u"定南县", "label": u"定南县",
        }, {
            "value": u"全南县", "label": u"全南县",
        }, {
            "value": u"宁都县", "label": u"宁都县",
        }, {
            "value": u"于都县", "label": u"于都县",
        }, {
            "value": u"兴国县", "label": u"兴国县",
        }, {
            "value": u"会昌县", "label": u"会昌县",
        }, {
            "value": u"寻乌县", "label": u"寻乌县",
        }, {
            "value": u"石城县", "label": u"石城县",
        }, {
            "value": u"瑞金市", "label": u"瑞金市",
        }]
    }, {
        "value": u"吉安市", "label": u"吉安市",
        "children": [{
            "value": u"吉州区", "label": u"吉州区",
        }, {
            "value": u"青原区", "label": u"青原区",
        }, {
            "value": u"吉安县", "label": u"吉安县",
        }, {
            "value": u"吉水县", "label": u"吉水县",
        }, {
            "value": u"峡江县", "label": u"峡江县",
        }, {
            "value": u"新干县", "label": u"新干县",
        }, {
            "value": u"永丰县", "label": u"永丰县",
        }, {
            "value": u"泰和县", "label": u"泰和县",
        }, {
            "value": u"遂川县", "label": u"遂川县",
        }, {
            "value": u"万安县", "label": u"万安县",
        }, {
            "value": u"安福县", "label": u"安福县",
        }, {
            "value": u"永新县", "label": u"永新县",
        }, {
            "value": u"井冈山市", "label": u"井冈山市",
        }]
    }, {
        "value": u"宜春市", "label": u"宜春市",
        "children": [{
            "value": u"袁州区", "label": u"袁州区",
        }, {
            "value": u"奉新县", "label": u"奉新县",
        }, {
            "value": u"万载县", "label": u"万载县",
        }, {
            "value": u"上高县", "label": u"上高县",
        }, {
            "value": u"宜丰县", "label": u"宜丰县",
        }, {
            "value": u"靖安县", "label": u"靖安县",
        }, {
            "value": u"铜鼓县", "label": u"铜鼓县",
        }, {
            "value": u"丰城市", "label": u"丰城市",
        }, {
            "value": u"樟树市", "label": u"樟树市",
        }, {
            "value": u"高安市", "label": u"高安市",
        }]
    }, {
        "value": u"抚州市", "label": u"抚州市",
        "children": [{
            "value": u"临川区", "label": u"临川区",
        }, {
            "value": u"东乡区", "label": u"东乡区",
        }, {
            "value": u"南城县", "label": u"南城县",
        }, {
            "value": u"黎川县", "label": u"黎川县",
        }, {
            "value": u"南丰县", "label": u"南丰县",
        }, {
            "value": u"崇仁县", "label": u"崇仁县",
        }, {
            "value": u"乐安县", "label": u"乐安县",
        }, {
            "value": u"宜黄县", "label": u"宜黄县",
        }, {
            "value": u"金溪县", "label": u"金溪县",
        }, {
            "value": u"资溪县", "label": u"资溪县",
        }, {
            "value": u"广昌县", "label": u"广昌县",
        }]
    }, {
        "value": u"上饶市", "label": u"上饶市",
        "children": [{
            "value": u"信州区", "label": u"信州区",
        }, {
            "value": u"广丰区", "label": u"广丰区",
        }, {
            "value": u"上饶县", "label": u"上饶县",
        }, {
            "value": u"玉山县", "label": u"玉山县",
        }, {
            "value": u"铅山县", "label": u"铅山县",
        }, {
            "value": u"横峰县", "label": u"横峰县",
        }, {
            "value": u"弋阳县", "label": u"弋阳县",
        }, {
            "value": u"余干县", "label": u"余干县",
        }, {
            "value": u"鄱阳县", "label": u"鄱阳县",
        }, {
            "value": u"万年县", "label": u"万年县",
        }, {
            "value": u"婺源县", "label": u"婺源县",
        }, {
            "value": u"德兴市", "label": u"德兴市",
        }]
    }]
    }, {
    "value": u"山东省", "label": u"山东省",
    "children": [{
        "value": u"济南市", "label": u"济南市",
        "children": [{
            "value": u"历下区", "label": u"历下区",
        }, {
            "value": u"市中区", "label": u"市中区",
        }, {
            "value": u"槐荫区", "label": u"槐荫区",
        }, {
            "value": u"天桥区", "label": u"天桥区",
        }, {
            "value": u"历城区", "label": u"历城区",
        }, {
            "value": u"长清区", "label": u"长清区",
        }, {
            "value": u"章丘区", "label": u"章丘区",
        }, {
            "value": u"济阳区", "label": u"济阳区",
        }, {
            "value": u"莱芜区", "label": u"莱芜区",
        }, {
            "value": u"钢城区", "label": u"钢城区",
        }, {
            "value": u"平阴县", "label": u"平阴县",
        }, {
            "value": u"商河县", "label": u"商河县",
        }, {
            "value": u"高新区", "label": u"高新区",
        }]
    }, {
        "value": u"青岛市", "label": u"青岛市",
        "children": [{
            "value": u"市南区", "label": u"市南区",
        }, {
            "value": u"市北区", "label": u"市北区",
        }, {
            "value": u"黄岛区", "label": u"黄岛区",
        }, {
            "value": u"崂山区", "label": u"崂山区",
        }, {
            "value": u"李沧区", "label": u"李沧区",
        }, {
            "value": u"城阳区", "label": u"城阳区",
        }, {
            "value": u"即墨区", "label": u"即墨区",
        }, {
            "value": u"胶州市", "label": u"胶州市",
        }, {
            "value": u"平度市", "label": u"平度市",
        }, {
            "value": u"莱西市", "label": u"莱西市",
        }, {
            "value": u"开发区", "label": u"开发区",
        }]
    }, {
        "value": u"淄博市", "label": u"淄博市",
        "children": [{
            "value": u"淄川区", "label": u"淄川区",
        }, {
            "value": u"张店区", "label": u"张店区",
        }, {
            "value": u"博山区", "label": u"博山区",
        }, {
            "value": u"临淄区", "label": u"临淄区",
        }, {
            "value": u"周村区", "label": u"周村区",
        }, {
            "value": u"桓台县", "label": u"桓台县",
        }, {
            "value": u"高青县", "label": u"高青县",
        }, {
            "value": u"沂源县", "label": u"沂源县",
        }]
    }, {
        "value": u"枣庄市", "label": u"枣庄市",
        "children": [{
            "value": u"市中区", "label": u"市中区",
        }, {
            "value": u"薛城区", "label": u"薛城区",
        }, {
            "value": u"峄城区", "label": u"峄城区",
        }, {
            "value": u"台儿庄区", "label": u"台儿庄区",
        }, {
            "value": u"山亭区", "label": u"山亭区",
        }, {
            "value": u"滕州市", "label": u"滕州市",
        }]
    }, {
        "value": u"东营市", "label": u"东营市",
        "children": [{
            "value": u"东营区", "label": u"东营区",
        }, {
            "value": u"河口区", "label": u"河口区",
        }, {
            "value": u"垦利区", "label": u"垦利区",
        }, {
            "value": u"利津县", "label": u"利津县",
        }, {
            "value": u"广饶县", "label": u"广饶县",
        }]
    }, {
        "value": u"烟台市", "label": u"烟台市",
        "children": [{
            "value": u"芝罘区", "label": u"芝罘区",
        }, {
            "value": u"福山区", "label": u"福山区",
        }, {
            "value": u"牟平区", "label": u"牟平区",
        }, {
            "value": u"莱山区", "label": u"莱山区",
        }, {
            "value": u"长岛县", "label": u"长岛县",
        }, {
            "value": u"龙口市", "label": u"龙口市",
        }, {
            "value": u"莱阳市", "label": u"莱阳市",
        }, {
            "value": u"莱州市", "label": u"莱州市",
        }, {
            "value": u"蓬莱市", "label": u"蓬莱市",
        }, {
            "value": u"招远市", "label": u"招远市",
        }, {
            "value": u"栖霞市", "label": u"栖霞市",
        }, {
            "value": u"海阳市", "label": u"海阳市",
        }, {
            "value": u"开发区", "label": u"开发区",
        }]
    }, {
        "value": u"潍坊市", "label": u"潍坊市",
        "children": [{
            "value": u"潍城区", "label": u"潍城区",
        }, {
            "value": u"寒亭区", "label": u"寒亭区",
        }, {
            "value": u"坊子区", "label": u"坊子区",
        }, {
            "value": u"奎文区", "label": u"奎文区",
        }, {
            "value": u"临朐县", "label": u"临朐县",
        }, {
            "value": u"昌乐县", "label": u"昌乐县",
        }, {
            "value": u"青州市", "label": u"青州市",
        }, {
            "value": u"诸城市", "label": u"诸城市",
        }, {
            "value": u"寿光市", "label": u"寿光市",
        }, {
            "value": u"安丘市", "label": u"安丘市",
        }, {
            "value": u"高密市", "label": u"高密市",
        }, {
            "value": u"昌邑市", "label": u"昌邑市",
        }, {
            "value": u"开发区", "label": u"开发区",
        }, {
            "value": u"高新区", "label": u"高新区",
        }]
    }, {
        "value": u"济宁市", "label": u"济宁市",
        "children": [{
            "value": u"任城区", "label": u"任城区",
        }, {
            "value": u"兖州区", "label": u"兖州区",
        }, {
            "value": u"微山县", "label": u"微山县",
        }, {
            "value": u"鱼台县", "label": u"鱼台县",
        }, {
            "value": u"金乡县", "label": u"金乡县",
        }, {
            "value": u"嘉祥县", "label": u"嘉祥县",
        }, {
            "value": u"汶上县", "label": u"汶上县",
        }, {
            "value": u"泗水县", "label": u"泗水县",
        }, {
            "value": u"梁山县", "label": u"梁山县",
        }, {
            "value": u"曲阜市", "label": u"曲阜市",
        }, {
            "value": u"邹城市", "label": u"邹城市",
        }, {
            "value": u"高新区", "label": u"高新区",
        }]
    }, {
        "value": u"泰安市", "label": u"泰安市",
        "children": [{
            "value": u"泰山区", "label": u"泰山区",
        }, {
            "value": u"岱岳区", "label": u"岱岳区",
        }, {
            "value": u"宁阳县", "label": u"宁阳县",
        }, {
            "value": u"东平县", "label": u"东平县",
        }, {
            "value": u"新泰市", "label": u"新泰市",
        }, {
            "value": u"肥城市", "label": u"肥城市",
        }]
    }, {
        "value": u"威海市", "label": u"威海市",
        "children": [{
            "value": u"环翠区", "label": u"环翠区",
        }, {
            "value": u"文登区", "label": u"文登区",
        }, {
            "value": u"荣成市", "label": u"荣成市",
        }, {
            "value": u"乳山市", "label": u"乳山市",
        }, {
            "value": u"经济技术开发区", "label": u"经济技术开发区",
        }]
    }, {
        "value": u"日照市", "label": u"日照市",
        "children": [{
            "value": u"东港区", "label": u"东港区",
        }, {
            "value": u"岚山区", "label": u"岚山区",
        }, {
            "value": u"五莲县", "label": u"五莲县",
        }, {
            "value": u"莒县", "label": u"莒县",
        }]
    }, {
        "value": u"临沂市", "label": u"临沂市",
        "children": [{
            "value": u"兰山区", "label": u"兰山区",
        }, {
            "value": u"罗庄区", "label": u"罗庄区",
        }, {
            "value": u"河东区", "label": u"河东区",
        }, {
            "value": u"沂南县", "label": u"沂南县",
        }, {
            "value": u"郯城县", "label": u"郯城县",
        }, {
            "value": u"沂水县", "label": u"沂水县",
        }, {
            "value": u"兰陵县", "label": u"兰陵县",
        }, {
            "value": u"费县", "label": u"费县",
        }, {
            "value": u"平邑县", "label": u"平邑县",
        }, {
            "value": u"莒南县", "label": u"莒南县",
        }, {
            "value": u"蒙阴县", "label": u"蒙阴县",
        }, {
            "value": u"临沭县", "label": u"临沭县",
        }]
    }, {
        "value": u"德州市", "label": u"德州市",
        "children": [{
            "value": u"德城区", "label": u"德城区",
        }, {
            "value": u"陵城区", "label": u"陵城区",
        }, {
            "value": u"宁津县", "label": u"宁津县",
        }, {
            "value": u"庆云县", "label": u"庆云县",
        }, {
            "value": u"临邑县", "label": u"临邑县",
        }, {
            "value": u"齐河县", "label": u"齐河县",
        }, {
            "value": u"平原县", "label": u"平原县",
        }, {
            "value": u"夏津县", "label": u"夏津县",
        }, {
            "value": u"武城县", "label": u"武城县",
        }, {
            "value": u"乐陵市", "label": u"乐陵市",
        }, {
            "value": u"禹城市", "label": u"禹城市",
        }]
    }, {
        "value": u"聊城市", "label": u"聊城市",
        "children": [{
            "value": u"东昌府区", "label": u"东昌府区",
        }, {
            "value": u"阳谷县", "label": u"阳谷县",
        }, {
            "value": u"莘县", "label": u"莘县",
        }, {
            "value": u"茌平县", "label": u"茌平县",
        }, {
            "value": u"东阿县", "label": u"东阿县",
        }, {
            "value": u"冠县", "label": u"冠县",
        }, {
            "value": u"高唐县", "label": u"高唐县",
        }, {
            "value": u"临清市", "label": u"临清市",
        }]
    }, {
        "value": u"滨州市", "label": u"滨州市",
        "children": [{
            "value": u"滨城区", "label": u"滨城区",
        }, {
            "value": u"沾化区", "label": u"沾化区",
        }, {
            "value": u"惠民县", "label": u"惠民县",
        }, {
            "value": u"阳信县", "label": u"阳信县",
        }, {
            "value": u"无棣县", "label": u"无棣县",
        }, {
            "value": u"博兴县", "label": u"博兴县",
        }, {
            "value": u"邹平市", "label": u"邹平市",
        }]
    }, {
        "value": u"菏泽市", "label": u"菏泽市",
        "children": [{
            "value": u"牡丹区", "label": u"牡丹区",
        }, {
            "value": u"定陶区", "label": u"定陶区",
        }, {
            "value": u"曹县", "label": u"曹县",
        }, {
            "value": u"单县", "label": u"单县",
        }, {
            "value": u"成武县", "label": u"成武县",
        }, {
            "value": u"巨野县", "label": u"巨野县",
        }, {
            "value": u"郓城县", "label": u"郓城县",
        }, {
            "value": u"鄄城县", "label": u"鄄城县",
        }, {
            "value": u"东明县", "label": u"东明县",
        }]
    }]
    }, {
    "value": u"河南省", "label": u"河南省",
    "children": [{
        "value": u"郑州市", "label": u"郑州市",
        "children": [{
            "value": u"中原区", "label": u"中原区",
        }, {
            "value": u"二七区", "label": u"二七区",
        }, {
            "value": u"管城回族区", "label": u"管城回族区",
        }, {
            "value": u"金水区", "label": u"金水区",
        }, {
            "value": u"上街区", "label": u"上街区",
        }, {
            "value": u"惠济区", "label": u"惠济区",
        }, {
            "value": u"中牟县", "label": u"中牟县",
        }, {
            "value": u"巩义市", "label": u"巩义市",
        }, {
            "value": u"荥阳市", "label": u"荥阳市",
        }, {
            "value": u"新密市", "label": u"新密市",
        }, {
            "value": u"新郑市", "label": u"新郑市",
        }, {
            "value": u"登封市", "label": u"登封市",
        }, {
            "value": u"高新技术开发区", "label": u"高新技术开发区",
        }, {
            "value": u"经济技术开发区", "label": u"经济技术开发区",
        }]
    }, {
        "value": u"开封市", "label": u"开封市",
        "children": [{
            "value": u"龙亭区", "label": u"龙亭区",
        }, {
            "value": u"顺河回族区", "label": u"顺河回族区",
        }, {
            "value": u"鼓楼区", "label": u"鼓楼区",
        }, {
            "value": u"禹王台区", "label": u"禹王台区",
        }, {
            "value": u"祥符区", "label": u"祥符区",
        }, {
            "value": u"杞县", "label": u"杞县",
        }, {
            "value": u"通许县", "label": u"通许县",
        }, {
            "value": u"尉氏县", "label": u"尉氏县",
        }, {
            "value": u"兰考县", "label": u"兰考县",
        }]
    }, {
        "value": u"洛阳市", "label": u"洛阳市",
        "children": [{
            "value": u"老城区", "label": u"老城区",
        }, {
            "value": u"西工区", "label": u"西工区",
        }, {
            "value": u"瀍河回族区", "label": u"瀍河回族区",
        }, {
            "value": u"涧西区", "label": u"涧西区",
        }, {
            "value": u"吉利区", "label": u"吉利区",
        }, {
            "value": u"洛龙区", "label": u"洛龙区",
        }, {
            "value": u"孟津县", "label": u"孟津县",
        }, {
            "value": u"新安县", "label": u"新安县",
        }, {
            "value": u"栾川县", "label": u"栾川县",
        }, {
            "value": u"嵩县", "label": u"嵩县",
        }, {
            "value": u"汝阳县", "label": u"汝阳县",
        }, {
            "value": u"宜阳县", "label": u"宜阳县",
        }, {
            "value": u"洛宁县", "label": u"洛宁县",
        }, {
            "value": u"伊川县", "label": u"伊川县",
        }, {
            "value": u"偃师市", "label": u"偃师市",
        }]
    }, {
        "value": u"平顶山市", "label": u"平顶山市",
        "children": [{
            "value": u"新华区", "label": u"新华区",
        }, {
            "value": u"卫东区", "label": u"卫东区",
        }, {
            "value": u"石龙区", "label": u"石龙区",
        }, {
            "value": u"湛河区", "label": u"湛河区",
        }, {
            "value": u"宝丰县", "label": u"宝丰县",
        }, {
            "value": u"叶县", "label": u"叶县",
        }, {
            "value": u"鲁山县", "label": u"鲁山县",
        }, {
            "value": u"郏县", "label": u"郏县",
        }, {
            "value": u"舞钢市", "label": u"舞钢市",
        }, {
            "value": u"汝州市", "label": u"汝州市",
        }]
    }, {
        "value": u"安阳市", "label": u"安阳市",
        "children": [{
            "value": u"文峰区", "label": u"文峰区",
        }, {
            "value": u"北关区", "label": u"北关区",
        }, {
            "value": u"殷都区", "label": u"殷都区",
        }, {
            "value": u"龙安区", "label": u"龙安区",
        }, {
            "value": u"安阳县", "label": u"安阳县",
        }, {
            "value": u"汤阴县", "label": u"汤阴县",
        }, {
            "value": u"滑县", "label": u"滑县",
        }, {
            "value": u"内黄县", "label": u"内黄县",
        }, {
            "value": u"林州市", "label": u"林州市",
        }, {
            "value": u"开发区", "label": u"开发区",
        }]
    }, {
        "value": u"鹤壁市", "label": u"鹤壁市",
        "children": [{
            "value": u"鹤山区", "label": u"鹤山区",
        }, {
            "value": u"山城区", "label": u"山城区",
        }, {
            "value": u"淇滨区", "label": u"淇滨区",
        }, {
            "value": u"浚县", "label": u"浚县",
        }, {
            "value": u"淇县", "label": u"淇县",
        }]
    }, {
        "value": u"新乡市", "label": u"新乡市",
        "children": [{
            "value": u"红旗区", "label": u"红旗区",
        }, {
            "value": u"卫滨区", "label": u"卫滨区",
        }, {
            "value": u"凤泉区", "label": u"凤泉区",
        }, {
            "value": u"牧野区", "label": u"牧野区",
        }, {
            "value": u"新乡县", "label": u"新乡县",
        }, {
            "value": u"获嘉县", "label": u"获嘉县",
        }, {
            "value": u"原阳县", "label": u"原阳县",
        }, {
            "value": u"延津县", "label": u"延津县",
        }, {
            "value": u"封丘县", "label": u"封丘县",
        }, {
            "value": u"长垣县", "label": u"长垣县",
        }, {
            "value": u"卫辉市", "label": u"卫辉市",
        }, {
            "value": u"辉县市", "label": u"辉县市",
        }]
    }, {
        "value": u"焦作市", "label": u"焦作市",
        "children": [{
            "value": u"解放区", "label": u"解放区",
        }, {
            "value": u"中站区", "label": u"中站区",
        }, {
            "value": u"马村区", "label": u"马村区",
        }, {
            "value": u"山阳区", "label": u"山阳区",
        }, {
            "value": u"修武县", "label": u"修武县",
        }, {
            "value": u"博爱县", "label": u"博爱县",
        }, {
            "value": u"武陟县", "label": u"武陟县",
        }, {
            "value": u"温县", "label": u"温县",
        }, {
            "value": u"沁阳市", "label": u"沁阳市",
        }, {
            "value": u"孟州市", "label": u"孟州市",
        }]
    }, {
        "value": u"濮阳市", "label": u"濮阳市",
        "children": [{
            "value": u"华龙区", "label": u"华龙区",
        }, {
            "value": u"清丰县", "label": u"清丰县",
        }, {
            "value": u"南乐县", "label": u"南乐县",
        }, {
            "value": u"范县", "label": u"范县",
        }, {
            "value": u"台前县", "label": u"台前县",
        }, {
            "value": u"濮阳县", "label": u"濮阳县",
        }]
    }, {
        "value": u"许昌市", "label": u"许昌市",
        "children": [{
            "value": u"魏都区", "label": u"魏都区",
        }, {
            "value": u"建安区", "label": u"建安区",
        }, {
            "value": u"鄢陵县", "label": u"鄢陵县",
        }, {
            "value": u"襄城县", "label": u"襄城县",
        }, {
            "value": u"禹州市", "label": u"禹州市",
        }, {
            "value": u"长葛市", "label": u"长葛市",
        }]
    }, {
        "value": u"漯河市", "label": u"漯河市",
        "children": [{
            "value": u"源汇区", "label": u"源汇区",
        }, {
            "value": u"郾城区", "label": u"郾城区",
        }, {
            "value": u"召陵区", "label": u"召陵区",
        }, {
            "value": u"舞阳县", "label": u"舞阳县",
        }, {
            "value": u"临颍县", "label": u"临颍县",
        }]
    }, {
        "value": u"三门峡市", "label": u"三门峡市",
        "children": [{
            "value": u"湖滨区", "label": u"湖滨区",
        }, {
            "value": u"陕州区", "label": u"陕州区",
        }, {
            "value": u"渑池县", "label": u"渑池县",
        }, {
            "value": u"卢氏县", "label": u"卢氏县",
        }, {
            "value": u"义马市", "label": u"义马市",
        }, {
            "value": u"灵宝市", "label": u"灵宝市",
        }]
    }, {
        "value": u"南阳市", "label": u"南阳市",
        "children": [{
            "value": u"宛城区", "label": u"宛城区",
        }, {
            "value": u"卧龙区", "label": u"卧龙区",
        }, {
            "value": u"南召县", "label": u"南召县",
        }, {
            "value": u"方城县", "label": u"方城县",
        }, {
            "value": u"西峡县", "label": u"西峡县",
        }, {
            "value": u"镇平县", "label": u"镇平县",
        }, {
            "value": u"内乡县", "label": u"内乡县",
        }, {
            "value": u"淅川县", "label": u"淅川县",
        }, {
            "value": u"社旗县", "label": u"社旗县",
        }, {
            "value": u"唐河县", "label": u"唐河县",
        }, {
            "value": u"新野县", "label": u"新野县",
        }, {
            "value": u"桐柏县", "label": u"桐柏县",
        }, {
            "value": u"邓州市", "label": u"邓州市",
        }]
    }, {
        "value": u"商丘市", "label": u"商丘市",
        "children": [{
            "value": u"梁园区", "label": u"梁园区",
        }, {
            "value": u"睢阳区", "label": u"睢阳区",
        }, {
            "value": u"民权县", "label": u"民权县",
        }, {
            "value": u"睢县", "label": u"睢县",
        }, {
            "value": u"宁陵县", "label": u"宁陵县",
        }, {
            "value": u"柘城县", "label": u"柘城县",
        }, {
            "value": u"虞城县", "label": u"虞城县",
        }, {
            "value": u"夏邑县", "label": u"夏邑县",
        }, {
            "value": u"永城市", "label": u"永城市",
        }]
    }, {
        "value": u"信阳市", "label": u"信阳市",
        "children": [{
            "value": u"浉河区", "label": u"浉河区",
        }, {
            "value": u"平桥区", "label": u"平桥区",
        }, {
            "value": u"罗山县", "label": u"罗山县",
        }, {
            "value": u"光山县", "label": u"光山县",
        }, {
            "value": u"新县", "label": u"新县",
        }, {
            "value": u"商城县", "label": u"商城县",
        }, {
            "value": u"固始县", "label": u"固始县",
        }, {
            "value": u"潢川县", "label": u"潢川县",
        }, {
            "value": u"淮滨县", "label": u"淮滨县",
        }, {
            "value": u"息县", "label": u"息县",
        }]
    }, {
        "value": u"周口市", "label": u"周口市",
        "children": [{
            "value": u"川汇区", "label": u"川汇区",
        }, {
            "value": u"扶沟县", "label": u"扶沟县",
        }, {
            "value": u"西华县", "label": u"西华县",
        }, {
            "value": u"商水县", "label": u"商水县",
        }, {
            "value": u"沈丘县", "label": u"沈丘县",
        }, {
            "value": u"郸城县", "label": u"郸城县",
        }, {
            "value": u"淮阳县", "label": u"淮阳县",
        }, {
            "value": u"太康县", "label": u"太康县",
        }, {
            "value": u"鹿邑县", "label": u"鹿邑县",
        }, {
            "value": u"项城市", "label": u"项城市",
        }, {
            "value": u"经济开发区", "label": u"经济开发区",
        }]
    }, {
        "value": u"驻马店市", "label": u"驻马店市",
        "children": [{
            "value": u"驿城区", "label": u"驿城区",
        }, {
            "value": u"西平县", "label": u"西平县",
        }, {
            "value": u"上蔡县", "label": u"上蔡县",
        }, {
            "value": u"平舆县", "label": u"平舆县",
        }, {
            "value": u"正阳县", "label": u"正阳县",
        }, {
            "value": u"确山县", "label": u"确山县",
        }, {
            "value": u"泌阳县", "label": u"泌阳县",
        }, {
            "value": u"汝南县", "label": u"汝南县",
        }, {
            "value": u"遂平县", "label": u"遂平县",
        }, {
            "value": u"新蔡县", "label": u"新蔡县",
        }]
    }, {
        "value": u"省直辖县", "label": u"省直辖县",
        "children": [{
            "value": u"济源市", "label": u"济源市",
        }]
    }]
    }, {
    "value": u"湖北省", "label": u"湖北省",
    "children": [{
        "value": u"武汉市", "label": u"武汉市",
        "children": [{
            "value": u"江岸区", "label": u"江岸区",
        }, {
            "value": u"江汉区", "label": u"江汉区",
        }, {
            "value": u"硚口区", "label": u"硚口区",
        }, {
            "value": u"汉阳区", "label": u"汉阳区",
        }, {
            "value": u"武昌区", "label": u"武昌区",
        }, {
            "value": u"青山区", "label": u"青山区",
        }, {
            "value": u"洪山区", "label": u"洪山区",
        }, {
            "value": u"东西湖区", "label": u"东西湖区",
        }, {
            "value": u"汉南区", "label": u"汉南区",
        }, {
            "value": u"蔡甸区", "label": u"蔡甸区",
        }, {
            "value": u"江夏区", "label": u"江夏区",
        }, {
            "value": u"黄陂区", "label": u"黄陂区",
        }, {
            "value": u"新洲区", "label": u"新洲区",
        }]
    }, {
        "value": u"黄石市", "label": u"黄石市",
        "children": [{
            "value": u"黄石港区", "label": u"黄石港区",
        }, {
            "value": u"西塞山区", "label": u"西塞山区",
        }, {
            "value": u"下陆区", "label": u"下陆区",
        }, {
            "value": u"铁山区", "label": u"铁山区",
        }, {
            "value": u"阳新县", "label": u"阳新县",
        }, {
            "value": u"大冶市", "label": u"大冶市",
        }]
    }, {
        "value": u"十堰市", "label": u"十堰市",
        "children": [{
            "value": u"茅箭区", "label": u"茅箭区",
        }, {
            "value": u"张湾区", "label": u"张湾区",
        }, {
            "value": u"郧阳区", "label": u"郧阳区",
        }, {
            "value": u"郧西县", "label": u"郧西县",
        }, {
            "value": u"竹山县", "label": u"竹山县",
        }, {
            "value": u"竹溪县", "label": u"竹溪县",
        }, {
            "value": u"房县", "label": u"房县",
        }, {
            "value": u"丹江口市", "label": u"丹江口市",
        }]
    }, {
        "value": u"宜昌市", "label": u"宜昌市",
        "children": [{
            "value": u"西陵区", "label": u"西陵区",
        }, {
            "value": u"伍家岗区", "label": u"伍家岗区",
        }, {
            "value": u"点军区", "label": u"点军区",
        }, {
            "value": u"猇亭区", "label": u"猇亭区",
        }, {
            "value": u"夷陵区", "label": u"夷陵区",
        }, {
            "value": u"远安县", "label": u"远安县",
        }, {
            "value": u"兴山县", "label": u"兴山县",
        }, {
            "value": u"秭归县", "label": u"秭归县",
        }, {
            "value": u"长阳土家族自治县", "label": u"长阳土家族自治县",
        }, {
            "value": u"五峰土家族自治县", "label": u"五峰土家族自治县",
        }, {
            "value": u"宜都市", "label": u"宜都市",
        }, {
            "value": u"当阳市", "label": u"当阳市",
        }, {
            "value": u"枝江市", "label": u"枝江市",
        }, {
            "value": u"经济开发区", "label": u"经济开发区",
        }]
    }, {
        "value": u"襄阳市", "label": u"襄阳市",
        "children": [{
            "value": u"襄城区", "label": u"襄城区",
        }, {
            "value": u"樊城区", "label": u"樊城区",
        }, {
            "value": u"襄州区", "label": u"襄州区",
        }, {
            "value": u"南漳县", "label": u"南漳县",
        }, {
            "value": u"谷城县", "label": u"谷城县",
        }, {
            "value": u"保康县", "label": u"保康县",
        }, {
            "value": u"老河口市", "label": u"老河口市",
        }, {
            "value": u"枣阳市", "label": u"枣阳市",
        }, {
            "value": u"宜城市", "label": u"宜城市",
        }]
    }, {
        "value": u"鄂州市", "label": u"鄂州市",
        "children": [{
            "value": u"梁子湖区", "label": u"梁子湖区",
        }, {
            "value": u"华容区", "label": u"华容区",
        }, {
            "value": u"鄂城区", "label": u"鄂城区",
        }]
    }, {
        "value": u"荆门市", "label": u"荆门市",
        "children": [{
            "value": u"东宝区", "label": u"东宝区",
        }, {
            "value": u"掇刀区", "label": u"掇刀区",
        }, {
            "value": u"沙洋县", "label": u"沙洋县",
        }, {
            "value": u"钟祥市", "label": u"钟祥市",
        }, {
            "value": u"京山市", "label": u"京山市",
        }]
    }, {
        "value": u"孝感市", "label": u"孝感市",
        "children": [{
            "value": u"孝南区", "label": u"孝南区",
        }, {
            "value": u"孝昌县", "label": u"孝昌县",
        }, {
            "value": u"大悟县", "label": u"大悟县",
        }, {
            "value": u"云梦县", "label": u"云梦县",
        }, {
            "value": u"应城市", "label": u"应城市",
        }, {
            "value": u"安陆市", "label": u"安陆市",
        }, {
            "value": u"汉川市", "label": u"汉川市",
        }]
    }, {
        "value": u"荆州市", "label": u"荆州市",
        "children": [{
            "value": u"沙市区", "label": u"沙市区",
        }, {
            "value": u"荆州区", "label": u"荆州区",
        }, {
            "value": u"公安县", "label": u"公安县",
        }, {
            "value": u"监利县", "label": u"监利县",
        }, {
            "value": u"江陵县", "label": u"江陵县",
        }, {
            "value": u"石首市", "label": u"石首市",
        }, {
            "value": u"洪湖市", "label": u"洪湖市",
        }, {
            "value": u"松滋市", "label": u"松滋市",
        }]
    }, {
        "value": u"黄冈市", "label": u"黄冈市",
        "children": [{
            "value": u"黄州区", "label": u"黄州区",
        }, {
            "value": u"团风县", "label": u"团风县",
        }, {
            "value": u"红安县", "label": u"红安县",
        }, {
            "value": u"罗田县", "label": u"罗田县",
        }, {
            "value": u"英山县", "label": u"英山县",
        }, {
            "value": u"浠水县", "label": u"浠水县",
        }, {
            "value": u"蕲春县", "label": u"蕲春县",
        }, {
            "value": u"黄梅县", "label": u"黄梅县",
        }, {
            "value": u"麻城市", "label": u"麻城市",
        }, {
            "value": u"武穴市", "label": u"武穴市",
        }]
    }, {
        "value": u"咸宁市", "label": u"咸宁市",
        "children": [{
            "value": u"咸安区", "label": u"咸安区",
        }, {
            "value": u"嘉鱼县", "label": u"嘉鱼县",
        }, {
            "value": u"通城县", "label": u"通城县",
        }, {
            "value": u"崇阳县", "label": u"崇阳县",
        }, {
            "value": u"通山县", "label": u"通山县",
        }, {
            "value": u"赤壁市", "label": u"赤壁市",
        }]
    }, {
        "value": u"随州市", "label": u"随州市",
        "children": [{
            "value": u"曾都区", "label": u"曾都区",
        }, {
            "value": u"随县", "label": u"随县",
        }, {
            "value": u"广水市", "label": u"广水市",
        }]
    }, {
        "value": u"恩施土家族苗族自治州", "label": u"恩施土家族苗族自治州",
        "children": [{
            "value": u"恩施市", "label": u"恩施市",
        }, {
            "value": u"利川市", "label": u"利川市",
        }, {
            "value": u"建始县", "label": u"建始县",
        }, {
            "value": u"巴东县", "label": u"巴东县",
        }, {
            "value": u"宣恩县", "label": u"宣恩县",
        }, {
            "value": u"咸丰县", "label": u"咸丰县",
        }, {
            "value": u"来凤县", "label": u"来凤县",
        }, {
            "value": u"鹤峰县", "label": u"鹤峰县",
        }]
    }, {
        "value": u"省直辖县", "label": u"省直辖县",
        "children": [{
            "value": u"仙桃市", "label": u"仙桃市",
        }, {
            "value": u"潜江市", "label": u"潜江市",
        }, {
            "value": u"天门市", "label": u"天门市",
        }, {
            "value": u"神农架林区", "label": u"神农架林区",
        }]
    }]
    }, {
    "value": u"湖南省", "label": u"湖南省",
    "children": [{
        "value": u"长沙市", "label": u"长沙市",
        "children": [{
            "value": u"芙蓉区", "label": u"芙蓉区",
        }, {
            "value": u"天心区", "label": u"天心区",
        }, {
            "value": u"岳麓区", "label": u"岳麓区",
        }, {
            "value": u"开福区", "label": u"开福区",
        }, {
            "value": u"雨花区", "label": u"雨花区",
        }, {
            "value": u"望城区", "label": u"望城区",
        }, {
            "value": u"长沙县", "label": u"长沙县",
        }, {
            "value": u"浏阳市", "label": u"浏阳市",
        }, {
            "value": u"宁乡市", "label": u"宁乡市",
        }]
    }, {
        "value": u"株洲市", "label": u"株洲市",
        "children": [{
            "value": u"荷塘区", "label": u"荷塘区",
        }, {
            "value": u"芦淞区", "label": u"芦淞区",
        }, {
            "value": u"石峰区", "label": u"石峰区",
        }, {
            "value": u"天元区", "label": u"天元区",
        }, {
            "value": u"渌口区", "label": u"渌口区",
        }, {
            "value": u"攸县", "label": u"攸县",
        }, {
            "value": u"茶陵县", "label": u"茶陵县",
        }, {
            "value": u"炎陵县", "label": u"炎陵县",
        }, {
            "value": u"醴陵市", "label": u"醴陵市",
        }]
    }, {
        "value": u"湘潭市", "label": u"湘潭市",
        "children": [{
            "value": u"雨湖区", "label": u"雨湖区",
        }, {
            "value": u"岳塘区", "label": u"岳塘区",
        }, {
            "value": u"湘潭县", "label": u"湘潭县",
        }, {
            "value": u"湘乡市", "label": u"湘乡市",
        }, {
            "value": u"韶山市", "label": u"韶山市",
        }]
    }, {
        "value": u"衡阳市", "label": u"衡阳市",
        "children": [{
            "value": u"珠晖区", "label": u"珠晖区",
        }, {
            "value": u"雁峰区", "label": u"雁峰区",
        }, {
            "value": u"石鼓区", "label": u"石鼓区",
        }, {
            "value": u"蒸湘区", "label": u"蒸湘区",
        }, {
            "value": u"南岳区", "label": u"南岳区",
        }, {
            "value": u"衡阳县", "label": u"衡阳县",
        }, {
            "value": u"衡南县", "label": u"衡南县",
        }, {
            "value": u"衡山县", "label": u"衡山县",
        }, {
            "value": u"衡东县", "label": u"衡东县",
        }, {
            "value": u"祁东县", "label": u"祁东县",
        }, {
            "value": u"耒阳市", "label": u"耒阳市",
        }, {
            "value": u"常宁市", "label": u"常宁市",
        }]
    }, {
        "value": u"邵阳市", "label": u"邵阳市",
        "children": [{
            "value": u"双清区", "label": u"双清区",
        }, {
            "value": u"大祥区", "label": u"大祥区",
        }, {
            "value": u"北塔区", "label": u"北塔区",
        }, {
            "value": u"邵东县", "label": u"邵东县",
        }, {
            "value": u"新邵县", "label": u"新邵县",
        }, {
            "value": u"邵阳县", "label": u"邵阳县",
        }, {
            "value": u"隆回县", "label": u"隆回县",
        }, {
            "value": u"洞口县", "label": u"洞口县",
        }, {
            "value": u"绥宁县", "label": u"绥宁县",
        }, {
            "value": u"新宁县", "label": u"新宁县",
        }, {
            "value": u"城步苗族自治县", "label": u"城步苗族自治县",
        }, {
            "value": u"武冈市", "label": u"武冈市",
        }]
    }, {
        "value": u"岳阳市", "label": u"岳阳市",
        "children": [{
            "value": u"岳阳楼区", "label": u"岳阳楼区",
        }, {
            "value": u"云溪区", "label": u"云溪区",
        }, {
            "value": u"君山区", "label": u"君山区",
        }, {
            "value": u"岳阳县", "label": u"岳阳县",
        }, {
            "value": u"华容县", "label": u"华容县",
        }, {
            "value": u"湘阴县", "label": u"湘阴县",
        }, {
            "value": u"平江县", "label": u"平江县",
        }, {
            "value": u"汨罗市", "label": u"汨罗市",
        }, {
            "value": u"临湘市", "label": u"临湘市",
        }]
    }, {
        "value": u"常德市", "label": u"常德市",
        "children": [{
            "value": u"武陵区", "label": u"武陵区",
        }, {
            "value": u"鼎城区", "label": u"鼎城区",
        }, {
            "value": u"安乡县", "label": u"安乡县",
        }, {
            "value": u"汉寿县", "label": u"汉寿县",
        }, {
            "value": u"澧县", "label": u"澧县",
        }, {
            "value": u"临澧县", "label": u"临澧县",
        }, {
            "value": u"桃源县", "label": u"桃源县",
        }, {
            "value": u"石门县", "label": u"石门县",
        }, {
            "value": u"津市市", "label": u"津市市",
        }]
    }, {
        "value": u"张家界市", "label": u"张家界市",
        "children": [{
            "value": u"永定区", "label": u"永定区",
        }, {
            "value": u"武陵源区", "label": u"武陵源区",
        }, {
            "value": u"慈利县", "label": u"慈利县",
        }, {
            "value": u"桑植县", "label": u"桑植县",
        }]
    }, {
        "value": u"益阳市", "label": u"益阳市",
        "children": [{
            "value": u"资阳区", "label": u"资阳区",
        }, {
            "value": u"赫山区", "label": u"赫山区",
        }, {
            "value": u"南县", "label": u"南县",
        }, {
            "value": u"桃江县", "label": u"桃江县",
        }, {
            "value": u"安化县", "label": u"安化县",
        }, {
            "value": u"沅江市", "label": u"沅江市",
        }]
    }, {
        "value": u"郴州市", "label": u"郴州市",
        "children": [{
            "value": u"北湖区", "label": u"北湖区",
        }, {
            "value": u"苏仙区", "label": u"苏仙区",
        }, {
            "value": u"桂阳县", "label": u"桂阳县",
        }, {
            "value": u"宜章县", "label": u"宜章县",
        }, {
            "value": u"永兴县", "label": u"永兴县",
        }, {
            "value": u"嘉禾县", "label": u"嘉禾县",
        }, {
            "value": u"临武县", "label": u"临武县",
        }, {
            "value": u"汝城县", "label": u"汝城县",
        }, {
            "value": u"桂东县", "label": u"桂东县",
        }, {
            "value": u"安仁县", "label": u"安仁县",
        }, {
            "value": u"资兴市", "label": u"资兴市",
        }]
    }, {
        "value": u"永州市", "label": u"永州市",
        "children": [{
            "value": u"零陵区", "label": u"零陵区",
        }, {
            "value": u"冷水滩区", "label": u"冷水滩区",
        }, {
            "value": u"祁阳县", "label": u"祁阳县",
        }, {
            "value": u"东安县", "label": u"东安县",
        }, {
            "value": u"双牌县", "label": u"双牌县",
        }, {
            "value": u"道县", "label": u"道县",
        }, {
            "value": u"江永县", "label": u"江永县",
        }, {
            "value": u"宁远县", "label": u"宁远县",
        }, {
            "value": u"蓝山县", "label": u"蓝山县",
        }, {
            "value": u"新田县", "label": u"新田县",
        }, {
            "value": u"江华瑶族自治县", "label": u"江华瑶族自治县",
        }]
    }, {
        "value": u"怀化市", "label": u"怀化市",
        "children": [{
            "value": u"鹤城区", "label": u"鹤城区",
        }, {
            "value": u"中方县", "label": u"中方县",
        }, {
            "value": u"沅陵县", "label": u"沅陵县",
        }, {
            "value": u"辰溪县", "label": u"辰溪县",
        }, {
            "value": u"溆浦县", "label": u"溆浦县",
        }, {
            "value": u"会同县", "label": u"会同县",
        }, {
            "value": u"麻阳苗族自治县", "label": u"麻阳苗族自治县",
        }, {
            "value": u"新晃侗族自治县", "label": u"新晃侗族自治县",
        }, {
            "value": u"芷江侗族自治县", "label": u"芷江侗族自治县",
        }, {
            "value": u"靖州苗族侗族自治县", "label": u"靖州苗族侗族自治县",
        }, {
            "value": u"通道侗族自治县", "label": u"通道侗族自治县",
        }, {
            "value": u"洪江市", "label": u"洪江市",
        }]
    }, {
        "value": u"娄底市", "label": u"娄底市",
        "children": [{
            "value": u"娄星区", "label": u"娄星区",
        }, {
            "value": u"双峰县", "label": u"双峰县",
        }, {
            "value": u"新化县", "label": u"新化县",
        }, {
            "value": u"冷水江市", "label": u"冷水江市",
        }, {
            "value": u"涟源市", "label": u"涟源市",
        }]
    }, {
        "value": u"湘西土家族苗族自治州", "label": u"湘西土家族苗族自治州",
        "children": [{
            "value": u"吉首市", "label": u"吉首市",
        }, {
            "value": u"泸溪县", "label": u"泸溪县",
        }, {
            "value": u"凤凰县", "label": u"凤凰县",
        }, {
            "value": u"花垣县", "label": u"花垣县",
        }, {
            "value": u"保靖县", "label": u"保靖县",
        }, {
            "value": u"古丈县", "label": u"古丈县",
        }, {
            "value": u"永顺县", "label": u"永顺县",
        }, {
            "value": u"龙山县", "label": u"龙山县",
        }]
    }]
    }, {
    "value": u"广东省", "label": u"广东省",
    "children": [{
        "value": u"广州市", "label": u"广州市",
        "children": [{
            "value": u"荔湾区", "label": u"荔湾区",
        }, {
            "value": u"越秀区", "label": u"越秀区",
        }, {
            "value": u"海珠区", "label": u"海珠区",
        }, {
            "value": u"天河区", "label": u"天河区",
        }, {
            "value": u"白云区", "label": u"白云区",
        }, {
            "value": u"黄埔区", "label": u"黄埔区",
        }, {
            "value": u"番禺区", "label": u"番禺区",
        }, {
            "value": u"花都区", "label": u"花都区",
        }, {
            "value": u"南沙区", "label": u"南沙区",
        }, {
            "value": u"从化区", "label": u"从化区",
        }, {
            "value": u"增城区", "label": u"增城区",
        }]
    }, {
        "value": u"韶关市", "label": u"韶关市",
        "children": [{
            "value": u"武江区", "label": u"武江区",
        }, {
            "value": u"浈江区", "label": u"浈江区",
        }, {
            "value": u"曲江区", "label": u"曲江区",
        }, {
            "value": u"始兴县", "label": u"始兴县",
        }, {
            "value": u"仁化县", "label": u"仁化县",
        }, {
            "value": u"翁源县", "label": u"翁源县",
        }, {
            "value": u"乳源瑶族自治县", "label": u"乳源瑶族自治县",
        }, {
            "value": u"新丰县", "label": u"新丰县",
        }, {
            "value": u"乐昌市", "label": u"乐昌市",
        }, {
            "value": u"南雄市", "label": u"南雄市",
        }]
    }, {
        "value": u"深圳市", "label": u"深圳市",
        "children": [{
            "value": u"罗湖区", "label": u"罗湖区",
        }, {
            "value": u"福田区", "label": u"福田区",
        }, {
            "value": u"南山区", "label": u"南山区",
        }, {
            "value": u"宝安区", "label": u"宝安区",
        }, {
            "value": u"龙岗区", "label": u"龙岗区",
        }, {
            "value": u"盐田区", "label": u"盐田区",
        }, {
            "value": u"龙华区", "label": u"龙华区",
        }, {
            "value": u"坪山区", "label": u"坪山区",
        }, {
            "value": u"光明区", "label": u"光明区",
        }]
    }, {
        "value": u"珠海市", "label": u"珠海市",
        "children": [{
            "value": u"香洲区", "label": u"香洲区",
        }, {
            "value": u"斗门区", "label": u"斗门区",
        }, {
            "value": u"金湾区", "label": u"金湾区",
        }]
    }, {
        "value": u"汕头市", "label": u"汕头市",
        "children": [{
            "value": u"龙湖区", "label": u"龙湖区",
        }, {
            "value": u"金平区", "label": u"金平区",
        }, {
            "value": u"濠江区", "label": u"濠江区",
        }, {
            "value": u"潮阳区", "label": u"潮阳区",
        }, {
            "value": u"潮南区", "label": u"潮南区",
        }, {
            "value": u"澄海区", "label": u"澄海区",
        }, {
            "value": u"南澳县", "label": u"南澳县",
        }]
    }, {
        "value": u"佛山市", "label": u"佛山市",
        "children": [{
            "value": u"禅城区", "label": u"禅城区",
        }, {
            "value": u"南海区", "label": u"南海区",
        }, {
            "value": u"顺德区", "label": u"顺德区",
        }, {
            "value": u"三水区", "label": u"三水区",
        }, {
            "value": u"高明区", "label": u"高明区",
        }]
    }, {
        "value": u"江门市", "label": u"江门市",
        "children": [{
            "value": u"蓬江区", "label": u"蓬江区",
        }, {
            "value": u"江海区", "label": u"江海区",
        }, {
            "value": u"新会区", "label": u"新会区",
        }, {
            "value": u"台山市", "label": u"台山市",
        }, {
            "value": u"开平市", "label": u"开平市",
        }, {
            "value": u"鹤山市", "label": u"鹤山市",
        }, {
            "value": u"恩平市", "label": u"恩平市",
        }]
    }, {
        "value": u"湛江市", "label": u"湛江市",
        "children": [{
            "value": u"赤坎区", "label": u"赤坎区",
        }, {
            "value": u"霞山区", "label": u"霞山区",
        }, {
            "value": u"坡头区", "label": u"坡头区",
        }, {
            "value": u"麻章区", "label": u"麻章区",
        }, {
            "value": u"遂溪县", "label": u"遂溪县",
        }, {
            "value": u"徐闻县", "label": u"徐闻县",
        }, {
            "value": u"廉江市", "label": u"廉江市",
        }, {
            "value": u"雷州市", "label": u"雷州市",
        }, {
            "value": u"吴川市", "label": u"吴川市",
        }, {
            "value": u"经济技术开发区", "label": u"经济技术开发区",
        }]
    }, {
        "value": u"茂名市", "label": u"茂名市",
        "children": [{
            "value": u"茂南区", "label": u"茂南区",
        }, {
            "value": u"电白区", "label": u"电白区",
        }, {
            "value": u"高州市", "label": u"高州市",
        }, {
            "value": u"化州市", "label": u"化州市",
        }, {
            "value": u"信宜市", "label": u"信宜市",
        }]
    }, {
        "value": u"肇庆市", "label": u"肇庆市",
        "children": [{
            "value": u"端州区", "label": u"端州区",
        }, {
            "value": u"鼎湖区", "label": u"鼎湖区",
        }, {
            "value": u"高要区", "label": u"高要区",
        }, {
            "value": u"广宁县", "label": u"广宁县",
        }, {
            "value": u"怀集县", "label": u"怀集县",
        }, {
            "value": u"封开县", "label": u"封开县",
        }, {
            "value": u"德庆县", "label": u"德庆县",
        }, {
            "value": u"四会市", "label": u"四会市",
        }]
    }, {
        "value": u"惠州市", "label": u"惠州市",
        "children": [{
            "value": u"惠城区", "label": u"惠城区",
        }, {
            "value": u"惠阳区", "label": u"惠阳区",
        }, {
            "value": u"博罗县", "label": u"博罗县",
        }, {
            "value": u"惠东县", "label": u"惠东县",
        }, {
            "value": u"龙门县", "label": u"龙门县",
        }]
    }, {
        "value": u"梅州市", "label": u"梅州市",
        "children": [{
            "value": u"梅江区", "label": u"梅江区",
        }, {
            "value": u"梅县区", "label": u"梅县区",
        }, {
            "value": u"大埔县", "label": u"大埔县",
        }, {
            "value": u"丰顺县", "label": u"丰顺县",
        }, {
            "value": u"五华县", "label": u"五华县",
        }, {
            "value": u"平远县", "label": u"平远县",
        }, {
            "value": u"蕉岭县", "label": u"蕉岭县",
        }, {
            "value": u"兴宁市", "label": u"兴宁市",
        }]
    }, {
        "value": u"汕尾市", "label": u"汕尾市",
        "children": [{
            "value": u"城区", "label": u"城区",
        }, {
            "value": u"海丰县", "label": u"海丰县",
        }, {
            "value": u"陆河县", "label": u"陆河县",
        }, {
            "value": u"陆丰市", "label": u"陆丰市",
        }]
    }, {
        "value": u"河源市", "label": u"河源市",
        "children": [{
            "value": u"源城区", "label": u"源城区",
        }, {
            "value": u"紫金县", "label": u"紫金县",
        }, {
            "value": u"龙川县", "label": u"龙川县",
        }, {
            "value": u"连平县", "label": u"连平县",
        }, {
            "value": u"和平县", "label": u"和平县",
        }, {
            "value": u"东源县", "label": u"东源县",
        }]
    }, {
        "value": u"阳江市", "label": u"阳江市",
        "children": [{
            "value": u"江城区", "label": u"江城区",
        }, {
            "value": u"阳东区", "label": u"阳东区",
        }, {
            "value": u"阳西县", "label": u"阳西县",
        }, {
            "value": u"阳春市", "label": u"阳春市",
        }]
    }, {
        "value": u"清远市", "label": u"清远市",
        "children": [{
            "value": u"清城区", "label": u"清城区",
        }, {
            "value": u"清新区", "label": u"清新区",
        }, {
            "value": u"佛冈县", "label": u"佛冈县",
        }, {
            "value": u"阳山县", "label": u"阳山县",
        }, {
            "value": u"连山壮族瑶族自治县", "label": u"连山壮族瑶族自治县",
        }, {
            "value": u"连南瑶族自治县", "label": u"连南瑶族自治县",
        }, {
            "value": u"英德市", "label": u"英德市",
        }, {
            "value": u"连州市", "label": u"连州市",
        }]
    }, {
        "value": u"东莞市", "label": u"东莞市",
        "children": [{
            "value": u"中堂镇", "label": u"中堂镇",
        }, {
            "value": u"南城街道办事处", "label": u"南城街道办事处",
        }, {
            "value": u"长安镇", "label": u"长安镇",
        }, {
            "value": u"东坑镇", "label": u"东坑镇",
        }, {
            "value": u"樟木头镇", "label": u"樟木头镇",
        }, {
            "value": u"莞城街道办事处", "label": u"莞城街道办事处",
        }, {
            "value": u"石龙镇", "label": u"石龙镇",
        }, {
            "value": u"桥头镇", "label": u"桥头镇",
        }, {
            "value": u"万江街道办事处", "label": u"万江街道办事处",
        }, {
            "value": u"麻涌镇", "label": u"麻涌镇",
        }, {
            "value": u"虎门镇", "label": u"虎门镇",
        }, {
            "value": u"谢岗镇", "label": u"谢岗镇",
        }, {
            "value": u"石碣镇", "label": u"石碣镇",
        }, {
            "value": u"茶山镇", "label": u"茶山镇",
        }, {
            "value": u"东城街道办事处", "label": u"东城街道办事处",
        }, {
            "value": u"洪梅镇", "label": u"洪梅镇",
        }, {
            "value": u"道滘镇", "label": u"道滘镇",
        }, {
            "value": u"高埗镇", "label": u"高埗镇",
        }, {
            "value": u"企石镇", "label": u"企石镇",
        }, {
            "value": u"凤岗镇", "label": u"凤岗镇",
        }, {
            "value": u"大岭山镇", "label": u"大岭山镇",
        }, {
            "value": u"松山湖管委会", "label": u"松山湖管委会",
        }, {
            "value": u"清溪镇", "label": u"清溪镇",
        }, {
            "value": u"望牛墩镇", "label": u"望牛墩镇",
        }, {
            "value": u"厚街镇", "label": u"厚街镇",
        }, {
            "value": u"常平镇", "label": u"常平镇",
        }, {
            "value": u"寮步镇", "label": u"寮步镇",
        }, {
            "value": u"石排镇", "label": u"石排镇",
        }, {
            "value": u"横沥镇", "label": u"横沥镇",
        }, {
            "value": u"塘厦镇", "label": u"塘厦镇",
        }, {
            "value": u"黄江镇", "label": u"黄江镇",
        }, {
            "value": u"大朗镇", "label": u"大朗镇",
        }, {
            "value": u"东莞港", "label": u"东莞港",
        }, {
            "value": u"东莞生态园", "label": u"东莞生态园",
        }, {
            "value": u"沙田镇", "label": u"沙田镇",
        }]
    }, {
        "value": u"中山市", "label": u"中山市",
        "children": [{
            "value": u"南头镇", "label": u"南头镇",
        }, {
            "value": u"神湾镇", "label": u"神湾镇",
        }, {
            "value": u"东凤镇", "label": u"东凤镇",
        }, {
            "value": u"五桂山街道办事处", "label": u"五桂山街道办事处",
        }, {
            "value": u"黄圃镇", "label": u"黄圃镇",
        }, {
            "value": u"小榄镇", "label": u"小榄镇",
        }, {
            "value": u"石岐区街道办事处", "label": u"石岐区街道办事处",
        }, {
            "value": u"横栏镇", "label": u"横栏镇",
        }, {
            "value": u"三角镇", "label": u"三角镇",
        }, {
            "value": u"三乡镇", "label": u"三乡镇",
        }, {
            "value": u"港口镇", "label": u"港口镇",
        }, {
            "value": u"沙溪镇", "label": u"沙溪镇",
        }, {
            "value": u"板芙镇", "label": u"板芙镇",
        }, {
            "value": u"东升镇", "label": u"东升镇",
        }, {
            "value": u"阜沙镇", "label": u"阜沙镇",
        }, {
            "value": u"民众镇", "label": u"民众镇",
        }, {
            "value": u"东区街道办事处", "label": u"东区街道办事处",
        }, {
            "value": u"火炬开发区街道办事处", "label": u"火炬开发区街道办事处",
        }, {
            "value": u"西区街道办事处", "label": u"西区街道办事处",
        }, {
            "value": u"南区街道办事处", "label": u"南区街道办事处",
        }, {
            "value": u"古镇镇", "label": u"古镇镇",
        }, {
            "value": u"坦洲镇", "label": u"坦洲镇",
        }, {
            "value": u"大涌镇", "label": u"大涌镇",
        }, {
            "value": u"南朗镇", "label": u"南朗镇",
        }]
    }, {
        "value": u"潮州市", "label": u"潮州市",
        "children": [{
            "value": u"湘桥区", "label": u"湘桥区",
        }, {
            "value": u"潮安区", "label": u"潮安区",
        }, {
            "value": u"饶平县", "label": u"饶平县",
        }]
    }, {
        "value": u"揭阳市", "label": u"揭阳市",
        "children": [{
            "value": u"榕城区", "label": u"榕城区",
        }, {
            "value": u"揭东区", "label": u"揭东区",
        }, {
            "value": u"揭西县", "label": u"揭西县",
        }, {
            "value": u"惠来县", "label": u"惠来县",
        }, {
            "value": u"普宁市", "label": u"普宁市",
        }]
    }, {
        "value": u"云浮市", "label": u"云浮市",
        "children": [{
            "value": u"云城区", "label": u"云城区",
        }, {
            "value": u"云安区", "label": u"云安区",
        }, {
            "value": u"新兴县", "label": u"新兴县",
        }, {
            "value": u"郁南县", "label": u"郁南县",
        }, {
            "value": u"罗定市", "label": u"罗定市",
        }]
    }]
    }, {
    "value": u"广西壮族自治区", "label": u"广西壮族自治区",
    "children": [{
        "value": u"南宁市", "label": u"南宁市",
        "children": [{
            "value": u"兴宁区", "label": u"兴宁区",
        }, {
            "value": u"青秀区", "label": u"青秀区",
        }, {
            "value": u"江南区", "label": u"江南区",
        }, {
            "value": u"西乡塘区", "label": u"西乡塘区",
        }, {
            "value": u"良庆区", "label": u"良庆区",
        }, {
            "value": u"邕宁区", "label": u"邕宁区",
        }, {
            "value": u"武鸣区", "label": u"武鸣区",
        }, {
            "value": u"隆安县", "label": u"隆安县",
        }, {
            "value": u"马山县", "label": u"马山县",
        }, {
            "value": u"上林县", "label": u"上林县",
        }, {
            "value": u"宾阳县", "label": u"宾阳县",
        }, {
            "value": u"横县", "label": u"横县",
        }]
    }, {
        "value": u"柳州市", "label": u"柳州市",
        "children": [{
            "value": u"城中区", "label": u"城中区",
        }, {
            "value": u"鱼峰区", "label": u"鱼峰区",
        }, {
            "value": u"柳南区", "label": u"柳南区",
        }, {
            "value": u"柳北区", "label": u"柳北区",
        }, {
            "value": u"柳江区", "label": u"柳江区",
        }, {
            "value": u"柳城县", "label": u"柳城县",
        }, {
            "value": u"鹿寨县", "label": u"鹿寨县",
        }, {
            "value": u"融安县", "label": u"融安县",
        }, {
            "value": u"融水苗族自治县", "label": u"融水苗族自治县",
        }, {
            "value": u"三江侗族自治县", "label": u"三江侗族自治县",
        }]
    }, {
        "value": u"桂林市", "label": u"桂林市",
        "children": [{
            "value": u"秀峰区", "label": u"秀峰区",
        }, {
            "value": u"叠彩区", "label": u"叠彩区",
        }, {
            "value": u"象山区", "label": u"象山区",
        }, {
            "value": u"七星区", "label": u"七星区",
        }, {
            "value": u"雁山区", "label": u"雁山区",
        }, {
            "value": u"临桂区", "label": u"临桂区",
        }, {
            "value": u"阳朔县", "label": u"阳朔县",
        }, {
            "value": u"灵川县", "label": u"灵川县",
        }, {
            "value": u"全州县", "label": u"全州县",
        }, {
            "value": u"兴安县", "label": u"兴安县",
        }, {
            "value": u"永福县", "label": u"永福县",
        }, {
            "value": u"灌阳县", "label": u"灌阳县",
        }, {
            "value": u"龙胜各族自治县", "label": u"龙胜各族自治县",
        }, {
            "value": u"资源县", "label": u"资源县",
        }, {
            "value": u"平乐县", "label": u"平乐县",
        }, {
            "value": u"恭城瑶族自治县", "label": u"恭城瑶族自治县",
        }, {
            "value": u"荔浦市", "label": u"荔浦市",
        }]
    }, {
        "value": u"梧州市", "label": u"梧州市",
        "children": [{
            "value": u"万秀区", "label": u"万秀区",
        }, {
            "value": u"长洲区", "label": u"长洲区",
        }, {
            "value": u"龙圩区", "label": u"龙圩区",
        }, {
            "value": u"苍梧县", "label": u"苍梧县",
        }, {
            "value": u"藤县", "label": u"藤县",
        }, {
            "value": u"蒙山县", "label": u"蒙山县",
        }, {
            "value": u"岑溪市", "label": u"岑溪市",
        }]
    }, {
        "value": u"北海市", "label": u"北海市",
        "children": [{
            "value": u"海城区", "label": u"海城区",
        }, {
            "value": u"银海区", "label": u"银海区",
        }, {
            "value": u"铁山港区", "label": u"铁山港区",
        }, {
            "value": u"合浦县", "label": u"合浦县",
        }]
    }, {
        "value": u"防城港市", "label": u"防城港市",
        "children": [{
            "value": u"港口区", "label": u"港口区",
        }, {
            "value": u"防城区", "label": u"防城区",
        }, {
            "value": u"上思县", "label": u"上思县",
        }, {
            "value": u"东兴市", "label": u"东兴市",
        }]
    }, {
        "value": u"钦州市", "label": u"钦州市",
        "children": [{
            "value": u"钦南区", "label": u"钦南区",
        }, {
            "value": u"钦北区", "label": u"钦北区",
        }, {
            "value": u"灵山县", "label": u"灵山县",
        }, {
            "value": u"浦北县", "label": u"浦北县",
        }]
    }, {
        "value": u"贵港市", "label": u"贵港市",
        "children": [{
            "value": u"港北区", "label": u"港北区",
        }, {
            "value": u"港南区", "label": u"港南区",
        }, {
            "value": u"覃塘区", "label": u"覃塘区",
        }, {
            "value": u"平南县", "label": u"平南县",
        }, {
            "value": u"桂平市", "label": u"桂平市",
        }]
    }, {
        "value": u"玉林市", "label": u"玉林市",
        "children": [{
            "value": u"玉州区", "label": u"玉州区",
        }, {
            "value": u"福绵区", "label": u"福绵区",
        }, {
            "value": u"容县", "label": u"容县",
        }, {
            "value": u"陆川县", "label": u"陆川县",
        }, {
            "value": u"博白县", "label": u"博白县",
        }, {
            "value": u"兴业县", "label": u"兴业县",
        }, {
            "value": u"北流市", "label": u"北流市",
        }]
    }, {
        "value": u"百色市", "label": u"百色市",
        "children": [{
            "value": u"右江区", "label": u"右江区",
        }, {
            "value": u"田阳县", "label": u"田阳县",
        }, {
            "value": u"田东县", "label": u"田东县",
        }, {
            "value": u"平果县", "label": u"平果县",
        }, {
            "value": u"德保县", "label": u"德保县",
        }, {
            "value": u"那坡县", "label": u"那坡县",
        }, {
            "value": u"凌云县", "label": u"凌云县",
        }, {
            "value": u"乐业县", "label": u"乐业县",
        }, {
            "value": u"田林县", "label": u"田林县",
        }, {
            "value": u"西林县", "label": u"西林县",
        }, {
            "value": u"隆林各族自治县", "label": u"隆林各族自治县",
        }, {
            "value": u"靖西市", "label": u"靖西市",
        }]
    }, {
        "value": u"贺州市", "label": u"贺州市",
        "children": [{
            "value": u"八步区", "label": u"八步区",
        }, {
            "value": u"平桂区", "label": u"平桂区",
        }, {
            "value": u"昭平县", "label": u"昭平县",
        }, {
            "value": u"钟山县", "label": u"钟山县",
        }, {
            "value": u"富川瑶族自治县", "label": u"富川瑶族自治县",
        }]
    }, {
        "value": u"河池市", "label": u"河池市",
        "children": [{
            "value": u"金城江区", "label": u"金城江区",
        }, {
            "value": u"宜州区", "label": u"宜州区",
        }, {
            "value": u"南丹县", "label": u"南丹县",
        }, {
            "value": u"天峨县", "label": u"天峨县",
        }, {
            "value": u"凤山县", "label": u"凤山县",
        }, {
            "value": u"东兰县", "label": u"东兰县",
        }, {
            "value": u"罗城仫佬族自治县", "label": u"罗城仫佬族自治县",
        }, {
            "value": u"环江毛南族自治县", "label": u"环江毛南族自治县",
        }, {
            "value": u"巴马瑶族自治县", "label": u"巴马瑶族自治县",
        }, {
            "value": u"都安瑶族自治县", "label": u"都安瑶族自治县",
        }, {
            "value": u"大化瑶族自治县", "label": u"大化瑶族自治县",
        }]
    }, {
        "value": u"来宾市", "label": u"来宾市",
        "children": [{
            "value": u"兴宾区", "label": u"兴宾区",
        }, {
            "value": u"忻城县", "label": u"忻城县",
        }, {
            "value": u"象州县", "label": u"象州县",
        }, {
            "value": u"武宣县", "label": u"武宣县",
        }, {
            "value": u"金秀瑶族自治县", "label": u"金秀瑶族自治县",
        }, {
            "value": u"合山市", "label": u"合山市",
        }]
    }, {
        "value": u"崇左市", "label": u"崇左市",
        "children": [{
            "value": u"江州区", "label": u"江州区",
        }, {
            "value": u"扶绥县", "label": u"扶绥县",
        }, {
            "value": u"宁明县", "label": u"宁明县",
        }, {
            "value": u"龙州县", "label": u"龙州县",
        }, {
            "value": u"大新县", "label": u"大新县",
        }, {
            "value": u"天等县", "label": u"天等县",
        }, {
            "value": u"凭祥市", "label": u"凭祥市",
        }]
    }]
    }, {
    "value": u"海南省", "label": u"海南省",
    "children": [{
        "value": u"海口市", "label": u"海口市",
        "children": [{
            "value": u"秀英区", "label": u"秀英区",
        }, {
            "value": u"龙华区", "label": u"龙华区",
        }, {
            "value": u"琼山区", "label": u"琼山区",
        }, {
            "value": u"美兰区", "label": u"美兰区",
        }]
    }, {
        "value": u"三亚市", "label": u"三亚市",
        "children": [{
            "value": u"海棠区", "label": u"海棠区",
        }, {
            "value": u"吉阳区", "label": u"吉阳区",
        }, {
            "value": u"天涯区", "label": u"天涯区",
        }, {
            "value": u"崖州区", "label": u"崖州区",
        }]
    }, {
        "value": u"三沙市", "label": u"三沙市",
        "children": [{
            "value": u"西沙群岛", "label": u"西沙群岛",
        }, {
            "value": u"南沙群岛", "label": u"南沙群岛",
        }, {
            "value": u"中沙群岛的岛礁及其海域", "label": u"中沙群岛的岛礁及其海域",
        }]
    }, {
        "value": u"儋州市", "label": u"儋州市",
        "children": [{
            "value": u"那大镇", "label": u"那大镇",
        }, {
            "value": u"和庆镇", "label": u"和庆镇",
        }, {
            "value": u"南丰镇", "label": u"南丰镇",
        }, {
            "value": u"大成镇", "label": u"大成镇",
        }, {
            "value": u"雅星镇", "label": u"雅星镇",
        }, {
            "value": u"兰洋镇", "label": u"兰洋镇",
        }, {
            "value": u"光村镇", "label": u"光村镇",
        }, {
            "value": u"木棠镇", "label": u"木棠镇",
        }, {
            "value": u"海头镇", "label": u"海头镇",
        }, {
            "value": u"峨蔓镇", "label": u"峨蔓镇",
        }, {
            "value": u"王五镇", "label": u"王五镇",
        }, {
            "value": u"白马井镇", "label": u"白马井镇",
        }, {
            "value": u"中和镇", "label": u"中和镇",
        }, {
            "value": u"排浦镇", "label": u"排浦镇",
        }, {
            "value": u"东成镇", "label": u"东成镇",
        }, {
            "value": u"新州镇", "label": u"新州镇",
        }, {
            "value": u"洋浦经济开发区", "label": u"洋浦经济开发区",
        }, {
            "value": u"华南热作学院", "label": u"华南热作学院",
        }]
    }, {
        "value": u"省直辖县", "label": u"省直辖县",
        "children": [{
            "value": u"五指山市", "label": u"五指山市",
        }, {
            "value": u"琼海市", "label": u"琼海市",
        }, {
            "value": u"文昌市", "label": u"文昌市",
        }, {
            "value": u"万宁市", "label": u"万宁市",
        }, {
            "value": u"东方市", "label": u"东方市",
        }, {
            "value": u"定安县", "label": u"定安县",
        }, {
            "value": u"屯昌县", "label": u"屯昌县",
        }, {
            "value": u"澄迈县", "label": u"澄迈县",
        }, {
            "value": u"临高县", "label": u"临高县",
        }, {
            "value": u"白沙黎族自治县", "label": u"白沙黎族自治县",
        }, {
            "value": u"昌江黎族自治县", "label": u"昌江黎族自治县",
        }, {
            "value": u"乐东黎族自治县", "label": u"乐东黎族自治县",
        }, {
            "value": u"陵水黎族自治县", "label": u"陵水黎族自治县",
        }, {
            "value": u"保亭黎族苗族自治县", "label": u"保亭黎族苗族自治县",
        }, {
            "value": u"琼中黎族苗族自治县", "label": u"琼中黎族苗族自治县",
        }]
    }]
    }, {
    "value": u"重庆市", "label": u"重庆市",
    "children": [{
        "value": u"重庆市", "label": u"重庆市",
        "children": [{
            "value": u"万州区", "label": u"万州区",
        }, {
            "value": u"涪陵区", "label": u"涪陵区",
        }, {
            "value": u"渝中区", "label": u"渝中区",
        }, {
            "value": u"大渡口区", "label": u"大渡口区",
        }, {
            "value": u"江北区", "label": u"江北区",
        }, {
            "value": u"沙坪坝区", "label": u"沙坪坝区",
        }, {
            "value": u"九龙坡区", "label": u"九龙坡区",
        }, {
            "value": u"南岸区", "label": u"南岸区",
        }, {
            "value": u"北碚区", "label": u"北碚区",
        }, {
            "value": u"綦江区", "label": u"綦江区",
        }, {
            "value": u"大足区", "label": u"大足区",
        }, {
            "value": u"渝北区", "label": u"渝北区",
        }, {
            "value": u"巴南区", "label": u"巴南区",
        }, {
            "value": u"黔江区", "label": u"黔江区",
        }, {
            "value": u"长寿区", "label": u"长寿区",
        }, {
            "value": u"江津区", "label": u"江津区",
        }, {
            "value": u"合川区", "label": u"合川区",
        }, {
            "value": u"永川区", "label": u"永川区",
        }, {
            "value": u"南川区", "label": u"南川区",
        }, {
            "value": u"璧山区", "label": u"璧山区",
        }, {
            "value": u"铜梁区", "label": u"铜梁区",
        }, {
            "value": u"潼南区", "label": u"潼南区",
        }, {
            "value": u"荣昌区", "label": u"荣昌区",
        }, {
            "value": u"开州区", "label": u"开州区",
        }, {
            "value": u"梁平区", "label": u"梁平区",
        }, {
            "value": u"武隆区", "label": u"武隆区",
        }]
    }, {
        "value": u"县", "label": u"县",
        "children": [{
            "value": u"城口县", "label": u"城口县",
        }, {
            "value": u"丰都县", "label": u"丰都县",
        }, {
            "value": u"垫江县", "label": u"垫江县",
        }, {
            "value": u"忠县", "label": u"忠县",
        }, {
            "value": u"云阳县", "label": u"云阳县",
        }, {
            "value": u"奉节县", "label": u"奉节县",
        }, {
            "value": u"巫山县", "label": u"巫山县",
        }, {
            "value": u"巫溪县", "label": u"巫溪县",
        }, {
            "value": u"石柱土家族自治县", "label": u"石柱土家族自治县",
        }, {
            "value": u"秀山土家族苗族自治县", "label": u"秀山土家族苗族自治县",
        }, {
            "value": u"酉阳土家族苗族自治县", "label": u"酉阳土家族苗族自治县",
        }, {
            "value": u"彭水苗族土家族自治县", "label": u"彭水苗族土家族自治县",
        }]
    }]
    }, {
    "value": u"四川省", "label": u"四川省",
    "children": [{
        "value": u"成都市", "label": u"成都市",
        "children": [{
            "value": u"锦江区", "label": u"锦江区",
        }, {
            "value": u"青羊区", "label": u"青羊区",
        }, {
            "value": u"金牛区", "label": u"金牛区",
        }, {
            "value": u"武侯区", "label": u"武侯区",
        }, {
            "value": u"成华区", "label": u"成华区",
        }, {
            "value": u"龙泉驿区", "label": u"龙泉驿区",
        }, {
            "value": u"青白江区", "label": u"青白江区",
        }, {
            "value": u"新都区", "label": u"新都区",
        }, {
            "value": u"温江区", "label": u"温江区",
        }, {
            "value": u"双流区", "label": u"双流区",
        }, {
            "value": u"郫都区", "label": u"郫都区",
        }, {
            "value": u"金堂县", "label": u"金堂县",
        }, {
            "value": u"大邑县", "label": u"大邑县",
        }, {
            "value": u"蒲江县", "label": u"蒲江县",
        }, {
            "value": u"新津县", "label": u"新津县",
        }, {
            "value": u"都江堰市", "label": u"都江堰市",
        }, {
            "value": u"彭州市", "label": u"彭州市",
        }, {
            "value": u"邛崃市", "label": u"邛崃市",
        }, {
            "value": u"崇州市", "label": u"崇州市",
        }, {
            "value": u"简阳市", "label": u"简阳市",
        }, {
            "value": u"高新区", "label": u"高新区",
        }]
    }, {
        "value": u"自贡市", "label": u"自贡市",
        "children": [{
            "value": u"自流井区", "label": u"自流井区",
        }, {
            "value": u"贡井区", "label": u"贡井区",
        }, {
            "value": u"大安区", "label": u"大安区",
        }, {
            "value": u"沿滩区", "label": u"沿滩区",
        }, {
            "value": u"荣县", "label": u"荣县",
        }, {
            "value": u"富顺县", "label": u"富顺县",
        }]
    }, {
        "value": u"攀枝花市", "label": u"攀枝花市",
        "children": [{
            "value": u"东区", "label": u"东区",
        }, {
            "value": u"西区", "label": u"西区",
        }, {
            "value": u"仁和区", "label": u"仁和区",
        }, {
            "value": u"米易县", "label": u"米易县",
        }, {
            "value": u"盐边县", "label": u"盐边县",
        }]
    }, {
        "value": u"泸州市", "label": u"泸州市",
        "children": [{
            "value": u"江阳区", "label": u"江阳区",
        }, {
            "value": u"纳溪区", "label": u"纳溪区",
        }, {
            "value": u"龙马潭区", "label": u"龙马潭区",
        }, {
            "value": u"泸县", "label": u"泸县",
        }, {
            "value": u"合江县", "label": u"合江县",
        }, {
            "value": u"叙永县", "label": u"叙永县",
        }, {
            "value": u"古蔺县", "label": u"古蔺县",
        }]
    }, {
        "value": u"德阳市", "label": u"德阳市",
        "children": [{
            "value": u"旌阳区", "label": u"旌阳区",
        }, {
            "value": u"罗江区", "label": u"罗江区",
        }, {
            "value": u"中江县", "label": u"中江县",
        }, {
            "value": u"广汉市", "label": u"广汉市",
        }, {
            "value": u"什邡市", "label": u"什邡市",
        }, {
            "value": u"绵竹市", "label": u"绵竹市",
        }]
    }, {
        "value": u"绵阳市", "label": u"绵阳市",
        "children": [{
            "value": u"涪城区", "label": u"涪城区",
        }, {
            "value": u"游仙区", "label": u"游仙区",
        }, {
            "value": u"安州区", "label": u"安州区",
        }, {
            "value": u"三台县", "label": u"三台县",
        }, {
            "value": u"盐亭县", "label": u"盐亭县",
        }, {
            "value": u"梓潼县", "label": u"梓潼县",
        }, {
            "value": u"北川羌族自治县", "label": u"北川羌族自治县",
        }, {
            "value": u"平武县", "label": u"平武县",
        }, {
            "value": u"江油市", "label": u"江油市",
        }, {
            "value": u"高新区", "label": u"高新区",
        }]
    }, {
        "value": u"广元市", "label": u"广元市",
        "children": [{
            "value": u"利州区", "label": u"利州区",
        }, {
            "value": u"昭化区", "label": u"昭化区",
        }, {
            "value": u"朝天区", "label": u"朝天区",
        }, {
            "value": u"旺苍县", "label": u"旺苍县",
        }, {
            "value": u"青川县", "label": u"青川县",
        }, {
            "value": u"剑阁县", "label": u"剑阁县",
        }, {
            "value": u"苍溪县", "label": u"苍溪县",
        }]
    }, {
        "value": u"遂宁市", "label": u"遂宁市",
        "children": [{
            "value": u"船山区", "label": u"船山区",
        }, {
            "value": u"安居区", "label": u"安居区",
        }, {
            "value": u"蓬溪县", "label": u"蓬溪县",
        }, {
            "value": u"射洪县", "label": u"射洪县",
        }, {
            "value": u"大英县", "label": u"大英县",
        }]
    }, {
        "value": u"内江市", "label": u"内江市",
        "children": [{
            "value": u"市中区", "label": u"市中区",
        }, {
            "value": u"东兴区", "label": u"东兴区",
        }, {
            "value": u"威远县", "label": u"威远县",
        }, {
            "value": u"资中县", "label": u"资中县",
        }, {
            "value": u"隆昌市", "label": u"隆昌市",
        }]
    }, {
        "value": u"乐山市", "label": u"乐山市",
        "children": [{
            "value": u"市中区", "label": u"市中区",
        }, {
            "value": u"沙湾区", "label": u"沙湾区",
        }, {
            "value": u"五通桥区", "label": u"五通桥区",
        }, {
            "value": u"金口河区", "label": u"金口河区",
        }, {
            "value": u"犍为县", "label": u"犍为县",
        }, {
            "value": u"井研县", "label": u"井研县",
        }, {
            "value": u"夹江县", "label": u"夹江县",
        }, {
            "value": u"沐川县", "label": u"沐川县",
        }, {
            "value": u"峨边彝族自治县", "label": u"峨边彝族自治县",
        }, {
            "value": u"马边彝族自治县", "label": u"马边彝族自治县",
        }, {
            "value": u"峨眉山市", "label": u"峨眉山市",
        }]
    }, {
        "value": u"南充市", "label": u"南充市",
        "children": [{
            "value": u"顺庆区", "label": u"顺庆区",
        }, {
            "value": u"高坪区", "label": u"高坪区",
        }, {
            "value": u"嘉陵区", "label": u"嘉陵区",
        }, {
            "value": u"南部县", "label": u"南部县",
        }, {
            "value": u"营山县", "label": u"营山县",
        }, {
            "value": u"蓬安县", "label": u"蓬安县",
        }, {
            "value": u"仪陇县", "label": u"仪陇县",
        }, {
            "value": u"西充县", "label": u"西充县",
        }, {
            "value": u"阆中市", "label": u"阆中市",
        }]
    }, {
        "value": u"眉山市", "label": u"眉山市",
        "children": [{
            "value": u"东坡区", "label": u"东坡区",
        }, {
            "value": u"彭山区", "label": u"彭山区",
        }, {
            "value": u"仁寿县", "label": u"仁寿县",
        }, {
            "value": u"洪雅县", "label": u"洪雅县",
        }, {
            "value": u"丹棱县", "label": u"丹棱县",
        }, {
            "value": u"青神县", "label": u"青神县",
        }]
    }, {
        "value": u"宜宾市", "label": u"宜宾市",
        "children": [{
            "value": u"翠屏区", "label": u"翠屏区",
        }, {
            "value": u"南溪区", "label": u"南溪区",
        }, {
            "value": u"叙州区", "label": u"叙州区",
        }, {
            "value": u"江安县", "label": u"江安县",
        }, {
            "value": u"长宁县", "label": u"长宁县",
        }, {
            "value": u"高县", "label": u"高县",
        }, {
            "value": u"珙县", "label": u"珙县",
        }, {
            "value": u"筠连县", "label": u"筠连县",
        }, {
            "value": u"兴文县", "label": u"兴文县",
        }, {
            "value": u"屏山县", "label": u"屏山县",
        }]
    }, {
        "value": u"广安市", "label": u"广安市",
        "children": [{
            "value": u"广安区", "label": u"广安区",
        }, {
            "value": u"前锋区", "label": u"前锋区",
        }, {
            "value": u"岳池县", "label": u"岳池县",
        }, {
            "value": u"武胜县", "label": u"武胜县",
        }, {
            "value": u"邻水县", "label": u"邻水县",
        }, {
            "value": u"华蓥市", "label": u"华蓥市",
        }]
    }, {
        "value": u"达州市", "label": u"达州市",
        "children": [{
            "value": u"通川区", "label": u"通川区",
        }, {
            "value": u"达川区", "label": u"达川区",
        }, {
            "value": u"宣汉县", "label": u"宣汉县",
        }, {
            "value": u"开江县", "label": u"开江县",
        }, {
            "value": u"大竹县", "label": u"大竹县",
        }, {
            "value": u"渠县", "label": u"渠县",
        }, {
            "value": u"万源市", "label": u"万源市",
        }]
    }, {
        "value": u"雅安市", "label": u"雅安市",
        "children": [{
            "value": u"雨城区", "label": u"雨城区",
        }, {
            "value": u"名山区", "label": u"名山区",
        }, {
            "value": u"荥经县", "label": u"荥经县",
        }, {
            "value": u"汉源县", "label": u"汉源县",
        }, {
            "value": u"石棉县", "label": u"石棉县",
        }, {
            "value": u"天全县", "label": u"天全县",
        }, {
            "value": u"芦山县", "label": u"芦山县",
        }, {
            "value": u"宝兴县", "label": u"宝兴县",
        }]
    }, {
        "value": u"巴中市", "label": u"巴中市",
        "children": [{
            "value": u"巴州区", "label": u"巴州区",
        }, {
            "value": u"恩阳区", "label": u"恩阳区",
        }, {
            "value": u"通江县", "label": u"通江县",
        }, {
            "value": u"南江县", "label": u"南江县",
        }, {
            "value": u"平昌县", "label": u"平昌县",
        }]
    }, {
        "value": u"资阳市", "label": u"资阳市",
        "children": [{
            "value": u"雁江区", "label": u"雁江区",
        }, {
            "value": u"安岳县", "label": u"安岳县",
        }, {
            "value": u"乐至县", "label": u"乐至县",
        }]
    }, {
        "value": u"阿坝藏族羌族自治州", "label": u"阿坝藏族羌族自治州",
        "children": [{
            "value": u"马尔康市", "label": u"马尔康市",
        }, {
            "value": u"汶川县", "label": u"汶川县",
        }, {
            "value": u"理县", "label": u"理县",
        }, {
            "value": u"茂县", "label": u"茂县",
        }, {
            "value": u"松潘县", "label": u"松潘县",
        }, {
            "value": u"九寨沟县", "label": u"九寨沟县",
        }, {
            "value": u"金川县", "label": u"金川县",
        }, {
            "value": u"小金县", "label": u"小金县",
        }, {
            "value": u"黑水县", "label": u"黑水县",
        }, {
            "value": u"壤塘县", "label": u"壤塘县",
        }, {
            "value": u"阿坝县", "label": u"阿坝县",
        }, {
            "value": u"若尔盖县", "label": u"若尔盖县",
        }, {
            "value": u"红原县", "label": u"红原县",
        }]
    }, {
        "value": u"甘孜藏族自治州", "label": u"甘孜藏族自治州",
        "children": [{
            "value": u"康定市", "label": u"康定市",
        }, {
            "value": u"泸定县", "label": u"泸定县",
        }, {
            "value": u"丹巴县", "label": u"丹巴县",
        }, {
            "value": u"九龙县", "label": u"九龙县",
        }, {
            "value": u"雅江县", "label": u"雅江县",
        }, {
            "value": u"道孚县", "label": u"道孚县",
        }, {
            "value": u"炉霍县", "label": u"炉霍县",
        }, {
            "value": u"甘孜县", "label": u"甘孜县",
        }, {
            "value": u"新龙县", "label": u"新龙县",
        }, {
            "value": u"德格县", "label": u"德格县",
        }, {
            "value": u"白玉县", "label": u"白玉县",
        }, {
            "value": u"石渠县", "label": u"石渠县",
        }, {
            "value": u"色达县", "label": u"色达县",
        }, {
            "value": u"理塘县", "label": u"理塘县",
        }, {
            "value": u"巴塘县", "label": u"巴塘县",
        }, {
            "value": u"乡城县", "label": u"乡城县",
        }, {
            "value": u"稻城县", "label": u"稻城县",
        }, {
            "value": u"得荣县", "label": u"得荣县",
        }]
    }, {
        "value": u"凉山彝族自治州", "label": u"凉山彝族自治州",
        "children": [{
            "value": u"西昌市", "label": u"西昌市",
        }, {
            "value": u"木里藏族自治县", "label": u"木里藏族自治县",
        }, {
            "value": u"盐源县", "label": u"盐源县",
        }, {
            "value": u"德昌县", "label": u"德昌县",
        }, {
            "value": u"会理县", "label": u"会理县",
        }, {
            "value": u"会东县", "label": u"会东县",
        }, {
            "value": u"宁南县", "label": u"宁南县",
        }, {
            "value": u"普格县", "label": u"普格县",
        }, {
            "value": u"布拖县", "label": u"布拖县",
        }, {
            "value": u"金阳县", "label": u"金阳县",
        }, {
            "value": u"昭觉县", "label": u"昭觉县",
        }, {
            "value": u"喜德县", "label": u"喜德县",
        }, {
            "value": u"冕宁县", "label": u"冕宁县",
        }, {
            "value": u"越西县", "label": u"越西县",
        }, {
            "value": u"甘洛县", "label": u"甘洛县",
        }, {
            "value": u"美姑县", "label": u"美姑县",
        }, {
            "value": u"雷波县", "label": u"雷波县",
        }]
    }]
    }, {
    "value": u"贵州省", "label": u"贵州省",
    "children": [{
        "value": u"贵阳市", "label": u"贵阳市",
        "children": [{
            "value": u"南明区", "label": u"南明区",
        }, {
            "value": u"云岩区", "label": u"云岩区",
        }, {
            "value": u"花溪区", "label": u"花溪区",
        }, {
            "value": u"乌当区", "label": u"乌当区",
        }, {
            "value": u"白云区", "label": u"白云区",
        }, {
            "value": u"观山湖区", "label": u"观山湖区",
        }, {
            "value": u"开阳县", "label": u"开阳县",
        }, {
            "value": u"息烽县", "label": u"息烽县",
        }, {
            "value": u"修文县", "label": u"修文县",
        }, {
            "value": u"清镇市", "label": u"清镇市",
        }]
    }, {
        "value": u"六盘水市", "label": u"六盘水市",
        "children": [{
            "value": u"钟山区", "label": u"钟山区",
        }, {
            "value": u"六枝特区", "label": u"六枝特区",
        }, {
            "value": u"水城县", "label": u"水城县",
        }, {
            "value": u"盘州市", "label": u"盘州市",
        }]
    }, {
        "value": u"遵义市", "label": u"遵义市",
        "children": [{
            "value": u"红花岗区", "label": u"红花岗区",
        }, {
            "value": u"汇川区", "label": u"汇川区",
        }, {
            "value": u"播州区", "label": u"播州区",
        }, {
            "value": u"桐梓县", "label": u"桐梓县",
        }, {
            "value": u"绥阳县", "label": u"绥阳县",
        }, {
            "value": u"正安县", "label": u"正安县",
        }, {
            "value": u"道真仡佬族苗族自治县", "label": u"道真仡佬族苗族自治县",
        }, {
            "value": u"务川仡佬族苗族自治县", "label": u"务川仡佬族苗族自治县",
        }, {
            "value": u"凤冈县", "label": u"凤冈县",
        }, {
            "value": u"湄潭县", "label": u"湄潭县",
        }, {
            "value": u"余庆县", "label": u"余庆县",
        }, {
            "value": u"习水县", "label": u"习水县",
        }, {
            "value": u"赤水市", "label": u"赤水市",
        }, {
            "value": u"仁怀市", "label": u"仁怀市",
        }]
    }, {
        "value": u"安顺市", "label": u"安顺市",
        "children": [{
            "value": u"西秀区", "label": u"西秀区",
        }, {
            "value": u"平坝区", "label": u"平坝区",
        }, {
            "value": u"普定县", "label": u"普定县",
        }, {
            "value": u"镇宁布依族苗族自治县", "label": u"镇宁布依族苗族自治县",
        }, {
            "value": u"关岭布依族苗族自治县", "label": u"关岭布依族苗族自治县",
        }, {
            "value": u"紫云苗族布依族自治县", "label": u"紫云苗族布依族自治县",
        }]
    }, {
        "value": u"毕节市", "label": u"毕节市",
        "children": [{
            "value": u"七星关区", "label": u"七星关区",
        }, {
            "value": u"大方县", "label": u"大方县",
        }, {
            "value": u"黔西县", "label": u"黔西县",
        }, {
            "value": u"金沙县", "label": u"金沙县",
        }, {
            "value": u"织金县", "label": u"织金县",
        }, {
            "value": u"纳雍县", "label": u"纳雍县",
        }, {
            "value": u"威宁彝族回族苗族自治县", "label": u"威宁彝族回族苗族自治县",
        }, {
            "value": u"赫章县", "label": u"赫章县",
        }]
    }, {
        "value": u"铜仁市", "label": u"铜仁市",
        "children": [{
            "value": u"碧江区", "label": u"碧江区",
        }, {
            "value": u"万山区", "label": u"万山区",
        }, {
            "value": u"江口县", "label": u"江口县",
        }, {
            "value": u"玉屏侗族自治县", "label": u"玉屏侗族自治县",
        }, {
            "value": u"石阡县", "label": u"石阡县",
        }, {
            "value": u"思南县", "label": u"思南县",
        }, {
            "value": u"印江土家族苗族自治县", "label": u"印江土家族苗族自治县",
        }, {
            "value": u"德江县", "label": u"德江县",
        }, {
            "value": u"沿河土家族自治县", "label": u"沿河土家族自治县",
        }, {
            "value": u"松桃苗族自治县", "label": u"松桃苗族自治县",
        }]
    }, {
        "value": u"黔西南布依族苗族自治州", "label": u"黔西南布依族苗族自治州",
        "children": [{
            "value": u"兴义市", "label": u"兴义市",
        }, {
            "value": u"兴仁市", "label": u"兴仁市",
        }, {
            "value": u"普安县", "label": u"普安县",
        }, {
            "value": u"晴隆县", "label": u"晴隆县",
        }, {
            "value": u"贞丰县", "label": u"贞丰县",
        }, {
            "value": u"望谟县", "label": u"望谟县",
        }, {
            "value": u"册亨县", "label": u"册亨县",
        }, {
            "value": u"安龙县", "label": u"安龙县",
        }]
    }, {
        "value": u"黔东南苗族侗族自治州", "label": u"黔东南苗族侗族自治州",
        "children": [{
            "value": u"凯里市", "label": u"凯里市",
        }, {
            "value": u"黄平县", "label": u"黄平县",
        }, {
            "value": u"施秉县", "label": u"施秉县",
        }, {
            "value": u"三穗县", "label": u"三穗县",
        }, {
            "value": u"镇远县", "label": u"镇远县",
        }, {
            "value": u"岑巩县", "label": u"岑巩县",
        }, {
            "value": u"天柱县", "label": u"天柱县",
        }, {
            "value": u"锦屏县", "label": u"锦屏县",
        }, {
            "value": u"剑河县", "label": u"剑河县",
        }, {
            "value": u"台江县", "label": u"台江县",
        }, {
            "value": u"黎平县", "label": u"黎平县",
        }, {
            "value": u"榕江县", "label": u"榕江县",
        }, {
            "value": u"从江县", "label": u"从江县",
        }, {
            "value": u"雷山县", "label": u"雷山县",
        }, {
            "value": u"麻江县", "label": u"麻江县",
        }, {
            "value": u"丹寨县", "label": u"丹寨县",
        }]
    }, {
        "value": u"黔南布依族苗族自治州", "label": u"黔南布依族苗族自治州",
        "children": [{
            "value": u"都匀市", "label": u"都匀市",
        }, {
            "value": u"福泉市", "label": u"福泉市",
        }, {
            "value": u"荔波县", "label": u"荔波县",
        }, {
            "value": u"贵定县", "label": u"贵定县",
        }, {
            "value": u"瓮安县", "label": u"瓮安县",
        }, {
            "value": u"独山县", "label": u"独山县",
        }, {
            "value": u"平塘县", "label": u"平塘县",
        }, {
            "value": u"罗甸县", "label": u"罗甸县",
        }, {
            "value": u"长顺县", "label": u"长顺县",
        }, {
            "value": u"龙里县", "label": u"龙里县",
        }, {
            "value": u"惠水县", "label": u"惠水县",
        }, {
            "value": u"三都水族自治县", "label": u"三都水族自治县",
        }]
    }]
    }, {
    "value": u"云南省", "label": u"云南省",
    "children": [{
        "value": u"昆明市", "label": u"昆明市",
        "children": [{
            "value": u"五华区", "label": u"五华区",
        }, {
            "value": u"盘龙区", "label": u"盘龙区",
        }, {
            "value": u"官渡区", "label": u"官渡区",
        }, {
            "value": u"西山区", "label": u"西山区",
        }, {
            "value": u"东川区", "label": u"东川区",
        }, {
            "value": u"呈贡区", "label": u"呈贡区",
        }, {
            "value": u"晋宁区", "label": u"晋宁区",
        }, {
            "value": u"富民县", "label": u"富民县",
        }, {
            "value": u"宜良县", "label": u"宜良县",
        }, {
            "value": u"石林彝族自治县", "label": u"石林彝族自治县",
        }, {
            "value": u"嵩明县", "label": u"嵩明县",
        }, {
            "value": u"禄劝彝族苗族自治县", "label": u"禄劝彝族苗族自治县",
        }, {
            "value": u"寻甸回族彝族自治县", "label": u"寻甸回族彝族自治县",
        }, {
            "value": u"安宁市", "label": u"安宁市",
        }]
    }, {
        "value": u"曲靖市", "label": u"曲靖市",
        "children": [{
            "value": u"麒麟区", "label": u"麒麟区",
        }, {
            "value": u"沾益区", "label": u"沾益区",
        }, {
            "value": u"马龙区", "label": u"马龙区",
        }, {
            "value": u"陆良县", "label": u"陆良县",
        }, {
            "value": u"师宗县", "label": u"师宗县",
        }, {
            "value": u"罗平县", "label": u"罗平县",
        }, {
            "value": u"富源县", "label": u"富源县",
        }, {
            "value": u"会泽县", "label": u"会泽县",
        }, {
            "value": u"宣威市", "label": u"宣威市",
        }]
    }, {
        "value": u"玉溪市", "label": u"玉溪市",
        "children": [{
            "value": u"红塔区", "label": u"红塔区",
        }, {
            "value": u"江川区", "label": u"江川区",
        }, {
            "value": u"澄江县", "label": u"澄江县",
        }, {
            "value": u"通海县", "label": u"通海县",
        }, {
            "value": u"华宁县", "label": u"华宁县",
        }, {
            "value": u"易门县", "label": u"易门县",
        }, {
            "value": u"峨山彝族自治县", "label": u"峨山彝族自治县",
        }, {
            "value": u"新平彝族傣族自治县", "label": u"新平彝族傣族自治县",
        }, {
            "value": u"元江哈尼族彝族傣族自治县", "label": u"元江哈尼族彝族傣族自治县",
        }]
    }, {
        "value": u"保山市", "label": u"保山市",
        "children": [{
            "value": u"隆阳区", "label": u"隆阳区",
        }, {
            "value": u"施甸县", "label": u"施甸县",
        }, {
            "value": u"龙陵县", "label": u"龙陵县",
        }, {
            "value": u"昌宁县", "label": u"昌宁县",
        }, {
            "value": u"腾冲市", "label": u"腾冲市",
        }]
    }, {
        "value": u"昭通市", "label": u"昭通市",
        "children": [{
            "value": u"昭阳区", "label": u"昭阳区",
        }, {
            "value": u"鲁甸县", "label": u"鲁甸县",
        }, {
            "value": u"巧家县", "label": u"巧家县",
        }, {
            "value": u"盐津县", "label": u"盐津县",
        }, {
            "value": u"大关县", "label": u"大关县",
        }, {
            "value": u"永善县", "label": u"永善县",
        }, {
            "value": u"绥江县", "label": u"绥江县",
        }, {
            "value": u"镇雄县", "label": u"镇雄县",
        }, {
            "value": u"彝良县", "label": u"彝良县",
        }, {
            "value": u"威信县", "label": u"威信县",
        }, {
            "value": u"水富市", "label": u"水富市",
        }]
    }, {
        "value": u"丽江市", "label": u"丽江市",
        "children": [{
            "value": u"古城区", "label": u"古城区",
        }, {
            "value": u"玉龙纳西族自治县", "label": u"玉龙纳西族自治县",
        }, {
            "value": u"永胜县", "label": u"永胜县",
        }, {
            "value": u"华坪县", "label": u"华坪县",
        }, {
            "value": u"宁蒗彝族自治县", "label": u"宁蒗彝族自治县",
        }]
    }, {
        "value": u"普洱市", "label": u"普洱市",
        "children": [{
            "value": u"思茅区", "label": u"思茅区",
        }, {
            "value": u"宁洱哈尼族彝族自治县", "label": u"宁洱哈尼族彝族自治县",
        }, {
            "value": u"墨江哈尼族自治县", "label": u"墨江哈尼族自治县",
        }, {
            "value": u"景东彝族自治县", "label": u"景东彝族自治县",
        }, {
            "value": u"景谷傣族彝族自治县", "label": u"景谷傣族彝族自治县",
        }, {
            "value": u"镇沅彝族哈尼族拉祜族自治县", "label": u"镇沅彝族哈尼族拉祜族自治县",
        }, {
            "value": u"江城哈尼族彝族自治县", "label": u"江城哈尼族彝族自治县",
        }, {
            "value": u"孟连傣族拉祜族佤族自治县", "label": u"孟连傣族拉祜族佤族自治县",
        }, {
            "value": u"澜沧拉祜族自治县", "label": u"澜沧拉祜族自治县",
        }, {
            "value": u"西盟佤族自治县", "label": u"西盟佤族自治县",
        }]
    }, {
        "value": u"临沧市", "label": u"临沧市",
        "children": [{
            "value": u"临翔区", "label": u"临翔区",
        }, {
            "value": u"凤庆县", "label": u"凤庆县",
        }, {
            "value": u"云县", "label": u"云县",
        }, {
            "value": u"永德县", "label": u"永德县",
        }, {
            "value": u"镇康县", "label": u"镇康县",
        }, {
            "value": u"双江拉祜族佤族布朗族傣族自治县", "label": u"双江拉祜族佤族布朗族傣族自治县",
        }, {
            "value": u"耿马傣族佤族自治县", "label": u"耿马傣族佤族自治县",
        }, {
            "value": u"沧源佤族自治县", "label": u"沧源佤族自治县",
        }]
    }, {
        "value": u"楚雄彝族自治州", "label": u"楚雄彝族自治州",
        "children": [{
            "value": u"楚雄市", "label": u"楚雄市",
        }, {
            "value": u"双柏县", "label": u"双柏县",
        }, {
            "value": u"牟定县", "label": u"牟定县",
        }, {
            "value": u"南华县", "label": u"南华县",
        }, {
            "value": u"姚安县", "label": u"姚安县",
        }, {
            "value": u"大姚县", "label": u"大姚县",
        }, {
            "value": u"永仁县", "label": u"永仁县",
        }, {
            "value": u"元谋县", "label": u"元谋县",
        }, {
            "value": u"武定县", "label": u"武定县",
        }, {
            "value": u"禄丰县", "label": u"禄丰县",
        }]
    }, {
        "value": u"红河哈尼族彝族自治州", "label": u"红河哈尼族彝族自治州",
        "children": [{
            "value": u"个旧市", "label": u"个旧市",
        }, {
            "value": u"开远市", "label": u"开远市",
        }, {
            "value": u"蒙自市", "label": u"蒙自市",
        }, {
            "value": u"弥勒市", "label": u"弥勒市",
        }, {
            "value": u"屏边苗族自治县", "label": u"屏边苗族自治县",
        }, {
            "value": u"建水县", "label": u"建水县",
        }, {
            "value": u"石屏县", "label": u"石屏县",
        }, {
            "value": u"泸西县", "label": u"泸西县",
        }, {
            "value": u"元阳县", "label": u"元阳县",
        }, {
            "value": u"红河县", "label": u"红河县",
        }, {
            "value": u"金平苗族瑶族傣族自治县", "label": u"金平苗族瑶族傣族自治县",
        }, {
            "value": u"绿春县", "label": u"绿春县",
        }, {
            "value": u"河口瑶族自治县", "label": u"河口瑶族自治县",
        }]
    }, {
        "value": u"文山壮族苗族自治州", "label": u"文山壮族苗族自治州",
        "children": [{
            "value": u"文山市", "label": u"文山市",
        }, {
            "value": u"砚山县", "label": u"砚山县",
        }, {
            "value": u"西畴县", "label": u"西畴县",
        }, {
            "value": u"麻栗坡县", "label": u"麻栗坡县",
        }, {
            "value": u"马关县", "label": u"马关县",
        }, {
            "value": u"丘北县", "label": u"丘北县",
        }, {
            "value": u"广南县", "label": u"广南县",
        }, {
            "value": u"富宁县", "label": u"富宁县",
        }]
    }, {
        "value": u"西双版纳傣族自治州", "label": u"西双版纳傣族自治州",
        "children": [{
            "value": u"景洪市", "label": u"景洪市",
        }, {
            "value": u"勐海县", "label": u"勐海县",
        }, {
            "value": u"勐腊县", "label": u"勐腊县",
        }]
    }, {
        "value": u"大理白族自治州", "label": u"大理白族自治州",
        "children": [{
            "value": u"大理市", "label": u"大理市",
        }, {
            "value": u"漾濞彝族自治县", "label": u"漾濞彝族自治县",
        }, {
            "value": u"祥云县", "label": u"祥云县",
        }, {
            "value": u"宾川县", "label": u"宾川县",
        }, {
            "value": u"弥渡县", "label": u"弥渡县",
        }, {
            "value": u"南涧彝族自治县", "label": u"南涧彝族自治县",
        }, {
            "value": u"巍山彝族回族自治县", "label": u"巍山彝族回族自治县",
        }, {
            "value": u"永平县", "label": u"永平县",
        }, {
            "value": u"云龙县", "label": u"云龙县",
        }, {
            "value": u"洱源县", "label": u"洱源县",
        }, {
            "value": u"剑川县", "label": u"剑川县",
        }, {
            "value": u"鹤庆县", "label": u"鹤庆县",
        }]
    }, {
        "value": u"德宏傣族景颇族自治州", "label": u"德宏傣族景颇族自治州",
        "children": [{
            "value": u"瑞丽市", "label": u"瑞丽市",
        }, {
            "value": u"芒市", "label": u"芒市",
        }, {
            "value": u"梁河县", "label": u"梁河县",
        }, {
            "value": u"盈江县", "label": u"盈江县",
        }, {
            "value": u"陇川县", "label": u"陇川县",
        }]
    }, {
        "value": u"怒江傈僳族自治州", "label": u"怒江傈僳族自治州",
        "children": [{
            "value": u"泸水市", "label": u"泸水市",
        }, {
            "value": u"福贡县", "label": u"福贡县",
        }, {
            "value": u"贡山独龙族怒族自治县", "label": u"贡山独龙族怒族自治县",
        }, {
            "value": u"兰坪白族普米族自治县", "label": u"兰坪白族普米族自治县",
        }]
    }, {
        "value": u"迪庆藏族自治州", "label": u"迪庆藏族自治州",
        "children": [{
            "value": u"香格里拉市", "label": u"香格里拉市",
        }, {
            "value": u"德钦县", "label": u"德钦县",
        }, {
            "value": u"维西傈僳族自治县", "label": u"维西傈僳族自治县",
        }]
    }]
    }, {
    "value": u"西藏自治区", "label": u"西藏自治区",
    "children": [{
        "value": u"拉萨市", "label": u"拉萨市",
        "children": [{
            "value": u"城关区", "label": u"城关区",
        }, {
            "value": u"堆龙德庆区", "label": u"堆龙德庆区",
        }, {
            "value": u"达孜区", "label": u"达孜区",
        }, {
            "value": u"林周县", "label": u"林周县",
        }, {
            "value": u"当雄县", "label": u"当雄县",
        }, {
            "value": u"尼木县", "label": u"尼木县",
        }, {
            "value": u"曲水县", "label": u"曲水县",
        }, {
            "value": u"墨竹工卡县", "label": u"墨竹工卡县",
        }]
    }, {
        "value": u"日喀则市", "label": u"日喀则市",
        "children": [{
            "value": u"桑珠孜区", "label": u"桑珠孜区",
        }, {
            "value": u"南木林县", "label": u"南木林县",
        }, {
            "value": u"江孜县", "label": u"江孜县",
        }, {
            "value": u"定日县", "label": u"定日县",
        }, {
            "value": u"萨迦县", "label": u"萨迦县",
        }, {
            "value": u"拉孜县", "label": u"拉孜县",
        }, {
            "value": u"昂仁县", "label": u"昂仁县",
        }, {
            "value": u"谢通门县", "label": u"谢通门县",
        }, {
            "value": u"白朗县", "label": u"白朗县",
        }, {
            "value": u"仁布县", "label": u"仁布县",
        }, {
            "value": u"康马县", "label": u"康马县",
        }, {
            "value": u"定结县", "label": u"定结县",
        }, {
            "value": u"仲巴县", "label": u"仲巴县",
        }, {
            "value": u"亚东县", "label": u"亚东县",
        }, {
            "value": u"吉隆县", "label": u"吉隆县",
        }, {
            "value": u"聂拉木县", "label": u"聂拉木县",
        }, {
            "value": u"萨嘎县", "label": u"萨嘎县",
        }, {
            "value": u"岗巴县", "label": u"岗巴县",
        }]
    }, {
        "value": u"昌都市", "label": u"昌都市",
        "children": [{
            "value": u"卡若区", "label": u"卡若区",
        }, {
            "value": u"江达县", "label": u"江达县",
        }, {
            "value": u"贡觉县", "label": u"贡觉县",
        }, {
            "value": u"类乌齐县", "label": u"类乌齐县",
        }, {
            "value": u"丁青县", "label": u"丁青县",
        }, {
            "value": u"察雅县", "label": u"察雅县",
        }, {
            "value": u"八宿县", "label": u"八宿县",
        }, {
            "value": u"左贡县", "label": u"左贡县",
        }, {
            "value": u"芒康县", "label": u"芒康县",
        }, {
            "value": u"洛隆县", "label": u"洛隆县",
        }, {
            "value": u"边坝县", "label": u"边坝县",
        }]
    }, {
        "value": u"林芝市", "label": u"林芝市",
        "children": [{
            "value": u"巴宜区", "label": u"巴宜区",
        }, {
            "value": u"工布江达县", "label": u"工布江达县",
        }, {
            "value": u"米林县", "label": u"米林县",
        }, {
            "value": u"墨脱县", "label": u"墨脱县",
        }, {
            "value": u"波密县", "label": u"波密县",
        }, {
            "value": u"察隅县", "label": u"察隅县",
        }, {
            "value": u"朗县", "label": u"朗县",
        }]
    }, {
        "value": u"山南市", "label": u"山南市",
        "children": [{
            "value": u"乃东区", "label": u"乃东区",
        }, {
            "value": u"扎囊县", "label": u"扎囊县",
        }, {
            "value": u"贡嘎县", "label": u"贡嘎县",
        }, {
            "value": u"桑日县", "label": u"桑日县",
        }, {
            "value": u"琼结县", "label": u"琼结县",
        }, {
            "value": u"曲松县", "label": u"曲松县",
        }, {
            "value": u"措美县", "label": u"措美县",
        }, {
            "value": u"洛扎县", "label": u"洛扎县",
        }, {
            "value": u"加查县", "label": u"加查县",
        }, {
            "value": u"隆子县", "label": u"隆子县",
        }, {
            "value": u"错那县", "label": u"错那县",
        }, {
            "value": u"浪卡子县", "label": u"浪卡子县",
        }]
    }, {
        "value": u"那曲市", "label": u"那曲市",
        "children": [{
            "value": u"色尼区", "label": u"色尼区",
        }, {
            "value": u"嘉黎县", "label": u"嘉黎县",
        }, {
            "value": u"比如县", "label": u"比如县",
        }, {
            "value": u"聂荣县", "label": u"聂荣县",
        }, {
            "value": u"安多县", "label": u"安多县",
        }, {
            "value": u"申扎县", "label": u"申扎县",
        }, {
            "value": u"索县", "label": u"索县",
        }, {
            "value": u"班戈县", "label": u"班戈县",
        }, {
            "value": u"巴青县", "label": u"巴青县",
        }, {
            "value": u"尼玛县", "label": u"尼玛县",
        }, {
            "value": u"双湖县", "label": u"双湖县",
        }]
    }, {
        "value": u"阿里地区", "label": u"阿里地区",
        "children": [{
            "value": u"普兰县", "label": u"普兰县",
        }, {
            "value": u"札达县", "label": u"札达县",
        }, {
            "value": u"噶尔县", "label": u"噶尔县",
        }, {
            "value": u"日土县", "label": u"日土县",
        }, {
            "value": u"革吉县", "label": u"革吉县",
        }, {
            "value": u"改则县", "label": u"改则县",
        }, {
            "value": u"措勤县", "label": u"措勤县",
        }]
    }]
    }, {
    "value": u"陕西省", "label": u"陕西省",
    "children": [{
        "value": u"西安市", "label": u"西安市",
        "children": [{
            "value": u"新城区", "label": u"新城区",
        }, {
            "value": u"碑林区", "label": u"碑林区",
        }, {
            "value": u"莲湖区", "label": u"莲湖区",
        }, {
            "value": u"灞桥区", "label": u"灞桥区",
        }, {
            "value": u"未央区", "label": u"未央区",
        }, {
            "value": u"雁塔区", "label": u"雁塔区",
        }, {
            "value": u"阎良区", "label": u"阎良区",
        }, {
            "value": u"临潼区", "label": u"临潼区",
        }, {
            "value": u"长安区", "label": u"长安区",
        }, {
            "value": u"高陵区", "label": u"高陵区",
        }, {
            "value": u"鄠邑区", "label": u"鄠邑区",
        }, {
            "value": u"蓝田县", "label": u"蓝田县",
        }, {
            "value": u"周至县", "label": u"周至县",
        }]
    }, {
        "value": u"铜川市", "label": u"铜川市",
        "children": [{
            "value": u"王益区", "label": u"王益区",
        }, {
            "value": u"印台区", "label": u"印台区",
        }, {
            "value": u"耀州区", "label": u"耀州区",
        }, {
            "value": u"宜君县", "label": u"宜君县",
        }]
    }, {
        "value": u"宝鸡市", "label": u"宝鸡市",
        "children": [{
            "value": u"渭滨区", "label": u"渭滨区",
        }, {
            "value": u"金台区", "label": u"金台区",
        }, {
            "value": u"陈仓区", "label": u"陈仓区",
        }, {
            "value": u"凤翔县", "label": u"凤翔县",
        }, {
            "value": u"岐山县", "label": u"岐山县",
        }, {
            "value": u"扶风县", "label": u"扶风县",
        }, {
            "value": u"眉县", "label": u"眉县",
        }, {
            "value": u"陇县", "label": u"陇县",
        }, {
            "value": u"千阳县", "label": u"千阳县",
        }, {
            "value": u"麟游县", "label": u"麟游县",
        }, {
            "value": u"凤县", "label": u"凤县",
        }, {
            "value": u"太白县", "label": u"太白县",
        }]
    }, {
        "value": u"咸阳市", "label": u"咸阳市",
        "children": [{
            "value": u"秦都区", "label": u"秦都区",
        }, {
            "value": u"杨陵区", "label": u"杨陵区",
        }, {
            "value": u"渭城区", "label": u"渭城区",
        }, {
            "value": u"三原县", "label": u"三原县",
        }, {
            "value": u"泾阳县", "label": u"泾阳县",
        }, {
            "value": u"乾县", "label": u"乾县",
        }, {
            "value": u"礼泉县", "label": u"礼泉县",
        }, {
            "value": u"永寿县", "label": u"永寿县",
        }, {
            "value": u"长武县", "label": u"长武县",
        }, {
            "value": u"旬邑县", "label": u"旬邑县",
        }, {
            "value": u"淳化县", "label": u"淳化县",
        }, {
            "value": u"武功县", "label": u"武功县",
        }, {
            "value": u"兴平市", "label": u"兴平市",
        }, {
            "value": u"彬州市", "label": u"彬州市",
        }]
    }, {
        "value": u"渭南市", "label": u"渭南市",
        "children": [{
            "value": u"临渭区", "label": u"临渭区",
        }, {
            "value": u"华州区", "label": u"华州区",
        }, {
            "value": u"潼关县", "label": u"潼关县",
        }, {
            "value": u"大荔县", "label": u"大荔县",
        }, {
            "value": u"合阳县", "label": u"合阳县",
        }, {
            "value": u"澄城县", "label": u"澄城县",
        }, {
            "value": u"蒲城县", "label": u"蒲城县",
        }, {
            "value": u"白水县", "label": u"白水县",
        }, {
            "value": u"富平县", "label": u"富平县",
        }, {
            "value": u"韩城市", "label": u"韩城市",
        }, {
            "value": u"华阴市", "label": u"华阴市",
        }]
    }, {
        "value": u"延安市", "label": u"延安市",
        "children": [{
            "value": u"宝塔区", "label": u"宝塔区",
        }, {
            "value": u"安塞区", "label": u"安塞区",
        }, {
            "value": u"延长县", "label": u"延长县",
        }, {
            "value": u"延川县", "label": u"延川县",
        }, {
            "value": u"子长县", "label": u"子长县",
        }, {
            "value": u"志丹县", "label": u"志丹县",
        }, {
            "value": u"吴起县", "label": u"吴起县",
        }, {
            "value": u"甘泉县", "label": u"甘泉县",
        }, {
            "value": u"富县", "label": u"富县",
        }, {
            "value": u"洛川县", "label": u"洛川县",
        }, {
            "value": u"宜川县", "label": u"宜川县",
        }, {
            "value": u"黄龙县", "label": u"黄龙县",
        }, {
            "value": u"黄陵县", "label": u"黄陵县",
        }]
    }, {
        "value": u"汉中市", "label": u"汉中市",
        "children": [{
            "value": u"汉台区", "label": u"汉台区",
        }, {
            "value": u"南郑区", "label": u"南郑区",
        }, {
            "value": u"城固县", "label": u"城固县",
        }, {
            "value": u"洋县", "label": u"洋县",
        }, {
            "value": u"西乡县", "label": u"西乡县",
        }, {
            "value": u"勉县", "label": u"勉县",
        }, {
            "value": u"宁强县", "label": u"宁强县",
        }, {
            "value": u"略阳县", "label": u"略阳县",
        }, {
            "value": u"镇巴县", "label": u"镇巴县",
        }, {
            "value": u"留坝县", "label": u"留坝县",
        }, {
            "value": u"佛坪县", "label": u"佛坪县",
        }]
    }, {
        "value": u"榆林市", "label": u"榆林市",
        "children": [{
            "value": u"榆阳区", "label": u"榆阳区",
        }, {
            "value": u"横山区", "label": u"横山区",
        }, {
            "value": u"府谷县", "label": u"府谷县",
        }, {
            "value": u"靖边县", "label": u"靖边县",
        }, {
            "value": u"定边县", "label": u"定边县",
        }, {
            "value": u"绥德县", "label": u"绥德县",
        }, {
            "value": u"米脂县", "label": u"米脂县",
        }, {
            "value": u"佳县", "label": u"佳县",
        }, {
            "value": u"吴堡县", "label": u"吴堡县",
        }, {
            "value": u"清涧县", "label": u"清涧县",
        }, {
            "value": u"子洲县", "label": u"子洲县",
        }, {
            "value": u"神木市", "label": u"神木市",
        }]
    }, {
        "value": u"安康市", "label": u"安康市",
        "children": [{
            "value": u"汉滨区", "label": u"汉滨区",
        }, {
            "value": u"汉阴县", "label": u"汉阴县",
        }, {
            "value": u"石泉县", "label": u"石泉县",
        }, {
            "value": u"宁陕县", "label": u"宁陕县",
        }, {
            "value": u"紫阳县", "label": u"紫阳县",
        }, {
            "value": u"岚皋县", "label": u"岚皋县",
        }, {
            "value": u"平利县", "label": u"平利县",
        }, {
            "value": u"镇坪县", "label": u"镇坪县",
        }, {
            "value": u"旬阳县", "label": u"旬阳县",
        }, {
            "value": u"白河县", "label": u"白河县",
        }]
    }, {
        "value": u"商洛市", "label": u"商洛市",
        "children": [{
            "value": u"商州区", "label": u"商州区",
        }, {
            "value": u"洛南县", "label": u"洛南县",
        }, {
            "value": u"丹凤县", "label": u"丹凤县",
        }, {
            "value": u"商南县", "label": u"商南县",
        }, {
            "value": u"山阳县", "label": u"山阳县",
        }, {
            "value": u"镇安县", "label": u"镇安县",
        }, {
            "value": u"柞水县", "label": u"柞水县",
        }]
    }]
    }, {
    "value": u"甘肃省", "label": u"甘肃省",
    "children": [{
        "value": u"兰州市", "label": u"兰州市",
        "children": [{
            "value": u"城关区", "label": u"城关区",
        }, {
            "value": u"七里河区", "label": u"七里河区",
        }, {
            "value": u"西固区", "label": u"西固区",
        }, {
            "value": u"安宁区", "label": u"安宁区",
        }, {
            "value": u"红古区", "label": u"红古区",
        }, {
            "value": u"永登县", "label": u"永登县",
        }, {
            "value": u"皋兰县", "label": u"皋兰县",
        }, {
            "value": u"榆中县", "label": u"榆中县",
        }]
    }, {
        "value": u"嘉峪关市", "label": u"嘉峪关市",
        "children": [{
            "value": u"市辖区", "label": u"市辖区",
        }, {
            "value": u"雄关区", "label": u"雄关区",
        }, {
            "value": u"长城区", "label": u"长城区",
        }, {
            "value": u"镜铁区", "label": u"镜铁区",
        }, {
            "value": u"新城镇", "label": u"新城镇",
        }, {
            "value": u"峪泉镇", "label": u"峪泉镇",
        }, {
            "value": u"文殊镇", "label": u"文殊镇",
        }]
    }, {
        "value": u"金昌市", "label": u"金昌市",
        "children": [{
            "value": u"金川区", "label": u"金川区",
        }, {
            "value": u"永昌县", "label": u"永昌县",
        }]
    }, {
        "value": u"白银市", "label": u"白银市",
        "children": [{
            "value": u"白银区", "label": u"白银区",
        }, {
            "value": u"平川区", "label": u"平川区",
        }, {
            "value": u"靖远县", "label": u"靖远县",
        }, {
            "value": u"会宁县", "label": u"会宁县",
        }, {
            "value": u"景泰县", "label": u"景泰县",
        }]
    }, {
        "value": u"天水市", "label": u"天水市",
        "children": [{
            "value": u"秦州区", "label": u"秦州区",
        }, {
            "value": u"麦积区", "label": u"麦积区",
        }, {
            "value": u"清水县", "label": u"清水县",
        }, {
            "value": u"秦安县", "label": u"秦安县",
        }, {
            "value": u"甘谷县", "label": u"甘谷县",
        }, {
            "value": u"武山县", "label": u"武山县",
        }, {
            "value": u"张家川回族自治县", "label": u"张家川回族自治县",
        }]
    }, {
        "value": u"武威市", "label": u"武威市",
        "children": [{
            "value": u"凉州区", "label": u"凉州区",
        }, {
            "value": u"民勤县", "label": u"民勤县",
        }, {
            "value": u"古浪县", "label": u"古浪县",
        }, {
            "value": u"天祝藏族自治县", "label": u"天祝藏族自治县",
        }]
    }, {
        "value": u"张掖市", "label": u"张掖市",
        "children": [{
            "value": u"甘州区", "label": u"甘州区",
        }, {
            "value": u"肃南裕固族自治县", "label": u"肃南裕固族自治县",
        }, {
            "value": u"民乐县", "label": u"民乐县",
        }, {
            "value": u"临泽县", "label": u"临泽县",
        }, {
            "value": u"高台县", "label": u"高台县",
        }, {
            "value": u"山丹县", "label": u"山丹县",
        }]
    }, {
        "value": u"平凉市", "label": u"平凉市",
        "children": [{
            "value": u"崆峒区", "label": u"崆峒区",
        }, {
            "value": u"泾川县", "label": u"泾川县",
        }, {
            "value": u"灵台县", "label": u"灵台县",
        }, {
            "value": u"崇信县", "label": u"崇信县",
        }, {
            "value": u"庄浪县", "label": u"庄浪县",
        }, {
            "value": u"静宁县", "label": u"静宁县",
        }, {
            "value": u"华亭市", "label": u"华亭市",
        }]
    }, {
        "value": u"酒泉市", "label": u"酒泉市",
        "children": [{
            "value": u"肃州区", "label": u"肃州区",
        }, {
            "value": u"金塔县", "label": u"金塔县",
        }, {
            "value": u"瓜州县", "label": u"瓜州县",
        }, {
            "value": u"肃北蒙古族自治县", "label": u"肃北蒙古族自治县",
        }, {
            "value": u"阿克塞哈萨克族自治县", "label": u"阿克塞哈萨克族自治县",
        }, {
            "value": u"玉门市", "label": u"玉门市",
        }, {
            "value": u"敦煌市", "label": u"敦煌市",
        }]
    }, {
        "value": u"庆阳市", "label": u"庆阳市",
        "children": [{
            "value": u"西峰区", "label": u"西峰区",
        }, {
            "value": u"庆城县", "label": u"庆城县",
        }, {
            "value": u"环县", "label": u"环县",
        }, {
            "value": u"华池县", "label": u"华池县",
        }, {
            "value": u"合水县", "label": u"合水县",
        }, {
            "value": u"正宁县", "label": u"正宁县",
        }, {
            "value": u"宁县", "label": u"宁县",
        }, {
            "value": u"镇原县", "label": u"镇原县",
        }]
    }, {
        "value": u"定西市", "label": u"定西市",
        "children": [{
            "value": u"安定区", "label": u"安定区",
        }, {
            "value": u"通渭县", "label": u"通渭县",
        }, {
            "value": u"陇西县", "label": u"陇西县",
        }, {
            "value": u"渭源县", "label": u"渭源县",
        }, {
            "value": u"临洮县", "label": u"临洮县",
        }, {
            "value": u"漳县", "label": u"漳县",
        }, {
            "value": u"岷县", "label": u"岷县",
        }]
    }, {
        "value": u"陇南市", "label": u"陇南市",
        "children": [{
            "value": u"武都区", "label": u"武都区",
        }, {
            "value": u"成县", "label": u"成县",
        }, {
            "value": u"文县", "label": u"文县",
        }, {
            "value": u"宕昌县", "label": u"宕昌县",
        }, {
            "value": u"康县", "label": u"康县",
        }, {
            "value": u"西和县", "label": u"西和县",
        }, {
            "value": u"礼县", "label": u"礼县",
        }, {
            "value": u"徽县", "label": u"徽县",
        }, {
            "value": u"两当县", "label": u"两当县",
        }]
    }, {
        "value": u"临夏回族自治州", "label": u"临夏回族自治州",
        "children": [{
            "value": u"临夏市", "label": u"临夏市",
        }, {
            "value": u"临夏县", "label": u"临夏县",
        }, {
            "value": u"康乐县", "label": u"康乐县",
        }, {
            "value": u"永靖县", "label": u"永靖县",
        }, {
            "value": u"广河县", "label": u"广河县",
        }, {
            "value": u"和政县", "label": u"和政县",
        }, {
            "value": u"东乡族自治县", "label": u"东乡族自治县",
        }, {
            "value": u"积石山保安族东乡族撒拉族自治县", "label": u"积石山保安族东乡族撒拉族自治县",
        }]
    }, {
        "value": u"甘南藏族自治州", "label": u"甘南藏族自治州",
        "children": [{
            "value": u"合作市", "label": u"合作市",
        }, {
            "value": u"临潭县", "label": u"临潭县",
        }, {
            "value": u"卓尼县", "label": u"卓尼县",
        }, {
            "value": u"舟曲县", "label": u"舟曲县",
        }, {
            "value": u"迭部县", "label": u"迭部县",
        }, {
            "value": u"玛曲县", "label": u"玛曲县",
        }, {
            "value": u"碌曲县", "label": u"碌曲县",
        }, {
            "value": u"夏河县", "label": u"夏河县",
        }]
    }]
    }, {
    "value": u"青海省", "label": u"青海省",
    "children": [{
        "value": u"西宁市", "label": u"西宁市",
        "children": [{
            "value": u"城东区", "label": u"城东区",
        }, {
            "value": u"城中区", "label": u"城中区",
        }, {
            "value": u"城西区", "label": u"城西区",
        }, {
            "value": u"城北区", "label": u"城北区",
        }, {
            "value": u"大通回族土族自治县", "label": u"大通回族土族自治县",
        }, {
            "value": u"湟中县", "label": u"湟中县",
        }, {
            "value": u"湟源县", "label": u"湟源县",
        }]
    }, {
        "value": u"海东市", "label": u"海东市",
        "children": [{
            "value": u"乐都区", "label": u"乐都区",
        }, {
            "value": u"平安区", "label": u"平安区",
        }, {
            "value": u"民和回族土族自治县", "label": u"民和回族土族自治县",
        }, {
            "value": u"互助土族自治县", "label": u"互助土族自治县",
        }, {
            "value": u"化隆回族自治县", "label": u"化隆回族自治县",
        }, {
            "value": u"循化撒拉族自治县", "label": u"循化撒拉族自治县",
        }]
    }, {
        "value": u"海北藏族自治州", "label": u"海北藏族自治州",
        "children": [{
            "value": u"门源回族自治县", "label": u"门源回族自治县",
        }, {
            "value": u"祁连县", "label": u"祁连县",
        }, {
            "value": u"海晏县", "label": u"海晏县",
        }, {
            "value": u"刚察县", "label": u"刚察县",
        }]
    }, {
        "value": u"黄南藏族自治州", "label": u"黄南藏族自治州",
        "children": [{
            "value": u"同仁县", "label": u"同仁县",
        }, {
            "value": u"尖扎县", "label": u"尖扎县",
        }, {
            "value": u"泽库县", "label": u"泽库县",
        }, {
            "value": u"河南蒙古族自治县", "label": u"河南蒙古族自治县",
        }]
    }, {
        "value": u"海南藏族自治州", "label": u"海南藏族自治州",
        "children": [{
            "value": u"共和县", "label": u"共和县",
        }, {
            "value": u"同德县", "label": u"同德县",
        }, {
            "value": u"贵德县", "label": u"贵德县",
        }, {
            "value": u"兴海县", "label": u"兴海县",
        }, {
            "value": u"贵南县", "label": u"贵南县",
        }]
    }, {
        "value": u"果洛藏族自治州", "label": u"果洛藏族自治州",
        "children": [{
            "value": u"玛沁县", "label": u"玛沁县",
        }, {
            "value": u"班玛县", "label": u"班玛县",
        }, {
            "value": u"甘德县", "label": u"甘德县",
        }, {
            "value": u"达日县", "label": u"达日县",
        }, {
            "value": u"久治县", "label": u"久治县",
        }, {
            "value": u"玛多县", "label": u"玛多县",
        }]
    }, {
        "value": u"玉树藏族自治州", "label": u"玉树藏族自治州",
        "children": [{
            "value": u"玉树市", "label": u"玉树市",
        }, {
            "value": u"杂多县", "label": u"杂多县",
        }, {
            "value": u"称多县", "label": u"称多县",
        }, {
            "value": u"治多县", "label": u"治多县",
        }, {
            "value": u"囊谦县", "label": u"囊谦县",
        }, {
            "value": u"曲麻莱县", "label": u"曲麻莱县",
        }]
    }, {
        "value": u"海西蒙古族藏族自治州", "label": u"海西蒙古族藏族自治州",
        "children": [{
            "value": u"格尔木市", "label": u"格尔木市",
        }, {
            "value": u"德令哈市", "label": u"德令哈市",
        }, {
            "value": u"茫崖市", "label": u"茫崖市",
        }, {
            "value": u"乌兰县", "label": u"乌兰县",
        }, {
            "value": u"都兰县", "label": u"都兰县",
        }, {
            "value": u"天峻县", "label": u"天峻县",
        }]
    }]
    }, {
    "value": u"宁夏回族自治区", "label": u"宁夏回族自治区",
    "children": [{
        "value": u"银川市", "label": u"银川市",
        "children": [{
            "value": u"兴庆区", "label": u"兴庆区",
        }, {
            "value": u"西夏区", "label": u"西夏区",
        }, {
            "value": u"金凤区", "label": u"金凤区",
        }, {
            "value": u"永宁县", "label": u"永宁县",
        }, {
            "value": u"贺兰县", "label": u"贺兰县",
        }, {
            "value": u"灵武市", "label": u"灵武市",
        }]
    }, {
        "value": u"石嘴山市", "label": u"石嘴山市",
        "children": [{
            "value": u"大武口区", "label": u"大武口区",
        }, {
            "value": u"惠农区", "label": u"惠农区",
        }, {
            "value": u"平罗县", "label": u"平罗县",
        }]
    }, {
        "value": u"吴忠市", "label": u"吴忠市",
        "children": [{
            "value": u"利通区", "label": u"利通区",
        }, {
            "value": u"红寺堡区", "label": u"红寺堡区",
        }, {
            "value": u"盐池县", "label": u"盐池县",
        }, {
            "value": u"同心县", "label": u"同心县",
        }, {
            "value": u"青铜峡市", "label": u"青铜峡市",
        }]
    }, {
        "value": u"固原市", "label": u"固原市",
        "children": [{
            "value": u"原州区", "label": u"原州区",
        }, {
            "value": u"西吉县", "label": u"西吉县",
        }, {
            "value": u"隆德县", "label": u"隆德县",
        }, {
            "value": u"泾源县", "label": u"泾源县",
        }, {
            "value": u"彭阳县", "label": u"彭阳县",
        }]
    }, {
        "value": u"中卫市", "label": u"中卫市",
        "children": [{
            "value": u"沙坡头区", "label": u"沙坡头区",
        }, {
            "value": u"中宁县", "label": u"中宁县",
        }, {
            "value": u"海原县", "label": u"海原县",
        }]
    }]
    }, {
    "value": u"新疆维吾尔自治区", "label": u"新疆维吾尔自治区",
    "children": [{
        "value": u"乌鲁木齐市", "label": u"乌鲁木齐市",
        "children": [{
            "value": u"天山区", "label": u"天山区",
        }, {
            "value": u"沙依巴克区", "label": u"沙依巴克区",
        }, {
            "value": u"新市区", "label": u"新市区",
        }, {
            "value": u"水磨沟区", "label": u"水磨沟区",
        }, {
            "value": u"头屯河区", "label": u"头屯河区",
        }, {
            "value": u"达坂城区", "label": u"达坂城区",
        }, {
            "value": u"米东区", "label": u"米东区",
        }, {
            "value": u"乌鲁木齐县", "label": u"乌鲁木齐县",
        }]
    }, {
        "value": u"克拉玛依市", "label": u"克拉玛依市",
        "children": [{
            "value": u"独山子区", "label": u"独山子区",
        }, {
            "value": u"克拉玛依区", "label": u"克拉玛依区",
        }, {
            "value": u"白碱滩区", "label": u"白碱滩区",
        }, {
            "value": u"乌尔禾区", "label": u"乌尔禾区",
        }]
    }, {
        "value": u"吐鲁番市", "label": u"吐鲁番市",
        "children": [{
            "value": u"高昌区", "label": u"高昌区",
        }, {
            "value": u"鄯善县", "label": u"鄯善县",
        }, {
            "value": u"托克逊县", "label": u"托克逊县",
        }]
    }, {
        "value": u"哈密市", "label": u"哈密市",
        "children": [{
            "value": u"伊州区", "label": u"伊州区",
        }, {
            "value": u"巴里坤哈萨克自治县", "label": u"巴里坤哈萨克自治县",
        }, {
            "value": u"伊吾县", "label": u"伊吾县",
        }]
    }, {
        "value": u"昌吉回族自治州", "label": u"昌吉回族自治州",
        "children": [{
            "value": u"昌吉市", "label": u"昌吉市",
        }, {
            "value": u"阜康市", "label": u"阜康市",
        }, {
            "value": u"呼图壁县", "label": u"呼图壁县",
        }, {
            "value": u"玛纳斯县", "label": u"玛纳斯县",
        }, {
            "value": u"奇台县", "label": u"奇台县",
        }, {
            "value": u"吉木萨尔县", "label": u"吉木萨尔县",
        }, {
            "value": u"木垒哈萨克自治县", "label": u"木垒哈萨克自治县",
        }]
    }, {
        "value": u"博尔塔拉蒙古自治州", "label": u"博尔塔拉蒙古自治州",
        "children": [{
            "value": u"博乐市", "label": u"博乐市",
        }, {
            "value": u"阿拉山口市", "label": u"阿拉山口市",
        }, {
            "value": u"精河县", "label": u"精河县",
        }, {
            "value": u"温泉县", "label": u"温泉县",
        }]
    }, {
        "value": u"巴音郭楞蒙古自治州", "label": u"巴音郭楞蒙古自治州",
        "children": [{
            "value": u"库尔勒市", "label": u"库尔勒市",
        }, {
            "value": u"轮台县", "label": u"轮台县",
        }, {
            "value": u"尉犁县", "label": u"尉犁县",
        }, {
            "value": u"若羌县", "label": u"若羌县",
        }, {
            "value": u"且末县", "label": u"且末县",
        }, {
            "value": u"焉耆回族自治县", "label": u"焉耆回族自治县",
        }, {
            "value": u"和静县", "label": u"和静县",
        }, {
            "value": u"和硕县", "label": u"和硕县",
        }, {
            "value": u"博湖县", "label": u"博湖县",
        }]
    }, {
        "value": u"阿克苏地区", "label": u"阿克苏地区",
        "children": [{
            "value": u"阿克苏市", "label": u"阿克苏市",
        }, {
            "value": u"温宿县", "label": u"温宿县",
        }, {
            "value": u"库车县", "label": u"库车县",
        }, {
            "value": u"沙雅县", "label": u"沙雅县",
        }, {
            "value": u"新和县", "label": u"新和县",
        }, {
            "value": u"拜城县", "label": u"拜城县",
        }, {
            "value": u"乌什县", "label": u"乌什县",
        }, {
            "value": u"阿瓦提县", "label": u"阿瓦提县",
        }, {
            "value": u"柯坪县", "label": u"柯坪县",
        }]
    }, {
        "value": u"克孜勒苏柯尔克孜自治州", "label": u"克孜勒苏柯尔克孜自治州",
        "children": [{
            "value": u"阿图什市", "label": u"阿图什市",
        }, {
            "value": u"阿克陶县", "label": u"阿克陶县",
        }, {
            "value": u"阿合奇县", "label": u"阿合奇县",
        }, {
            "value": u"乌恰县", "label": u"乌恰县",
        }]
    }, {
        "value": u"喀什地区", "label": u"喀什地区",
        "children": [{
            "value": u"喀什市", "label": u"喀什市",
        }, {
            "value": u"疏附县", "label": u"疏附县",
        }, {
            "value": u"疏勒县", "label": u"疏勒县",
        }, {
            "value": u"英吉沙县", "label": u"英吉沙县",
        }, {
            "value": u"泽普县", "label": u"泽普县",
        }, {
            "value": u"莎车县", "label": u"莎车县",
        }, {
            "value": u"叶城县", "label": u"叶城县",
        }, {
            "value": u"麦盖提县", "label": u"麦盖提县",
        }, {
            "value": u"岳普湖县", "label": u"岳普湖县",
        }, {
            "value": u"伽师县", "label": u"伽师县",
        }, {
            "value": u"巴楚县", "label": u"巴楚县",
        }, {
            "value": u"塔什库尔干塔吉克自治县", "label": u"塔什库尔干塔吉克自治县",
        }]
    }, {
        "value": u"和田地区", "label": u"和田地区",
        "children": [{
            "value": u"和田市", "label": u"和田市",
        }, {
            "value": u"和田县", "label": u"和田县",
        }, {
            "value": u"墨玉县", "label": u"墨玉县",
        }, {
            "value": u"皮山县", "label": u"皮山县",
        }, {
            "value": u"洛浦县", "label": u"洛浦县",
        }, {
            "value": u"策勒县", "label": u"策勒县",
        }, {
            "value": u"于田县", "label": u"于田县",
        }, {
            "value": u"民丰县", "label": u"民丰县",
        }]
    }, {
        "value": u"伊犁哈萨克自治州", "label": u"伊犁哈萨克自治州",
        "children": [{
            "value": u"伊宁市", "label": u"伊宁市",
        }, {
            "value": u"奎屯市", "label": u"奎屯市",
        }, {
            "value": u"霍尔果斯市", "label": u"霍尔果斯市",
        }, {
            "value": u"伊宁县", "label": u"伊宁县",
        }, {
            "value": u"察布查尔锡伯自治县", "label": u"察布查尔锡伯自治县",
        }, {
            "value": u"霍城县", "label": u"霍城县",
        }, {
            "value": u"巩留县", "label": u"巩留县",
        }, {
            "value": u"新源县", "label": u"新源县",
        }, {
            "value": u"昭苏县", "label": u"昭苏县",
        }, {
            "value": u"特克斯县", "label": u"特克斯县",
        }, {
            "value": u"尼勒克县", "label": u"尼勒克县",
        }]
    }, {
        "value": u"塔城地区", "label": u"塔城地区",
        "children": [{
            "value": u"塔城市", "label": u"塔城市",
        }, {
            "value": u"乌苏市", "label": u"乌苏市",
        }, {
            "value": u"额敏县", "label": u"额敏县",
        }, {
            "value": u"沙湾县", "label": u"沙湾县",
        }, {
            "value": u"托里县", "label": u"托里县",
        }, {
            "value": u"裕民县", "label": u"裕民县",
        }, {
            "value": u"和布克赛尔蒙古自治县", "label": u"和布克赛尔蒙古自治县",
        }]
    }, {
        "value": u"阿勒泰地区", "label": u"阿勒泰地区",
        "children": [{
            "value": u"阿勒泰市", "label": u"阿勒泰市",
        }, {
            "value": u"布尔津县", "label": u"布尔津县",
        }, {
            "value": u"富蕴县", "label": u"富蕴县",
        }, {
            "value": u"福海县", "label": u"福海县",
        }, {
            "value": u"哈巴河县", "label": u"哈巴河县",
        }, {
            "value": u"青河县", "label": u"青河县",
        }, {
            "value": u"吉木乃县", "label": u"吉木乃县",
        }]
    }, {
        "value": u"自治区直辖县级行政区划", "label": u"自治区直辖县级行政区划",
        "children": [{
            "value": u"石河子市", "label": u"石河子市",
        }, {
            "value": u"阿拉尔市", "label": u"阿拉尔市",
        }, {
            "value": u"图木舒克市", "label": u"图木舒克市",
        }, {
            "value": u"五家渠市", "label": u"五家渠市",
        }, {
            "value": u"北屯市", "label": u"北屯市",
        }, {
            "value": u"铁门关市", "label": u"铁门关市",
        }, {
            "value": u"双河市", "label": u"双河市",
        }, {
            "value": u"可克达拉市", "label": u"可克达拉市",
        }, {
            "value": u"昆玉市", "label": u"昆玉市",
        }]
    }]
}]
