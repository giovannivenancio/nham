import time
import os
import sys

from vim import *
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
        self._vim = VirtualizedInfrastructureManager()
        self.update_devices()
        self.fd = Process(target=self.mainloop)
        self.fd.start()

    def _exit(self):
        self.fd.terminate()

    def monitor(self):
        """Monitor each virtual device and reports if a failure was found."""

        for id in self.devices:
            device = self.devices[id]
            status, networking = self.check_health(device['id'], device['ip'])

            # verify if device is up and running and if it is reachable
            # status could be paused because of checkpointing mechanism
            # that pauses the container for a few moments to take the snapshot.
            print "checking health of %s %s" % (device['id'], device['ip'])
            if status not in ['running', 'paused'] or not networking:
               print "Fault found on device %s: status = %s networking = %s" % (id, status, networking)
               self.alarm(id)

    def update_devices(self):
        """Update list of devices to be monitored.
        This function monitors only the master VNFs,
        and not the backups."""

        self.devices = {}

        vnfs = load_db('vnf')
        recovering = load_db('recovering')

        for vnf_id in vnfs:
            if vnf_id not in recovering:
                device_id = vnfs[vnf_id]['device_id']
                self.devices[device_id] = self._vim.get_virtual_device(device_id)

    def check_health(self, device_id, ip):
        """Check the health of specified device.
        This function is used to verify if a VNF is up and running or is faulty."""

        networking = not os.system("ping -q -c 1 -W 2 %s > /dev/null 2>&1" % ip)
        status = self._vim.get_status(device_id)
        return (status, networking)

    def alarm(self, device_id):
        """Upon failure, start fault isolation, recovery and reconfiguration."""

        from vim import VirtualizedInfrastructureManager
        from sm import StateManager

        vim = VirtualizedInfrastructureManager()
        sm = StateManager()

        vnfs = load_db('vnf')
        sfcs = load_db('sfc')

        # find the VNF that has a faulty device
        for vnf_id in vnfs:
            if vnfs[vnf_id]['device_id'] == device_id:
                faulty_vnf = vnfs[vnf_id]
                break

        insert_db('recovering', faulty_vnf['id'], {'status': "recovering"})

        # find the SFC that has the faulty VNF
        for sfc_id in sfcs:
            if faulty_vnf['id'] in sfcs[sfc_id]['chain']:
                faulty_sfc = sfcs[sfc_id]
                break

        # isolate fault
        print "isolating fault of VNF %s in the SFC %s" % (faulty_vnf['id'], faulty_sfc['id'])
        self.isolation(vim, faulty_sfc, faulty_vnf)

        # recovery from fault
        print "recovering VNF"
        self.recovery(sm, vim, faulty_vnf)

        print "successfully recovered VNF %s" % faulty_vnf['id']
        remove_db('recovering', faulty_vnf['id'])

    def isolation(self, vim, faulty_sfc, faulty_vnf):
        """Isolate the fault of a VNF in the SFC.
        All communications of the previous and the next VNF of the faulty VNF are disabled.
        """

        vnfs = load_db('vnf')

        # if a SFC has only one SFC, there is no need to isolate
        if len(faulty_sfc['chain']) == 1:
            print "SFC has only one VNF, no need to isolate"
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

    def recovery(self, sm, vim, faulty_vnf):
        """Recover VNF from fault."""

        recovery_method = faulty_vnf['recovery']['method']

        # VNF doesn't have a backup, create a
        # new instance and import state
        if recovery_method == None:
            # stop and remove "master" VNF
            vim.delete_virtual_device(faulty_vnf['device_id'])

            image = faulty_vnf['properties']['image']
            num_cpus = faulty_vnf['properties']['num_cpus']
            mem_size = faulty_vnf['properties']['mem_size']

            # create new virtual device for VNF
            new_device = vim.create_virtual_device(
                'container',
                image,
                num_cpus,
                mem_size)

            sm.import_vnf_state(destination=new_device, source=faulty_vnf['id'], epoch=None)

            self.reconfigure(vim, recovery_method, faulty_vnf, new_device)

        # VNF has a standby backup, remove the
        # faulty VNF and import state
        elif recovery_method == 'active-standby':
            # stop and remove "master" VNF
            vim.delete_virtual_device(faulty_vnf['device_id'])

            backup = faulty_vnf['recovery']['backups'][0]
            sm.import_vnf_state(destination=backup, source=faulty_vnf['id'], epoch=None)

            # TODO: create new backup in background

            self.reconfigure(vim, recovery_method, faulty_vnf, None)

        # VNF has an active backup, remove the
        # faulty VNF and create a new backup
        elif recovery_method == 'active-active':
            # stop and remove "master" VNF
            print "deleting %s" % faulty_vnf['device_id']
            vim.delete_virtual_device(faulty_vnf['device_id'])

            # TODO: create new backup in background

            self.reconfigure(vim, recovery_method, faulty_vnf, None)

        elif recovery_method == 'multisync':
            # reconfigure
            pass

    def reconfigure(self, vim, recovery_method, faulty_vnf, new_device):
        """After fault recovery, reconfigure VNF and SFC."""

        if recovery_method == None:
            # update VNF
            faulty_vnf['short_id'] = new_device['short_id']
            faulty_vnf['device_id'] = new_device['id']
            faulty_vnf['ip'] = new_device['ip']

            update_db('replace', 'vnf', faulty_vnf['id'], faulty_vnf)

        elif recovery_method == 'active-standby' or recovery_method == 'active-active':
            # replace VNF backup device
            backup_device = faulty_vnf['recovery']['backups'][0]

            # remove used backup
            del faulty_vnf['recovery']['backups'][0]

            faulty_vnf['short_id'] = backup_device['short_id']
            faulty_vnf['device_id'] = backup_device['id']

            if recovery_method == 'active-standby':
                faulty_vnf['ip'] = vim.get_updated_ip(backup_device['id'])
                backup_device['ip'] = faulty_vnf['ip']

                # docker pulls an IP from the pool, so
                # update device ID with new IP
                update_db('replace', 'device', backup_device['id'], backup_device)
            else:
                faulty_vnf['ip'] = vim.get_updated_ip(backup_device['id'])

            # TODO: insert new backup --> should be done asynchronously
            #faulty_vnf['recovery']['backups'].append(new_device)

            update_db('replace', 'vnf', faulty_vnf['id'], faulty_vnf)

            while True:
                print "checking on %s %s" % (faulty_vnf['device_id'], faulty_vnf['ip'])
                status, networking = self.check_health(faulty_vnf['device_id'], faulty_vnf['ip'])
                print "waiting for VNF to boot: status = %s networking = %s" % (status, networking)

                if status in ['running', 'paused'] and networking:
                    print "VNF boot: OK"
                    break

        elif recovery_method == 'multisync':
            pass

    def mainloop(self):
        """Periodically monitors each virtual device."""

        while True:
            self.update_devices()
            self.monitor()
            time.sleep(3)
