#!/usr/bin/env python2.7
# v 1.0 
# Ryan Nguyen

# upload a specified directory to a Cloud Files container
# this script will automatically flatten and rename any nested folders and files accordingly
# todo: implement an option to not overwrite files

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

# take a single argument: a valid folder to upload to cloud files
if len(sys.argv)<2:
	print 'ERROR: ohai! please specify a directory to upload'
	sys.exit(1)
else:
        local_dir_raw = sys.argv[1]
	# test for folder
	try:
		os.chdir(local_dir_raw)
	except OSError:
	        print 'ERROR: the resource:', local_dir_raw, 'is not a valid directory'
		sys.exit(1)
	local_dir_cwd = os.getcwd()
	local_dir_abs = os.path.abspath(local_dir_raw)
	local_dir_relpath = os.path.relpath(local_dir_cwd)
	local_dir_name = os.path.basename(local_dir_abs)

# check for container, create one if it does not exist in CF
cont = helper.act_loop(cf.get_container, local_dir_name)

# get a list of local files, perserve nested structure in filename
local_files = {}
for dir, subdir, files in os.walk(local_dir_relpath):
	dir = str.split(dir, '/')
	dir[0] = ''
	if dir != []:
		fol = '/'.join(dir)
	for file in files:
		name = '{0}/{1}'.format(fol, file)
		path = '{0}{1}'.format(local_dir_cwd, name)
		name = name[1:]
		local_files[name] = path
"""
sys.exit(0)
print local_files
"""

# get a list of remote files and convert into a single list
remote_files = []
remote_objects= cont.get_objects()
for rem_obj in remote_objects:
    remote_files.append(rem_obj.name)
#files_not_on_server = list(set(local_files).difference(set(remote_files)))

# this filters out any files that already exist in the container, so we can warn before overwriting
duplicate_files = list(set(remote_files) & set(local_files))

# this will allow us to pull out any 'skipped' files in case user does not wish to upload duplicates
upload_files = local_files

if len(duplicate_files) > 0:
	l = len(duplicate_files)
	# warn if overwriting any files
	print 'WARNING: would you like to override the following', l, 'files that exist on the system already:'
	for file in duplicate_files:
		print file

print '----------------'
print ' UPLOADING '
print '----------------'
for file,path in upload_files.items():
	print 'uploading file:', file 
	chksum = pyrax.utils.get_checksum(path)
	obj = helper.act_loop(cf.upload_file, cont, path, file, etag=chksum)
