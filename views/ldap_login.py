# -*- coding:utf-8 -*-
from flask import Blueprint, render_template, redirect, session, url_for, request, flash, jsonify,current_app,g
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, SelectMultipleField, TextAreaField
from login import UserLoginForm
from wtforms.validators import DataRequired, ValidationError

mod = Blueprint('ldap_login', __name__, static_url_path='/')


class UserLoginForm(FlaskForm):
    account = StringField(label='user', validators=[DataRequired(u'请输入账号!'), ], description=u'账号', render_kw={
        'class': "form-control",
        'placeholder': u"请输入账号！", 'required': 'required'}
                          )
    password = PasswordField(label='password', validators=[DataRequired(u'请输入密码'), ], description=u'密码', render_kw={
        'class': "form-control",
        'placeholder': u"请输入密码！", 'required': 'required'}
                             )
    submit = SubmitField(label='ldap_login', render_kw={
        'class': 'btn btn-primary btn-block btn-flat',
        'id': "btn-sub"}
                         )

    def validate_account(self, field):
        account = field.data

        # users = User.query.filter_by(name=account).count()
        # if users == 0:
        #     raise ValidationError(u'账号不存在！')


@mod.route('/ldap_login/', methods=['GET', 'POST'])
def login():
    form = UserLoginForm()
    if form.validate_on_submit():
        account = form.data.get('account')
        password = form.data.get('password')
        test = current_app.zdnst_ldap.bind_user(account,password)
        if test is None:
            flash(u'Invalid credentials, ldap auth failed')
        else:
            session['user_name'] = request.form['account']
            user_group = current_app.zdnst_ldap.get_user_groups(user=request.form['account'])
            if user_group == 'operation':
                session['is_admin'] = "true"
            session['user_group'] = user_group
            return redirect(request.args.get('next')) if request.args.get('next') else redirect(url_for('index.index'))
    return render_template('login.html', form=form)


@mod.route('/ldap_logout/')
def logout():
    session.pop('user_name',None)
    session.pop('is_admin',None)
    session.pop('user_group',None)
    return redirect('/index')