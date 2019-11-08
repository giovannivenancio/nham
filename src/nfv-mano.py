#!/usr/bin/env python

import sys

from nfvo import *
from vnfm import *
from vim import *
from nham import *

vim = VirtualizedInfrastructureManager()
vnfm = VNFManager()
nfvo = NFVOrchestrator()

action = sys.argv[1]

if action == 'create':
    type = sys.argv[2]

    if type == 'sfc':
        num_vnfs = int(sys.argv[3])
        vnfd = sys.argv[4]

        nfvo.create_sfc(num_vnfs, vnfd)

elif action == 'list':
    type = sys.argv[2]

    if type == 'sfc':
        nfvo.list_sfcs()
    elif type == 'vnf':
        vnfm.list_vnfs()
    elif type == 'device':
        vim.list_virtual_devices()

elif action == 'delete':
    type = sys.argv[2]
    id = sys.argv[3]

    if type == 'sfc':
        nfvo.delete_sfc(id)
    elif type == 'vnf':
        vnfm.delete_vnf(id)
    elif type == 'device':
        vim.delete_virtual_device(id)

elif action == 'purge':
    type = sys.argv[2]

    if type == 'sfc':
        nfvo.purge_sfcs()
    elif type == 'vnf':
        vnfm.purge_vnfs()
    elif type == 'device':
        vim.purge_devices()

elif action == '-h' or action == '--help':
    print "Usage:"
    print "sys.argv[0] create [sfc|vnf|device] <>.... #TODO"
