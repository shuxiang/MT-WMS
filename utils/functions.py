#coding=utf8
import json
from uuid import uuid4
from sqlalchemy import or_, and_
from datetime import datetime, date, tzinfo, timedelta
from random import randint
from decimal import Decimal
# from urllib2 import unquote
from urllib.parse import unquote

from .base import Dict, DictNone




common_poplist = ['id', 'remark', 'update_time', 'create_time', 'state', 'source',]
common_poplist2 = ['id', 'remark', 'update_time', 'create_time',]
common_poplist3 = ['id', 'update_time', 'create_time', ]


# clear_empty
def clear_empty(d, empty_str=True):
    popkeys = []
    for k, v in d.items():
        if not v and not empty_str and type(v) in (str, unicode):
            d[k] = ''
        elif not v:
            popkeys.append(k)
            #d.pop(k)
        elif type(v) in (str, unicode):
            d[k] = v.strip()
    for k in popkeys:
        d.pop(k, None)
    return d

# model to dict
def m2dict(m, empty=False):
    if not m:
        return {}
    return {c.name: (getattr(m, c.name, None) if not empty else None) for c in m.__table__.columns}

# sqlalchemy result to dict
def sqla_res2dict(m):
    return {c: getattr(m, c, None) for c in m.keys()}

def json2mdict(m, json):
    return {k:v for k,v in json.items() if k in m.__table__.columns}

def json2mdict_pop(m, json, poplist=None):
    poplist = poplist if poplist else common_poplist
    return {k:v for k,v in json.items() if k in m.__table__.columns and k not in poplist}

# 从不同的模型里拷贝数据并更新
def update_model_with_fields(model, instance, poplist, **kw):
    data = m2dict(model, empty=True)
    for i in poplist:
        data.pop(i, None)

    for k,v in m2dict(instance).items():
        if k in data:
            data[k] = v

    data.update(kw)
    return model(**data)

# 拷贝相同的模型，并更新某些数据
def copy_and_update_model(model, instance, poplist, **kw):
    data = m2dict(instance)
    for i in poplist:
        data.pop(i, None)

    data.update(kw)
    return model(**data)

#------------ restless query functions -------------


def gen_query(argstr, query, M, db=None, per_page=20, get_objects=False, export=False):
    q = make_q(argstr or '{}')
    query = make_query(q, query, M, db, export)

    if export:
        return query

    if q.single:
        if get_objects:
            return query.first()
        ret = query.first().as_dict
    else:
        if q.limit:
            # 不用分页了
            pagin = query.paginate(1, per_page=q.limit)
        else:
            pagin = query.paginate(q.page, per_page=(q.per_page or per_page))
        if get_objects:
            return pagin
        ret =  {
          "num_results": pagin.total,
          "total_pages": pagin.pages,
          "page": pagin.page,
          "per_page": pagin.per_page,
          "objects": [i.as_dict for i in pagin.items]
        }
    return ret

# restless make q from request.args.get('q')
def make_q(argstr):
    argstr = unquote(argstr)
    q = json.loads(argstr) if argstr else Dict()
    q = Dict(q)
    q.filters = [Dict(i) for i in q.filters] if 'filters' in q else []
    q.order_by = [Dict(i) for i in q.order_by] if 'order_by' in q else []
    q.group_by = [Dict(i) for i in q.group_by] if 'group_by' in q else []

    q.single = True if 'single' in q else False

    q.limit = int(q.limit) if 'limit' in q else None
    q.offset = int(q.offset) if 'offset' in q else None
    q.page = int(q.page) if 'page' in q else None
    q.per_page = int(q.per_page) if 'per_page' in q else None
    # single, limit, offset, page, per_page

    return q


# make aqla query from restless q;　没有实现多重循环的查询条件
def make_query(q, query, M, db=None, export=False):
    # {"name": <fieldname>, "op": <operatorname>, "val": <argument>}
    # {"name": <fieldname>, "op": <operatorname>, "field": <fieldname>}
    # {"or": [<filterobject>, {"and": [<filterobject>, ...]}, ...]}

    if q.filters:
        for f in q.filters:

            if 'or' in f:
                ors = []
                for f1 in f['or']:
                    exp1 = gen_where_filter(Dict(f1), M, db)
                    if exp1 is not None:
                        ors.append(exp1)
                query = query.filter(or_(*ors))
            elif 'and' in f:
                ands = []
                for f1 in f['and']:
                    exp1 = gen_where_filter(Dict(f1), M, db)
                    if exp1 is not None:
                        ands.append(exp1)
                query = query.filter(and_(*ands))
            else:
                exp = gen_where_filter(f, M, db)
                if exp is not None:
                    query = query.filter(exp)

    # {"field": <fieldname>, "direction": <directionname>}
    if q.order_by:
        query = query.order_by(*[gen_order_by(f, M, db) for f in q.order_by])
    else:
        query = query.order_by(M.id.desc())

    # {"field": <fieldname>}
    if q.group_by:
        query = query.group_by(*[gen_group_by(f, M, db) for f in q.group_by])

    if not export:
        if q.limit:
            query = query.limit(q.limit)

        if q.offset:
            query = query.offset(q.offset)

        # if not q.limit and not q.offset and page:
        #     query = query.limit(per_page).offset((page-1)*per_page)

    return query

def gen_group_by(f, M, db=None):
    fd = getattr(M, f.field)
    return fd

def gen_order_by(f, M, db=None):
    fd = getattr(M, f.field)
    exp = None
    if f.direction == 'asc':
        exp = fd.asc()
    elif f.direction == 'desc':
        exp = fd.desc()
    return exp

def gen_where_filter(f, M, db=None):
    # ==, eq, equals, equals_to
    # !=, neq, does_not_equal, not_equal_to
    # >, gt, <, lt
    # >=, ge, gte, geq, <=, le, lte, leq
    # in, not_in
    # is_null, is_not_null
    # like
    # has
    # any
    op = f.op
    name = f.name
    val = f.val
    fd = getattr(M, name, None)
    if fd is None:
        return None
        
    exp = None
    is_str = type(val) in (str, unicode)
    if op == 'like':
        #ret = "_.%(name)s like '%(val)s'"%f
        val = val.strip() if is_str else val
        exp = fd.like('%s%%'%val)
    elif op == 'ilike':
        #ret = "_.%(name)s like '%(val)s'"%f
        val = val.strip() if is_str else val
        exp = fd.like('%%%s%%'%val)
    elif op in ('==', 'eq', 'equals', 'equals_to', '='):
        #ret = "_.%(name)s = '%(val)s'" %f
        val = val.strip() if is_str else val
        exp = fd == val
    elif op in ('!=', 'neq', 'does_not_equal', 'not_equal_to'):
        #ret = "_.%(name)s != '%(val)s'" %f
        val = val.strip() if is_str else val
        exp = fd != val
    elif op in ('>=', 'ge', 'gte', 'geq'):
        #ret = "_.%(name)s >= '%(val)s'" %f
        exp = fd >= val
    elif op in ('>', 'gt'):
        #ret = "_.%(name)s > '%(val)s'" %f
        exp = fd > val
    elif op in ('<=', 'le', 'lte', 'leq'):
        #ret = "_.%(name)s <= '%(val)s'" %f
        exp = fd <= val
    elif op in ('<', 'lt'):
        #ret = "_.%(name)s < '%(val)s'" %f
        exp = fd < val
    elif op == 'in':
        #ret = "_.%(name)s in %(val)s" %f
        #if getattr(fd, 'in_', None) is not None:
        exp = fd.in_(val.split(',') if is_str else val)
    elif op == 'not_in':
        #ret = "_.%(name)s not in %(val)s" %f
        exp = ~fd.in_(val.split(',') if is_str else val)
    elif op == 'is_null':
        #ret = "_.%(name)s is null" %f
        exp = fd == None
    elif op == 'is_not_null':
        #ret = "_.%(name)s is not null" %f
        exp = fd != None
    # has any not support
    return exp


# ------------ some -----------

code_map = ( 
      'a' , 'b' , 'c' , 'd' , 'e' , 'f' , 'g' , 'h' , 
      'i' , 'j' , 'k' , 'l' , 'm' , 'n' , 'o' , 'p' , 
      'q' , 'r' , 's' , 't' , 'u' , 'v' , 'w' , 'x' , 
      'y' , 'z' , '0' , '1' , '2' , '3' , '4' , '5' , 
      '6' , '7' , '8' , '9' , 'A' , 'B' , 'C' , 'D' , 
      'E' , 'F' , 'G' , 'H' , 'I' , 'J' , 'K' , 'L' , 
      'M' , 'N' , 'O' , 'P' , 'Q' , 'R' , 'S' , 'T' , 
      'U' , 'V' , 'W' , 'X' , 'Y' , 'Z'
      ) 
def get_hash_key():
    hkeys = [] 
    hex = str(uuid4()).replace('-','')
    for i in xrange(0, 4): 
        n = int(hex[i*8:(i+1)*8], 16) 
        v = [] 
        e = 0
        for j in xrange(0, 4): 
            x = 0x0000003D & n 
            e |= ((0x00000002 & n ) >> 1) << j 
            v.insert(0, code_map[x]) 
            n = n >> 5
        e |= n << 4
        v.insert(0, code_map[e & 0x0000003D]) 
        hkeys.append(''.join(v)) 
    return hkeys 

get_pages = lambda x,p:x/p+1 if x%p > 0 else x/p



# create order_code
gen_order_code = lambda prefix: '%s%s-%04d'%(prefix, datetime.now().strftime('%y%m%d%H%M%S'), randint(1, 9999))



def export_attr(k, line, order, dicts=None):
    v = ''
    if k.startswith('o.'):
        v = getattr(order, k[2:], '') or ''
    else:
        v = getattr(line, k, '') or getattr(order, k, '') or ''
    return v


# 中文转拼音
import unicodedata
from xpinyin import Pinyin

pinyin = Pinyin()

def ubarcode(t):
    return pinyin.get_initials(unicodedata.normalize('NFKC', t), u'')

def split_list(li, n):
    length = len(li)
    each = length / n

    if length % n > 0:
        each = each + 1

    left = li[0:each]
    mid  = li[each:2*each]
    right = li[2*each:]

    return left, mid, right
