# -*- coding:utf-8 -*-
from flask import Blueprint , render_template , current_app ,g , session , request ,jsonify
import urllib
from models import Publish, Jenkins_build, Jenkins_job , db
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, ValidationError
from utils.jenkins import get_jenkins_job_git_url
from utils.jenkins import get_git_branches


from zdnst_ldap import login_required
from zdnst_ldap import group_required


mod = Blueprint('cicd',__name__,static_url_path='/')

class NewPublishForm(FlaskForm):
    publush_name = StringField(label='publish_name', validators=[DataRequired(u'请输入发布名称'), ], description=u'名称', render_kw={
        'class': "form-control",
        'placeholder': u"请输入发布名称!", 'required': 'required'}
                          )
    publish_content = StringField(label='publish_content', validators=[DataRequired(u'请输入发布说明'), ], description=u'说明', render_kw={
        'class': "form-control",
        'placeholder': u"请输入发布说明!", 'required': 'required'}
                             )
    submit = SubmitField(label='pulish_new', render_kw={
        'class': 'btn btn-primary btn-block btn-flat',
        'id': "btn-sub"}
                         )

    def validate_publush(self, field):
        publish_name = field.data
        rows = Publish.query.filter_by(publish_name=publish_name).count()
        if rows != 0:
            raise ValidationError(u'已存在同名发布!')




@mod.route('/publish/new',methods = ['GET','POST'])
@login_required
@group_required(groups=["admin",'operation','dev'])
def new_publish():
    if request.method == "GET":
        if request.args.has_key('publish_name'):
            publish_name = urllib.unquote(request.args.get('publish_name'))
            return publish_name
        else: return "please provide publish_name & publish_content"


    elif request.method == "POST":
        form = NewPublishForm
        publish_name = form.data.get('publish_name')

    return publish_name

@mod.route('/jenkins/job_git_url/<job_name>',methods = ['GET'])
@login_required
@group_required(groups=["admin",'operation','dev'])
def jenkins_job_git_url(job_name):
    if request.method == "GET":
        job_info = get_jenkins_job_git_url(job_name)
        return jsonify(job_info if (job_info is not None) else "")



@mod.route('/jenkins/job_git_url/all', methods=['GET'])
@login_required
@group_required(groups=["admin", 'operation', 'dev'])
def jenkins_jobs_git_urls():
    if request.method == "GET":
        # for job in Jenkins_job.query(Jenkins_job.job_name).all():
        #     print job

        job_git_urls = {}
        records = db.session.query(Jenkins_job.job_name).all()
        for _job in records:
            job_name = _job[0]
            _job_url = get_jenkins_job_git_url(job_name)
            job_git_urls[job_name]= _job_url if (_job_url is not None) else ""
        return jsonify(job_git_urls)


@mod.route('/jenkins/job_params/all', methods=['GET'])
@login_required
@group_required(groups=["admin", 'operation', 'dev'])
def jenkins_jobs_git_url():
    if request.method == "GET":
        # for job in Jenkins_job.query(Jenkins_job.job_name).all():
        #     print job

        job_params = {}
        records = db.session.query(Jenkins_job.job_params).all()
        for _job in records:
            job_params = _job[0]
            job_git_urls[job_name]= job_params if (job_params is not None) else ""
        return jsonify(job_params)


@mod.route('/jenkins/job_branch/<job_name>', methods=['GET'])
@login_required
@group_required(groups=["admin", 'operation', 'dev'])
def jenkins_job_params(job_name):
    if request.method == "GET":

        job_git_branch = {}
        records = Jenkins_job.query.filter(Jenkins_job.job_name == job_name).count()
        if records == 0:
            return jsonify({"err":["job not found"]})

        _job_url = get_jenkins_job_git_url(job_name)
        if _job_url is None:
            return jsonify({job_name:[]})
        else:
            git_branche = get_git_branches(_job_url,current_app.config['GIT_USER'],current_app.config['GIT_PASSWD'])
            job_git_branch[job_name] = git_branche

            return jsonify(job_git_branch)




@mod.route('/jenkins/job_branch/all', methods=['GET'])
@login_required
@group_required(groups=["admin", 'operation', 'dev'])
def jenkins_jobs_params():
    if request.method == "GET":
        # for job in Jenkins_job.query(Jenkins_job.job_name).all():
        #     print job

        job_git_branches = {}
        records = db.session.query(Jenkins_job.job_name).all()
        for _job in records:
            job_name = _job[0]
            _job_url = get_jenkins_job_git_url(job_name)
            if _job_url is None:
                git_branches = []
            else:
                # job_url = _job_url if (_job_url is not None) else ""
                git_branches = get_git_branches(_job_url,current_app.config['GIT_USER'],current_app.config['GIT_PASSWD'])
            job_git_branches[job_name]= git_branches

        return jsonify(job_git_branches)
