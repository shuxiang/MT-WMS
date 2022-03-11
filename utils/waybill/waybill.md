## 电子面单 - 快递鸟

0. 对方开通kdniao, 完成企业认证与充值

1. 配置 
    owner.express_on = 'on'
    owner.express_type = 'kdniao'

2. 配置 owner 电子面单平台相关参数
    express = 快递公司代码
    express_month_code = 月结账户
    express_bid = kdniao商务id
    express_appkey = 
    express_secret = 
    express_passwd = kdniao月结密码

3. 配置 owner 收货信息与发货信息
    sender_name    = db.Column(db.String(50), server_default='')
    sender_tel     = db.Column(db.String(50), server_default='')
    sender_province = db.Column(db.String(250), server_default='')
    sender_city     = db.Column(db.String(250), server_default='')
    sender_area     = db.Column(db.String(250), server_default='')
    sender_town     = db.Column(db.String(250), server_default='')
    sender_address = db.Column(db.String(250), server_default='')

    receiver_name    = db.Column(db.String(50), server_default='')
    receiver_tel     = db.Column(db.String(50), server_default='')
    receiver_province = db.Column(db.String(250), server_default='')
    receiver_city     = db.Column(db.String(250), server_default='')
    receiver_area     = db.Column(db.String(250), server_default='')
    receiver_town     = db.Column(db.String(250), server_default='')
    receiver_address = db.Column(db.String(250), server_default='')

