from flask import Blueprint
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import Server , db

class AdminBlueprint(Blueprint):
    views = None

    def __init__(self,*args,**kwargs):
        self.views = []
        return super(AdminBlueprint,self).__init__("easyops_admin",__name__,url_prefix='/admin')

    def add_view(self,view):
        self.views.append(view)

    def register(self, app, options, first_registration=False):
        #print app
        admin = Admin(app,name="easyops_admin",template_mode="bootstrap3")

        for v in self.views:
            admin.add_view(v)

        return super(AdminBlueprint,self).register(app,options,first_registration)


easyops_admin = AdminBlueprint('easyops_admin',__name__,url_prefix='/admin')
easyops_admin.add_view(ModelView(Server,db.session))