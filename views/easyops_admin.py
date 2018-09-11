from flask import Blueprint , session , redirect , url_for, abort
from flask_admin import Admin , expose , AdminIndexView
from flask_admin.contrib.sqla import ModelView
from models import *


class AdminBlueprint(Blueprint):
    views = None

    def __init__(self, *args, **kwargs):
        self.views = []
        return super(AdminBlueprint, self).__init__("easyops_admin", __name__, url_prefix='/admin')

    def add_view(self, view):
        self.views.append(view)

    def register(self, app, options, first_registration=False):
        admin = Admin(app, name="easyops_admin",index_view=EasyOpsAdminIndexView(),  template_mode="bootstrap3")

        for v in self.views:
            admin.add_view(v)

        return super(AdminBlueprint, self).register(app, options, first_registration)


class EasyOpsAdminIndexView(AdminIndexView):
    @expose('/')
    @expose('/index')
    def index(self):
        return "this is easyops admin manager."

    def is_accessible(self):
        print "run to here"
        if session.get('is_admin') == "true":
            return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        return abort(403)

class EasyOpsAdminServerView(ModelView):
    column_searchable_list = (Server.name, Server.lan_ip, Server.lan_mac, Server.services_tag)

    def is_accessible(self):
        print "user_name: " + str(session.get('user_name'))
        print "is_admin: " + str(session.get('is_admin'))
        if session.get('is_admin') == "true":
            return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login.login', next="/admin/server"))

class EasyOpsAdminUserView(ModelView):
    column_searchable_list = (User.name, User.group, User.email,User.state)
    can_edit = False
    column_exclude_list = ('pwd')

    def is_accessible(self):
        print "user_name: " + str(session.get('user_name'))
        print "is_admin: " + str(session.get('is_admin'))
        if session.get('is_admin') == "true":
            return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login.login', next="/admin/user"))


easyops_admin = AdminBlueprint('easyops_admin',__name__, url_prefix='/admin')


easyops_admin.add_view(EasyOpsAdminServerView(Server, db.session))
easyops_admin.add_view(EasyOpsAdminUserView(User, db.session))
easyops_admin.add_view(ModelView(Publish,db.session))
easyops_admin.add_view(ModelView(Jenkins_build,db.session))
easyops_admin.add_view(ModelView(Jenkins_job,db.session))
