#coding=utf8

import os
import settings
import traceback
from datetime import datetime, timedelta
from huey import crontab
from sqlalchemy import func, or_, and_
from extensions.hueyext import hueyapp
from extensions.celeryext import celeryapp
from extensions.database import db

from models.auth import Company
from models.inv import Good
from models.stockin import Stockin
from models.stockout import Stockout

"""
crontab(minute='*', hour='*', day='*', month='*', day_of_week='*')
    Convert a "crontab"-style set of parameters into a test function that will
    return True when the given datetime matches the parameters set forth in
    the crontab.
    
    For day-of-week, 0=Sunday and 6=Saturday.
    
    Acceptable inputs:
    * = every distinct value
    */n = run every "n" times, i.e. hours='*/4' == 0, 4, 8, 12, 16, 20
    m-n = run every time m..n
    m,n = run on m and n
"""


@hueyapp.periodic_task(crontab(minute='*/10'))
def qimen_confirm():
    print ('====== confirm_order =======', datetime.now())
    from blueprints.qimen.action import confirm_order

    for stockin in Stockin.query.filter_by(is_qimen=True, is_passback=False, state='done').all():
        confirm_order(stockin.id, 'in')

    for stockout in Stockout.query.filter_by(is_qimen=True, is_passback=False, state='done', state_ship='done').all():
        confirm_order(stockout.id, 'out')
