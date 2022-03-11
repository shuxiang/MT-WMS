# coding=utf8
import os
import json

from flask import Blueprint, request, session, current_app, \
    url_for, render_template, make_response, redirect, jsonify, g
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_principal import Principal, Identity, AnonymousIdentity, identity_changed


from extensions.database import db
from extensions.permissions import admin_perm, manager_perm, normal_perm

from blueprints.auth.action import AuthAction

bp_index = Blueprint("index", __name__)


@bp_index.route('/')
@bp_index.route('/erp')
def vue_index():
    # return 'VUE INDEX'
    nginx_host = os.environ.get('NGINX_HOST', '')
    if getattr(g, 'user', None) is None:
        return render_template('website/index.html')

    # init company
    comp = g.user.company
    if not comp.is_init:
        AuthAction.init_company(comp)
        comp.is_init = True
        db.session.commit()

    resp = make_response(render_template('index.html'))

    AuthAction.set_openresty_cookie(g.user, resp)
    return resp


@bp_index.route('/pda')
def vue_pda_index():
    # return 'VUE INDEX'
    nginx_host = os.environ.get('NGINX_HOST', '')
    if getattr(g, 'user', None) is None:
        return redirect(nginx_host+'/auth/login/pda')

    # init company
    comp = g.user.company
    if not comp.is_init:
        AuthAction.init_company(comp)
        comp.is_init = True
        db.session.commit()

    resp = make_response(render_template('index_pda.html'))
    AuthAction.set_openresty_cookie(g.user, resp)
    return resp
