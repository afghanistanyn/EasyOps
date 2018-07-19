# -*- coding:utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text , func

db=SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100))
    pwd = db.Column(db.String(100))
    group = db.Column(db.String(20))
    info = db.Column(db.Text)
    is_admin = db.Column(db.Boolean)
    state = db.Column(db.String(255))
    updatetime = db.Column(db.TIMESTAMP(True), nullable=True)
    createtime = db.Column(db.TIMESTAMP(True), nullable=False, server_default=text('NOW()'))

    def __repr__(self):
        return '<User: %r>' % self.name

    def check_pwd_hash(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)

    def check_pwd_plain(self , pwd):
        from werkzeug.security import safe_str_cmp
        return safe_str_cmp(self.pwd , pwd)

class Server(db.Model):
    __tablename__ = "servers"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), nullable=True,unique=True)
    lan_ip = db.Column(db.String(32), nullable=True,unique=True)
    lan_mac = db.Column(db.String(32), nullable=True)
    wan_ip = db.Column(db.String(32), nullable=True)
    wan_mac = db.Column(db.String(32), nullable=True)
    osrelease = db.Column(db.String(32),nullable=True)
    ssh_port = db.Column(db.Integer,nullable=True)
    ssh_passwd = db.Column(db.String(32),nullable=True)
    system = db.Column(db.String(64),nullable=True)
    idc = db.Column(db.String(64),nullable=True)
    virtual = db.Column(db.String(12),nullable=True)
    services_tag = db.Column(db.String(64),nullable=True)
    updatetime = db.Column(db.TIMESTAMP(True), nullable=True)
    createtime = db.Column(db.TIMESTAMP(True), nullable=False, server_default=text('NOW()'))


    def __init__(self,name,lan_ip,lan_mac="",wan_ip="",wan_mac="",osrelease="",ssh_port=54110,ssh_passwd="",system="",idc="",virtual="",services_tag=""):
                self.name = name
                self.lan_ip = lan_ip
                self.lan_mac = lan_mac
                self.wan_ip = wan_ip
                self.wan_mac = wan_mac
                self.osrelease = osrelease
                self.ssh_port = ssh_port
                self.ssh_passwd = ssh_passwd
                self.system = system
                self.idc = idc
                self.virtual = virtual
                self.services_tag = services_tag

    def __repr__(self):
                return '<Server %r>' % self.name