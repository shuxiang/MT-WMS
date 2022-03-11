# MT-WMS系统

MT-WMS 是开源的WMS(仓储管理系统)
遵循Apache License 2.0协议，前后端分离，可以支持多仓多货主，订单入库出库, 波次合并拣货出库.

系统可以当作WMS来使用, 管理货物; 也可以充当ERP来使用, 进行进销存管理. 电商用户可以自行开发对接奇门QIMEN, 京东JD等电商的接口, 接收平台订单. 也可以联系作者进行功能定制, 添加新的统计图表等. 添加BOM功能和相应的生产流程后, 亦可充当MES使用. 定制系统请联系(QQ 3527477665)

MT-WMS是已在多个大公司里使用的系统的简化版, 只开源了核心的仓库操作功能, 代码基本没有封装, 简单易懂易维护. MT-WMS支持PDA, Web, App. 目前只开源Web的前后端代码, 后续会开源PDA代码.


[MT-WMS前端项目地址(frontend code)](https://github.com/shuxiang/MT-WMS-Front)

[文档地址(documents)](https://www.m-front.cn/docs#/dash)

[线上测试帐户登录地址(test account)](https://wms.m-front.cn/auth/login)线上测试用户信息: 公司 test 用户名 test  密码 123456 

线上免费注册即可使用[免费注册地址(free registry)](https://wms.m-front.cn/auth/register)

## 开发运行/部署


### 环境初始化
```
pip3 install -r requirements.txt
```
修改 settings_local.py 的 SQLALCHEMY_DATABASE_URI 与 SQLALCHEMY_BINDS 的数据库连接地址

Flask版本为2.0.3, 前端版本 VUE 2.6.11 antd-design-vue 1.6.2


### 初始化数据(init data)
```
python manage.py db create_all
python manage.py init_data
flask run / python run.py
```

### supervisorctl监控进程
```
/usr/bin/supervisorctl -c /etc/supervisor.d/supervisord.ini
```

### 默认超级管理员登录 
公司 default
管理员 admin
密码 admin123456

### 升级数据库(migration)
```
flask db migrate
flask db upgrade
```

### 命令行重置管理员密码
```
flask shell
>>> u = db.M('User')
>>> u1 = u.query.get(2)
>>> u1.set_password('admin123456')
>>> db.session.commit()
```
