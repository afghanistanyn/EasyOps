
# -*- coding:utf-8 -*-ß
from __future__ import print_function
from jenkinsapi import jenkins


J = jenkins.Jenkins("http://192.168.0.8", username="admin", password="jenkins")  # type: Jenkins

print (J.version)
print (J.base_server_url())

print (type(J.plugins.keys()))


print(J.nodes.keys())

print (J.credentials.keys())

print (J.jobs.keys())


print(J.get_job("test").get_build_dict().items())