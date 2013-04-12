#!/usr/bin/env python2.6
# v1.0
# Ryan Nguyen

# 1. creates a specified number of 512MB cloud servers
# 2. prints out a compiled report of the created servers containing: id, public ipv4, private ipv4, root password

import os
import sys 
import time
import argparse
import common as helper
import pyrax

# prelimsies
creds_file = os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(creds_file)
cs = pyrax.cloudservers
prefix = 'test'

# get quantity of servers
parser = argparse.ArgumentParser(description = "creates a specified number of 512MB cloud servers")
parser.add_argument('qty', action='store', type=int, help='quantity of servers to create') 
args = parser.parse_args()

# limit quantity to less than 50
if (args.qty < 1) or (args.qty > 50):
        print 'ERROR: qty is limited to 1-50 servers'
        sys.exit(1)
print 'building %s servers...' % args.qty

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
for n in range (1, args.qty+1):
	host = prefix+str(n)
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

