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
    role = db.Column(db.String(20))
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
    osrelease = db.Column(db.String(64),nullable=True)
    ssh_port = db.Column(db.Integer,nullable=True)
    ssh_passwd = db.Column(db.String(32),nullable=True)
    system = db.Column(db.String(64),nullable=True)
    idc = db.Column(db.String(64),nullable=True)
    virtual = db.Column(db.String(12),nullable=True)
    services_tag = db.Column(db.String(128),nullable=True)
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



class Publish(db.Model):
    __tablename__ = 'publish'
    publish_id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    publish_name = db.Column(db.String(128),nullable=False)
    publish_create_by = db.Column(db.String(64),nullable=True)
    publish_confirm_by = db.Column(db.String(64),nullable=True)
    publish_state = db.Column(db.String(4),nullable=True)
    publish_details = db.Column(db.String(128),nullable=True)
    publish_content = db.Column(db.String(128),nullable=True)
    publish_roll_back_support =  db.Column(db.String(1),nullable=True)
    updatetime = db.Column(db.TIMESTAMP(True), nullable=True)
    createtime = db.Column(db.TIMESTAMP(True), nullable=False, server_default=text('NOW()'))


    tasks = db.relationship('Jenkins_build',backref='Publish', lazy=True)

    def __repr__(self):
        return '<Publish %r>' % self.publish_id


class Jenkins_build(db.Model):
    __tablename__ = 'jenkins_build'
    build_id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    publish_id = db.Column(db.Integer, db.ForeignKey('publish.publish_id'), nullable=False)
    build_job_name = db.Column(db.String(128),nullable=False,unique=True)
    build_number = db.Column(db.Integer,nullable=False)
    build_params = db.Column(db.String(128),nullable=True)
    build_state = db.Column(db.String(8),nullable=True)
    updatetime = db.Column(db.TIMESTAMP(True), nullable=False, server_default=text('NOW()'))

    def __repr__(self):
        return '<Jenkin_Build %r>' % self.build_job_name + "# " + str(self.build_number)

class Jenkins_job(db.Model):
    __tablename__ = 'jenkins_job'
    job_id = db.Column(db.Integer , primary_key = True,autoincrement=True)
    job_name = db.Column(db.String(32),unique=True)
    job_description = db.Column(db.String(128),nullable=True)
    job_params = db.Column(db.String(128),nullable=True)
    job_state = db.Column(db.String(1),nullable=True)
    updatetime = db.Column(db.TIMESTAMP(True), nullable=False, server_default=text('NOW()'))


    def __init__(self,job_name="default_job_name",job_description="",job_params="",job_state=""):
        self.job_name = job_name
        self.job_description = job_description
        self.job_params = job_params
        self.job_state = job_state

    def __repr__(self):
        return '<Jenkins_job %r>' % self.job_name