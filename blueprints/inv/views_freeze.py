#coding=utf8
import os
import re
import os.path
import json
import traceback
from sqlalchemy import func, or_
from pprint import pprint
from datetime import datetime
from random import randint

from flask import Blueprint, g, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from extensions.database import db
from extensions.permissions import admin_perm, manager_perm, normal_perm

from models.inv import Inv, Good, Category, InvRfid, GoodMap
from models.inv import InvMove, InvAdjust, InvCount
from models.warehouse import Location
from blueprints.inv.action import InvAction, InvCountAction, InvMoveAction, InvAdjustAction

from utils.flask_tools import json_response, gen_csv
from utils.functions import update_model_with_fields, m2dict, copy_and_update_model, common_poplist
from utils.functions import gen_query, make_q
from utils.base import Dict, DictNone
import settings

bp_inv_freeze = Blueprint("inv_freeze", __name__)


# action.freeze_inv(sku=None, spec=None, location_code=None, area_code=None, qty=None, inv_list=None)


# 冻结批次的id, 按库位与SKU冻结, 按库位与SKU冻结数量, 按SKU冻结数量
@bp_inv_freeze.route('/do', methods=('GET', 'POST',))
@normal_perm.require()
def freeze_do_api():
    action = InvAction()
    
    ok, msg = action.freeze_inv(**request.json)
    if ok:
        db.session.commit()
        return json_response({'status': 'success', 'msg': msg})

    db.session.rollback()
    return json_response({'status': 'fail', 'msg': msg})

# 解冻
@bp_inv_freeze.route('/undo', methods=('GET', 'POST',))
@normal_perm.require()
def unfreeze_undo_api():
    action = InvAction()

    ok, msg = action.unfreeze_inv(**request.json)
    if ok:
        db.session.commit()
        return json_response({'status': 'success', 'msg': msg})

    db.session.rollback()
    return json_response({'status': 'fail', 'msg': msg})
