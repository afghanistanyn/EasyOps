# -*- coding:utf-8 -*-
from flask import Blueprint, render_template, redirect, session, url_for, request, flash, jsonify
from models import User
from flask_wtf import FlaskForm, CsrfProtect
from wtforms import StringField, PasswordField, SubmitField, SelectField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, ValidationError
from werkzeug.security import generate_password_hash
from functools import wraps

mod = Blueprint('login', __name__, static_url_path='/')

class UserLoginForm(FlaskForm):
    account = StringField(label='user', validators=[DataRequired(u'请输入账号!'), ], description=u'账号', render_kw={
        'class': "form-control",
        'placeholder': u"请输入账号！", 'required': 'required'}
                          )
    password = PasswordField(label='password', validators=[DataRequired(u'请输入密码'), ], description=u'密码', render_kw={
        'class': "form-control",
        'placeholder': u"请输入密码！", 'required': 'required'}
                             )
    submit = SubmitField(label='login', render_kw={
        'class': 'btn btn-primary btn-block btn-flat',
        'id': "btn-sub"}
                         )

    def validate_account(self, field):
        account = field.data
        users = User.query.filter_by(name=account).count()
        if users == 0:
            raise ValidationError(u'账号不存在！')


def login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_name' in session and 'is_admin' not in session:
            print 'role admin require , please login as admin'
            return redirect(url_for('login.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@mod.route('/logout/')
def logout():
    session.pop('user_name',None)
    session.pop('user_group', None)
    session.pop('is_admin',None)
    return redirect('/index')

@mod.route('/login', methods= ['GET','POST'])
def login():
    form = UserLoginForm()
    if form.validate_on_submit():
        account = form.data.get('account')
        password = form.data.get('password')
        user = User.query.filter_by(name=account).first()
        # user hash-password check
        if user.state == 'off':
            flash(u'账户已经被冻结，请联系管理员')
        elif not user.check_pwd_plain(password):
            flash(u'密码错误！')
        else:
            session['user_name'] = user.name
            session['user_group'] = user.group
            if user.role == 'admin':
                session['is_admin'] = "true"
            return redirect(request.args.get('next')) if request.args.get('next') else redirect(url_for('index.index'))
    return render_template('login.html', form=form)

