#!/usr/bin/env python2.7
# v 1.0
# Ryan Nguyen

# create an A record with specified domain, hostname, and IP 

import sys
import os
import re
import time
import common as helper
import pyrax

# preliminary
creds_file = os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(creds_file)
cdns = pyrax.cloud_dns

# take three parameters: 1: your hosted domain 2: a valid hostname (e.g.: www), 3: a valid IPv4 address
if len(sys.argv) < 3:
        print '{0}: <domain> <hostname> <ipv4address>'.format(sys.argv[0])
        sys.exit(1)

valid_fqdn = helper.validate_fqdn(sys.argv[1])
valid_host = helper.validate_fqdn(sys.argv[2])
valid_ipv4 = helper.validate_ipv4(sys.argv[3])

# use helper function to ensure that the specified domain is valid
if valid_fqdn:
	valid_fqdn = sys.argv[1]
else:
        print 'ERROR: invalid characters in your FQDN'
        sys.exit(1)

# use helper function to ensure that the specified hostname is valid
if valid_host:
	valid_host = sys.argv[2]
	print 'validated host:', valid_host, 'successfully'
else:
        print 'ERROR: invalid hostname'
        sys.exit(1)

# use helper function to ensure that the specified ipv4 address is valid
if valid_ipv4:
	valid_ipv4 = sys.argv[3]
	print 'validated IPv4:', valid_ipv4, 'successfully'
else:
        print 'ERROR: invalid ipv4 address'
        sys.exit(1)

# retrieve a list of all domains on this cloud account, limit result to a specified domain, retrieve domain object 
get_domain = [dom for dom in helper.act_loop(cdns.list) if valid_fqdn == dom.name]
if len(get_domain) == 1:
	domain = get_domain[0]
    print 'validated domain: %s successfully' % domain
else:
	print 'ERROR:', valid_fqdn, 'does not exist on your account'
	sys.exit(1)

# format the subdomain record using the specified hostname
subdomain = '{0}.{1}'.format(valid_host, domain.name)
# create a record using dict
records = [{"type": "A", "name": subdomain, "data": valid_ipv4, "ttl": 300}]
print 'adding A record for:', subdomain

helper.act_loop(cdns.add_records, domain, records)
print 'created dns record: {0} -> {1} on domain: {2}'.format(valid_host, valid_ipv4, domain.name)
