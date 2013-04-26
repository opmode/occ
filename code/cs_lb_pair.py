#!/usr/bin/env python2.7
# v 1.0
# Ryan Nguyen

# this script will 
# - create a specified qty of CentOS 6+ 512MB  servers
# - create a load balancer 
# - add the respective servers to the load balancer for HTTP:80

import os
import sys
import time
import argparse
import pyrax
import common as helper

# preliminary
seconds_before_retrying = 5
prefix = 'test'
creds_file = os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(creds_file)
cs = pyrax.cloudservers
clb = pyrax.cloud_loadbalancers

disp_time = helper.disp_time()

# get quantity of servers
parser = argparse.ArgumentParser(description = "creates a specified number of 512MB cloud servers")
parser.add_argument('qty', action='store', type=int, help='quantity of servers to create')
args = parser.parse_args()

# limit quantity to less than 50
if (args.qty < 1) or (args.qty > 50):
    print 'ERROR: qty is limited to 1-50 servers'
    sys.exit(1)

# get all OS's in a list, filter list for Cent* matches, sort filtered list, and grab latest version
print 'getting os image information..'
os_imgs = helper.act_loop(cs.images.list)
cent_os_imgs = [img for img in helper.act_loop(cs.images.list) if "Cent" in img.name]
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
	# add nodes to load balancer while im at it
        nodes.append(helper.act_loop(clb.Node, address=svr['priv'], port=80, condition="ENABLED"))

vip = helper.act_loop(clb.VirtualIP, type="PUBLIC")
default_algorithm = helper.act_loop(map, str, clb.algorithms)[0]
lb_name = '{0}-lb'.format(prefix)
lb = helper.act_loop(clb.create, lb_name, port="80", protocol="HTTP", nodes=nodes, virtual_ips=[vip], algorithm=default_algorithm)

while True:
        lb = helper.act_loop(clb.get, lb.id)
        print 'checking server until LB is active...', helper.disp_time()
        if lb.status == 'ACTIVE':
                print "Load Balancer:", lb.name
                print "ID:", lb.id
                print "Status:", lb.status
                print "Nodes:", lb.nodes
                print "Virtual IPs:", lb.virtual_ips
                print "Algorithm:", lb.algorithm
                print "Protocol:", lb.protocol
                break
        time.sleep(1)
