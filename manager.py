import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from easyops import app
from models import *
from sqlalchemy.sql import func
from flask_script import Manager
from jenkinsapi import jenkins


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

@manager.command
def sync_jenkins_jobs():
	J = jenkins.Jenkins(app.config['JENKINS_URL'],app.config['JENKINS_USER'],app.config['JENKINS_PASSWD'])
	print(J.jobs)

	from inspect import isgenerator
	assert isgenerator(J.jobs.iteritems())


	for job in J.jobs.iteritems():

		print "job_name = %r" % job[0]
		print "job_description = %r" % job[1].get_description()
		print "job_params = %r" % job[1].get_params_list()
		print "job is enabled = %r" % job[1].is_enabled()
		print "job name with build = %r" % job[1].get_build_metadata(job[1].get_last_buildnumber())



		last_build = job[1].get_build_metadata(job[1].get_last_buildnumber())
		print last_build.get_status()
		print last_build.get_params()
		print last_build.get_causes()
		print last_build.get_actions()
		print last_build.get_console()
		print last_build.baseurl


		print "..........................................."



	# 	jenkins_job = Jenkins_job()
	# 	db.session.add(jenkins_job)
	# db.session.commit()


if __name__=="__main__":
	manager.run()
