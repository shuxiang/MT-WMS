# -*- coding: utf-8 -*-
__all__ = ['Async', ]
import os
import requests
import mimetypes
import traceback
import os.path
import json
from sqlalchemy.sql import text
from uuid import uuid4
from datetime import datetime
from sqlalchemy import Index, UniqueConstraint
import settings

from extensions.database import db
from utils.upload import oss2, oss2_access_key_id, oss2_access_key_secret, oss2_endpoint
from utils.oss import oss_http_put 

# --------任务名称----------------------------|--状态-------|--日期-----------|--下载------|---类型----
# --------2015-5、2015-7入库统计报表--|---未完成---|---2018-5-23----|--无链接---|--下载----
# --------2015-4、2015-6出库报表--------|---完成------|---2018-5-23----|--链接------|--下载----
# --------2015-4入库单----------------------|---完成------|---2018-5-23----|--------------|--上传----

class Async(db.Model):
    __tablename__ = 'ext_async'
    __table_args__ = (Index("ix_ext_async_company", "company_code",),
                      Index("ix_ext_async_code", "company_code", "code",),
                      )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), default='')
    code = db.Column(db.String(50), default='')
    
    company_code = db.Column(db.String(50), default='')
    warehouse_code = db.Column(db.String(50))
    owner_code = db.Column(db.String(50))

    state = db.Column(db.Enum('done', 'doing', 'fail'), default='doing', server_default='doing')
    xtype = db.Column(db.Enum('import', 'export'), default='export', server_default='export')

    func = db.Column(db.String(250), default='')
    func_name = db.Column(db.String(250), default='')
    
    # link to aliyun oss file
    oss_link = db.Column(db.String(250), default='')
    # _link file to blob_uuid
    _link = db.Column(db.String(250), name="link", default='')
    blob_uuid = db.Column(db.String(50), server_default='')
    # exc_info
    exc_uuid = db.Column(db.String(50), server_default='')
    # celery task id
    async_id = db.Column(db.String(60), default='')

    remark = db.Column(db.String(200), server_default='')
    create_time = db.Column(db.DateTime, default=db.default_datetime())
    update_time = db.Column(db.DateTime, default=db.default_datetime(), onupdate=db.default_datetime())

    # -- link to file --
    @property
    def link(self):
        return self._link

    @link.setter
    def link(self, val):
        self._link = val
        blob = b''
        with open(val, 'rb') as f:
            blob = f.read()

        if not self.owner.async2oss:
            return
        try:
            file_name = '9-' + val.split('/')[-1]
            if oss2:
                bucket = oss2.Bucket(oss2.Auth(oss2_access_key_id, oss2_access_key_secret), oss2_endpoint, 'wms-export')
                bucket.put_object(file_name, blob)
            else:
                oss_http_put('wms-export', file_name, blob, mimetypes.guess_type(file_name)[0])
            self.oss_link = file_name
            print('save file to oss success: %s'%file_name)
        except:
            print('upload file to oss error: %s'%self.async_id)
            traceback.print_exc()

            if settings.UPLOAD_TO_DB:
                if self.blob_uuid:
                    db.M('Big').query.filter_by(code='Async', subcode='link_file', uuid=self.blob_uuid).update({'blob':blob})
                else:
                    uuid = str(uuid4())
                    big = db.M('Big')(company_code=self.company_code, code='Async', subcode='link_file', blob=blob, uuid=uuid)
                    db.session.add(big)
                    self.blob_uuid = uuid

    def get_file(self):
        if self.oss_link:
            file_path =  os.path.join(settings.UPLOAD_DIR, self.oss_link)
            if os.path.exists(file_path):
                return

            if not self.owner.async2oss:
                return

            if oss2:
                bucket = oss2.Bucket(oss2.Auth(oss2_access_key_id, oss2_access_key_secret), oss2_endpoint, 'wms-export')
                bucket.get_object_to_file(self.oss_link, file_path)
            else:
                OSS_URL_PREFIX = os.environ.get('OSS_URL_PREFIX', '')
                iurl = OSS_URL_PREFIX + self.oss_link
                r = requests.get(iurl)
                with open(file_path, 'wb') as f:
                    f.write(r.content)
            print('get file from oss_link', self.oss_link)
        else:
            if os.path.exists(self.link):
                return

            if settings.UPLOAD_TO_DB:
                big = db.M('Big').query.filter_by(uuid=self.blob_uuid).first()
                if big:
                    with open(self.link, 'wb') as f:
                        f.write(big.blob)

    def drop_file(self):
        if self.oss_link:
            db.M('Big').query.filter_by(uuid=self.blob_uuid).delete()

    def unlink_file(self):
        # delete local file
        try:
            os.unlink(self.link)
        except:
            pass
        # delete oss file
        try:
            if oss2:
               bucket = oss2.Bucket(oss2.Auth(oss2_access_key_id, oss2_access_key_secret), oss2_endpoint, 'wms-export')
               bucket.delete_object(self.oss_link)
        except:
            pass

    # -- exc info --
    @property
    def exc_info(self):
        e = db.M('Big').query.filter_by(uuid=self.exc_uuid).first()
        if e:
            return e.blob
        return ''

    @exc_info.setter
    def exc_info(self, val):
        if self.exc_uuid:
            db.M('Big').query.filter_by(code='Async', subcode='exc_info', uuid=self.exc_uuid).update({'blob':val})
        else:
            uuid = str(uuid4())
            big = db.M('Big')(company_code=self.company_code, code='Async', subcode='exc_info', blob=val.encode('utf8'), uuid=uuid)
            db.session.add(big)
            self.exc_uuid = uuid

    @property
    def owner(self):
        return db.M('Partner').query.filter_by(code=self.owner_code, company_code=self.company_code).first()
    




















