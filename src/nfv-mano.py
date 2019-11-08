#!/usr/bin/env python

import sys

from nfvo import *
from vnfm import *
from vim import *
from nham import *

vim = VirtualizedInfrastructureManager()
vnfm = VNFManager()
nfvo = NFVOrchestrator()

#vnfm.vnf_create(sys.argv[1])
#vnfm.list_vnfs()
#nfvo.sfc_create(3, sys.argv[1])

#nfvo.sfc_delete('HpnpxT7f6f0UtrIM')
nfvo.list_sfcs()
nfvo.purge_sfcs()
nfvo.list_sfcs()
