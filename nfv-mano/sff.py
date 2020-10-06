#! /usr/bin/env python

"""
implementation of the SFF (Service Function Forwarder).
Receives an SFC ID and create links between each of the chains' VNFs.
"""

import requests
import sys, time
from socket import *

VNF_URL = 'http://0.0.0.0:9001/vnf/'
SFC_URL = 'http://0.0.0.0:9002/sfc/'

port = 10000
count = 10000
BUFSIZE = 8192
data = "x" * (BUFSIZE-1) + "\n"

sfp = [] # Service Function Path

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: %s <sfc_id>" % sys.argv[0]
        exit()

    sfc_id = sys.argv[1]

    r = requests.get(SFC_URL + 'show', json={'sfc_id': sfc_id})
    chain = r.json()['chain']

    # Create links between each VNF of the chain
    for vnf in chain:
        r = requests.get(VNF_URL + 'show', json={'vnf_id': vnf})
        vnf_host = r.json()['ip']

        print "Connecting with ", vnf_host
        vnf_conn = socket(AF_INET, SOCK_STREAM)
        vnf_conn.connect((vnf_host, port))

        sfp.append(vnf_conn)

        vnf_conn = None

    # Starts measuring the time for the packets to traverse the entire SFC chain
    t1 = time.time()

    # Perform the SFP forwarding
    for vnf in sfp:
        # send data to VNF
        i = 0
        while i < count:
            i += 1
            vnf.send(data)
            data = vnf.recv(BUFSIZE)

        vnf.shutdown(1)

    t2 = time.time()

    # Compute SFC throughput

    throughput_KB = round((BUFSIZE*count*0.001) / (t2 - t1), 3) # K/sec
    throughput_MB = throughput_KB/1000 # M/sec
    throughput_GB = throughput_MB/1000 # G/sec

    throughput_Kb = throughput_KB * 8
    throughput_Mb = throughput_MB * 8
    throughput_Gb = throughput_GB * 8

    print "\nThroughput: %f Mbps" % throughput_Mb
