#!/usr/bin/env python2.7
# v 1.0
# Ryan Nguyen

# this script creates a CDN enabled container with a specified name

import sys
import os
import re
import time
import pyrax
import common as helper

# preliminary
creds_file = os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(creds_file)
cf = pyrax.cloudfiles

# take one parameter: the name of the CF container to create
if len(sys.argv) < 2:
        print 'syntax: {0} <container_name>'.format(sys.argv[0])
        sys.exit(1)
else:
        site_cont_name = sys.argv[1]

# try to use the container if it exists, otherwise create one using provided name and then use it
cont = helper.act_loop(cf.get_container, site_cont_name)

# make container public, cdn enable container
cont.make_public(ttl=1200)

# print results
print 'created public CDN container: {0}'.format(site_cont_name)
