from flask import Flask, g, request, session, redirect, url_for ,current_app ,abort
from flask_simpleldap import LDAP
from functools import wraps

from ldap import filter as pyldap_filter
from ldap import LDAPError as pyldap_LDAPError
from ldap import SCOPE_SUBTREE as pyldap_SCOPE_SUBTREE
import sys
#from ldap_login import login

#override the get_user_groups() , cause of our openldap group settings
class zdnst_ldap(LDAP):

    def get_user_gid(self,user):
        query = None
        fields = None
        conn = self.bind
        if user is not None:
            fields = '*'
            query = pyldap_filter.filter_format(current_app.config['LDAP_USER_OBJECT_FILTER'], (user,))
        try:
            records = conn.search_s(current_app.config['LDAP_BASE_DN'],pyldap_SCOPE_SUBTREE, query, fields)
            conn.unbind_s()

            if records:
                if current_app.config['LDAP_GROUP_ID_FIELD'] in records[0][1]:
                    gid = records[0][1][current_app.config['LDAP_GROUP_ID_FIELD']]
                    return ''.join(gid)

        except pyldap_LDAPError as e:
            raise pyldap_LDAPError(self.error(e.args))


    def get_user_groups(self, user):

        conn = self.bind
        try:
            if current_app.config['LDAP_OPENLDAP']:
                fields = \
                    [str(current_app.config['LDAP_GROUP_MEMBER_FILTER_FIELD'])]
                records = conn.search_s(
                    current_app.config['LDAP_GROUP_BASE_DN'], pyldap_SCOPE_SUBTREE,
                    pyldap_filter.filter_format(
                        current_app.config['LDAP_GROUP_MEMBER_FILTER'],
                        (self.get_user_gid(user),)),
                    fields)
                conn.unbind_s()
            else:
                records = []

            if records:
                if current_app.config['LDAP_OPENLDAP']:
                    group_member_filter = \
                        current_app.config['LDAP_GROUP_MEMBER_FILTER_FIELD']
                    if sys.version_info[0] > 2:
                        groups = [record[1][group_member_filter][0].decode(
                            'utf-8') for record in records]
                    else:
                        groups = [record[1][group_member_filter][0] for
                                  record in records]
                    return ''.join(groups)
                else:
                    if current_app.config['LDAP_USER_GROUPS_FIELD'] in \
                            records[0][1]:
                        groups = records[0][1][
                            current_app.config['LDAP_USER_GROUPS_FIELD']]
                        result = [re.findall(b'(?:cn=|CN=)(.*?),', group)[0]
                                  for group in groups]
                        if sys.version_info[0] > 2:
                            result = [r.decode('utf-8') for r in result]
                        return ''.join(result)
        except pyldap_LDAPError as e:
            raise LDAPException(self.error(e.args))

def login_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        print g.user
        if g.user is None:
            return redirect(url_for(current_app.config['LDAP_LOGIN_VIEW'], next=request.path))
        return func(*args, **kwargs)

    return wrapped


def group_required(groups=None):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if g.user is None:
                return redirect(
                    url_for(current_app.config['LDAP_LOGIN_VIEW'],next=request.path))
            match = [group for group in groups if group in session['user_group']]
            if not match:
                abort(401)

            return func(*args, **kwargs)

        return wrapped

    return wrapper

def basic_auth_required(self, func):
    def make_auth_required_response():
        response = make_response('Unauthorized', 401)
        response.www_authenticate.set_basic(
            current_app.config['LDAP_REALM_NAME'])
        return response

    @wraps(func)
    def wrapped(*args, **kwargs):
        if request.authorization is None:
            req_username = None
            req_password = None
        else:
            req_username = request.authorization.username
            req_password = request.authorization.password


        if req_username in ['', None] or req_password in ['', None]:
            current_app.logger.debug('Got a request without auth data')
            return make_auth_required_response()

        if not self.bind_user(req_username, req_password):
            current_app.logger.debug('User {0!r} gave wrong '
                                         'password'.format(req_username))
            return make_auth_required_response()

        g.ldap_username = req_username
        g.ldap_password = req_password

        return func(*args, **kwargs)

    return wrapped