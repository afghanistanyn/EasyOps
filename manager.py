import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from easyops import app
from models import *
from sqlalchemy.sql import exists
from sqlalchemy import and_
from sqlalchemy import text
from sqlalchemy import or_
from sqlalchemy import update
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
	print(J.jobs.__repr__())

	from inspect import isgenerator
	assert isgenerator(J.jobs.iteritems())

	for job in J.jobs.iteritems():

		job_name = job[0]
		job_description = job[1].get_description()
		job_params = str(job[1].get_params_list())
		job_state = 1 if job[1].is_enabled() else 0
		#last_build = job[1].get_build_metadata(job[1].get_last_buildnumber())

		# print last_build.get_status()
		#print last_build.get_params()
		# print last_build.get_causes()
		# print last_build.get_actions()
		# print last_build.get_console()
		# print last_build.baseurl

		#print Jenkins_job.query.filter_by(job_name=job[0]).scalar() != None
		# print Jenkins_job.query.filter_by(job_name=job[0]).count() != 1
		# #print db.session.query(Jenkins_job.job_name).filter_by(job_name=job[0]).scalar() is not None

	 	if db.session.query(exists().where(Jenkins_job.job_name == job[0])).scalar():
	 	 	print "the job %s exists , update ..." % job[0]
			row_changed = Jenkins_job.query.filter_by(job_name=job[0]).update(dict(job_description=job_description,
																		   job_params=job_params, job_state=job_state))
			db.session.commit()
	 	else:
	 	 	jenkins_job = Jenkins_job(job_name=job_name, job_description=job_description, job_params=job_params, job_state=job_state)
	 	 	db.session.add(jenkins_job)
	 	 	db.session.commit()

	# delete exists in db but not jenkins
	db_jobs = [ x[0] for x in db.session.query(Jenkins_job.job_name).filter().all() ]
	print db_jobs
	jk_jobs = [ x[0] for x in J.jobs.iteritems() ]
	print jk_jobs
	for job in list(set(db_jobs).difference(set(jk_jobs))):
		print "the job %s exists in db , but not jenkins , clean it " % job


if __name__=="__main__":
	manager.run()
