#!/usr/bin/env python
# v 0.0.1
# Ryan Nguyen

# wrapper for RS API challenge

import os
import sys

try:
	os.system('./code/cdb_create_db.py %s %s' % (sys.argv[1], sys.argv[2]))
except:
	os.system('./code/cdb_create_db.py')
