#!/usr/bin/env python2.7
# v 1.0
# Ryan Nguyen

# this script performs the following actions: 
# 1. creates a new RS cloud DB instance using specified name
# 2. creates a specified number of databases inside the instance 
# 3. generates a unique username & password for each database

import os
import string
import re
import sys
import time
import pyrax
import common as helper

# preliminary
creds_file = os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(creds_file)
cdb = pyrax.cloud_databases
seconds_before_retrying = 2
prefix = 'testdb'

# take two parameters: 1: an instance name, 2: number of databases to create
if len(sys.argv) < 3:
        print "syntax: {0} <instance name> <qty db's>".format(sys.argv[0])
        sys.exit(1)

db_instance_name = sys.argv[1]
db_count = helper.strip_non_numbers(sys.argv[2])

# ensure that a valid amount of databases are provided or fail
if db_count == '':
	print 'ERROR: you entered an invalid number of databases, please try again with a proper amount'
	sys.exit(1)

db_count = int(db_count)
if (db_count < 1) or (db_count > 50):
	print 'ERROR: you provided either too few (<1) or too many (>50)'
	sys.exit(1)

# search through flavors and get object for the "1GB" one
inst_512 = [flavor for flavor in helper.act_loop(cdb.list_flavors) if "1GB" in flavor.name][0]
# create instance with our flavor 
db_instance = helper.act_loop(cdb.create, db_instance_name, flavor=inst_512.name)
while True:
	db_instance = helper.act_loop(cdb.get, db_instance)
	if db_instance.status == 'ACTIVE':
		print 'instance: {0} has been created!'.format(db_instance.name)
		break
	print 'instance: {0} is still in BUILD status, checking server every {1} seconds until completion..'.format(db_instance.name,seconds_before_retrying)
	time.sleep(seconds_before_retrying)

# queue up a list of db's to build out
create_dbs = []
for n in range (1, db_count+1):
        create_dbs.append(prefix+str(n))

# within our instance
# build out our queue of db's, create a unique user/password for each db and compile this information together for the final report
db_queue = [] 
user_ct = 0
for dbn in create_dbs:
	helper.act_loop(cdb.create_database, db_instance, dbn)
	user_ct += 1
	gen_user_name = '{0}-user{1}'.format(db_instance.name, user_ct)
	gen_user_pass = helper.gen_password(12)
	user = helper.act_loop(db_instance.create_user, name=gen_user_name, password=gen_user_pass, database_names=[dbn])
	data = {'name': dbn, 'user': gen_user_name, 'pass': gen_user_pass }
	db_queue.append(data)

print ' '
print '-------------'
print 'YAY, TIME FOR THE BUILD REPORT..'
print '-------------'
print ' '
# print out the compiled report
for dbs in db_queue:
	print "DBN:", dbs['name']
	print "User:", dbs['user']
	print "Pass:", dbs['pass']
	print '-------------'
	print ' '
