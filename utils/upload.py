#coding=utf8

'''
openpyxl==2.6.4
Pillow==6.2.1
'''

import mimetypes
import os
import os.path
from uuid import uuid4
import requests
from datetime import datetime
from flask import request
from xlrd import open_workbook
from openpyxl import load_workbook
from pprint import pprint
try:
    import oss2
except:
    from .oss import oss_http_put
    oss2 = None

def get_file_content(file_path, with_im=False, im_keys=None):
    ws = open_workbook(file_path).sheet_by_index(0)
    row_values = ws.row_values

    if not with_im:
        return [{k: (row_values(i)[j].strip() if type(row_values(i)[j]) in (str, unicode) else row_values(i)[j]) for j, k in enumerate(row_values(0))} for i in range(2, ws.nrows)]
    else:
        if file_path.endswith('.xls'):
            raise Exception(u'由于操作系统原因, 图片上传不支持`.xls`格式文件, 请先转成`.xlsx`格式')
        sheet = load_workbook(file_path).worksheets[0]
        # im.anchor.to 是表示图片的跨度, 比如图片太大, 显示上跨了多个单元格, to就是图片右下角的单元格位置
        ims = {(im.anchor._from.row, im.anchor._from.col):im for im in sheet._images}

        table = []
        for i in range(2, ws.nrows):
            d = {}
            for j,k in enumerate(row_values(0)):
                if type(row_values(i)[j]) in (str, unicode):
                    v = row_values(i)[j].strip()
                else:
                    v = row_values(i)[j]
                if with_im and k in im_keys:
                    v = ims.get((i,j), None)
                d[k] = v
            table.append(d)

        # os.remove(file_path)
        return table

def save_request_file(upload_dir, filename='file', company_id=1):
    fobj = request.files[filename]
    ext = os.path.splitext(fobj.filename)[1]

    save_name = str(datetime.now().date()) + '_' + str(uuid4())[:8] + ext

    dirpath = os.path.join(upload_dir, str(company_id))
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
        
    file_path = os.path.join(upload_dir, str(company_id), save_name)
    fobj.save(file_path)

    return fobj.filename, file_path

def save_request_file_to_oss(upload_dir, save2oss=False, filedir='images', bucketname='wms-images', request_file_name='file', prefix='UP', company_id=1):
    fobj = request.files[request_file_name]
    ext = os.path.splitext(fobj.filename)[1]

    filename = prefix+str(datetime.now().date()) + '_' + str(uuid4())[:8] + ext
    filepath = os.path.join(upload_dir, filedir, str(company_id), filename)

    dirpath = os.path.join(upload_dir, filedir, str(company_id))
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    # 先保存
    fobj.save(filepath)
    # 读取blob
    blob = None
    with open(filepath, 'rb') as f:
        blob = f.read()

    if save2oss:
        try:
            if oss2:
                bucket = oss2.Bucket(oss2.Auth(oss2_access_key_id, oss2_access_key_secret), oss2_endpoint, bucketname)
                o = bucket.put_object(filename, blob)
            else:
                oss_http_put(bucketname, filename, blob, mimetypes.guess_type(filename)[0])
        except:
            print('save oss file error: %s' % filename)
    # local path, localname&ossname, origin name
    return filepath, filename, fobj.filename


def save_image(upload_dir, blob, ext='jpeg', save2oss=False, filedir='images', bucketname='wms-images', company_id=1):
    filename = str(datetime.now().date()) + '_' + str(uuid4())[:8] + '.' + ext

    if save2oss:
        try:
            if oss2:
                bucket = oss2.Bucket(oss2.Auth(oss2_access_key_id, oss2_access_key_secret), oss2_endpoint, bucketname)
                o = bucket.put_object(filename, blob)
            else:
                oss_http_put(bucketname, filename, blob, mimetypes.guess_type(filename)[0])
        except:
            print('save oss file error: %s' % filename)

    dirpath = os.path.join(upload_dir, filedir, str(company_id))
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    # save 2 local
    path = os.path.join(upload_dir, filedir, str(company_id), filename)
    with open(path, 'wb') as f:
        f.write(blob)

    return path, filename

def get_oss_image(upload_dir, osslink, filedir='images', bucketname='wms-images', company_id=1):
    file_path =  os.path.join(upload_dir, filedir, str(company_id), osslink)

    dirpath = os.path.join(upload_dir, filedir, str(company_id))
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    try:
        if oss2:
            bucket = oss2.Bucket(oss2.Auth(oss2_access_key_id, oss2_access_key_secret), oss2_endpoint, bucketname)
            bucket.get_object_to_file(osslink, file_path)
        else:
            OSS_URL_PREFIX = os.environ.get('OSS_URL_PREFIX', '')
            iurl = OSS_URL_PREFIX + osslink
            r = requests.get(iurl) 
            with open(file_path, 'wb') as f:
                f.write(r.content)
    except:
        print('get oss file error: %s' % osslink)

    if os.path.exists(file_path):
        return


# oss2 wms settings
oss2_access_key_id = os.environ.get('oss2_access_key_id', '')
oss2_access_key_secret = os.environ.get('oss2_access_key_secret', '')
oss2_endpoint = os.environ.get('oss2_endpoint', '')

# ======== qrcode & barcode ========
import qrcode
from pystrich.code128 import Code128Encoder

def save_inv_qrcode(upload_dir, company_id, content):
    dirpath = os.path.join(upload_dir, 'qrcode', str(company_id))
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    path = os.path.join(dirpath, "%s.png"%content)
    vpath = '/static/upload/qrcode/%s/%s.png'%(company_id, content)
    save_qrcode(content, path)

    return path, vpath

def save_inv_barcode(upload_dir, company_id, content):
    dirpath = os.path.join(upload_dir, 'barcode', str(company_id))
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    path = os.path.join(dirpath, "%s.png"%content)
    vpath = '/static/upload/barcode/%s/%s.png'%(company_id, content)
    save_barcode(content, path)

    return path, vpath


def save_barcode(content, path):
    try:
        encoder = Code128Encoder(content, {'bottom_border':3})
        encoder.save(path)
    except:
        pass
    return path

def save_qrcode(content, path):
    # 实例化QRCode生成qr对象
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    # 传入数据
    qr.add_data(content)
    qr.make(fit=True)

    # 生成二维码
    img = qr.make_image()

    # 保存二维码
    img.save(path)
    # 展示二维码
    # img.show()
    return path
