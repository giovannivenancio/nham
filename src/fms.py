import time
import os
import sys

from utils import *
from multiprocessing import Process

class FaultManagementSystem():
    """
    Implementation of the Fault Management System. This system comprises:

    1. Failure detection;
    2. Failure isolation;
    3. Failure recovery.
    """

    def __init__(self):
        self.update_devices()
        self.fd = Process(target=self.mainloop)
        self.fd.start()

    def _exit(self):
        print "EXITING FD"
        self.fd.terminate()

    def monitor(self):
        """Monitor each virtual device and reports if a failure was found."""

        for id in self.devices:
            device = self.devices[id]
            health = self.check_health(device)
            print "checking health of %s: %s" % (device['ip'], health)

            if not health:
                self.alarm()

    def update_devices(self):
        """Update list of devices to be monitored."""
        self.devices = load_db('device')

    def check_health(self, device):
        """Check the health of specified device.
        This function is used to verify if a VNF is up and running or is faulty."""
        return not os.system("ping -q -c 1 -W 2 %s > /dev/null 2>&1" % device['ip'])

    def alarm(self):
        """."""
        pass

    def isolation(self):
        """."""
        #iptables -I FORWARD -d 172.17.0.3 -j DROP
        #iptables -D FORWARD -d 172.17.0.3 -j DROP
        pass

    def recovery(self):
        """."""
        pass

    def mainloop(self):
        """."""

        while True:
            print "Monitoring..."
            self.update_devices()
            self.monitor()
            time.sleep(1)
