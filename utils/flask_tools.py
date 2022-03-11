#coding=utf8

import tempfile
import os.path
import json
import xmltodict
from datetime import datetime, date, tzinfo, timedelta, time
from decimal import Decimal
from pprint import pprint
from functools import wraps
from flask import Response, make_response, send_file

import csv
from io import BytesIO
import xlsxwriter


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, time):
            return obj.strftime('%H:%M')
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, bytes):
            return obj.decode('utf8')
        else:
            return json.JSONEncoder.default(self, obj)

def json_dump(data, indent=None):
    return json.dumps(data, ensure_ascii=False, indent=indent, cls=ComplexEncoder)

def json_response(data, indent=None, total=None, code=None):
    resp = Response()
    if code:
        resp.status_code = code
    resp.headers["Content-Type"] = "application/json;charset=UTF-8"
    if total:
        resp.headers['X-Total'] = str(total)
    resp.set_data(json.dumps(data, ensure_ascii=False, indent=indent, cls=ComplexEncoder))
    return resp

def xml_response(data, code=None):
    resp = Response()
    if code:
        resp.status_code = code
    resp.headers["Content-Type"] = "application/xml;charset=UTF-8"
    data2 = json.loads(json.dumps(data, ensure_ascii=False, cls=ComplexEncoder))
    resp.set_data(xmltodict.unparse(data2, pretty=True))
    return resp


CROS_HEADERS = {
    'Access-Control-Allow-Origin': "*",
    'Access-Control-Allow-Credentials': 'true',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': '*'
    }

def cros_decorater(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        ret = func(*args, **kwargs)
        ret.headers.extend(CROS_HEADERS)
        return ret
    return decorated_view


def gen_csv(title, table, fname='sample', is_titles=False, get_file=False, to_txt=False):
    si = BytesIO()
    cw = csv.writer(si)
    # type transfer problem, correct it after
    rows = (title + table) if is_titles else ([title] + table)
    data = [[c if type(c) is unicode else c for c in r] for r in rows]
    cw.writerows(data)

    if get_file:
        return si

    output = make_response(si.getvalue())
    if to_txt:
        output.headers["Content-Disposition"] = "attachment; filename=%s.txt"%fname
        output.headers["Content-type"] = "text/plain"
    else:
        output.headers["Content-Disposition"] = "attachment; filename=%s.csv"%fname
        output.headers["Content-type"] = "text/csv"
    return output

def gen_xlsx(title, table, fname='sample', is_titles=False, get_file=False):
    with tempfile.NamedTemporaryFile(dir='/tmp') as fp:
        workbook = xlsxwriter.Workbook(fp.name, {'in_memory': True})
        worksheet = workbook.add_worksheet()
        
        row = 0
        col = 0
        rows = (title + table) if is_titles else ([title] + table)
        for arow in rows:
            for c, colm in enumerate(arow):
                # type transfer problem, correct it after
                worksheet.write(row, col+c, unicode(colm))
            row += 1

        workbook.close()
        fp.seek(0)
        if get_file:
            si = BytesIO()
            si.write(fp.read())
            si.seek(0)
            return si
        
        return send_file(output, 
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
            as_attachment=True, attachment_filename='%s.xlsx'%fname)


def to_resp(fname, bs):
    response = make_response(bs)
    ext = os.path.splitext(fname)[1]
    ct = "text/plain"
    if ext == '.js':
        ct = "application/javascript"
    elif ext == '.html':
        ct = "text/html"
    elif ext == '.css':
        ct = "text/css"
    response.headers['Content-Type'] = ct
    return response


def is_xhr(request):
    return request.headers.get('Content-Type','') == 'application/json' or 'application/json' in request.headers.get('Content-Type', '')
