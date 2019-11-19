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
                print "Fault found on device %s" % id
                self.alarm(id)

    def update_devices(self):
        """Update list of devices to be monitored."""
        self.devices = load_db('device')

    def check_health(self, device):
        """Check the health of specified device.
        This function is used to verify if a VNF is up and running or is faulty."""

        return not os.system("ping -q -c 1 -W 2 %s > /dev/null 2>&1" % device['ip'])

    def alarm(self, device_id):
        """Upon failure, start fault isolation, recovery and reconfiguration."""

        vnfs = load_db('vnf')
        sfcs = load_db('sfc')

        # find the VNF that has a faulty device
        for vnf_id in vnfs:
            if vnfs[vnf_id]['device_id'] == device_id:
                faulty_vnf = vnfs[vnf_id]
                break

        # find the SFC that has the faulty VNF
        for sfc_id in sfcs:
            if faulty_vnf['id'] in sfcs[sfc_id]['chain']:
                faulty_sfc = sfcs[sfc_id]
                break

        # isolate fault
        print "isolating fault of VNF %s in the SFC %s" % (faulty_vnf['id'], faulty_sfc['id'])
        self.isolation(faulty_sfc, faulty_vnf)

        # recovery from fault
        #self.recovery()

        # reconfigure SFC
        #self.reconfigure()

    def isolation(self, faulty_sfc, faulty_vnf):
        """Isolate the fault of a VNF in the SFC.
        All communications of the previous and the next VNF of the faulty VNF are disabled.
        """

        from vim import VirtualizedInfrastructureManager
        vim = VirtualizedInfrastructureManager()

        vnfs = load_db('vnf')

        # if a SFC has only one SFC, there is no need to isolate
        if len(faulty_sfc['chain']) == 1:
            return

        # locate the fault position in the chain
        chain_fault_position = faulty_sfc['chain'].index(faulty_vnf['id'])

        if chain_fault_position == 0:
            # its the first VNF in the chain, disable the next
            next_vnf_id = faulty_sfc['chain'][chain_fault_position+1]
            next_device_id = vnfs[next_vnf_id]['device_id']
            input_drop = 'iptables -I INPUT -s %s -j DROP' % faulty_vnf['ip']

            print "disabling next VNF %s" % next_vnf_id
            #print "docker exec [%s] [%s]" % (next_device_id, input_drop)
            vim.exec_cmd(next_device_id, input_drop)

        elif chain_fault_position == len(faulty_sfc['chain'])-1:
            # its the last VNF in the chain, disable the previous
            previous_vnf_id = faulty_sfc['chain'][chain_fault_position-1]
            previous_device_id = vnfs[previous_vnf_id]['device_id']
            forward_drop = 'iptables -I INPUT -d %s -j DROP' % faulty_vnf['ip']
            nat_drop = 'iptables -t nat -D PREROUTING -p icmp -j DNAT --to-destination %s' % faulty_vnf['ip']

            print "disabling previous VNF %s" % previous_vnf_id
            vim.exec_cmd(previous_device_id, forward_drop)
            vim.exec_cmd(previous_device_id, nat_drop)

        else:
            # disable the previous and the next
            next_vnf_id = faulty_sfc['chain'][chain_fault_position+1]
            next_device_id = vnfs[next_vnf_id]['device_id']
            input_drop = 'iptables -I INPUT -s %s -j DROP' % faulty_vnf['ip']

            previous_vnf_id = faulty_sfc['chain'][chain_fault_position-1]
            previous_device_id = vnfs[previous_vnf_id]['device_id']
            forward_drop = 'iptables -I INPUT -d %s -j DROP' % faulty_vnf['ip']
            nat_drop = 'iptables -t nat -D PREROUTING -p icmp -j DNAT --to-destination %s' % faulty_vnf['ip']

            print "disabling next VNF %s and previous VNF %s" % (next_vnf_id, previous_vnf_id)
            #print "docker exec [%s] [%s]" % (next_device_id, input_drop)
            vim.exec_cmd(next_device_id, input_drop)

            #print "docker exec [%s] [%s]" % (previous_device_id, forward_drop)
            #print "docker exec [%s] [%s]" % (previous_device_id, nat_drop)
            vim.exec_cmd(previous_device_id, forward_drop)
            vim.exec_cmd(previous_device_id, nat_drop)

    def recovery(self):
        """."""
        # define os tipos de recovery
        # se for 1: stop/rm (master); create; reconfigure
        # se for 2: stop/rm (master); reconfigure
        # se for 3, 4: reconfigure
        pass

    def reconfiguration(self):
        """."""
        pass

    def mainloop(self):
        """Periodically monitors each virtual device."""

        while True:
            print "Monitoring..."
            self.update_devices()
            self.monitor()
            time.sleep(3)
