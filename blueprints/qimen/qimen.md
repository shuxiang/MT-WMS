# qimen相关配置

0. 开通qimen相关应用(wms)与企业认证

1. 配置 qimen 参数
    qimen_url        = qimen标准地址或对方地址
    qimen_customerid = qimen标准客户id或空
    qimen_secret     = qimen标准appsecret或空

2. 提供我方qimen地址给对方或qimen控制台, 提供我方公司码customerid, 仓库码, 货主码, secret, appkey(MFOS)

3. 单据完成后会自动回传, 自动回传不成功的会定时回传(10分钟), 手动点击按钮回传未做


## 货品同步
```
request ItemSynRequest  false       
    actionType  String  true    add 操作类型(两种类型：add|update)
    warehouseCode   String  true    CK1234  仓库编码(统仓统配等无需ERP指定仓储编码的情况填OTHER)
    ownerCode   String  true    HZ123   货主编码
    supplierCode    String  false   GY123   供应商编码
    supplierName    String  false   淘宝  供应商名称
    extendProps Map false       扩展属性
    item    Item    false       商品信息
        itemCode    String  true    I1234   商品编码
        itemId  String  false   WI1234  仓储系统商品编码(该字段是WMS分配的商品编号;WMS如果分配了商品编码;则后续的商品操作都需要传该字段;如果WMS不使用;WMS可 以返回itemId=itemCode的值)
        goodsCode   String  false   H1234   货号
        itemName    String  true    SN123   商品名称
        shortName   String  false   JC123   商品简称
        englishName String  false   EN123   英文名
        barCode String  true    T1;T2   条形码(可多个;用分号;隔开)
        skuProperty String  false   红色  商品属性(如红色;XXL)
        stockUnit   String  false   个   商品计量单位
        length  String  false   12.0    长(单位：厘米)
        width   String  false   12.0    宽(单位：厘米)
        height  String  false   12.0    高(单位：厘米)
        volume  String  false   12.0    体积(单位：升)
        grossWeight String  false   12.0    毛重(单位：千克)
        netWeight   String  false   12.0    净重(单位：千克)
        color   String  false   红色  颜色
        size    String  false   5英尺 尺寸
        title   String  false   淘公仔 渠道中的商品标题
        categoryId  String  false   LB123   商品类别ID
        categoryName    String  false   手机  商品类别名称
        pricingCategory String  false   手机类 计价货类
        safetyStock Number  false   12  安全库存
        itemType    String  true    ZC  商品类型(ZC=正常商品;FX=分销商品;ZH=组合商品;ZP=赠品;BC=包材;HC=耗材;FL=辅料;XN=虚拟品;FS=附属品;CC=残次品; OTHER=其它;只传英文编码)
        tagPrice    String  false   12.0    吊牌价
        retailPrice String  false   12.0    零售价
        costPrice   String  false   12.0    成本价
        purchasePrice   String  false   12.0    采购价
        seasonCode  String  false   CHUN    季节编码
        seasonName  String  false   春季  季节名称
        brandCode   String  false   LAL 品牌代码
        brandName   String  false   HM  品牌名称
        isSNMgmt    String  false   N   是否需要串号管理(Y/N ;默认为N)
        productDate String  false   2016-09-09  生产日期(YYYY-MM-DD)
        expireDate  String  false   2016-09-09  过期日期(YYYY-MM-DD)
        isShelfLifeMgmt String  false   N   是否需要保质期管理(Y/N ;默认为N)
        shelfLife   Number  false   1   保质期(单位：小时)
        rejectLifecycle Number  false   1   保质期禁收天数
        lockupLifecycle Number  false   1   保质期禁售天数
        adventLifecycle Number  false   1   保质期临期预警天数
        isBatchMgmt String  false   N   是否需要批次管理(Y/N ;默认为N)
        batchCode   String  false   P1234   批次代码
        batchRemark String  false   备注信息    批次备注
        packCode    String  false   B12 包装代码
        pcs String  false   XG123   箱规
        originAddress   String  false   HK  商品的原产地
        approvalNumber  String  false   PB123   批准文号
        isFragile   String  false   N   是否易碎品(Y/N ;默认为N)
        isHazardous String  false   N   是否危险品(Y/N ;默认为N)
        remark  String  false   备注信息    备注
        createTime  String  false   2017-09-09 12:00:00 创建时间(YYYY-MM-DD HH:MM:SS)
        updateTime  String  false   2017-09-09 12:00:00 更新时间(YYYY-MM-DD HH:MM:SS)
        isValid String  false   N   是否有效(Y/N ;默认为N)
        isSku   String  false   N   是否sku(Y/N ;默认为N)
        packageMaterial String  false   BX123   商品包装材料类型
        supplierCode    String  false   temp    temp
        logisticsType   String  false   0   销售配送方式（0=自配|1=菜鸟）
        isLiquid    String  false   Y   是否液体, Y/N, (默认为N)
```

## 入库单
```
entryOrder  EntryOrder  false       入库单信息
    entryOrderCode  String  true    E1234   入库单号
    ownerCode   String  true    O1234   货主编码
    purchaseOrderCode   String  false   C123455 采购单号(当orderType=CGRK时使用)
    warehouseCode   String  true    W1234   入库仓库编码(统仓统配等无需ERP指定仓储编码的情况填OTHER)
    orderCreateTime String  false   2016-09-09 12:00:00 订单创建时间(YYYY-MM-DD HH:MM:SS)
    orderType   String  false   SCRK    业务类型(SCRK=生产入库;LYRK=领用入库;CCRK=残次品入库;CGRK=采购入库;DBRK=调拨入库;QTRK=其他入库;B2BRK=B2B入 库;XNRK=虚拟入库;只传英文编码)
    remark  String  false   备注信息    备注
    totalOrderLines String  false   12  totalOrderLines
    warehouseName   String  false   E1234   入库仓库名称
    sourceWarehouseCode String  false   E1234   出库仓库编码
    sourceWarehouseName String  false   E1234   出库仓库名称

    relatedOrders   RelatedOrder[]  false       关联订单信息
        orderType   String  false   CG  关联的订单类型(CG=采购单;DB=调拨单;CK=出库单;RK=入库单;只传英文编码)
        orderCode   String  false   G1234   关联的订单编号
    expectStartTime String  false   2015-09-09 12:00:00 预期到货时间(YYYY-MM-DD HH:MM:SS)
    expectEndTime   String  false   2015-09-09 12:00:00 最迟预期到货时间(YYYY-MM-DD HH:MM:SS)
    logisticsCode   String  false   SF  物流公司编码(SF=顺丰、EMS=标准快递、EYB=经济快件、ZJS=宅急送、YTO=圆通 、ZTO=中通(ZTO)、HTKY=百世汇通、 UC=优速、STO=申通、TTKDEX=天天快递、QFKD=全峰、FAST=快捷、POSTB=邮政小包、GTO=国通、YUNDA=韵达、JD=京东配送、DD=当当宅配、 AMAZON=亚马逊物流、OTHER=其他(只传英文编码))
    logisticsName   String  false   顺丰  物流公司名称
    expressCode String  false   Y1234   运单号
    supplierCode    String  false   G1234   供应商编码
    supplierName    String  false   GN1234  供应商名称
    operatorCode    String  false   ON1234  操作员编码
    operatorName    String  false   老王  操作员名称
    operateTime String  false   2017-09-09 12:00:00 操作时间(YYYY-MM-DD HH:MM:SS)
    senderInfo  SenderInfo  false       发件人信息
        company String  false   淘宝  公司名称
        name    String  true    老王  姓名
        zipCode String  false   043300  邮编
        tel String  false   81020340    固定电话
        mobile  String  true    13214567869 移动电话
        email   String  false   345@gmail.com   电子邮箱
        countryCode String  false   051532  国家二字码
        province    String  true    浙江省 省份
        city    String  true    杭州  城市
        area    String  false   余杭  区域
        town    String  false   横加桥 村镇
        detailAddress   String  true    杭州市余杭区989号  详细地址
    receiverInfo    ReceiverInfo    false       收件人信息
        company String  false   淘宝  公司名称
        name    String  true    老王  姓名
        zipCode String  false   043300  邮编
        tel String  false   808786543   固定电话
        mobile  String  true    13423456785 移动电话
        idType  String  false   1   收件人证件类型(1-身份证;2-军官证;3-护照;4-其他)
        idNumber    String  false   12345   收件人证件号码
        email   String  false   878987654@qq.com    电子邮箱
        countryCode String  false   045565  国家二字码
        province    String  true    浙江省 省份
        city    String  true    杭州  城市
        area    String  false   余杭  区域
        town    String  false   横加桥 村镇
        detailAddress   String  true    杭州市余杭区989号  详细地址
    
orderLines  OrderLine[] false       入库单详情
    outBizCode  String  false   O123    外部业务编码(消息ID;用于去重;当单据需要分批次发送时使用)
    orderLineNo String  false   EL123   入库单的行号
    ownerCode   String  true    O123    货主编码
    itemCode    String  true    I123    商品编码
    itemId  String  false   CI123   仓储系统商品ID
    itemName    String  false   IN123   商品名称
    planQty Number  true    12  应收商品数量
    skuProperty String  false   属性  商品属性
    purchasePrice   String  false   12.0    采购价
    retailPrice String  false   12.0    零售价
    inventoryType   String  false   ZP  库存类型(ZP=正品;CC=残次;JS=机损;XS=箱损;默认为ZP)
    productDate String  false   2017-09-09  商品生产日期(YYYY-MM-DD)
    expireDate  String  false   2017-09-09  商品过期日期(YYYY-MM-DD)
    produceCode String  false   P1234   生产批号
    batchCode   String  false   PCODE123    批次编码
    unit    String  false   个/盒/箱/柜等    单位
    snList  SnList  false       sn编码列表
        sn  String[]    false       sn编码
extendProps Map false       扩展属性
```

## 入库单确认
```
entryOrder  EntryOrder  false       入库单信息
    orderCode   String  false   订单编码    订单编码
    orderId String  false   后端订单id  后端订单id
    orderType   String  false   订单类型    订单类型
    warehouseName   String  false   仓库名称    仓库名称
    totalOrderLines Number  false   12  单据总行数(当单据需要分多个请求发送时;发送方需要将totalOrderLines填入;接收方收到后;根据实际接收到的 条数和 totalOrderLines进行比对;如果小于;则继续等待接收请求。如果等于;则表示该单据的所有请求发送完 成)
    entryOrderCode  String  true    E1234   入库单号
    ownerCode   String  true    O1234   货主编码
    purchaseOrderCode   String  false   C123455 采购单号(当orderType=CGRK时使用)
    warehouseCode   String  true    W1234   仓库编码(统仓统配等无需ERP指定仓储编码的情况填OTHER)
    entryOrderId    String  false   E1234   仓储系统入库单ID
    entryOrderType  String  false   SCRK    入库单类型(SCRK=生产入库;LYRK=领用入库;CCRK=残次品入库;CGRK=采购入库;DBRK=调拨入库;QTRK=其他入 库;B2BRK=B2B入库)
    outBizCode  String  true    O1234   外部业务编码(消息ID;用于去重;ISV对于同一请求;分配一个唯一性的编码。用来保证因为网络等原因导致重复传输;请求 不会被重复处理)
    confirmType Number  false   0   支持出入库单多次收货(多次收货后确认时:0:表示入库单最终状态确认;1:表示入库单中间状态确认;每次入库传入的数量为增 量;特殊情况;同一入库单;如果先收到0;后又收到1;允许修改收货的数量)
    status  String  true    NEW 入库单状态(NEW-未开始处理;ACCEPT-仓库接单;PARTFULFILLED-部分收货完成;FULFILLED-收货完成;EXCEPTION-异 常;CANCELED-取消;CLOSED-关闭;REJECT-拒单;CANCELEDFAIL-取消失败;只传英文编码)
    operateTime String  false   2017-09-09 12:00:00 操作时间(YYYY-MM-DD HH:MM:SS;当status=FULFILLED;operateTime为入库时间)
    remark  String  false   备注信息    备注
    freight String  false   奇门仓储字段,说明,string(50),,  邮费
    subOrderType    String  false   hss 入库单确认的其他入库子类型，用于entryOrderType设置为其他入库时设置
    responsibleDepartment   String  false   财务部 该笔入库单的费用承担部门或责任部门
    shopNick    String  true    旗舰店 店铺名称
    shopCode    String  true    ssss    店铺编码
orderLines  OrderLine[] false       订单信息
    outBizCode  String  false   O123    外部业务编码(消息ID;用于去重;当单据需要分批次发送时使用)
    orderLineNo String  false   EL123   入库单的行号
    ownerCode   String  true    O123    货主编码
    itemCode    String  true    I123    商品编码
    itemId  String  false   CI123   仓储系统商品ID
    itemName    String  false   IN123   商品名称
    planQty Number  true    12  应收商品数量
    inventoryType   String  false   ZP  库存类型(ZP=正品;CC=残次;JS=机损;XS=箱损;默认为ZP)
    actualQty   Number  true    12  实收数量
    productDate String  false   2017-09-09  商品生产日期(YYYY-MM-DD)
    expireDate  String  false   2017-09-09  商品过期日期(YYYY-MM-DD)
    produceCode String  false   P1234   生产批号
    batchCode   String  false   PCODE123    批次编码
    batchs  Batch[] false       批次信息
    remark  String  false   备注信息    备注
    unit    String  false   盒/箱/个等  单位
```

## 退货入库
```
returnOrder ReturnOrder false       退货单信息
    returnOrderCode String  true    R1234   ERP的退货入库单编码
    warehouseCode   String  true    W1234   仓库编码(统仓统配等无需ERP指定仓储编码的情况填OTHER)
    orderType   String  false   THRK    单据类型(THRK=退货入库;HHRK=换货入库;只传英文编码)
    orderFlag   String  false   VISIT   用字符串格式来表示订单标记列表(比如VISIT^ SELLER_AFFORD^SYNC_RETURN_BILL等;中间用“^”来隔开订单标记list (所 有字母全部大写) VISIT=上门；SELLER_AFFORD=是否卖家承担运费(默认是)SYNC_RETURN_BILL=同时退回发票)
    preDeliveryOrderCode    String  true    PD1234  原出库单号(ERP分配)
    preDeliveryOrderId  String  false   PDI1234 原出库单号(WMS分配)
    logisticsCode   String  true    SF  物流公司编码(SF=顺丰、EMS=标准快递、EYB=经济快件、ZJS=宅急送、YTO=圆通、ZTO=中通(ZTO)、HTKY=百世汇通、 UC=优速、STO=申通、TTKDEX=天天快递、QFKD=全峰、FAST=快捷、POSTB=邮政小包、GTO=国通、YUNDA=韵达、JD=京东配送、DD=当当宅配、 AMAZON=亚马逊物流、OTHER=其他;只传英文编码)
    logisticsName   String  false   顺丰  物流公司名称
    expressCode String  false   YD1234  运单号
    returnReason    String  false   破损退货    退货原因
    buyerNick   String  false   淘宝  买家昵称
    senderInfo  SenderInfo  false       发件人信息
    remark  String  false   备注信息    备注
    sourcePlatformCode  String  false   TB  订单来源平台编码, string (50),TB= 淘宝 、TM=天猫 、JD=京东、DD=当当、PP=拍拍、YX=易讯、EBAY=ebay、QQ=QQ网购、AMAZON=亚马逊、SN=苏宁、GM=国美、WPH=唯品会、JM=聚美、LF=乐蜂、MGJ=蘑菇街、JS=聚尚、PX=拍鞋、YT=银泰、YHD=1号店、VANCL=凡客、YL=邮乐、YG=优购、1688=阿里巴巴、POS=POS门店、MIA=蜜芽、GW=商家官网、CT=村淘、YJWD=云集微店、PDD=拼多多、OTHERS=其他,
    sourcePlatformName  String  false   淘宝  订单来源平台名称
    shopNick    String  false   店铺名称    店铺名称
    sellerNick  String  false   卖家名称    卖家名称
orderLines  OrderLine[] false       订单信息
    orderLineNo String  false   D1234   单据行号
    sourceOrderCode String  false   PD1224  交易平台订单
    subSourceOrderCode  String  false   PL1234  交易平台子订单编码
    ownerCode   String  true    HZ1234  货主编码
    itemCode    String  true    I1234   商品编码
    itemId  String  false   CK1234  仓储系统商品编码(条件为提供后端（仓储系统）商品编码的仓储系统)
    inventoryType   String  false   ZP  库存类型(ZP=正品;CC=残次;JS=机损;XS=箱损;默认为ZP)
    planQty Number  true    12  应收商品数量
    batchCode   String  false   P123    批次编码
    productDate String  false   2016-09-09  生产日期(YYYY-MM-DD)
    expireDate  String  false   2016-09-09  过期日期(YYYY-MM-DD)
    produceCode String  false   P1234   生产批号
    snList  SnList  false       sn列表
    orderFlag   String  true    visit   用字符串格式来表示订单标记列表(比如VISIT^ SELLER_AFFORD^SYNC_RETURN_BILL等;中间用“^”来隔开订单标记list (所 有字母全部大写) VISIT=上门；SELLER_AFFORD=是否卖家承担运费(默认是)SYNC_RETURN_BILL=同时退回发票)
    returnReason    String  true    破损退货    退货原因
```

## 退货入库单确认
```
returnOrder ReturnOrder false       退货单信息
    returnOrderCode String  true    R1234   ERP的退货入库单编码
    returnOrderId   String  false   R1234   仓库系统订单编码
    warehouseCode   String  true    W1234   仓库编码(统仓统配等无需ERP指定仓储编码的情况填OTHER)
    outBizCode  String  false   OZ1234  外部业务编码(消息ID;用于去重;ISV对于同一请求;分配一个唯一性的编码。用来保证因为网络等原因导致重复传输;请求不会 被重复处理)
    orderType   String  false   THRK    单据类型(THRK=退货入库;HHRK=换货入库;只传英文编码)
    orderConfirmTime    String  false   2016-09-09 12:00:00 确认入库时间(YYYY-MM-DD HH:MM:SS)
    logisticsCode   String  true    SF  物流公司编码(SF=顺丰、EMS=标准快递、EYB=经济快件、ZJS=宅急送、YTO=圆通、ZTO=中通(ZTO)、HTKY=百世汇通、 UC=优速、STO=申通、TTKDEX=天天快递、QFKD=全峰、FAST=快捷、POSTB=邮政小包、GTO=国通、YUNDA=韵达、JD=京东配送、DD=当当宅配、 AMAZON=亚马逊物流、OTHER=其他;只传英文编码)
    logisticsName   String  false   顺丰  物流公司名称
    expressCode String  false   YD1234  运单号
    returnReason    String  false   破损退货    退货原因
    remark  String  false   备注信息    备注
    senderInfo  SenderInfo  false       发件人信息
        company String  false   淘宝  公司名称
        name    String  true    老王  姓名
        zipCode String  false   043300  邮编
        tel String  false   81020340    固定电话
        mobile  String  true    13214567869 移动电话
        email   String  false   345@gmail.com   电子邮箱
        countryCode String  false   051532  国家二字码
        province    String  true    浙江省 省份
        city    String  true    杭州  城市
        area    String  false   余杭  区域
        town    String  false   横加桥 村镇
        detailAddress   String  true    杭州市余杭区989号  详细地址
    remark  String  false   备注  备注
orderLines  OrderLine[] false       订单信息
    remark  String  false   备注  备注
    orderLineNo String  false   D1234   单据行号
    sourceOrderCode String  false   PD1224  交易平台订单
    subSourceOrderCode  String  false   PL1234  交易平台子订单编码
    ownerCode   String  true    HZ1234  货主编码
    itemCode    String  true    I1234   商品编码
    itemId  String  false   CK1234  仓储系统商品编码(条件为提供后端（仓储系统）商品编码的仓储系统)
    inventoryType   String  false   ZP  库存类型(ZP=正品;CC=残次;JS=机损;XS=箱损;默认为ZP)
    planQty Number  true    12  应收商品数量
    batchCode   String  false   P123    批次编码
    productDate String  false   2016-09-09  生产日期(YYYY-MM-DD)
    expireDate  String  false   2016-09-09  过期日期(YYYY-MM-DD)
    produceCode String  false   P1234   生产批号
    batchs  Batch[] false       批次信息
    qrCode  String  false   1;1;1   商品的二维码(类似电子产品的SN码;用来进行商品的溯源;多个二维码之间用分号;隔开)
    actualQty   String  true    12  实收商品数量
```

## 出库单
```
deliveryOrder   DeliveryOrder   false       出库单信息
    totalOrderLines Number  false   12  单据总行数(当单据需要分多个请求发送时;发送方需要将totalOrderLines填入;接收方收到后;根据实际接收到的条数和totalOrderLines进行比对;如果小于;则继续等待接收请求。如果等于;则表示该单据的所有请求发送完成.)
    deliveryOrderCode   String  true    TB1234  出库单号
    orderType   String  true    PTCK    出库单类型(PTCK=普通出库单;DBCK=调拨出库;B2BCK=B2B出库;QTCK=其他出库;CGTH=采购退货出库单;XNCK=虚拟出库单, JITCK=唯品出库)
    relatedOrders   RelatedOrder[]  false       关联单据信息
    warehouseCode   String  true    CK1234  仓库编码(统仓统配等无需ERP指定仓储编码的情况填OTHER)
    createTime  String  true    2016-09-09 12:00:00 出库单创建时间(YYYY-MM-DD HH:MM:SS)
    scheduleDate    String  false   2017-09-09  要求出库时间(YYYY-MM-DD)
    logisticsCode   String  false   SF  物流公司编码(SF=顺丰、EMS=标准快递、EYB=经济快件、ZJS=宅急送、YTO=圆通 、ZTO=中通(ZTO)、HTKY=百世汇通、UC=优速、STO=申通、TTKDEX=天天快递、QFKD=全峰、FAST=快捷、POSTB=邮政小包、GTO=国通、YUNDA=韵达、JD=京东配送、DD=当当宅配、AMAZON=亚马逊物流、OTHER=其他;只传英文编码)
    logisticsName   String  false   顺丰  物流公司名称(包括干线物流公司等)
    supplierCode    String  false   TB  供应商编码
    supplierName    String  false   淘宝  供应商名称
    transportMode   String  false   自提  提货方式(到仓自提、快递、干线物流)
    pickerInfo  PickerInfo  false       提货人信息
    senderInfo  SenderInfo  false       发件人信息
        company String  false   淘宝  公司名称
        name    String  true    老王  姓名
        zipCode String  false   043300  邮编
        tel String  false   81020340    固定电话
        mobile  String  true    13214567869 移动电话
        email   String  false   345@gmail.com   电子邮箱
        countryCode String  false   051532  国家二字码
        province    String  true    浙江省 省份
        city    String  true    杭州  城市
        area    String  false   余杭  区域
        town    String  false   横加桥 村镇
        detailAddress   String  true    杭州市余杭区989号  详细地址
        id  String  false   476543213245733 证件号
    receiverInfo    ReceiverInfo    false       收件人信息
        company String  false   淘宝  公司名称
        name    String  true    老王  姓名
        zipCode String  false   043300  邮编
        tel String  false   808786543   固定电话
        mobile  String  true    13423456785 移动电话
        idType  String  false   1   收件人证件类型(1-身份证、2-军官证、3-护照、4-其他)
        idNumber    String  false   1234567 收件人证件号码
        email   String  false   878987654@qq.com    电子邮箱
        countryCode String  false   045565  国家二字码
        province    String  true    浙江省 省份
        city    String  true    杭州  城市
        area    String  false   余杭  区域
        town    String  false   横加桥 村镇
        detailAddress   String  true    杭州市余杭区989号  详细地址
        id  String  false   4713242536  证件号
    remark  String  false   备注信息    备注
    orderSourceType String  false   VIP 出库单渠道类型,VIP=唯品会，FX=分销 ，SHOP=门店
    receivingTime   String  false   2016-09-09 12:00:00 到货时间(YYYY-MM-DD HH:MM:SS)
    shippingTime    String  false   2016-09-09 12:00:00 送货时间(YYYY-MM-DD HH:MM:SS)
    targetWarehouseName String  false   入库仓库名称, string (50) 入库仓库名称, string (50)
    targetWarehouseCode String  false   入库仓库编码, string (50) ，统仓统配等无需ERP指定仓储编码的情况填OTHER  入库仓库编码, string (50) ，统仓统配等无需ERP指定仓储编码的情况填OTHER
    targetEntryOrderCode    String  false   关联的入库单号（ERP分配）  关联的入库单号（ERP分配）
    warehouseName   String  false   123 仓库名称
orderLines  OrderLine[] false       单据信息
    outBizCode  String  false   OB1234  外部业务编码(消息ID;用于去重;当单据需要分批次发送时使用)
    orderLineNo String  false   11  单据行号
    ownerCode   String  true    H1234   货主编码
    itemCode    String  true    I1234   商品编码
    itemId  String  false   W1234   仓储系统商品编码
    inventoryType   String  false   ZP  库存类型(ZP=正品;CC=残次;JS=机损;XS= 箱损;ZT=在途库存;默认为查所有类型的库存)
    itemName    String  false   淘公仔 商品名称
    planQty Number  true    11  应发商品数量
    batchCode   String  false   123 批次编码
    productDate String  false   2016-07-06  生产日期(YYYY-MM-DD)
    expireDate  String  false   2016-07-06  过期日期(YYYY-MM-DD)
    produceCode String  false   P11233  生产批号
    platformCode    String  false   123456789   交易平台商品编码
    unit    String  false   个/箱/盒等  单位
    extendProps Map false       扩展属性
```
## 出库单确认
```
deliveryOrder   DeliveryOrder   false       deliveryOrder
    totalOrderLines Number  false   11  单据总行数
    deliveryOrderCode   String  true    Ox123456    出库单号
    deliveryOrderId String  false   Dx123456    仓储系统出库单号
    warehouseCode   String  true    Wx123456    仓库编码
    orderType   String  true    PTCK    出库单类型
    status  String  false   NEW 出库单状态
    outBizCode  String  false   23456   外部业务编码
    confirmType Number  false   1   支持出库单多次发货的状态位
    logisticsCode   String  false   SF  物流公司编码
    logisticsName   String  false   顺丰  物流公司名称
    expressCode String  false   Q123456 运单号
    orderConfirmTime    String  false   2015-09-12 12:00:00 订单完成时间
    responsibleDepartment   String  false   财务部 该笔出库单的费用承担部门或责任部门
    subOrderType    String  false   hss 出库单确认其他出库单的子类型，用于 orderType设置为其他 出库单时设置
packages    Package[]   false       packages
orderLines  OrderLine[] false       orderLines
    outBizCode  String  false   O123456 外部业务编码
    orderLineNo String  false   1   单据行号
    itemCode    String  true    SH123456    商品编码
    itemId  String  false   Q123456 商品仓储系统编码
    itemName    String  false   小都进 商品名称
    inventoryType   String  false   ZP  库存类型
    actualQty   Number  true    11  实发商品数量
    batchCode   String  false   P12 批次编号
    productDate String  false   2015-09-12  生产日期
    expireDate  String  false   2015-09-12  过期日期
    produceCode String  false   P23 生产批号
    batchs  Batch[] false       batchs
    unit    String  false   个/盒/箱等  单位
```

## 发货出库单
```
deliveryOrder   DeliveryOrder   false       发货单信息
    deliveryOrderCode   String  true    TB1234  出库单号
    preDeliveryOrderCode    String  false   Old1234 原出库单号(ERP分配)
    preDeliveryOrderId  String  false   Oragin1234  原出库单号(WMS分配)
    orderType   String  true    JYCK    出库单类型(JYCK=一般交易出库单;HHCK=换货出库单;BFCK=补发出库单;QTCK=其他出 库 单)
    warehouseCode   String  true    OTHER   仓库编码(统仓统配等无需ERP指定仓储编码的情况填OTHER)
    orderFlag   String  false   COD 订单标记(用字符串格式来表示订单标记列表:例如COD=货到付款;LIMIT=限时配 送;PRESELL=预 售;COMPLAIN=已投诉;SPLIT=拆单;EXCHANGE=换货;VISIT=上门;MODIFYTRANSPORT=是否 可改配送方式;CONSIGN = 物流宝代理发货;SELLER_AFFORD=是否卖家承担运费;FENXIAO=分销订 单)
    sourcePlatformCode  String  false   TB  订单来源平台编码(TB=淘宝、TM=天猫、JD=京东、DD=当当、PP=拍拍、YX= 易讯、 EBAY=ebay、QQ=QQ网购、AMAZON=亚马逊、SN=苏宁、GM=国美、WPH=唯品会、JM=聚美、LF=乐蜂 、MGJ=蘑菇街、 JS=聚尚、PX=拍鞋、YT=银泰、YHD=1号店、VANCL=凡客、YL=邮乐、YG=优购、1688=阿 里巴巴、POS=POS门店、 MIA=蜜芽、OTHER=其他(只传英文编码))
    sourcePlatformName  String  false   淘宝  订单来源平台名称
    createTime  String  true    2016-07-06 12:00:00 发货单创建时间(YYYY-MM-DD HH:MM:SS)
    placeOrderTime  String  true    2016-07-06 12:00:00 前台订单/店铺订单的创建时间/下单时间
    payTime String  false   2016-07-06 12:00:00 订单支付时间(YYYY-MM-DD HH:MM:SS)
    payNo   String  false   P1234   支付平台交易号
    operatorCode    String  false   0123    操作员(审核员)编码
    operatorName    String  false   老王  操作员(审核员)名称
    operateTime String  true    2016-07-06 12:00:00 操作(审核)时间(YYYY-MM-DD HH:MM:SS)
    shopNick    String  true    淘宝店 店铺名称
    sellerNick  String  false   淘宝店主    卖家名称
    buyerNick   String  false   淘公仔 买家昵称
    totalAmount String  false   123 订单总金额(订单总金额=应收金额+已收金额=商品总金额-订单折扣金额+快递费用 ;单位 元)
    itemAmount  String  false   234 商品总金额(元)
    discountAmount  String  false   111 订单折扣金额(元)
    freight String  false   111 快递费用(元)
    arAmount    String  false   111 应收金额(消费者还需要支付多少--货到付款时消费者还需要支付多少约定使用这个字 段;单位元 )
    gotAmount   String  false   111 已收金额(消费者已经支付多少;单位元)
    serviceFee  String  false   111 COD服务费
    logisticsCode   String  true    SF  物流公司编码(SF=顺丰、EMS=标准快递、EYB=经济快件、ZJS=宅急送、YTO=圆通 、ZTO=中 通(ZTO)、HTKY=百世汇通、UC=优速、STO=申通、TTKDEX=天天快递、QFKD=全峰、FAST=快捷 、POSTB=邮政小包、 GTO=国通、YUNDA=韵达、JD=京东配送、DD=当当宅配、AMAZON=亚马逊物流、 OTHER=其他)
    logisticsName   String  false   顺丰  物流公司名称
    expressCode String  false   Y12345  运单号
    logisticsAreaCode   String  false   043300  快递区域编码
    deliveryRequirements    DeliveryRequirements    false       发货要求列表
    senderInfo  SenderInfo  false       发件人信息
    receiverInfo    ReceiverInfo    false       收件人信息
        isUrgency   String  false   N   是否紧急(Y/N;默认为N)
        invoiceFlag String  false   N   是否需要发票(Y/N;默认为N)
        invoices    Invoice[]   false       发票信息
        insuranceFlag   String  false   N   是否需要保险(Y/N;默认为N)
        insurance   Insurance   false       保险信息
        buyerMessage    String  false   商品不错    买家留言
        sellerMessage   String  false   谢谢光顾    卖家留言
    remark  String  false   备注信息    备注
    serviceCode String  false   NCWLJH  服务编码
    ownerCode   String  false   TB1234  旧版本货主编码
    latestCollectionTime    String  false   最晚揽收时间, string (19) , YYYY-MM-DD HH:MM:SS   最晚揽收时间, string (19) , YYYY-MM-DD HH:MM:SS
    latestDeliveryTime  String  false   最晚发货时间, string (19) , YYYY-MM-DD HH:MM:SS   最晚发货时间, string (19) , YYYY-MM-DD HH:MM:SS
orderLines  OrderLine[] false       订单列表
    orderLineNo String  false   11  单据行号
    sourceOrderCode String  false   S12345  交易平台订单
    subSourceOrderCode  String  false   S1234   交易平台子订单编码
    payNo   String  false   J1234   支付平台交易号(淘系订单传支付宝交易号)
    ownerCode   String  true    H1234   货主编码
    itemCode    String  true    I1234   商品编码
    itemId  String  false   W1234   仓储系统商品编码
    inventoryType   String  false   ZP  库存类型(ZP=正品;CC=残次;JS=机损;XS= 箱损;ZT=在途库存;默认为查所有类型的库存)
    itemName    String  false   淘公仔 商品名称
    extCode String  false   J1234   交易平台商品编码
    planQty Number  true    11  应发商品数量
    retailPrice String  false   12.0    零售价(零售价=实际成交价+单件商品折扣金额)
    actualPrice String  true    12.0    实际成交价
    discountAmount  String  false   0   单件商品折扣金额
    batchCode   String  false   123 批次编码
    productDate String  false   2016-07-06  生产日期(YYYY-MM-DD)
    expireDate  String  false   2016-07-06  过期日期(YYYY-MM-DD)
    produceCode String  false   123 生产批号
extendProps Map false       扩展属性
```

## 发货单确认
## 出库单确认
```
deliveryOrder   DeliveryOrder   false       deliveryOrder
    totalOrderLines Number  false   11  单据总行数
    deliveryOrderCode   String  true    Ox123456    出库单号
    deliveryOrderId String  false   Dx123456    仓储系统出库单号
    warehouseCode   String  true    Wx123456    仓库编码
    orderType   String  true    PTCK    出库单类型
    status  String  false   NEW 出库单状态
    outBizCode  String  false   23456   外部业务编码
    confirmType Number  false   1   支持出库单多次发货的状态位
    logisticsCode   String  false   SF  物流公司编码
    logisticsName   String  false   顺丰  物流公司名称
    expressCode String  false   Q123456 运单号
    orderConfirmTime    String  false   2015-09-12 12:00:00 订单完成时间
    responsibleDepartment   String  false   财务部 该笔出库单的费用承担部门或责任部门
    subOrderType    String  false   hss 出库单确认其他出库单的子类型，用于 orderType设置为其他 出库单时设置
packages    Package[]   false       packages
orderLines  OrderLine[] false       orderLines
    outBizCode  String  false   O123456 外部业务编码
    orderLineNo String  false   1   单据行号
    itemCode    String  true    SH123456    商品编码
    itemId  String  false   Q123456 商品仓储系统编码
    itemName    String  false   小都进 商品名称
    inventoryType   String  false   ZP  库存类型
    actualQty   Number  true    11  实发商品数量
    batchCode   String  false   P12 批次编号
    productDate String  false   2015-09-12  生产日期
    expireDate  String  false   2015-09-12  过期日期
    produceCode String  false   P23 生产批号
    batchs  Batch[] false       batchs
    unit    String  false   个/盒/箱等  单位
```

## 库存查询
```
criteriaList    Criteria[]  false       查询准则
    warehouseCode   String  false   W1234   仓库编码
    ownerCode   String  false   H1234   货主编码
    itemCode    String  true    I1234   商品编码
    itemId  String  false   C1234   仓储系统商品ID
    inventoryType   String  false   ZP  库存类型(ZP=正品;CC=残次;JS=机损;XS=箱损;ZT=在途库存;默认为查所有类型的库存)
    remark  String  false   备注  备注
extendProps Map false       扩展属性
remark  String  false   备注  备注
```


# API文档

## 签名算法(参数为示例参数)
do_sign(method='Method', customerid='Customerid', secret='Secret', timestamp='2020-11-20 20:01:01', app_key='MFOS', format='json', sign_method='md5', v='2.0'){
        kw = {}
        kw.method = method
        kw.format = format
        kw.customerid = customerid
        kw.app_key = app_key
        kw.sign_method = sign_method
        kw.v = v
        kw.timestamp = timestamp

        kw_list = []
        kw_list.append(secret)
        keys = kw.keys()

        # 排序后, keys = ['app_key', 'customerid', 'format', 'method', 'sign_method', 'timestamp', 'v']
        keys.sort()

        # 按排序结果将键与值插入到列表kw_list中, 或者相加成字符串
        for k in keys:
            kw_list.append(k)
            kw_list.append(kw[k])
        kw_list.append(body)

        # astr = "Secretapp_keyMFOScustomeridCustomeridformatjsonmethodMethodsign_methodmd5timestamp2020-11-20 20:01:01v2.0"
        astr = "".join(kw_list)

        # 做md5后取十进制, sign = "b5bf1901c5351e4e8785703a0a374ae9"
        sign = md5(astr).hexdigest()

        return sign
}
请求url=
"http://host/path?format=json&timestamp=2020-11-20+20%3A01%3A01&app_key=MFOS&customerid=Customerid&sign_method=md5&v=2.0&sign=b5bf1901c5351e4e8785703a0a374ae9&method=Method
b5bf1901c5351e4e8785703a0a374ae9"

http请求体(json格式):
{
    "request": {
        "orderLines": [
            {
                "planQty": "5/数量,数字", 
                "itemCode": "货品编码", 
                "itemName": "货品名称"
            }, 
            {
                "planQty": "4", 
                "itemCode": "货品编码2", 
                "itemName": "货品名称2"
            }
        ], 
        "deliveryOrder": {
            "senderInfo": {
                "province": "上海/必填,直辖市不要带市字", 
                "town": "浦江镇", 
                "name": "发货人名称/必填", 
                "area": "闵行区", 
                "mobile": "123/必填", 
                "detailAddress": "闵行区浦江镇xx路8号1103/必填", 
                "city": "上海市/必填,要带市字"
            }, 
            "warehouseCode": "default/仓库", 
            "deliveryOrderCode": "ck001/订单号", 
            "orderType": "CGRK/订单类型", 
            "receiverInfo": {
                "province": "上海/必填,直辖市不要带市字", 
                "town": "浦江镇", 
                "name": "发货人名称/必填", 
                "area": "闵行区", 
                "mobile": "123/必填", 
                "detailAddress": "闵行区浦江镇xx路8号1103/必填", 
                "city": "上海市/必填,要带市字"
            }, 
            "ownerCode": "default/货主号"
        }
    }
}

## 订单类型
入库单 类型(SCRK=生产入库;LYRK=领用入库;CCRK=残次品入库;CGRK=采购入库;DBRK=调拨入库;QTRK=其他入库;B2BRK=B2B入 库;XNRK=虚拟入库;只传英文编码)
退库入库单 类型(THRK=退货入库;HHRK=换货入库;只传英文编码)
出库单 类型(PTCK=普通出库单;DBCK=调拨出库;B2BCK=B2B出库;QTCK=其他出库;CGTH=采购退货出库单;XNCK=虚拟出库单, JITCK=唯品出库)
发货出库单 类型(JYCK=一般交易出库单;HHCK=换货出库单;BFCK=补发出库单;QTCK=其他出 库 单)

## 物流公司
淘宝 物流公司编码(SF=顺丰、EMS=标准快递、EYB=经济快件、ZJS=宅急送、YTO=圆通 、ZTO=中通(ZTO)、HTKY=百世汇通、UC=优速、STO=申通、TTKDEX=天天快递、QFKD=全峰、FAST=快捷、POSTB=邮政小包、GTO=国通、YUNDA=韵达、JD=京东配送、DD=当当宅配、AMAZON=亚马逊物流、OTHER=其他;只传英文编码)
快递鸟: [
        {"code":"SF", "name":"顺丰"},
        {"code":"EMS", "name":"EMS"},
        // {"code":"ZJS", "name":"宅急送"},  
        {"code":"YZPY", "name":"邮政快递包裹"},  ##
        {"code":"ZTKY", "name":"中铁快运"},  ##
        {"code":"YZBK", "name":"邮政国内标快"}, ##
        {"code":"UAPEX", "name":"全一快递"}, ##
        {"code":"UC", "name":"优速"},  
        {"code":"YD", "name":"韵达"},  #
        {"code":"YTO", "name":"圆通"},  
        {"code":"YCWL", "name":"远成"},  ##
        {"code":"ANE", "name":"安能"},  ##
        {"code":"HTKY", "name":"百世快递"}, 
        {"code":"ZTO", "name":"中通"},  
        {"code":"STO", "name":"申通"},  
        {"code":"DBL", "name":"德邦"},  ##
        {"code":"JD", "name":"京东"},  
        {"code":"XFEX", "name":"信丰"},  ##
        {"code":"GTO", "name":"国通"},  
        {"code":"HHTT", "name":"天天快递"},  ##
        {"code":"SURE", "name":"速尔快递"},  ##
        {"code":"PJ", "name":"品骏快递"}, ##
        {"code":"JDKY", "name":"京东快运"}, ##
        {"code":"ANEKY", "name":"安能快运"}, ##
        {"code":"DBLKY", "name":"德邦快运"},  ##
        {"code":"LB", "name":"龙邦快运"}, ##
      ],
