#coding=utf8

import json
from flask import g, session
from hashlib import sha256
from sqlalchemy import or_, and_, func

from extensions.database import db
from extensions.permissions import ROLES_PERM, VROLES

from models.auth import User, Partner, Config, Big, Company
from models.inv import Category, Good
from models.warehouse import Warehouse, Area, Workarea, Location

from utils.flask_tools import json_response
from utils.functions import gen_query, clear_empty, json2mdict, json2mdict_pop
import settings

class AuthAction(object):

    def __init__(self, user=None):
        self.user = user

    @staticmethod
    def encrypt_password(password):
        return sha256((password+'+SomeSaltToFoodIsDelicious!').encode()).hexdigest()
    
    @staticmethod
    def auth_user(user, password, company=None, xtype=None):
        hashpass = AuthAction.encrypt_password(password)
        # subq = User.query.filter_by(code=user, password=hashpass, state='on')
        subq = User.query.filter(or_(User.code==user, User.tel==user)).filter_by(password=hashpass, state='on')
        if not company and xtype=='client':
            subq = subq.filter_by(xtype=xtype)
        user = subq.order_by(User.id.asc()).first()
        # 客户用户不用验证公司
        if user and not user.is_client and company:
            comp = Company.query.filter(or_(Company.code==company, Company.name==company, Company.tel==company)).first()
            if comp is None:
                print ('comp is none')
                return None
            company_code = comp.code
            subq = subq.filter_by(company_code=company_code)
        elif user and not user.is_client and not company:
            if xtype=='ams':
                return user
            print ('comp code is none')
            return None
        user = subq.order_by(User.id.asc()).first()
        if user is not None and user.is_employee:
            print ('is_employee')
            return None
        return user

    @staticmethod
    def set_openresty_cookie(user, resp):
        if user.company.host:
            resp.set_cookie('oip', user.company.host)

    @staticmethod
    def create_company(**kw):
        if Company.query.filter(Company.code==kw.get('code', '')).count():
            return None
        tel = kw.get('tel', '')
        if tel and len(tel) >= 11:
            if Company.query.filter(Company.tel==tel).count():
                return None
        comp = Company(**json2mdict_pop(Company, clear_empty(kw)))
        db.session.add(comp)
        comp.agent = g.user.code
        db.session.flush()
        return comp

    @staticmethod
    def create_user(is_boss=False, **kw):
        roles = kw.pop('roles', None)
        vroles = kw.pop('vroles', None)
        is_employee = kw.get('is_employee', False)
        # print(kw)
        company_code = kw.pop('company_code', None) or g.company_code

        if User.query.filter_by(code=kw.get('code', ''), company_code=company_code).filter(User.state!='delete').count():
            user = User.query.filter_by(code=kw.get('code', ''), company_code=company_code).filter(User.state!='delete').first()
            if is_boss:
                user.set_perm('manager')
                user.set_vrole(list(VROLES.get('boss')))
                return True, user
            return False, u'已经存在该用户, 请换一个用户码'

        comp = Company.query.filter_by(code=company_code).first()
        num_users = User.query.filter(User.company_code==company_code, ~User.roles.like('%%employee%%'), User.state!='delete', 
            or_(User.xtype=='user', User.xtype=='client')).count()
        if int(comp.max_users) > 0 and num_users >= (int(comp.max_users)+1) and not g.user.is_admin and not is_employee:
            return False, u'超过用户数量限定了, 请联系服务商'

        user = User(company_code=company_code, **json2mdict_pop(User, clear_empty(kw)))
        user.password = AuthAction.encrypt_password(user.password)
        if roles == 'manager':
            user.set_perm('manager')
            if is_boss:
                user.set_vrole(list(VROLES.get('boss')))
            elif vroles:
                user.set_vrole(vroles.split(','))
            else:
                user.set_vrole(list(VROLES.get('manager')))
        elif kw.get('is_employee', False):
            user.set_perm('employee')
            if vroles:
                user.set_vrole(vroles.split(','))
        else:
            user.set_perm('normal')
            if vroles:
                user.set_vrole(vroles.split(','))

        db.session.add(user)
        return True, user

    @staticmethod
    def init_company(comp):
        if comp.is_init:
            return False
        print('first init company===>', comp.code)
        # 创建默认货主
        owner = Partner(code='default', name=u"默认货主", company_code=comp.code, tel=comp.tel)
        db.session.add(owner)

        # 创建默认货类
        cate = Category(code='default', name=u'默认货类', company_code=comp.code, owner_code=owner.code)
        db.session.add(cate)


        # 增加监控员
        user = User(code='monitor', password=AuthAction.encrypt_password('monitor@mf9527'), name=u"监控员")
        user.company_code = comp.code
        user.set_perm('manager')
        user.set_vrole(list(VROLES.get('boss')))
        user.xtype = 'monitor'
        db.session.add(user)

        # 普通默认仓库
        ware = Warehouse(code='default', name=u'默认仓库', tel=comp.tel)
        ware.company_code = comp.code
        db.session.add(ware)

        # 普通默认库区
        area = Area(code='default', name=u'默认库区')
        area.company_code = comp.code
        area.warehouse_code = ware.code
        db.session.add(area)

        # 创建收货作业区，创建临时收货库位
        wa2 = Workarea(code='default', name=u'默认工作区', is_inner=True)
        wa2.company_code = comp.code
        wa2.warehouse_code = ware.code
        db.session.add(wa2)

        # 创建拣货作业区，创建拣货库位
        wa3 = Workarea(code='OUT', name=u'出库工作区', is_inner=True)
        wa3.company_code = comp.code
        wa3.warehouse_code = ware.code
        db.session.add(wa3)

        wa4 = Workarea(code='RECV', name=u'收货工作区', is_inner=True)
        wa4.company_code = comp.code
        wa4.warehouse_code = ware.code
        db.session.add(wa4)

        wa5 = Workarea(code='QC', name=u'质检工作区', is_inner=True)
        wa5.company_code = comp.code
        wa5.warehouse_code = ware.code
        db.session.add(wa5)

        wa6 = Workarea(code='SEND', name=u'拆零发货工作区', is_inner=True)
        wa6.company_code = comp.code
        wa6.warehouse_code = ware.code
        db.session.add(wa6)

        loc2 = Location(code='STAGE', is_inner=True)
        loc2.company_code = comp.code
        loc2.warehouse_code = ware.code
        loc2.area_code = area.code
        loc2.workarea_code = wa4.code
        db.session.add(loc2)

        loc5 = Location(code='ZERO', is_inner=True)
        loc5.company_code = comp.code
        loc5.warehouse_code = ware.code
        loc5.area_code = area.code
        loc5.workarea_code = wa6.code
        db.session.add(loc5)

        loc3 = Location(code='PICK', is_inner=True)
        loc3.company_code = comp.code
        loc3.warehouse_code = ware.code
        loc3.area_code = area.code
        loc3.workarea_code = wa3.code
        db.session.add(loc3)

        loc4 = Location(code='QC', is_inner=True)
        loc4.company_code = comp.code
        loc4.warehouse_code = ware.code
        loc4.area_code = area.code
        loc4.workarea_code = wa5.code
        db.session.add(loc4)

        # 创建默认配置
        c1 = Config(code='overcharge', subcode='overcharge', owner_code=owner.code, company_code=comp.code,
            bool1=True, remark=u'设置·bool1·为该货主是否允许超收'
            )
        c2 = Config(code='partalloc', subcode='partalloc', owner_code=owner.code, company_code=comp.code,
            bool1=True, remark=u'设置·bool1·为该货主是否允许部分分配'
            )
        c21 = Config(code='close_when_pick', subcode='close_when_pick', owner_code=owner.code, company_code=comp.code,
            bool1=True, remark=u'设置·bool1·为该货主是否拣货后直接关闭订单无发运流程配置'
            )
        c3 = Config(code='translation', subcode='stockout_order_type', owner_code=owner.code, company_code=comp.code,
            remark=u'设置·str1,str2·为翻译对应的key-value值，需选择仓库与货主',
            str1='purchase', str2=u'采购单'
            )
        c4 = Config(code='translation', subcode='stockin_order_type', owner_code=owner.code, company_code=comp.code,
            remark=u'设置·str1,str2·为翻译对应的key-value值，需选择仓库与货主',
            str1='sale', str2=u'销售出库'
            )
        c5 = Config(code='alloc_rule', subcode='alloc_rule', owner_code=owner.code, company_code=comp.code,
            remark=u'''设置·str1·为出库单分配的优先规则，需选择仓库与货主; 
                ## 先进先出 入库时间(stockin_date) 'FIFO'
                ## 后进先出 入库时间(stockin_date) 'FILO' 
                ## 生产时间(product_date)
                ## 'FPFO': 先生产的后出
                ## 'FPLO': # 先生产的后出
                ## 过期时间(expire_date) 'FEFO': # 快过期的先出
                ## 'FELO': # 快过期的后出
                ## 清库位库存优先 ，库位库存少的先出 'clear_location'
                ## 保质期与过期时间, (Inv.expire_date - Inv.product_date).asc 
                ## 'FBFO': # 保质期短的先出; 'FBLO': # 保质期长的先出
                ## 库位优先级高先出 'priority_location' L5 > L1
                ## 库位完整远近优先 'index_location_asc': # 库位近的优先, 库位序小的先出 
                ## 'index_location_desc': # 库位远的优先，库位序大的先出;
                --- 设置·str1·为前后规则，小的规则先使用 ''',
            str1='FIFO', multi=True, xtype='select',
            )
        c6 = Config(code='print_rule', subcode='print_rule', owner_code=owner.code, company_code=comp.code,
            remark=u'设置·str1·为拣货单打印的规则，按库位序大小排序，需选择仓库与货主; asc 为小到大， desc 为大到小',
            str1='index_desc',
            )
        c7 = Config(code='selection', subcode='units', owner_code=owner.code, company_code=comp.code,
            remark=u'个,件,只,台,箱,盒,支,瓶,克,千克,市斤,米,厘米',
            str1='desc', xtype='text',
            )
        c8 = Config(code='selection', subcode='qq_list', owner_code=owner.code, company_code=comp.code,
            remark=u'3527477665',
            str1='desc', xtype='text',
            )
        db.session.add(c1)
        db.session.add(c2)
        db.session.add(c21)
        db.session.add(c3)
        db.session.add(c4)
        db.session.add(c5)
        db.session.add(c6)
        db.session.add(c7)
        db.session.add(c8)

        return True

    @staticmethod
    def register(data):
        user_json = data.pop('user')
        comp = AuthAction.create_company(**json2mdict(Company, data))
        if comp:
            # 创建管理员
            user_json['company_code'] = comp.code
            user_json['roles'] = 'manager'
            ok, manager = AuthAction.create_user(is_boss=True, **json2mdict(User, user_json))
            # 不填手机号时, 用管理员的手机号
            if not comp.tel and ok:
                comp.tel = manager.tel or manager.code
            if ok:
                # AuthAction.init_company()
                return True, comp, manager, ''
                
            return False, None, None, u'创建管理员失败, 用戶已經存在, 请换一个号码'
        else:
            return False, None, None, u'该公司已经注册过, 请换一个'


    @staticmethod
    def logoff(company_code):
        from models.finance import __all__
        for t in __all__:
            db.M(t).query.filter_by(company_code=company_code).delete()

        from models.asyncmodel import __all__
        for t in __all__:
            db.M(t).query.filter_by(company_code=company_code).delete()

        from models.inv import __all__
        for t in __all__:
            db.M(t).query.filter_by(company_code=company_code).delete()

        from models.warehouse import __all__
        for t in __all__:
            db.M(t).query.filter_by(company_code=company_code).delete()

        from models.stockin import __all__
        for t in __all__:
            db.M(t).query.filter_by(company_code=company_code).delete()

        from models.stockout import __all__
        for t in __all__:
            db.M(t).query.filter_by(company_code=company_code).delete()

        from models.auth import __all__
        for t in __all__:
            if t == 'Company':
                db.M(t).query.filter_by(code=company_code).delete()
            else:# delete Big too
                db.M(t).query.filter_by(company_code=company_code).delete()