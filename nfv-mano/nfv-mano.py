#!/usr/bin/env python

"""
This is a general purpose NFV-MANO. It should be used for high-level operations of VIM, VNFM, and NFVO.
"""

import os
import sys
import requests

VIM_URL = 'http://0.0.0.0:9000/vim/'
VNF_URL = 'http://0.0.0.0:9001/vnf/'
SFC_URL = 'http://0.0.0.0:9002/sfc/'

os.system('clear')

while True:
    print "1. VIM create"
    print "2. VIM list"
    print "3. VIM show"
    print "4. VIM status"
    print "5. VIM delete"
    print "6. VIM stop"
    print "7. VIM purge"
    print ""
    print "8. VNF create"
    print "9. VNF list"
    print "10. VNF show"
    print "11. VNF delete"
    print "12. VNF stop"
    print "13. VNF purge"
    print ""
    print "14. SFC create"
    print "15. SFC list"
    print "16. SFC show"
    print "17. SFC delete"
    print "18. SFC stop"
    print "19. SFC purge"
    print ""
    print "20. Reset DB"
    print "21. Exit"

    opt = input("> ")

    if opt == 1:
        print "----------------"
        print "VIM CREATE"
        print "----------------\n"

        r = requests.post(VIM_URL + 'create', json={'type': 'container', 'image': 'ubuntu', 'num_cpus': 1, 'mem_size': '256MB'})
        print r.text

    elif opt == 2:
        print "----------------"
        print "VIM LIST"
        print "----------------\n"

        r = requests.get(VIM_URL + 'list')
        print r.text

    elif opt == 3:
        print "----------------"
        print "VIM SHOW"
        print "----------------\n"

        vim_id = raw_input("> ")

        r = requests.get(VIM_URL + 'show', json={'id': vim_id})
        print "\n", r.json(), "\n"

    elif opt == 4:
        print "----------------"
        print "VIM STATUS"
        print "----------------\n"

        vim_id = raw_input("> ")

        r = requests.get(VIM_URL + 'status', json={'id': vim_id})
        print "\n", r.text, "\n"

    elif opt == 5:
        print "----------------"
        print "VIM DELETE"
        print "----------------\n"

        vim_id = raw_input("> ")

        r = requests.delete(VIM_URL + 'delete', json={'id': vim_id})
        print "\n", r.text, "\n"

    elif opt == 6:
        print "----------------"
        print "VIM STOP"
        print "----------------\n"

        vim_id = raw_input("> ")

        r = requests.post(VIM_URL + 'stop', json={'id': vim_id})
        print "\n", r.text, "\n"

    elif opt == 7:
        print "----------------"
        print "VIM PURGE"
        print "----------------\n"

        r = requests.delete(VIM_URL + 'purge')
        print "\n", r.text, "\n"

    elif opt == 8:
        print "----------------"
        print "VNF CREATE"
        print "----------------\n"

        vnfd_file = '../vnfd.yaml'
        r = requests.post(VNF_URL + 'create', json={'vnfd_file': vnfd_file})
        print "\n", r.json(), "\n"

    elif opt == 9:
        print "----------------"
        print "VNF LIST"
        print "----------------\n"

        r = requests.get(VNF_URL + 'list')
        print "\n", r.text, "\n"

    elif opt == 10:
        print "----------------"
        print "VNF SHOW"
        print "----------------\n"

        vnf_id = raw_input("> ")

        r = requests.get(VNF_URL + 'show', json={'vnf_id': vnf_id})
        print "\n", r.json(), "\n"

    elif opt == 11:
        print "----------------"
        print "VNF DELETE"
        print "----------------\n"

        vnf_id = raw_input("> ")

        r = requests.delete(VNF_URL + 'delete', json={'vnf_id': vnf_id})
        print "\n", r.text, "\n"

    elif opt == 12:
        print "----------------"
        print "VNF STOP"
        print "----------------\n"

        vnf_id = raw_input("> ")

        r = requests.post(VNF_URL + 'stop', json={'vnf_id': vnf_id})
        print "\n", r.text, "\n"

    elif opt == 13:
        print "----------------"
        print "VNF PURGE"
        print "----------------\n"

        r = requests.delete(VNF_URL + 'purge')
        print "\n", r.text, "\n"

    elif opt == 14:
        print "----------------"
        print "SFC CREATE"
        print "----------------\n"

    elif opt == 15:
        print "----------------"
        print "SFC LIST"
        print "----------------\n"

    elif opt == 16:
        print "----------------"
        print "SFC SHOW"
        print "----------------\n"

    elif opt == 17:
        print "----------------"
        print "SFC DELETE"
        print "----------------\n"

    elif opt == 18:
        print "----------------"
        print "SFC PURGE"
        print "----------------\n"

    elif opt == 19:
        print "----------------"
        print "RESET DB"
        print "----------------\n"

    elif opt == 20:
        exit()
