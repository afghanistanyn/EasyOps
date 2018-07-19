from flask import Flask,g,session
from flask import render_template
from flask_debugtoolbar import DebugToolbarExtension
from models import User
from flask import session

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://easyops:easyops@192.168.1.27:3306/easyops'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///easyops.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = 'thisissecretkey'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.debug = True
toolbar = DebugToolbarExtension(app)

from views import index
app.register_blueprint(index.mod)

from views import cmdb
app.register_blueprint(cmdb.mod)

from views import easyops_admin as Admin
app.register_blueprint(Admin.easyops_admin)

from views import login
app.register_blueprint(login.mod)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.before_request
def load_user():
    if session.__contains__('user_id'):
        user = User.query.filter_by(id=session["user_id"]).first()
    else:
        user = User(name="guest",group="anonymous",is_admin=False)
        session.pop('user_id', None)
        session.pop('is_admin', None)

    g.user = user