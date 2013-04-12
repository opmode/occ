#!/usr/bin/env python
# v 1.0
# Ryan Nguyen

# creates a clone of your newest server

import os
import pyrax
import string
import re
import sys
import time
import common as helper

# preliminary
seconds_before_retrying = 5
prefix = 'test'
creds_file = os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(creds_file)
cs = pyrax.cloudservers
	
disp_time = helper.disp_time()

# takes a single parameter: quantity of clones to create 
# ensure that a valid amount is provided, cap the amount to 50 for sanity reasons
if len(sys.argv)<2:
        print '{0}: <number of servers>'.format(sys.argv[0])
        sys.exit(1)
else:
        num_servers = helper.strip_non_numbers(sys.argv[1])
        error = 'ERROR: you entered an invalid number of servers'
        if num_servers == '':
                print error
                sys.exit(1)
        num_servers = int(num_servers)
        if (num_servers < 1) or (num_servers > 50):
                print error, '[ either too few (0) or too many >50 ]'
                sys.exit(1)

create_servers = []
for n in range (1, num_servers+1):
        create_servers.append(prefix+str(n))

# get most recent cloud server, take an clone image of it
server = helper.act_loop(cs.servers.list)[0]
print 'targeting server:', server.name
print 'Creating clone image of target server...'
image_label = '{0}-image'.format(server.name)
os_img = helper.act_loop(server.create_image, image_label)

while True:
	os_img = helper.act_loop(cs.images.get, os_img)
	if os_img.status == 'ACTIVE': 
		break
	print 'waiting for image build, status: {0}, progress: {1}%'.format(os_img.status, os_img.progress)
	time.sleep(seconds_before_retrying)
print 'SUCCESS: cloned images, proceeding to build servers..'

# get the right server for our image, upgrade any legacy images to 512 server 
img_ram_req = os_img.minRam
if img_ram_req < 512:
	img_ram_req = 512
sv_flavor = [flavor for flavor in helper.act_loop(cs.flavors.list) if img_ram_req == flavor.ram][0]

# grab the SSH keys from the host so we can inject them into the server via files kwarg
try:
	with open ("/root/.ssh/authorized_keys", "r") as root_ssh_auth_keys:
		ssh_auth_file=root_ssh_auth_keys.read().replace('\n', '')
	files = {"/root/.ssh/authorized_keys": ssh_auth_file}
except IOError as e:
	print 'WARNING:', e
	files = None


# queue a list of servers to build out
queued_servers = []
data = {}
for host in create_servers:
        data = {
                'name': host,
                'os_img_id': os_img.id,
                'flavor_id': sv_flavor.id,
                'files': files,
                'completed': 'no'
                }
        queued_servers.append(data)

# build out the servers in the queue
finished_servers = helper.build_servers(queued_servers)
nodes = []
print ' '
print '-------------'
print 'YAY, TIME FOR THE BUILD REPORT..'
print '-------------'
for svr in finished_servers:
        print "ID:", svr['id']
        print "Server:", svr['name']
        print "Public IP:", svr['pub']
        print "Private IP:", svr['priv']
        print "Admin password:", svr['pass']
        print '-------------'

