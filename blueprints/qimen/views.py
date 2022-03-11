#coding=utf8
import json
import xmltodict
from sqlalchemy import func, or_, and_
from pprint import pprint
from datetime import datetime, timedelta
from random import randint
from decimal import Decimal as dec

from flask import Blueprint, g, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from extensions.database import db
from extensions.permissions import admin_perm, manager_perm, normal_perm

from models.inv import Inv, Good, Category, InvRfid
from models.auth import Did, Seq, Company
from models.stockout import Stockout, StockoutLine
from models.stockin import Stockin, StockinLine

from utils.flask_tools import json_response, gen_csv, xml_response
from utils.functions import gen_query, clear_empty, json2mdict, json2mdict_pop
from utils.functions import update_model_with_fields, m2dict, copy_and_update_model, common_poplist
from utils.functions import gen_query, DictNone
from utils.base import Dict, DictNone

from blueprints.qimen.action import QimenAction, confirm_order

import settings


bp_qimen = Blueprint("qimen", __name__)



# 获取订单
@bp_qimen.route('', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@bp_qimen.route('/xml', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
def qimen_api():
    method = request.args.get('method', None)
    is_xml = '/xml' in request.path

    action = QimenAction()

    error = {
            "error_response":{
                "flag":"failure",
                "code":"1",
                "message":"error"
            },
            # "response":{
            #     "flag":"failure",
            #     "code":"1",
            #     "message":"error"
            # }
        }

    if method not in action.api_list:
        error['error_response']['message'] = 'method not support~'
        #error['response']['message'] = 'method not support~'
        if is_xml:
            return xml_response(error, code=404)
        return json_response(error, code=404)

    # 签名验证
    body = request.get_data()
    check = action.check_sign(request.args, body=(body if is_xml else ''))
    if not check:
        error['error_response']['message'] = 'sign not pass valid'
        #error['response']['message'] = 'sign not pass valid'
        if is_xml:
            return xml_response(error, code=401)
        return json_response(error, code=401)

    reqdata = xmltodict.parse(body) if is_xml else request.json
    ok, data = action.do(method, request.args, reqdata)

    if not ok:
        db.session.rollback()
        if is_xml:
            return xml_response(data)
        return json_response(data)

    db.session.commit()
    if is_xml:
        return xml_response(data)
    return json_response(data)

# 手动回传
@bp_qimen.route('/confirm/<inout>/<order_id>', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@normal_perm.require()
def confirm_api(inout, order_id):
    ok, msg = confirm_order(order_id, inout)
    if ok:
        return json_response({'status': 'success', 'msg': 'ok'})
    return json_response({'status': 'fail', 'msg': msg})


@bp_qimen.route('/confirm/backtest', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
@bp_qimen.route('/confirm/backtest/xml', methods=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
def confirm_backtest_api():
    is_xml = '/xml' in request.path
    ret = {
            "response":{
                "flag":"success",
                "code":"0",
                "message":"ok"
            }
        }
    if is_xml:
        return xml_response(ret)
    return json_response(ret)
