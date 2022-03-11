#coding=utf8

import traceback

from extensions.database import db
from extensions.hueyext import hueyapp
from extensions.celeryext import celeryapp
from models.asyncmodel import Async
from models.warehouse import Warehouse, Area, Workarea, Location
from models.inv import Good, Category, Inv, GoodMap
from models.auth import Partner, Seq, User, Company

from utils.upload import get_file_content, save_image
from utils.functions import clear_empty
from utils.upload import get_oss_image
from utils.functions import clear_empty, ubarcode
from utils.base import DictNone
from utils.functions import gen_query, clear_empty, json2mdict, json2mdict_pop, DictNone, common_poplist3

import settings

# 仓库信息导入
#@hueyapp.task()
@celeryapp.task
def import_location(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    ret = import_location_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=user_code, user_name=user_name)
    db.session.close()
    return ret

def import_location_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    task = Async.query.get(task_id)
    print('handle async task_id ==> ', task_id, task.async_id)

    task.get_file()
    content = get_file_content(task.link)

    success = True
    exc_info = ''

    try:
        task.code = 'location'
        for row in content:
            d = DictNone(clear_empty(row))
            if not d.code:
                continue
            if Location.query.filter_by(company_code=company_code, warehouse_code=warehouse_code, code=d['code']).count() == 0:
                obj = Location(company_code=company_code, warehouse_code=warehouse_code, **d)
                db.session.add(obj)
                obj.workarea_code = d.workarea_code if d.workarea_code else 'default'
                obj.area_code = d.area_code if d.area_code else 'default'
                obj.index = int(d.index or 0)

        db.session.flush()
        exc_info = 'save location: %s'%len(content)
    except:
        exc_info = traceback.format_exc()
        success = False

    if success:
        db.session.commit()
        task.state = 'done'
        task.exc_info = 'SUCCESS'
    else:
        db.session.rollback()
        task.state = 'fail'
        task.exc_info = exc_info[-1500:]
        print(exc_info)

    db.session.commit()
    

#@hueyapp.task()
@celeryapp.task
def import_workarea(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    ret = import_workarea_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=user_code, user_name=user_name)
    db.session.close()
    return ret

def import_workarea_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    task = Async.query.get(task_id)
    print('handle async task_id ==> ', task_id, task.async_id)

    task.get_file()
    content = get_file_content(task.link)

    success = True
    exc_info = ''

    try:
        task.code = 'workarea'
        for row in content:
            d = DictNone(clear_empty(row))
            if not d.code:
                continue
            if Workarea.query.filter_by(company_code=company_code, warehouse_code=warehouse_code, code=d['code']).count() == 0:
                db.session.add(Workarea(company_code=company_code, warehouse_code=warehouse_code, **d))
        db.session.flush()
        exc_info = 'save workarea: %s'%len(content)
    except:
        exc_info = traceback.format_exc()
        success = False

    if success:
        db.session.commit()
        task.state = 'done'
        task.exc_info = 'SUCCESS'
    else:
        db.session.rollback()
        task.state = 'fail'
        task.exc_info = exc_info[-1500:]
        print(exc_info)

    db.session.commit()
    

#@hueyapp.task()
@celeryapp.task
def import_area(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    ret = import_area_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=user_code, user_name=user_name)
    db.session.close()
    return ret

def import_area_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    task = Async.query.get(task_id)
    print('handle async task_id ==> ', task_id, task.async_id)

    task.get_file()
    content = get_file_content(task.link)

    success = True
    exc_info = ''

    try:
        task.code = 'area'
        for row in content:
            d = DictNone(clear_empty(row))
            if not d.code:
                continue
            if Area.query.filter_by(company_code=company_code, warehouse_code=warehouse_code, code=d['code']).count() == 0:
                db.session.add(Area(company_code=company_code, warehouse_code=warehouse_code, **d))
        db.session.flush()
        exc_info = 'save area: %s'%len(content)
    except:
        exc_info = traceback.format_exc()
        success = False

    if success:
        db.session.commit()
        task.state = 'done'
        task.exc_info = 'SUCCESS'
    else:
        db.session.rollback()
        task.state = 'fail'
        task.exc_info = exc_info[-1500:]
        print(exc_info)

    db.session.commit()
    

#@hueyapp.task()
@celeryapp.task
def import_warehouse(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    ret = import_warehouse_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=user_code, user_name=user_name)
    db.session.close()
    return ret

def import_warehouse_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    task = Async.query.get(task_id)
    print('handle async task_id ==> ', task_id, task.async_id)

    task.get_file()
    content = get_file_content(task.link)

    success = True
    exc_info = ''

    try:
        task.code = 'warehouse'
        for row in content:
            d = DictNone(clear_empty(row))
            if not d.code:
                continue
            if Warehouse.query.filter_by(company_code=company_code, code=d['code']).count() == 0:
                db.session.add(Warehouse(company_code=company_code, **d))
        db.session.flush()
        exc_info = 'save warehouse: %s'%len(content)
    except:
        exc_info = traceback.format_exc()
        success = False

    if success:
        db.session.commit()
        task.state = 'done'
        task.exc_info = 'SUCCESS'
    else:
        db.session.rollback()
        task.state = 'fail'
        task.exc_info = exc_info[-1500:]
        print(exc_info)

    db.session.commit()
    


#@hueyapp.task()
@celeryapp.task
def import_good(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    ret = import_good_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=user_code, user_name=user_name)
    db.session.close()
    return ret

def import_good_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    task = Async.query.get(task_id)
    print('handle async task_id ==> ', task_id, task.async_id)

    task.get_file()
    content = get_file_content(task.link, True, im_keys=['image', 'image1', 'image2', 'image3', 'image4', 'image5', 'image6'])

    success = True
    exc_info = ''

    #from blueprints.openapi.action import LaoaAction
    #action = LaoaAction(settings.LAOA_HBB_URL, settings.LAOA_HBB_APPKEY, settings.LAOA_HBB_APPSECRET)

    try:
        company_id = Company.query.filter_by(code=company_code).first().id

        task.code = 'good'
        for row in content:
            d = DictNone(clear_empty(row))
            if not d.code:
                # 自动生成barcode?
                d.code = Seq.make_order_code('BAR', company_code, warehouse_code, owner_code)
                #continue
            if type(d.code) is float:
                d.code = str(int(d.code))
            # d.code = ubarcode(d.code).replace(' ', '') # 不转换英文
            d.name_en = ubarcode(d.name).replace(' ', '')
            d.is_produce = (d.is_produce==1 or d.is_produce == 'Y' or d.is_produce == u'是' or d.is_produce == '1')
            # 以后做覆盖, 不要覆盖价格
            if Good.query.filter_by(code=d['code'], owner_code=owner_code, company_code=company_code).count() == 0:
                cc, cn = d.get('category_code'), d.pop('category_name', '')
                if cc and Category.query.filter_by(code=cc, owner_code=owner_code, company_code=company_code).count() == 0:
                    c = Category(
                        code=cc, 
                        name=(cn or cc), 
                        owner_code=owner_code, 
                        company_code=company_code)
                    db.session.add(c)

                im = d.pop('image', None)
                good = Good(company_code=company_code, owner_code=owner_code, **d)
                db.session.add(good)
                if not good.barcode:
                    good.barcode = good.code
                if good.price and not good.last_in_price:
                    good.last_in_price = (good.cost_price or good.price)
                if not good.category_code:
                    good.category_code = 'default'

                # 保存图片
                if im is not None:
                    path, osslink = save_image(settings.UPLOAD_DIR, im._data(), im.format, settings.UPLOAD_IMG_TO_OSS, company_id=company_id)
                    if settings.UPLOAD_IMG_TO_OSS:
                        iurl = settings.OSS_URL_PREFIX + osslink
                    else:
                        #iurl = '/static/upload/images/'+osslink
                        iurl = '/static/upload/images/%s/%s'%(company_id, osslink)
                    good.image_url = iurl
                # 商品图片
                imgs = [d.pop('image1', None), d.pop('image2', None), d.pop('image3', None), d.pop('image4', None), d.pop('image5', None), d.pop('image6', None)]
                imgs_url = []
                for im in imgs:
                    if im is not None:
                        path, osslink = save_image(settings.UPLOAD_DIR, im._data(), im.format, settings.UPLOAD_IMG_TO_OSS, company_id=company_id)
                        if settings.UPLOAD_IMG_TO_OSS:
                            iurl = settings.OSS_URL_PREFIX + osslink
                        else:
                            #iurl = '/static/upload/images/'+osslink
                            iurl = '/static/upload/images/%s/%s'%(company_id, osslink)
                        imgs_url.append(iurl)
                good.images = ",".join(imgs_url)
                # 广告图片
                ad_imgs = [d.pop('ad_image1', None), d.pop('ad_image2', None), d.pop('ad_image3', None), d.pop('ad_image4', None), d.pop('ad_mage5', None), d.pop('ad_image6', None)]
                ad_imgs_url = []
                for im in ad_imgs:
                    if im is not None:
                        path, osslink = save_image(settings.UPLOAD_DIR, im._data(), im.format, settings.UPLOAD_IMG_TO_OSS, company_id=company_id)
                        if settings.UPLOAD_IMG_TO_OSS:
                            iurl = settings.OSS_URL_PREFIX + osslink
                        else:
                            #iurl = '/static/upload/images/'+osslink
                            iurl = '/static/upload/images/%s/%s'%(company_id, osslink)
                        ad_imgs_url.append(iurl)
                good.ad_images = ",".join(ad_imgs_url)
                # good.is_sync = '1'
            else:
                good = Good.query.filter_by(code=d['code'], owner_code=owner_code, company_code=company_code).first()
                # good.is_sync = '1'

            if good.is_main or good.is_sync=='1':
                # action.remote_add_good(good)
                pass
            if good.is_main:
                good.has_subs = True

        db.session.flush()
        exc_info = 'save good: %s'%len(content)
    except:
        exc_info = traceback.format_exc()
        success = False

    if success:
        db.session.commit()
        task.state = 'done'
        task.exc_info = 'SUCCESS'
    else:
        db.session.rollback()
        task.state = 'fail'
        task.exc_info = exc_info[-1500:]
        print(exc_info)

    db.session.commit()
    


#@hueyapp.task()
@celeryapp.task
def import_goodmap(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    ret = import_goodmap_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=user_code, user_name=user_name)
    db.session.close()
    return ret

def import_goodmap_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    task = Async.query.get(task_id)
    print('handle async task_id ==> ', task_id, task.async_id)

    task.get_file()
    content = get_file_content(task.link)

    success = True
    exc_info = ''

    try:
        task.code = 'goodmap'
        cost_dict = {}
        for row in content:
            d = DictNone(clear_empty(row))
            if not d.code or not d.subcode:
                continue
            main = Good.query.filter_by(code=d['code'], owner_code=owner_code, company_code=company_code).first()
            sub = Good.query.filter_by(code=d['subcode'], owner_code=owner_code, company_code=company_code).first()
            if main is not None and sub is not None:
                main.is_produce = True
                main.is_sync = '1'
                main.has_subs = True
                line = GoodMap.query.filter_by(company_code=company_code, owner_code=owner_code, code=d['code'], subcode=d['subcode']).first()
                # 更新数量
                if line:
                    line.qty = d['qty'] or line.qty
                # 添加新的关系
                else:
                    db.session.add(GoodMap(company_code=company_code, owner_code=owner_code, qty=d['qty'] or 1,
                        code=d['code'], name=main.name, barcode=main.barcode,
                        subcode=d['subcode'], subname=sub.name, subbarcode=sub.barcode))
                if main.code not in cost_dict:
                    cost_dict[main.code] = 0
                cost_dict[main.code] += float(sub.cost_price or sub.price)*int(d['qty'])
            elif main is None:
                raise Exception(u'找不到主件 %s, 请先添加主件的货品信息'%d['code'])
            elif sub is None:
                raise Exception(u'找不到配件 %s, 请先添加配件的货品信息'%d['subcode'])

        for k, v in cost_dict.items():
            m = Good.query.filter_by(code=k, owner_code=owner_code, company_code=company_code).first()
            if m:
                m.cost_price = v if v else m.cost_price

        db.session.flush()
        exc_info = 'save goodmap: %s'%len(content)
    except:
        exc_info = traceback.format_exc()
        success = False

    if success:
        db.session.commit()
        task.state = 'done'
        task.exc_info = 'SUCCESS'
    else:
        db.session.rollback()
        task.state = 'fail'
        task.exc_info = exc_info[-1500:]
        print(exc_info)

    db.session.commit()
    

#@hueyapp.task()
@celeryapp.task
def import_category(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    ret = import_category_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=user_code, user_name=user_name)
    db.session.close()
    return ret

def import_category_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    task = Async.query.get(task_id)
    print('handle async task_id ==> ', task_id, task.async_id)

    task.get_file()
    content = get_file_content(task.link)

    success = True
    exc_info = ''

    try:
        task.code = 'category'
        for row in content:
            d = DictNone(clear_empty(row))
            if not d.code:
                continue
            if Category.query.filter_by(company_code=company_code, owner_code=owner_code, code=d['code']).count() == 0:
                db.session.add(Category(company_code=company_code, owner_code=owner_code, **d))
        db.session.flush()
        exc_info = 'save category: %s'%len(content)
    except:
        exc_info = traceback.format_exc()
        success = False

    if success:
        db.session.commit()
        task.state = 'done'
        task.exc_info = 'SUCCESS'
    else:
        db.session.rollback()
        task.state = 'fail'
        task.exc_info = exc_info[-1500:]
        print(exc_info)

    db.session.commit()
    

#@hueyapp.task()
@celeryapp.task
def import_inv(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    ret = import_inv_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=user_code, user_name=user_name)
    db.session.close()
    return ret

def import_inv_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    task = Async.query.get(task_id)
    print('handle async task_id ==> ', task_id, task.async_id)

    task.get_file()
    content = get_file_content(task.link, True, im_keys=['image', 
        'image1', 'image2', 'image3', 'image4', 'image5', 'image6', 
        'ad_image1', 'ad_image2', 'ad_image3', 'ad_image4', 'ad_image5', 'ad_image6'])

    success = True
    exc_info = ''

    try:
        company_id = Company.query.filter_by(code=company_code).first().id

        task.code = 'inv'
        for row in content:
            d = DictNone(clear_empty(row))
            if not d.location_code or not d.sku:
                d.sku = Seq.make_order_code('BAR', company_code, warehouse_code, owner_code)
                #continue
            if type(d.sku) is float:
                d.sku = str(int(d.sku))
            location = Location.query.filter_by(company_code=company_code, warehouse_code=warehouse_code, code=d.location_code).first()
            d.area_code = location.area_code
            d.workarea_code = location.workarea_code
            d.qty_able = d.qty or 0
            if not d.category_code:
                d.category_code = 'default'
            count = Inv.query.filter_by(company_code=company_code, warehouse_code=warehouse_code, owner_code=owner_code) \
                .filter_by(sku=d.sku, location_code=d.location_code, lpn=d.lpn or '', 
                    stockin_date=d.stockin_date or None, 
                    supplier_code=d.supplier_code or '',
                    quality_type=d.quality_type or 'ZP', batch_code=d.batch_code or '', virtual_warehouse=d.virtual_warehouse or '',
                    spec=d.spec or '', unit=d.unit or '',
                    product_date=d.product_date or None, expire_date=d.expire_date or None).count()
            if count == 0:
                _d = json2mdict_pop(Inv, clear_empty(d), common_poplist3)
                db.session.add(Inv(company_code=company_code, warehouse_code=warehouse_code, owner_code=owner_code, **_d))
            if d.sku:
                good = Good.query.filter_by(company_code=company_code, owner_code=owner_code, code=d.sku).first()
                if not good:
                    good = Good(company_code=company_code, owner_code=owner_code, code=d.sku, barcode=d.barcode, name=d.name, 
                        category_code=d.category_code, spec=d.spec or '', unit=d.unit, brand=d.brand or '', price=d.price or 0, args=d.args or '',
                        weight=d.weight or 0, style=d.style or '', color=d.color or '', size=d.size or '', 
                        max_qty=d.max_qty or 0, min_qty=d.min_qty or 0, quality_month=d.quality_month or 0, 
                        )
                    db.session.add(good)
                    good.name_en = ubarcode(good.name)

                    # 商品图片
                    imgs = [d.pop('image1', None), d.pop('image2', None), d.pop('image3', None), d.pop('image4', None), d.pop('image5', None), d.pop('image6', None)]
                    imgs_url = []
                    for im in imgs:
                        if im is not None:
                            path, osslink = save_image(settings.UPLOAD_DIR, im._data(), im.format, settings.UPLOAD_IMG_TO_OSS, company_id=company_id)
                            if settings.UPLOAD_IMG_TO_OSS:
                                iurl = settings.OSS_URL_PREFIX + osslink
                            else:
                                #iurl = '/static/upload/images/'+osslink
                                iurl = '/static/upload/images/%s/%s'%(company_id, osslink)
                            imgs_url.append(iurl)
                    good.images = ",".join(imgs_url)
                    # 广告图片
                    ad_imgs = [d.pop('ad_image1', None), d.pop('ad_image2', None), d.pop('ad_image3', None), d.pop('ad_image4', None), d.pop('ad_mage5', None), d.pop('ad_image6', None)]
                    ad_imgs_url = []
                    for im in ad_imgs:
                        if im is not None:
                            path, osslink = save_image(settings.UPLOAD_DIR, im._data(), im.format, settings.UPLOAD_IMG_TO_OSS, company_id=company_id)
                            if settings.UPLOAD_IMG_TO_OSS:
                                iurl = settings.OSS_URL_PREFIX + osslink
                            else:
                                #iurl = '/static/upload/images/'+osslink
                                iurl = '/static/upload/images/%s/%s'%(company_id, osslink)
                            ad_imgs_url.append(iurl)
                    good.ad_images = ",".join(ad_imgs_url)

            if d.category_code:
                cate = Category.query.filter_by(company_code=company_code, owner_code=owner_code, code=d.category_code).first()
                if not cate:
                    cate = Category(company_code=company_code, owner_code=owner_code, 
                        code=d.category_code, name=d.category_name or d.category_code)
                    db.session.add(cate)

        db.session.flush()
        exc_info = 'save inv: %s'%len(content)
    except:
        exc_info = traceback.format_exc()
        success = False

    if success:
        db.session.commit()
        task.state = 'done'
        task.exc_info = 'SUCCESS'
    else:
        db.session.rollback()
        task.state = 'fail'
        task.exc_info = exc_info[-1500:]
        print(exc_info)

    db.session.commit()
    

# 合作伙伴导入
#@hueyapp.task()
@celeryapp.task
def import_partner(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    ret = import_partner_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=user_code, user_name=user_name)
    db.session.close()
    return ret

def import_partner_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    task = Async.query.get(task_id)
    print('handle async task_id ==> ', task_id, task.async_id)

    task.get_file()
    content = get_file_content(task.link)

    success = True
    exc_info = ''

    try:
        task.code = 'partner'
        for row in content:
            d = DictNone(clear_empty(row))
            if not d.code:
                continue
            if Partner.query.filter_by(company_code=company_code, code=d['code']).count() == 0:
                obj = Partner(company_code=company_code, **d)
                db.session.add(obj)
                if not obj.name:
                    obj.name = obj.code
                if not obj.code:
                    obj.code = obj.name
                if not obj.xtype:
                    obj.xtype = 'client_supplier'
        db.session.flush()
        exc_info = 'save partner: %s'%len(content)
    except:
        exc_info = traceback.format_exc()
        success = False

    if success:
        db.session.commit()
        task.state = 'done'
        task.exc_info = 'SUCCESS'
    else:
        db.session.rollback()
        task.state = 'fail'
        task.exc_info = exc_info[-1500:]
        print(exc_info)

    db.session.commit()
    


#@hueyapp.task()
@celeryapp.task
def import_employee(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    ret = import_employee_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=user_code, user_name=user_name)
    db.session.close()
    return ret

def import_employee_sync(company_code, warehouse_code, owner_code, args, task_id, user_code=None, user_name=None):
    task = Async.query.get(task_id)
    print('handle async task_id ==> ', task_id, task.async_id)

    task.get_file()
    content = get_file_content(task.link, True)

    success = True
    exc_info = ''

    try:
        task.code = 'employee'
        for row in content:
            d = DictNone(clear_empty(row))
            if not d.code:
                continue
            if User.query.filter_by(code=d['code'], company_code=company_code).count() == 0:
                u = User(roles='employee', company_code=company_code, **d)
                db.session.add(u)

        db.session.flush()
        exc_info = 'save employee: %s'%len(content)
    except:
        exc_info = traceback.format_exc()
        success = False

    if success:
        db.session.commit()
        task.state = 'done'
        task.exc_info = 'SUCCESS'
    else:
        db.session.rollback()
        task.state = 'fail'
        task.exc_info = exc_info[-1500:]
        print(exc_info)

    db.session.commit()
    




