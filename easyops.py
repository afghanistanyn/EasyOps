from flask import Flask
from flask import render_template
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://easyops:easyops@192.168.1.27:3306/easyops'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///easyops.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'thisissecretkey'

app.debug = True
toolbar = DebugToolbarExtension(app)

from views import cmdb
app.register_blueprint(cmdb.mod)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

