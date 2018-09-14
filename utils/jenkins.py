from models import Jenkins_job
from flask import current_app
from jenkinsapi import jenkins
from jenkinsapi import custom_exceptions
import re

from git import  Git
from git import GitCommandError
from giturlparse import parse






# install
#pip install git+https://github.com/afghanistanyn/git-url-parse , a hacked version

def _add_auth_info(url, git_user, git_passwd):
    p = parse(url)
    if p.user is None and p.passwd is None:
        if p.port != None:
            new_url = p.protocol + "://" + git_user + ":" + git_passwd + "@" + p.host + ":" + p.port + p.pathname
        else:
            new_url =  p.protocol + "://" + git_user + ":" + git_passwd + "@" + p.host  + p.pathname
        return new_url
    else:
        return url

def get_git_branches(url, git_user, git_passwd):
    if url.startswith('git') or url.startswith('ssh'):
        raise TypeError('The git scheme not support !')
        #return []

    if git_user != '' and git_passwd != '':
        url_with_auth = _add_auth_info(url, git_user, git_passwd)

    else:
        url_with_auth = url

    cmd = 'git ls-remote -h %s ' % url_with_auth
    try:
        data = Git().execute(cmd)
        branches = [ x.split('/')[-1] for x in data.split('\n') ]
        return branches
    except GitCommandError as e:
        print e
        return []


def get_jenkins_job_git_url(jenkins_job_name):
    J = jenkins.Jenkins(current_app.config['JENKINS_URL'], current_app.config['JENKINS_USER'], current_app.config['JENKINS_PASSWD'])
    try:
        job = J.get_job(jenkins_job_name)
        #return job.get_scm_url()
        et =  job._get_config_element_tree()
        try:
            jenkins_file = et.find('definition').find('script').text
            git_url_list = re.findall(re.compile(current_app.config['JENKINS_GITREPO_URL_PATTERN']), jenkins_file)
            git_url_str = ''.join(git_url_list).replace('\'', '').replace('"', '').lstrip()
            return git_url_str
        except AttributeError as e:
            print e
            return None
    except custom_exceptions.UnknownJob as e:
        print 'UnknownJob %s' % e
        return None


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