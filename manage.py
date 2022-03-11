# -*- coding:utf-8 -*-
import os

import click
from flask.cli import with_appcontext

from app import application as app
from app import celeryapp
from app import db as dbm

from models.auth import User, Company, Partner
from models.inv import Category
from models.warehouse import Warehouse, Area, Workarea, Location

from extensions.permissions import ROLES_PERM, VROLES

@click.group()
def db():
    """Perform database migrations."""
    pass

@db.command()
@with_appcontext
def init_data():
    from blueprints.auth.action import AuthAction

    # 普通默认公司
    comp = Company(code='default', name='default')
    comp.is_init = True
    dbm.session.add(comp)

    # 超级管理员
    user = User(code='admin0', password=AuthAction.encrypt_password('admin123456'), name=u"超级管理员")
    user.company_code = comp.code
    user.set_perm('admin')
    user.set_vrole(list(VROLES.get('boss')))
    user.xtype = 'monitor'
    dbm.session.add(user)

    admin = User(code='admin', password=AuthAction.encrypt_password('admin123456'), name=u"管理员")
    admin.company_code = comp.code
    admin.set_perm('manager')
    admin.set_vrole(list(VROLES.get('boss')))
    admin.xtype = 'monitor'
    dbm.session.add(admin)

    dbm.session.flush()

    from blueprints.auth.action import AuthAction
    AuthAction.init_company(comp)

    dbm.session.commit()


@db.command()
@with_appcontext
def create_all():
    dbm.create_all()

