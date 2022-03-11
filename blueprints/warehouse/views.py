#coding=utf8
import traceback
from sqlalchemy import func, and_, or_
from pprint import pprint

from flask import Blueprint, g, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from extensions.database import db
from extensions.permissions import admin_perm, manager_perm, normal_perm

from models.warehouse import Warehouse, Workarea, Area, Location
from models.auth import Partner, Config
from models.inv import Category, Good, GoodMap

from utils.flask_tools import json_response
from utils.functions import gen_query, make_q, make_query, json2mdict, json2mdict_pop, clear_empty, ubarcode
from utils.base import Dict

from blueprints.inv.action import InvAction
import settings

bp_warehouse = Blueprint("warehouse", __name__)



# 获取库存列表
@bp_warehouse.route('/warehouse', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def warehouse_api():
    """
    查询库存列表
    get req:
    q={filters:[{}], order_by, single, limit, offset, group_by, without_batch}

    创建
    post req:
        {...}

    更新
    put req:
        {...}
    """
    try:
        if request.method == 'GET':
            # q = {filters:[{}], order_by, single, limit, offset, group_by}
            company_code = request.args.get('company_code', '')
            if company_code:
                query = Warehouse.query.filter_by(company_code=company_code)
            else:
                query = Warehouse.query.c_query
            res = gen_query(request.args.get('q', ''), query, Warehouse, db=db, per_page=settings.PER_PAGE)
            return json_response(res, indent=4)

        elif request.method == 'POST':
            if Warehouse.query.c_query.filter_by(code=request.json['code']).count() > 0:
                return json_response({'status': 'fail', 'msg': u'已经存在该编号, 请换一个编号'})
            obj = Warehouse(company_code=g.company_code, **clear_empty(request.json))
            if not obj.name:
                obj.name = obj.code
            db.session.add(obj)

            # if g.user.company.is_match_ow:
            #     if Partner.query.c_query.filter_by(code=obj.code).count() == 0:
            #         ow = Partner(company_code=g.company_code, code=obj.code, name=obj.name)
            #         db.session.add(ow)
            # 创建库区
            area = Area(code='default', name=u"默认库区")
            area.company_code = g.company_code
            area.warehouse_code = obj.code
            db.session.add(area)
            # 创建工作区
            wa = Workarea(code='default', name=u'默认工作区')
            wa.company_code = g.company_code
            wa.warehouse_code = obj.code
            db.session.add(wa)
            # 创建STAGE库位
            loc = Location(code='STAGE', remark=u"暂存库位")
            loc.company_code = g.company_code
            loc.warehouse_code = obj.code
            loc.area_code = area.code
            loc.workarea_code = wa.code
            db.session.add(loc)

            db.session.commit()

            return json_response({'status': 'success', 'msg': u'创建成功', 'data': obj.as_dict})

        elif request.method == 'PUT':
            _id = request.json.pop('id')
            Warehouse.query.c_query.filter_by(id=_id).update(json2mdict_pop(Warehouse, clear_empty(request.json)))
            db.session.commit()

            return json_response({'status': 'success', 'msg': u'创建成功'})

    except:
        err = traceback.format_exc()
        return json_response({'status': 'fail', 'msg': err})




# 获取工作区列表
@bp_warehouse.route('/workarea', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def workarea_api():
    """
    查询工作区列表
    get req:
    q={filters:[{}], order_by, single, limit, offset, group_by, without_batch}

    创建
    post req:
        {...}

    更新
    put req:
        {...}
    """
    try:
        if request.method == 'GET':
            # q = {filters:[{}], order_by, single, limit, offset, group_by}
            query = Workarea.query.w_query
            res = gen_query(request.args.get('q', ''), query, Workarea, db=db, per_page=settings.PER_PAGE)
            return json_response(res, indent=4)

        elif request.method == 'POST':
            if Workarea.query.w_query.filter_by(code=request.json['code']).count() > 0:
                return json_response({'status': 'fail', 'msg': u'已经存在该编号, 请换一个编号'})
            obj = Workarea(company_code=g.company_code, warehouse_code=g.warehouse_code, **clear_empty(request.json))
            if not obj.name:
                obj.name = obj.code
            db.session.add(obj)
            db.session.commit()

            return json_response({'status': 'success', 'msg': u'创建成功', 'data': obj.as_dict})

        elif request.method == 'PUT':
            _id = request.json.pop('id')
            Workarea.query.w_query.filter_by(id=_id).update(json2mdict_pop(Workarea, clear_empty(request.json)))
            db.session.commit()

            return json_response({'status': 'success', 'msg': u'创建成功'})

    except:
        err = traceback.format_exc()
        return json_response({'status': 'fail', 'msg': err})


# 获取库区列表
@bp_warehouse.route('/area', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def area_api():
    """
    查询库区列表
    get req:
    q={filters:[{}], order_by, single, limit, offset, group_by, without_batch}

    创建
    post req:
        {...}

    更新
    put req:
        {...}
    """
    try:
        if request.method == 'GET':
            # q = {filters:[{}], order_by, single, limit, offset, group_by}
            query = Area.query.w_query
            res = gen_query(request.args.get('q', ''), query, Area, db=db, per_page=settings.PER_PAGE)
            return json_response(res, indent=4)

        elif request.method == 'POST':
            if Area.query.w_query.filter_by(code=request.json['code']).count() > 0:
                return json_response({'status': 'fail', 'msg': u'已经存在该编号, 请换一个编号'})
            obj = Area(company_code=g.company_code, warehouse_code=g.warehouse_code, **clear_empty(request.json))
            if not obj.name:
                obj.name = obj.code
            db.session.add(obj)
            db.session.commit()

            return json_response({'status': 'success', 'msg': u'创建成功', 'data': obj.as_dict})

        elif request.method == 'PUT':
            _id = request.json.pop('id')
            Area.query.w_query.filter_by(id=_id).update(json2mdict_pop(Area, clear_empty(request.json)))
            db.session.commit()

            return json_response({'status': 'success', 'msg': u'创建成功'})

    except:
        err = traceback.format_exc()
        return json_response({'status': 'fail', 'msg': err})


# 获取库位列表
@bp_warehouse.route('/location', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def location_api():
    """
    查询库位列表
    get req:
    q={filters:[{}], order_by, single, limit, offset, group_by, without_batch}

    创建
    post req:
        {...}

    更新
    put req:
        {...}
    """
    try:
        if request.method == 'GET':
            # q = {filters:[{}], order_by, single, limit, offset, group_by}
            query = Location.query.w_query
            res = gen_query(request.args.get('q', ''), query, Location, db=db, per_page=settings.PER_PAGE)
            return json_response(res, indent=4)

        elif request.method == 'POST':
            if Location.query.w_query.filter_by(code=request.json['code']).count() > 0:
                return json_response({'status': 'fail', 'msg': u'已经存在该编号, 请换一个编号'})
            obj = Location(company_code=g.company_code, warehouse_code=g.warehouse_code, **clear_empty(request.json))
            if not obj.workarea_code:
                obj.workarea_code = 'default'
            if not obj.area_code:
                obj.area_code = 'default'
            db.session.add(obj)
            db.session.commit()

            return json_response({'status': 'success', 'msg': u'创建成功', 'data': obj.as_dict})

        elif request.method == 'PUT':
            _id = request.json.pop('id')
            Location.query.w_query.filter_by(id=_id).update(json2mdict_pop(Location, clear_empty(request.json)))
            db.session.commit()

            return json_response({'status': 'success', 'msg': u'创建成功'})

    except:
        err = traceback.format_exc()
        return json_response({'status': 'fail', 'msg': err})


# 获取合作伙伴列表
@bp_warehouse.route('/partner', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@bp_warehouse.route('/partner/owner', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def partner_api():
    """
    查询合作伙伴列表
    get req:
    q={filters:[{}], order_by, single, limit, offset, group_by, without_batch}

    创建
    post req:
        {...}

    更新
    put req:
        {...}
    """
    if request.method == 'GET':
        # q = {filters:[{}], order_by, single, limit, offset, group_by}
        qstr = request.args.get('q', '')
        sku = request.args.get('sku', '')
        val = request.args.get('val', '') # qstr name=


        company_code = request.args.get('company_code', '')
        if company_code:
            query = Partner.query.filter_by(company_code=company_code)
        else:
            query = Partner.query.c_query
        if 'owner' in request.path:
            query = query.filter_by(xtype='owner')
        res = gen_query(qstr, query, Partner, db=db, per_page=settings.PER_PAGE)

        return json_response(res, indent=4)

    elif request.method == 'POST':
        if Partner.query.c_query.filter_by(code=request.json['code']).count() > 0:
            return json_response({'status': 'fail', 'msg': u'已经存在该编号, 请换一个编号'})
        obj = Partner(company_code=g.company_code, **clear_empty(request.json))
        if not obj.name:
            obj.name = obj.code
        db.session.add(obj)
        db.session.commit()

        return json_response({'status': 'success', 'msg': u'创建成功', 'data': obj.as_dict})

    elif request.method == 'PUT':
        _id = request.json.pop('id')
        Partner.query.c_query.filter_by(id=_id).update(json2mdict_pop(Partner, clear_empty(request.json)))
        db.session.commit()

        return json_response({'status': 'success', 'msg': u'创建成功'})





# 获取货类列表
@bp_warehouse.route('/category', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def category_api():
    """
    查询货类列表
    get req:
    q={filters:[{}], order_by, single, limit, offset, group_by, without_batch}

    创建
    post req:
        {...}

    更新
    put req:
        {...}
    """
    try:
        if request.method == 'GET':
            # q = {filters:[{}], order_by, single, limit, offset, group_by}
            query = Category.query.o_query
            res = gen_query(request.args.get('q', ''), query, Category, db=db, per_page=settings.PER_PAGE)
            return json_response(res, indent=4)

        elif request.method == 'POST':
            if Category.query.o_query.filter_by(code=request.json['code']).count() > 0:
                return json_response({'status': 'fail', 'msg': u'已经存在该编号, 请换一个编号'})
            obj = Category(company_code=g.company_code, owner_code=g.owner_code, **clear_empty(request.json))
            if not obj.name:
                obj.name = obj.code
            db.session.add(obj)
            db.session.commit()

            return json_response({'status': 'success', 'msg': u'创建成功', 'data': obj.as_dict})

        elif request.method == 'PUT':
            _id = request.json.pop('id')
            Category.query.o_query.filter_by(id=_id).update(json2mdict_pop(Category, clear_empty(request.json)))
            db.session.commit()

            return json_response({'status': 'success', 'msg': u'创建成功'})

    except:
        err = traceback.format_exc()
        return json_response({'status': 'fail', 'msg': err})


# 获取货品列表
@bp_warehouse.route('/good', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def good_api():
    """
    查询货品列表
    get req:
    q={filters:[{}], order_by, single, limit, offset, group_by, without_batch}

    创建
    post req:
        {...}

    更新
    put req:
        {...}
    """
    # try:
    if request.method == 'GET':
        # q = {filters:[{}], order_by, single, limit, offset, group_by}
        per_page = settings.PER_PAGE
        if request.args.get('fetchall', None) == 'true':
            per_page = 1000
        query = Good.query.o_query
        pagin = gen_query(request.args.get('q', ''), query, Good, db=db, per_page=per_page, get_objects=True)

        # return json_response(res, indent=4)

        company_id = str(g.user.company.id)
        objects = []
        for item in pagin.items:
            o = item.as_dict
            o['barcode_url'] = item.get_barcode(company_id)
            o['qrcode_url'] = item.get_qrcode(company_id)
            objects.append(o)

        ret =  {
              "num_results": pagin.total,
              "total_pages": pagin.pages,
              "page": pagin.page,
              "per_page": pagin.per_page,
              "objects": objects
            }
        return json_response(ret, indent=4)

    elif request.method == 'POST':
        if Good.query.o_query.filter_by(code=request.json['code']).count() > 0:
            return json_response({'status': 'fail', 'msg': u'已经存在该编号, 请换一个编号'})
        images_list = request.json.pop('images_list', []) or []
        images = ",".join(images_list)

        ad_images_list = request.json.pop('ad_images_list', []) or []
        ad_images = ",".join(ad_images_list)

        obj = Good(company_code=g.company_code, owner_code=g.owner_code, **clear_empty(request.json))
        if obj.category_code:
            category = InvAction.create_category(obj.category_code)
        else:
            category = InvAction.default_category()
        obj.category_code = category.code

        obj.images = images
        obj.ad_images = ad_images
        if not obj.name:
            obj.name = obj.code
        else:
            obj.name_en = ubarcode(obj.name).replace(' ', '')
        if not obj.barcode:
            obj.barcode = obj.code
        if not obj.code:
            obj.code = obj.barcode
        db.session.add(obj)
        db.session.commit()

        print('add good code: %s ---------'%request.json['code'])

        return json_response({'status': 'success', 'msg': u'创建成功', 'data': obj.as_dict})

    elif request.method == 'PUT':
        _id = request.json.pop('id')
        remark = request.json.pop('remark')
        request.json.pop('images', '')
        request.json.pop('images_list', '')
        request.json.pop('ad_images', '')
        request.json.pop('ad_images_list', '')

        data = json2mdict_pop(Good, clear_empty(request.json))

        good = Good.query.o_query.filter_by(id=_id).first()
        good.update(data)
        good.name_en = ubarcode(good.name).replace(' ', '')
        good.remark = remark or good.remark

        if good.category_code:
            category = InvAction.create_category(good.category_code)
        else:
            category = InvAction.default_category()
        good.category_code = category.code

        if good.name != data['name']:
            gm = GoodMap.query.o_query.filter_by(code=good.code).update({'name': data['name']})
            Inv = db.M('Inv')
            Inv.query.t_query.filter_by(sku=good.code).update({'name':data['name']})

        db.session.commit()

        obj = Good.query.o_query.filter_by(id=_id).first()
        if obj.is_main:
            obj.has_subs = True
            db.session.commit()
        print('update good code: %s ---------'%request.json['code'])
        return json_response({'status': 'success', 'msg': u'创建成功'})

    # except:
    #     err = traceback.format_exc()
    #     return json_response({'status': 'fail', 'msg': err})


@bp_warehouse.route('/selection/<selection>', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def selection_api(selection):
    if request.method == 'POST':
        c = Config.query.t_query.filter_by(code='selection', subcode=selection).first()
        if c is None:
            c = Config(company_code=g.company_code, owner_code=g.owner_code, warehouse_code=g.warehouse_code, code='selection', subcode=selection, xtype='text')
            db.session.add(c)

        units = c.remark.split(',') if c and c.remark else []
        un = request.json.get('unit', '')
        if un:
            units.append(un)
        units = list(set(units))

        c.remark = ",".join(units)
        db.session.commit()

        return json_response({'status': 'success', 'msg': u'创建成功', 'units': units, 'data': units})

    if selection in ('qq_list', 'wx_list'):
        c = Config.query.filter(or_(Config.code=='selection', Config.code==selection)).filter_by(subcode=selection).first()
    else:
        c = Config.query.t_query.filter_by(code='selection', subcode=selection).first()

    units = []
    if c:
        units = c.remark.split(',') if c and c.remark else []

    if c is None:
        c = Config.query.c_query.filter_by(code=selection, subcode=selection).first()
        units = []
        if c:
            units = [i.strip() for i in c.str1.split(',')] if c and c.str1 else []

    if selection in ('qq_list', 'wx_list'):
        units = [i.strip() for i in c.str1.split(',')] if c and c.str1 else []
    
    return json_response({'status': 'success', 'units':units, 'data': units})

# 获取货品列表
@bp_warehouse.route('/goodmap', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@bp_warehouse.route('/goodmap/one', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@bp_warehouse.route('/goodmap/<mapid>', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def goodmap_api(mapid=None):
    """
    查询货品配料列表
    get req:
    q={filters:[{}], order_by, single, limit, offset, group_by, without_batch}

    创建
    post req:
        {...}

    更新
    put req:
        [{...}]
    """
    #try:
    if request.method == 'GET':
        # q = {filters:[{}], order_by, single, limit, offset, group_by}
        query = GoodMap.query.o_query
        q = make_q(request.args.get('q', ''))
        query = make_query(q, query, GoodMap, db, export=True)
        query = query.group_by(GoodMap.code)

        pagin = query.paginate(q.page or 1, per_page=(q.per_page or 20))
        objects = []
        for i in pagin.items:
            o = i.as_dict
            o['cost_price'] = i.good.cost_price if i.good else 0
            objects.append(o)
            lines = []

            query = db.session.query(GoodMap, Good).filter(GoodMap.code==i.code, GoodMap.owner_code==i.owner_code, GoodMap.company_code==i.company_code)
            gms = query.filter(Good.code==GoodMap.subcode, Good.company_code==GoodMap.company_code, Good.owner_code==GoodMap.owner_code).all()
            for j, sub_good in gms:
                jo = j.as_dict
                jo['cost_price'] = sub_good.cost_price if sub_good else 0
                lines.append(jo)
            # for j in i.map_goods:
            #     jo = j.as_dict
            #     jo['cost_price'] = j.sub_good.cost_price if j.sub_good else 0
            #     lines.append(jo)
            o['lines'] = lines
        ret =  {
          "num_results": pagin.total,
          "total_pages": pagin.pages,
          "page": pagin.page,
          "per_page": pagin.per_page,
          "objects": objects
        }

        return json_response(ret, indent=4)

    elif request.method == 'PUT' and 'one' in request.path:
        d = request.json
        main = Good.query.filter_by(code=d['code'], owner_code=g.owner_code, company_code=g.company_code).first()
        main.is_produce = True
        main.is_sync = '1'
        main.has_subs = True
        sub = Good.query.filter_by(code=d['subcode'], owner_code=g.owner_code, company_code=g.company_code).first()

        if main is not None and sub is not None:
            if d['qty'] and d['qty'] > 0:
                line = GoodMap.query.o_query.filter_by(code=d['code'], subcode=d['subcode']).first()
                # 更新数量
                if line:
                    line.qty = d['qty'] or line.qty
                # 添加新的关系
                else:
                    line = GoodMap(company_code=g.company_code, owner_code=g.owner_code, qty=d['qty'],
                        code=d['code'], name=main.name, barcode=main.barcode,
                        subcode=d['subcode'], subname=sub.name, subbarcode=sub.barcode)
                    db.session.add(line)
                db.session.flush()
                main.calc_main_cost_price()

                db.session.commit()

                # wrap return data
                lines = []
                line_data = line.as_dict
                line_data['cost_price'] = line.sub_good.cost_price or 0

                return json_response({'status': 'success', 'msg': u'更新成功', 'data': line_data, 'main_cost_price': main.cost_price})

        return json_response({'status': 'fail', 'msg': u'找不到货品'})


    elif request.method == 'PUT':
        main = None
        cost_price = 0
        for d in request.json:
            if not main:
                main = Good.query.filter_by(code=d['code'], owner_code=g.owner_code, company_code=g.company_code).first()
                main.is_produce = True
                main.is_sync = '1'
                main.has_subs = True
            sub = Good.query.filter_by(code=d['subcode'], owner_code=g.owner_code, company_code=g.company_code).first()

            if main is not None and sub is not None:
                if d['qty'] and d['qty'] > 0:
                    line = GoodMap.query.o_query.filter_by(code=d['code'], subcode=d['subcode']).first()
                    # 更新数量
                    if line:
                        line.qty = d['qty'] or line.qty
                    # 添加新的关系
                    else:
                        db.session.add(GoodMap(company_code=g.company_code, owner_code=g.owner_code, qty=d['qty'],
                            code=d['code'], name=main.name, barcode=main.barcode,
                            subcode=d['subcode'], subname=sub.name, subbarcode=sub.barcode))

                    cost_price += float(sub.cost_price or sub.price)*int(d['qty'])

        main.cost_price = cost_price
        db.session.commit()

        return json_response({'status': 'success', 'msg': u'更新成功'})

    elif request.method == 'POST':
        cost_price_dict = {}
        main_list = []
        for d in request.json:
            main = Good.query.filter_by(code=d['code'], owner_code=g.owner_code, company_code=g.company_code).first()
            sub = Good.query.filter_by(code=d['subcode'], owner_code=g.owner_code, company_code=g.company_code).first()

            if main.code not in cost_price_dict:
                cost_price_dict[main.code] = 0
            main_list.append(main)

            if main is not None and sub is not None:
                main.is_produce = True
                main.is_sync = '1'
                main.has_subs = True
                # 添加新的关系
                if d['qty'] and d['qty'] > 0:
                    db.session.add(GoodMap(company_code=g.company_code, owner_code=g.owner_code, qty=d['qty'],
                        code=d['code'], name=main.name, barcode=main.barcode,
                        subcode=d['subcode'], subname=sub.name, subbarcode=sub.barcode))

                    if main.code not in cost_price_dict:
                        cost_price_dict[main.code] = 0
                    main_list.append(main)
                    cost_price_dict[main.code] += float(sub.cost_price or sub.price)*int(d['qty'])

        for main in main_list:
            main.cost_price = cost_price_dict.get(main.sku, main.price)

        db.session.commit()

        return json_response({'status': 'success', 'msg': u'添加成功'})

    elif request.method == 'DELETE':
        gm = GoodMap.query.o_query.filter_by(id=mapid).first()
        main_cost_price = 0
        if gm:
            db.session.delete(gm)
            good = gm.good
            db.session.flush()
            good.calc_main_cost_price()
            main_cost_price = good.cost_price

            # 删光了, 非主件
            if GoodMap.query.filter(GoodMap.code==good.code, GoodMap.owner_code==good.owner_code, GoodMap.company_code==good.company_code).count() == 0:
                good.has_subs = False

        db.session.commit()
        return json_response({'status': 'success', 'msg': u'删除成功', 'main_cost_price': main_cost_price})

    # except:
    #     err = traceback.format_exc()
    #     return json_response({'status': 'fail', 'msg': err})

























