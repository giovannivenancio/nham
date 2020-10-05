#! /usr/bin/env python3

"""
implementation of the SFF (Service Function Forwarder).
Receives an SFC ID and create links between each of the chains' VNFs.
"""

import sys, time
from socket import *

port = 10000
count = 10000
BUFSIZE = 8192

if __name__ == "__main__":
    sfc_id = sys.argv[1]

    # get VNFs IPs

    # for each VNF: create connections and put in a dict (or list?)

    # ==== sfc communication ====
    # for each vnf in the chain: send, receive the response, forward to the next
    # change enabler behaviour to send back the data
    # compute SFC throughput


    # host = sys.argv[3]
    # if len(sys.argv) > 4:
    #     port = eval(sys.argv[4])
    # else:
    #     port = MY_PORT
    # testdata = "x" * (BUFSIZE-1) + "\n"
    # t1 = time.time()
    # s = socket(AF_INET, SOCK_STREAM)
    # t2 = time.time()
    # s.connect((host, port))
    # t3 = time.time()
    # i = 0
    # while i < count:
    #     i = i+1
    #     s.send(testdata)
    # s.shutdown(1) # Send EOF
    # t4 = time.time()
    # data = s.recv(BUFSIZE)
    # t5 = time.time()
    #
    # throughput_k = round((BUFSIZE*count*0.001) / (t5-t1), 3) # K/sec
    # throughput_m = throughput_k/1000 # M/sec
    # throughput_g = throughput_m/1000 # G/sec
    #
    # print("Throughput (KBps): %f" % throughput_k)
    # print("Throughput (MBps): %f" % throughput_m)
    # print("Throughput (GBps): %f" % throughput_g)
