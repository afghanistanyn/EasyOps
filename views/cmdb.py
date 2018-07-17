
from flask import Blueprint , render_template
from models import Server

mod = Blueprint('cmdb',__name__,static_url_path='/')
#mod = Blueprint('cmdb',__name__,static_url_path='/%s' % __name__)


@mod.route('/server_info')
def server_info():
	server_infos = Server.query.all()
	print server_infos[0].__dict__.keys()
	#show_p_t=list(filter(lambda x: not x.startswith('_') , server_infos[0].__dict__.keys()))
	#show_p=list(filter(lambda x: not 'time' in x , show_p_t))


	show_p=['id','name','lan_ip','system','virtual','services_tag']
	return render_template('cmdb/server_info.html',shown_p=show_p,server_infos=server_infos)
