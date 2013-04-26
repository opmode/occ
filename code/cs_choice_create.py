#!/usr/bin/env python2.7
# v1.0
# Ryan Nguyen

# 1. creates a cloud server with arguments FQDN, IMAGE, and FLAVOR
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
parser = argparse.ArgumentParser(description = "creates a cloud servers")
parser.add_argument('hostname', action='store', type=str, help='i.e.: hostname') 
parser.add_argument('os_image', action='store', type=str, help='uses search keyword: Cent, Ubuntu') 
parser.add_argument('flavor', action='store', type=int, help='choose either: 512, 1024, 2048, 4096, or 8192') 
args = parser.parse_args()

print 'getting os image information..'
# get all OS's in a list, filter list for Cent* matches, sort filtered list, and grab latest version
os_imgs = helper.act_loop(cs.images.list)
os_img = [img for img in os_imgs if args.os_image in img.name]
os_img.sort(key=lambda x: x.name, reverse=True)
os_img = os_img[0]
# search flavors, get 512* instance via match
sv_flavor = [flavor for flavor in helper.act_loop(cs.flavors.list) if args.flavor == flavor.ram][0]

# queue a list of servers to build out
queued_servers = []
data = {}
for n in range (1, 0+1):
    host = prefix+str(n)
    data = {
        'name': args.hostname,
        'os_img_id': os_img.id,
        'flavor_id': sv_flavor.id,
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

domains = helper.act_loop(cdns.list, limit=1)
for domain in domains:
    dom = domain
    dom_name = dom.name
    # create a cname for the container we created
    subdomain = '{0}.{1}'.format(svr['name'], dom_name)
    recs = [{"type": "A", "name": subdomain, "data": svr['pub'], "ttl": 300}]
    # add our A record
    helper.act_loop(cdns.add_records, dom, recs)

