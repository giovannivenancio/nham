from __future__ import division

import psutil
import sys
import time
import signal

def exit_handler(signal, frame):
    print "Average CPU usage:", sum(cpu_history)/len(cpu_history)
    print "Average memory usage:", sum(mem_history)/len(mem_history)
    sys.exit(0)

signal.signal(signal.SIGINT, exit_handler)

pid = int(sys.argv[1])

cpu_history = []
mem_history = []

p = psutil.Process(pid)

while True:
    cpu_usage = int(p.cpu_percent())
    memory_usage = (p.memory_info()[0]/2.**30)*1000
    print "CPU:", cpu_usage
    print "memory:", memory_usage
    cpu_history.append(cpu_usage)
    mem_history.append(memory_usage)
    time.sleep(0.5)
