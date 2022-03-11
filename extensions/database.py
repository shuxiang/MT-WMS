#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import json
import traceback
from datetime import datetime, date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, distinct
from sqlalchemy.orm import lazyload
from flask import request, abort, has_request_context, g
from flask_sqlalchemy import BaseQuery, Pagination

from sqlalchemy.orm.attributes import InstrumentedAttribute


class DataBase(SQLAlchemy):

    def init_app(self, app):
        """需要用到。要不sqlalchemy部分功能无法正常使用"""
        self.app = app
        super(DataBase, self).init_app(app)


db = DataBase()


def get_count(q):
    disable_group_by = False
    if len(q._entities) > 1:
        # currently support only one entity
        raise Exception('only one entity is supported for get_count, got: %s' % q)
    entity = q._entities[0]
    if hasattr(entity, 'column'):
        # _ColumnEntity has column attr - on case: query(Model.column)...
        col = entity.column
        if q._group_by and q._distinct:
            # which query can have both?
            raise NotImplementedError
        if q._group_by or q._distinct:
            col = distinct(col)
        if q._group_by:
            # need to disable group_by and enable distinct - we can do this because we have only 1 entity
            disable_group_by = True
        count_func = func.count(col)
    else:
        # _MapperEntity doesn't have column attr - on case: query(Model)...
        count_func = func.count()
    if q._group_by and not disable_group_by:
        count_func = count_func.over(None)
    count_q = q.options(lazyload('*')).statement.with_only_columns([count_func]).order_by(None)
    if disable_group_by:
        count_q = count_q.group_by(None)
    return q.session.execute(count_q).scalar()

class Query(BaseQuery):
    def real_sql(self):
        # do not use in production; 性能较差, 不要用于生产环境
        return self.statement.compile(compile_kwargs={"literal_binds": True})
        
    @property
    def c_query(self):
        return self.filter_by(company_code=g.company_code)

    @property
    def w_query(self):
        return self.filter_by(company_code=g.company_code, warehouse_code=g.warehouse_code)

    @property
    def o_query(self):
        return self.filter_by(company_code=g.company_code, owner_code=g.owner_code)

    @property
    def t_query(self):
        return self.filter_by(company_code=g.company_code, warehouse_code=g.warehouse_code, owner_code=g.owner_code)
    

    def paginate(self, page=None, per_page=None, error_out=True, max_per_page=None, count=True):
        """Returns ``per_page`` items from page ``page``.
        If ``page`` or ``per_page`` are ``None``, they will be retrieved from
        the request query. If ``max_per_page`` is specified, ``per_page`` will
        be limited to that value. If there is no request or they aren't in the
        query, they default to 1 and 20 respectively. If ``count`` is ``False``,
        no query to help determine total page count will be run.
        When ``error_out`` is ``True`` (default), the following rules will
        cause a 404 response:
        * No items are found and ``page`` is not 1.
        * ``page`` is less than 1, or ``per_page`` is negative.
        * ``page`` or ``per_page`` are not ints.
        When ``error_out`` is ``False``, ``page`` and ``per_page`` default to
        1 and 20 respectively.
        Returns a :class:`Pagination` object.
        """

        if request:
            if page is None:
                try:
                    page = int(request.args.get('page', 1))
                except (TypeError, ValueError):
                    if error_out:
                        abort(404)

                    page = 1

            if per_page is None:
                try:
                    per_page = int(request.args.get('per_page', 20))
                except (TypeError, ValueError):
                    if error_out:
                        abort(404)

                    per_page = 20
        else:
            if page is None:
                page = 1

            if per_page is None:
                per_page = 20

        if max_per_page is not None:
            per_page = min(per_page, max_per_page)

        if page < 1:
            if error_out:
                abort(404)
            else:
                page = 1

        if per_page < 0:
            if error_out:
                abort(404)
            else:
                per_page = 20

        items = self.limit(per_page).offset((page - 1) * per_page).all()

        if not items and page != 1 and error_out:
            return self.paginate(page=1, per_page=per_page, error_out=error_out, max_per_page=max_per_page, count=count)

        # No need to count if we're on the first page and there are fewer
        # items than we expected or if count is disabled.

        if not count:
            total = None
        elif page == 1 and len(items) < per_page:
            total = len(items)
        else:
            try:
                total = get_count(self)
                if len(items) > 0 and total == 0:
                    total = self.order_by(None).count()
            except:
                #traceback.print_exc()
                print('----get_count() error, use origin count()----')
                total = self.order_by(None).count()

        return Pagination(self, page, per_page, total, items)

class Model(db.Model):
    __abstract__ = True
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
    }
    __dump_prop__ = []

    query_class = Query

    @property
    def _columns_name(self):
        return [c.name for c in self.__table__.columns]

    @property
    def as_dict(self):
        # return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}
        data = {}
        # get table columns
        for c in self.__table__.columns:
            v = getattr(self, c.name, None)
            if type(v) is datetime:
                v = str(v)[:16]#19
            if type(v) is date:
                v = str(v)
            data[c.name] = v
        # get __dump_prop__
        for c in self.__dump_prop__:
            data[c] = getattr(self, c, None)

        return data

    def to_json(self):
        return self.as_dict

    def update(self, vars):
        for k, v in vars.items():
            setattr(self, k, v)


db.Model = Model

get_pages = lambda c, p:  c / p + 1 if c % p > 0 else c / p


class Paginate(object):
    def __init__(self, data, page=1, per_page=10):
        self.data = data
        self.total = len(data)
        self.page = page
        self.per_page = per_page
        self.pages = get_pages(self.total, self.per_page)

    @property
    def items(self):
        return self.data[(self.page-1)*self.per_page: self.page*self.per_page]

    def iter_items(self, page, per_page):
        return self.data[(page-1)*per_page: page*per_page]

db.paginate = Paginate

# db.M = lambda x: db.Model._decl_class_registry[x]
db.M = lambda x: db.Model.registry._class_registry[x]

def default_datetime():
    if os.environ.get('T_FUNC', None) == 'python':
        return datetime.now
    return db.func.current_timestamp()

db.default_datetime = default_datetime


