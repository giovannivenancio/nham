import time
import sys

from fms import *

import signal

def exit_handler(signal, frame):
    print "EXITING NHAM"
    fms._exit()
    sys.exit(0)

signal.signal(signal.SIGINT, exit_handler)

fms = FaultManagementSystem()

while True:
    #print "doing something else"
    time.sleep(1)
