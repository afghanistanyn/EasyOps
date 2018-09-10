from flask import Flask, g, request, session, redirect, url_for ,current_app
from flask_simpleldap import LDAP

from ldap import filter as pyldap_filter
from ldap import LDAPError as pyldap_LDAPError
from ldap import SCOPE_SUBTREE as pyldap_SCOPE_SUBTREE
import sys

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
                    return groups
                else:
                    if current_app.config['LDAP_USER_GROUPS_FIELD'] in \
                            records[0][1]:
                        groups = records[0][1][
                            current_app.config['LDAP_USER_GROUPS_FIELD']]
                        result = [re.findall(b'(?:cn=|CN=)(.*?),', group)[0]
                                  for group in groups]
                        if sys.version_info[0] > 2:
                            result = [r.decode('utf-8') for r in result]
                        return result
        except pyldap_LDAPError as e:
            raise LDAPException(self.error(e.args))

app = Flask(__name__)
app.secret_key = 'this is a secret key'
app.debug = True

app.config.from_pyfile('../conf/ldap.conf')
app.config['LDAP_OPENLDAP'] = app.config.get('LDAP_OPENLDAP')
app.config['LDAP_REALM_NAME'] = app.config.get('LDAP_REALM_NAME')
app.config['LDAP_HOST'] = app.config.get('LDAP_HOST')
app.config['LDAP_BASE_DN'] = app.config.get('LDAP_BASE_DN')
app.config['LDAP_USER_BASE_DN'] = app.config.get('LDAP_USER_BASE_DN')
app.config['LDAP_GROUP_BASE_DN'] = app.config.get('LDAP_GROUP_BASE_DN')
app.config['LDAP_USER_OBJECT_FILTER'] = app.config.get('LDAP_USER_OBJECT_FILTER')

# Admin configuration (not allow anonymous)
app.config['LDAP_USERNAME'] = app.config.get('LDAP_USERNAME')
app.config['LDAP_PASSWORD'] = app.config.get('LDAP_PASSWORD')

# Group configuration
app.config['LDAP_GROUP_OBJECT_FILTER'] = app.config.get('LDAP_GROUP_OBJECT_FILTER')
app.config['LDAP_GROUP_MEMBERS_FIELD'] = app.config.get('LDAP_GROUP_MEMBERS_FIELD')
app.config['LDAP_GROUP_ID_FIELD'] = app.config.get('LDAP_GROUP_ID_FIELD')
app.config['LDAP_GROUP_MEMBER_FILTER'] = app.config.get('LDAP_GROUP_MEMBER_FILTER')
app.config['LDAP_GROUP_MEMBER_FILTER_FIELD'] = app.config.get('LDAP_GROUP_MEMBER_FILTER_FIELD')



ldap = zdnst_ldap(app)

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        # This is where you'd query your database to get the user info.
        g.user = {}
        # Create a global with the LDAP groups the user is a member of.
        g.ldap_groups = ldap.get_user_groups(user=session['user_id'])

@app.route('/')
@ldap.login_required
def index():
    return 'Successfully logged in!'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = request.form['user']
        passwd = request.form['passwd']
        test = ldap.bind_user(user, passwd)
        if test is None or passwd == '':
            return 'Invalid credentials'
        else:
            session['user_id'] = request.form['user']
            return redirect('/')
    return """<form action="" method="post">
                user: <input name="user"><br>
                password:<input type="password" name="passwd"><br>
                <input type="submit" value="Submit"></form>"""


@app.route('/group')
@ldap.group_required(groups=['test','operation'])
def group():
    return 'Group restricted page'


@app.route('/g')
def show_group():
    if 'user_id' in session:
        group = ''.join(ldap.get_user_groups(user=session['user_id']))
        return group
    else:
        return 'login need'


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()