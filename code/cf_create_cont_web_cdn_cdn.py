#!/usr/bin/env python2.7
# v 1.0
# Ryan Nguyen

# this script must will create a new CF container using specified name
# - cdn enable container
# - enable container to serve an index file,
# - create an index file object and upload the object to the container
# - create a CNAME record pointing to the CDN URL of the container

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
cdns = pyrax.cloud_dns

# takes a single parameter: container name to create
if len(sys.argv) < 2:
	print 'syntax: {0} <container_name>'.format(sys.argv[0])
        sys.exit(1)
else:
        valid_fqdn = helper.validate_fqdn(sys.argv[1])
        if valid_fqdn:
        	site_cont_name= sys.argv[1]
	else:
                print 'ERROR: the specified name contains invalid characters (see: RFC 1123 sec. 2.1)'
                sys.exit(1)

# check for container
cont = helper.act_loop(cf.get_container, site_cont_name)

# make container public, cdn enable container
helper.act_loop(cont.make_public, ttl=1200)

# create an index page for our container
index_page_content = "Welcome to Ryan's test site on the rack cloud CDN!"
obj = helper.act_loop(cf.store_object, site_cont_name, "index.htm", index_page_content)

# enable it to serve an index file,
helper.act_loop(cont.set_web_index_page, 'index.htm')
print 'SUCCESS: uploaded web page to new container..'

# create a CNAME record pointing to the CDN URL of the container
uri = helper.act_loop(str, cont.cdn_uri)
uri_host = uri.split('http://') # parse the hostname from the URI
uri_host = uri_host[1]

# get list of domains on account and use the first one
domains = helper.act_loop(cdns.list, limit=1)
for domain in domains:
        dom = domain
        dom_name = dom.name

# create a cname for the container we created
cname = '{0}.{1}'.format(site_cont_name, dom_name)
recs = [{"type": "CNAME", "name": cname, "data": uri_host, "ttl": 6000}]

# add our CNAME record
helper.act_loop(cdns.add_records, dom, recs)
print 'SUCCESS: created dns record: {0} IN CNAME {1}'.format(uri_host, cname)
