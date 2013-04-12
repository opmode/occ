#!/usr/bin/env python
# v 0.0.1
# Ryan Nguyen

# wrapper for RS API challenge

import os
import sys

try:
	os.system('./code/cdns_create_a.py %s %s %s' % (sys.argv[1], sys.argv[2], sys.argv[3]))
except:
	os.system('./code/cdns_create_a.py')
