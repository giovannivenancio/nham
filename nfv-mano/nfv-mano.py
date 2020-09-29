#!/usr/bin/env python

"""
This is a general purpose NFV-MANO. It should be used for high-level operations, such as create, delete, and list VNFs and SFC.
"""

import sys
import requests

commands = [
    'VNF create',
    'VNF list',
    'VNF show',
    'VNF status',
    'VNF delete',
    'VNF stop',
    'VNF purge',

]

url = 'http://0.0.0.0:9000/vim/'

d = {
    'type': 'container',
    'image': 'ubuntu',
    'num_cpus': 1,
    'mem_size': '256MB'
}
# r = requests.post(url + 'create', json=d)
# print r

r = requests.get(url + 'list')
print r.text
#
d = {
    'id': 'd0e65619fc85ce7d6fa44120c999893aeb894f8597eca2da2ba9d8549cb38d04'
}
# r = requests.get(url + 'show', json=d)
# print r.text

# r = requests.get(url + 'status', json=d)
# print r.text
#
# r = requests.delete(url + 'delete', json=d)
# print r.text

r = requests.delete(url + 'purge')
print r.text


# from nfvo import *
# from vnfm import *
# from vim import *
# # from sm import *
#
# vim = VirtualizedInfrastructureManager()
# vnfm = VNFManager()
# nfvo = NFVOrchestrator()
#
# if __name__ == "__main__":
#
#     action = sys.argv[1]
#
#     if action == 'create':
#         type = sys.argv[2]
#
#         if type == 'sfc':
#             num_vnfs = int(sys.argv[3])
#             vnfd = sys.argv[4]
#
#             nfvo.create_sfc(num_vnfs, vnfd)
#
#     elif action == 'list':
#         type = sys.argv[2]
#
#         if type == 'sfc':
#             nfvo.list_sfcs()
#         elif type == 'vnf':
#             vnfm.list_vnfs()
#         elif type == 'device':
#             vim.list_virtual_devices()
#         elif type == 'state':
#             sm.list_states()
#
#     elif action == 'delete':
#         type = sys.argv[2]
#         id = sys.argv[3]
#
#         if type == 'sfc':
#             nfvo.delete_sfc(id)
#         elif type == 'vnf':
#             vnfm.delete_vnf(id)
#         elif type == 'device':
#             vim.delete_virtual_device(id)
#
#     elif action == 'purge':
#         type = sys.argv[2]
#
#         if type == 'sfc':
#             nfvo.purge_sfcs()
#         elif type == 'vnf':
#             vnfm.purge_vnfs()
#         elif type == 'device':
#             vim.purge_devices()
#
#     elif action == '-h' or action == '--help':
#         print "Usage:"
#         print "sys.argv[0] create [sfc|vnf|device] <>.... #TODO"
