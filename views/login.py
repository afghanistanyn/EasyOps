from flask import Blueprint , render_template ,redirect, session, url_for, request, flash, jsonify
from models import User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, ValidationError
from werkzeug.security import generate_password_hash


mod = Blueprint('login',__name__,static_url_path='/')

class UserLoginForm(FlaskForm):
    account = StringField(label='user',  validators=[DataRequired('请输入账号!'), ],description='账号',render_kw={
                              'class': "form-control",
                              'placeholder': "请输入账号！", 'required': 'required' }
                          )
    password = PasswordField(label='password',validators=[DataRequired('请输入密码'), ],description='密码',render_kw={
                                 'class': "form-control",
                                 'placeholder': "请输入密码！", 'required': 'required'}
                          )
    submit = SubmitField(label='login',render_kw={
	'class': 'btn btn-primary btn-block btn-flat',
                             'id': "btn-sub"}
                         )

    def validate_account(self, field):
        account = field.data
        users = User.query.filter_by(name=account).count()
        if users == 0:
            raise ValidationError('账号不存在！')

			
def login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('/login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@mod.route('/logout/')
def logout():
	#do with session
    return redirect(url_for('/inde'))
	
@mod.route('/login',methods=['GET','POST'])
def login():
	form = UserLoginForm()
    if form.validate_on_submit():
        account = form.data.get('account')
        password = form.data.get('password')
        user = User.query.filter_by(name=account).first()
		#user hash-password check
        if not user.check_pwd(password):
            flash('密码错误！')
        elif user.state == 'off':
            flash('账户已经被冻结，请联系管理员')
        else:
            session['user_id'] = user.id
            if user.group == "ops":
                session['is_admin'] = True
            return redirect(request.args.get('next')) if request.args.get('next') else redirect(url_for('/index'))
    return render_template('/login', form=form)


	