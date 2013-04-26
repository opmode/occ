#!/usr/bin/env python2.7
# v 0.0.1
# Ryan Nguyen

# test wrapper for interactive debugging

import os
import string
import re
import sys
import time
import common as helper
import pyrax

# prelimsies
seconds_before_retrying = 5
prefix = 'test'
creds_file = os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(creds_file)
cs = pyrax.cloudservers
clb = pyrax.cloud_loadbalancers
cdns = pyrax.cloud_dns



