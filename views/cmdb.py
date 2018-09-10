from flask import Blueprint , render_template , current_app ,g , session

from models import Server
from zdnst_ldap import login_required
from zdnst_ldap import group_required


# zdnst_ldap.login_required
# from .zdnst_ldap import group_required


mod = Blueprint('cmdb',__name__,static_url_path='/')
#mod = Blueprint('cmdb',__name__,static_url_path='/%s' % __name__)


@mod.route('/server_info')
@login_required
@group_required(groups=["admin",'operation'])
def server_info():
	main_infos = {}
	main_infos["mod_name"]  = "CMDB"
	main_infos["mod_info"]  = "zdnst server informations"

	main_infos["user_name"] = session["user_name"]
	main_infos["user_group"] = session["user_group"]
	main_infos["user_img"] = "https://avatars3.githubusercontent.com/u/5069076?s=400&v=4"
	
	
	
	server_infos = Server.query.all()
	
	print server_infos[0].__dict__.keys()
	show_p_t=list(filter(lambda x: not x.startswith('_') , server_infos[0].__dict__.keys()))
	show_p=list(filter(lambda x: not 'time' in x , show_p_t))
	show_p=['id','name','lan_ip','lan_mac','system','virtual','services_tag']
	
	return render_template('cmdb/server_info.html',shown_p=show_p,Main_infos=main_infos,server_infos=server_infos)