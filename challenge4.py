#!/usr/bin/env python
# v 0.0.1
# Ryan Nguyen

# wrapper for RS API challenge
import os
import sys
"""
import pyrax

# prelimz
creds_file = os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(creds_file)
cdns = pyrax.cloud_dns

domain = cdns.list()[0].name
"""
try:
	os.system('./code/cdns_create_a.py {0} {1} {2}'.format(sys.argv[1], sys.argv[2], sys.argv[3]))
except Exception as e:
	os.system('./code/cdns_create_a.py')
