import time
import sys
import signal

from fms import *
from vnfm import *
from sm import *

def exit_handler(signal, frame):
    fms._exit()
    sys.exit(0)

signal.signal(signal.SIGINT, exit_handler)

fms = FaultManagementSystem()
sm = StateManager()

sync_vnfs = []

while True:
    vnf = load_db('vnf')

    print "sync vnfs: ", sync_vnfs

    for id in vnf:
        if id not in sync_vnfs:
            sm.sync_state(vnf[id])
            sync_vnfs.append(id)

    time.sleep(3)
