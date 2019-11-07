#!/usr/bin/env python

import sys

from nfvo import *
from vnfm import *
from vim import *
from nham import *

vim = VirtualizedInfrastructureManager()
vnfm = VNFManager()

type = 'container'
image = 'ubuntu'
cpu_count = int('2')
mem_limit = '512MB'

#vnfm.vnf_create(sys.argv[1])
#vnfm.vnf_create(sys.argv[1])
#vnfm.vnf_create(sys.argv[1])
#vim.list_virtual_devices()
#vim.purge_devices()
