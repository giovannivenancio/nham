import sys
import time
import os
from multiprocessing import Process
from subprocess import check_output, Popen

from fcntl import flock, lockf, LOCK_UN, LOCK_SH, LOCK_EX, LOCK_NB


# def child():
#    print('\nA new child ',  os.getpid())
#    cmd = Popen(['python', 'dummy.py', '&'], shell=True)
#    #os._exit(0)
#    time.sleep(1000)



ns_last_pid = open('/proc/sys/kernel/ns_last_pid', 'w+', buffering=0)
lockf(ns_last_pid, LOCK_EX | LOCK_NB )

ns_last_pid.write(sys.argv[1])

pid = os.fork()
if pid == 0: # new process
    os.system("python dummy_disk.py &")

lockf(ns_last_pid, LOCK_UN)
ns_last_pid.close()

exit()

# child_proc = Process(target=child)
# child_proc.daemon = True
# child_proc.start()


#time.sleep(100)
