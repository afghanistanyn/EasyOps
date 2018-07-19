from flask import Blueprint, render_template, g,jsonify,session


mod = Blueprint('index', __name__, static_url_path='/')

@mod.route('/')
@mod.route('/index')

def index():
    print "user_id: " + str(session.get('user_id'))
    print "is_admin: " + str(session.get('is_admin'))
    return jsonify([g.user.name,g.user.group])
