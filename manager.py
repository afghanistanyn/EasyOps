import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from easyops import app
from models import db
from models import Server
from sqlalchemy.sql import func
from flask_script import Manager


db.init_app(app)
manager = Manager(app)
@manager.command
def init_db():
	db.create_all()
	db.session.commit()

def destory_db():
	db.drop_all()
	
@manager.command
def init_test_data():
	init_db()
	s1 = Server(name='k8s_master',lan_ip='192.168.40.128')
	s2 = Server(name='k8s_node1',lan_ip='192.168.40.129')
	s3 = Server(name='k8s_node2',lan_ip='192.168.40.130')
	db.session.add(s1)
	db.session.add(s2)
	db.session.add(s3)
	db.session.commit()
	
if __name__=="__main__":
	manager.run()
