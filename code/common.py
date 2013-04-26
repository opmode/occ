#!/usr/bin/env python2.7
# v 1.0
# Ryan Nguyen
""" common helper functions for overused tasks and advanced API error handling """

import os
import re
import sys
import time
import binascii
import pyrax

def act_loop(function, *args, **kwargs):
    """ function to wrap all API requests to consolidate error handling and provide centralized repudiation"""
    delay = 2
    tries = 3
    backoff = 2
    while True:
        try:
            time.sleep(delay)
            if (len(args) >= 1) and (len(kwargs) >= 1):
                return function(*args, **kwargs)
            elif (len(args) >= 1) and (len(kwargs) == 0):
                return function(*args)
            elif (len(args) == 0) and (len(kwargs) >= 1):
                return function(**kwargs)
            else:
                return function()
            break
        except KeyboardInterrupt:
            print 'ERROR: quitting due to CTRL-C'
            sys.exit(1)
        except pyrax.exceptions.NoSuchContainer, e:
            print 'container does not exist, will create container:', args[0]
            cf = pyrax.cloudfiles
            act_loop(cf.create_container, args[0])
        except pyrax.exceptions.OverLimit, e:
            delay *= backoff
            print "%s, Retrying in %d seconds..." % (str(e), delay)
            time.sleep(delay)
            if function.__name__ == 'add_records':
                cdns = pyrax.cloud_dns
                domx = args[0]
                match = args[1][0]['name']
                chk_rec = [rec for rec in act_loop(cdns.list_records, domx) if match == rec.name]
                if len(chk_rec) >= 1:
                    break
        except Exception, e:
            tries -= 1
            delay *= backoff
            print "%s, Retrying in %d seconds..." % (str(e), delay)
            if tries <= 0:
                print 'ERROR: could not complete request, giving up'
                sys.exit(1)
            time.sleep(delay)

def build_servers(queued_servers):
    """ engages RS cloud servers to build out and monitor a provided dictionay (queue) of servers """
    # start build and gather additional information
    cs = pyrax.cloudservers
    for svr in queued_servers:
        print 'creating host:', svr['name']
        server = act_loop(cs.servers.create, svr['name'], svr['os_img_id'], svr['flavor_id'], files=svr['files'])
        svr['id'] = server.id
        svr['net'] = server.networks
        svr['pub'] = None
        svr['priv'] = None
        svr['pass'] = server.adminPass
        svr['completed'] = 'no'
        num_completed_servers = 0
        num_queued_servers = len(queued_servers)
    # monitor the build
    while True:
        print '-------------'
        print 'builds in progress -', disp_time()
        print '-------------'
        print ' '
        for svr in queued_servers:
            id = svr['id']
            name = svr['name']
            pubip = svr['pub']
            server = act_loop(cs.servers.get, id)
            if svr['completed'] == 'y':
                print name, ': build complete'
            else:
                if server.networks:
                    svr['net'] = server.networks
                    svr['priv'] = svr['net']['private'][0]
                    # pub network information is coming back in random order
                    if validate_ipv4(svr['net']['public'][0]):
                        svr['pub'] = svr['net']['public'][0]
                    else:
                        svr['pub'] = svr['net']['public'][1]
                    if server.status == 'ACTIVE':
                        svr['completed'] = 'y'
                        print name, ': build is finishing up..'
                        num_completed_servers += 1
                    else:
                        print '{0}: assigned pub: {1} - building: {2}%'.format(name, pubip, server.progress)
                else:
                    print '{0}: waiting for pub address - building: {1}%'.format(name, server.progress)
        print ' ' # spacer for better formatting
        if num_completed_servers == num_queued_servers:
            return queued_servers
            break

def gen_password(chars):
    """ generates a random password of specified size """
    return binascii.b2a_hex(os.urandom(chars))

def disp_time():
    """ prints the date """
    return time.asctime(time.localtime(time.time()))

def strip_non_numbers(arg):
    """ srips all non numbers from a string """
    return re.sub(r'[^0-9]', '', arg)

def validate_fqdn(host):
    """ determines if provided string is valid hostname """
    return re.match('^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$', host)
        # [0-9]+(?:\.[0-9]+){3}
        # ^([a-zA-Z0-9]{1}([a-zA-Z0-9\-]*))$

def validate_ipv4(address):
    """ determines if provided string is valid IPv4 address """
    return re.match('^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', address)
