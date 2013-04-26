#!/usr/bin/env python2.7
# v1.0
# Ryan Nguyen

# 1. creates a specified number of 512MB cloud servers
# 2. prints out a compiled report of the created servers containing: id, public ipv4, private ipv4, root password

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

disp_time = helper.disp_time()

# takes a single parameter: quantity of servers to create
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
        print 'building {0} servers...'.format(num_servers)

create_servers = []
for n in range (1, num_servers+1):
        create_servers.append(prefix+str(n))

# get all OS's in a list, filter list for Cent* matches, sort filtered list, and grab latest version
os_imgs = helper.act_loop(cs.images.list)
cent_os_imgs = [img for img in os_imgs if "Cent" in img.name]
cent_os_imgs.sort(key=lambda x: x.name, reverse=True)
latest_cent_os_img = cent_os_imgs[0]
# search flavors, get 512* instance via match
sv_512 = [flavor for flavor in helper.act_loop(cs.flavors.list) if "512" in flavor.name][0]

# queue a list of servers to build out
queued_servers = []
data = {}
for host in create_servers:
        data = {
                'name': host,
                'os_img_id': latest_cent_os_img.id,
                'flavor_id': sv_512.id,
                'files': None, 
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

