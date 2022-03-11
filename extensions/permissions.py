# coding=utf8
from flask_principal import RoleNeed, UserNeed, Permission

__roles__ = ('admin', 'manager', 'normal',)

admin_perm      = Permission(RoleNeed('admin'),)
manager_perm    = Permission(RoleNeed('admin'), RoleNeed('manager'),)
normal_perm     = Permission(RoleNeed('admin'), RoleNeed('manager'), RoleNeed('normal'),)

# 系统权限
ROLES_PERM = {
    # 超级管理员
    'admin': ('admin', 'manager', 'normal',),
    # 管理
    'manager': ('manager', 'normal',),
    # 普通登录人员
    'normal': ('normal',),
    # 
    # 普通非登录员工
    'employee': ('employee',),
}

# 公司内部权限
# 老板boss 管理员manager 财务finance 仓库stock 
VROLES = {
    'boss': ('boss', 'manager', 'finance', 'stock', ), # 老板
    'manager': ('manager', 'finance', 'stock',), # 管理员
    'finance': ('finance', 'stock',), # 财务
    'stock': ('stock',), # 仓库
    'express': ('express',), # 快递
    'empty': ('empty',), # 空视图权限
}
