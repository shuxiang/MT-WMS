#coding=utf8

import traceback
from flask import g
from datetime import datetime
from random import randint
from itertools import groupby
from sqlalchemy import and_, or_
from utils.functions import update_model_with_fields, m2dict, copy_and_update_model, common_poplist, json2mdict_pop, clear_empty

from models.stockout import Stockout, StockoutLine, StockoutLineTrans, Alloc, StockoutMerge
from blueprints.inv.action import InvAction

from extensions.database import db
from models.inv import Inv, Good, InvTrans
from models.auth import Seq, Partner

class MergeAction(object):

    def __init__(self):
        pass

    def create_merge(self, remark=''):
        merge = StockoutMerge(company_code=g.company_code, warehouse_code=g.warehouse_code, owner_code=g.owner_code, remark=remark, 
                user_code=g.user.code, user_name=g.user.name)
        merge.order_code = Seq.make_order_code('MC', g.company_code, g.warehouse_code, g.owner_code)
        db.session.add(merge)
        return merge
