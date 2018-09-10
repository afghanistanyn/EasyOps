from flask import Blueprint, render_template, g,jsonify,session

from models import User

mod = Blueprint('index', __name__, static_url_path='/')

@mod.route('/')
@mod.route('/index')

def index():
    print "user_name: " + str(session.get('user_name'))
    print "is_admin: " + str(session.get('is_admin'))
    if session.__contains__('user_group'):
        return jsonify([session['user_name'],session['user_group']])

    if g.user is None:
        user = User(name="guest", role='anonymous')
        return jsonify([user.name, user.role])

    else:
        return jsonify(g.user)

