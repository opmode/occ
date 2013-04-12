#!/usr/bin/env python
# v 0.0.1
# Ryan Nguyen

# test wrapper for interactive debugging

import os
import pyrax
import string
import re
import sys
import time
import common as helper

# prelimsies
seconds_before_retrying = 5
prefix = 'test'
creds_file = os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(creds_file)
cs = pyrax.cloudservers
cdns = pyrax.cloud_dns
cf = pyrax.cloudfiles
clb = pyrax.cloud_loadbalancers

queued_servers = [
                        {
                        'id': '25008223-4eff-4c6c-9bd9-745e24ae5c07',
                        'name': 'web2',
                        'net': {u'private': [u'192.168.0.2'], u'public': [u'64.101.1.1', u'2001:4800:780d:0509:8ca7:b42c:xxxx:xxxx']},
			'ipv4': '64.101.1.1',
			'pnet': '192.168.0.2',
                        'pass': 'secretpass2',
                        'completed': 'y'
                        },
                        {
                        'id': '25008223-4eff-4c6c-9bd9-745e24ae5c07',
                        'name': 'web3',
                        'net': {u'private': [u'192.168.0.2'], u'public': [u'64.101.1.1', u'2001:4800:780d:0509:8ca7:b42c:xxxx:xxxx']},
			'ipv4': '64.101.1.1',
			'pnet': '192.168.0.3',
                        'pass': 'secretpass3',
                        'completed': 'y'
                        },
                        {
                        'id': '25008223-4eff-4c6c-9bd9-745e24ae5c07',
                        'name': 'web1',
                        'net': {u'private': [u'192.168.0.2'], u'public': [u'64.101.1.1', u'2001:4800:780d:0509:8ca7:b42c:xxxx:xxxx']},
			'ipv4': '64.101.1.1',
			'pnet': '192.168.0.4',
                        'pass': 'secretpass1',
                        'completed': 'y'
                        }
sys.exit(0)
                ]
# grab the SSH keys from the host 
with open ("/root/.ssh/authorized_keys", "r") as root_ssh_auth_keys:
	ssh_auth_file=root_ssh_auth_keys.read().replace('\n', '')
files = {"/root/.ssh/authorized_keys": ssh_auth_file}

create_servers = ['test123', 'test123-banana']
queued_servers = []
data = {}
for host in create_servers:
        data = {
                'name': host,
                'os_img_id': 'c195ef3b-9195-4474-b6f7-16e5bd86acd0',
                'flavor_id': '2',
                'files': files,
                'completed': 'no'
                }
        queued_servers.append(data)

finished_servers = helper.build_servers(queued_servers)
print ' '
print '-------------'
print 'YAY, TIME FOR THE BUILD REPORT..'
print '-------------'
print ' '
for svr in finished_servers:
        print "ID:", svr['id']
        print "Server:", svr['name']
        print "Public IP:", svr['pub']
        print "Private IP:", svr['priv']
        print "Admin password:", svr['pass']
        print '-------------'
