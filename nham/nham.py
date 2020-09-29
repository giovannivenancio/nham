import time
import sys
import signal
import os

from fms import *
from vnfm import *
from sm import *

def exit_handler(signal, frame):
    fms._exit()
    sys.exit(0)

signal.signal(signal.SIGINT, exit_handler)

print "########### DEBUG - PID:", os.getpid()

fms = FaultManagementSystem()
sm = StateManager()
vnfm = VNFManager()

sync_vnfs = []

while True:
    vnf = load_db('vnf')

    #print "sync vnfs: ", sync_vnfs

    for id in vnf:
        if id not in sync_vnfs:
            sm.sync_state(vnf[id])
            sync_vnfs.append(id)

    time.sleep(3)
