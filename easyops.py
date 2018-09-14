from flask import Flask,g,session
from flask import render_template
from flask_debugtoolbar import DebugToolbarExtension
from models import User
from flask import session
from flask_wtf import CsrfProtect


app = Flask(__name__)

app.config.from_pyfile('conf/jenkins.conf')
app.config['JENKINS_URL'] = app.config.get('JENKINS_URL')
app.config['JENKINS_USER'] = app.config.get('JENKINS_USER')
app.config['JENKINS_PASSWD'] = app.config.get('JENKINS_PASSWD')
app.config['JENKINS_GITREPO_URL_PATTERN'] = app.config.get('JENKINS_GITREPO_URL_PATTERN')


app.config.from_pyfile('conf/git.conf')
app.config['GIT_USER'] = app.config.get('GIT_USER')
app.config['GIT_PASSWD'] = app.config.get('GIT_PASSWD')

app.config.from_pyfile('conf/ldap.conf')
app.config['LDAP_LOGIN_VIEW'] = app.config.get('LDAP_LOGIN_VIEW')
app.config['LDAP_OPENLDAP'] = app.config.get('LDAP_OPENLDAP')
app.config['LDAP_REALM_NAME'] = app.config.get('LDAP_REALM_NAME')
app.config['LDAP_HOST'] = app.config.get('LDAP_HOST')
app.config['LDAP_BASE_DN'] = app.config.get('LDAP_BASE_DN')
app.config['LDAP_USER_BASE_DN'] = app.config.get('LDAP_USER_BASE_DN')
app.config['LDAP_GROUP_BASE_DN'] = app.config.get('LDAP_GROUP_BASE_DN')
app.config['LDAP_USER_OBJECT_FILTER'] = app.config.get('LDAP_USER_OBJECT_FILTER')

# Admin configuration (not allow anonymous)
app.config['LDAP_USERNAME'] = app.config.get('LDAP_USERNAME')
app.config['LDAP_PASSWORD'] = app.config.get('LDAP_PASSWORD')

# Group configuration
app.config['LDAP_GROUP_OBJECT_FILTER'] = app.config.get('LDAP_GROUP_OBJECT_FILTER')
app.config['LDAP_GROUP_MEMBERS_FIELD'] = app.config.get('LDAP_GROUP_MEMBERS_FIELD')
app.config['LDAP_GROUP_ID_FIELD'] = app.config.get('LDAP_GROUP_ID_FIELD')
app.config['LDAP_GROUP_MEMBER_FILTER'] = app.config.get('LDAP_GROUP_MEMBER_FILTER')
app.config['LDAP_GROUP_MEMBER_FILTER_FIELD'] = app.config.get('LDAP_GROUP_MEMBER_FILTER_FIELD')


app.config.from_pyfile('conf/mysql.conf')
MYSQL_HOST = app.config.get('MYSQL_HOST')
MYSQL_PORT = app.config.get('MYSQL_PORT')
MYSQL_USER = app.config.get('MYSQL_USER')
MYSQL_PASSWD = app.config.get('MYSQL_PASSWD')
MYSQL_DB = app.config.get('MYSQL_DB')

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://%s:%s@%s:%s/%s" % (MYSQL_USER,MYSQL_PASSWD,MYSQL_HOST,MYSQL_PORT,MYSQL_DB)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = 'thisissecretkey'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.debug = True
toolbar = DebugToolbarExtension(app)



from views import index
app.register_blueprint(index.mod)

from views import cmdb
app.register_blueprint(cmdb.mod)

from views import cicd
app.register_blueprint(cicd.mod)

from views import easyops_admin as Admin
app.register_blueprint(Admin.easyops_admin)

from views import login
app.register_blueprint(login.mod)

from views.zdnst_ldap import zdnst_ldap
app.zdnst_ldap = zdnst_ldap(app)

from views import ldap_login
app.register_blueprint(ldap_login.mod)

CsrfProtect(app)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(401)
def page_unauthorized(error):
    return render_template('401.html'), 401


@app.before_request
def load_user():
    if session.__contains__('user_name'):
        user = session["user_name"]

    else:
        user = None

        if session.__contains__('user_name'):
            session.pop('user_name', None)
        if session.__contains__('user_group'):
            session.pop('user_group', None)
        if session.__contains__('is_admin'):
            session.pop('is_admin', None)

    g.user = user