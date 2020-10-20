import requests
import time
import os
import sys

sys.path.append("../nfv-mano/")

from utils import *

VIM_URL = 'http://0.0.0.0:9000/vim/'
VNF_URL = 'http://0.0.0.0:9001/vnf/'
SFC_URL = 'http://0.0.0.0:9002/sfc/'

class FaultManagementSystem():
    """
    Implementation of the Fault Management System. This system comprises:
      - Failure detection;
      - Failure recovery.
    """

    def __init__(self):
        self.devices = {}
        self.update_devices()

    def update_devices(self):
        """Update list of devices to be monitored.
        This function monitors only the master VNFs,
        and not the backups."""

        vnfs = load_db('vnf')

        for vnf_id in vnfs:
            device_id = vnfs[vnf_id]['device_id']
            r = requests.get(VIM_URL + 'show', json={'id': device_id})
            self.devices[device_id] = r.json()

    def monitor(self):
        """Monitor each virtual device and reports if a failure was found."""

        for id in self.devices:
            device = self.devices[id]

            print "checking health of %s %s" % (device['id'], device['ip'])

            # verify if device is up and running and if it is reachable
            # status could be paused because of checkpointing mechanism
            # that pauses the container for a few moments to take the checkpoint.
            status, networking = self.check_health(device['id'], device['ip'])

            if status not in ['running', 'paused'] or not networking:
               print "Fault found on device %s: status = %s networking = %s" % (id, status, networking)
               self.alarm(id)

    def check_health(self, device_id, ip):
        """Check the health of specified device.
        This function is used to verify if a VNF is up and running or is faulty."""

        networking = not os.system("ping -q -c 1 -W 2 %s > /dev/null 2>&1" % ip)
        r = requests.get(VIM_URL + 'status', json={'id': device_id})
        status = r.text
        return (status, networking)

    def alarm(self, device_id):
        """Upon failure, start recovery and reconfiguration."""

        vnfs = load_db('vnf')

        # find the VNF that has a faulty device
        for vnf_id in vnfs:
            if vnfs[vnf_id]['device_id'] == device_id:
                faulty_vnf = vnfs[vnf_id]
                break

        # recovery from failure
        print "recovering VNF"
        runtime = self.recovery(faulty_vnf)

        print "========================================="
        print "Total recovery time: %s" % str(runtime).replace('.', ',')
        print "========================================="

        print "successfully recovered VNF %s" % faulty_vnf['id']

    def recovery(self, faulty_vnf):
        """Recover VNF from fault.
        Recovery methods supported by NHAM are:
        1)    0R: no resiliency; create a new instance, recover state from DB, and reconfigure.
        2) 1R-AS: one replica in standby mode; import last state from DB, and reconfigure.
        3) 1R-AA: one replica in active mode; just reconfiguration.
        4) MR-AA: multiple replicas in active mode; just check if it has any more backups.
        """

        runtime = 0

        recovery_method = faulty_vnf['recovery']['method']

        if recovery_method == '0R':
            # stop and remove "master" VNF
            print "removing faulty virtual device"
            vim.delete_virtual_device(faulty_vnf['device_id'])

            start = time.time()

            image = faulty_vnf['properties']['image']
            num_cpus = faulty_vnf['properties']['num_cpus']
            mem_size = faulty_vnf['properties']['mem_size']

            # create new virtual device for VNF
            print "creating new virtual device"
            r = requests.post(
                VIM_URL + 'create',
                json = {
                    'type': 'container',
                    'image': image,
                    'num_cpus': num_cpus,
                    'mem_size': mem_size
                })

            new_device = r.json()

            print "importing updated state"
            sm.import_vnf_state(destination=new_device, source=faulty_vnf['id'], epoch=None)

            print "reconfiguring"
            self.reconfigure(vim, recovery_method, faulty_vnf, new_device)

            end = time.time()
            runtime += end-start

        elif recovery_method == '1R-AS':
            # stop and remove "master" VNF
            vim.delete_virtual_device(faulty_vnf['device_id'])

            start = time.time()

            backup = faulty_vnf['recovery']['backups'][0]
            print "importing updated state"
            pause_time = sm.import_vnf_state(destination=backup, source=faulty_vnf['id'], epoch=None)
            print "tempo de pausa =", pause_time

            # TODO: create new backup in background

            self.reconfigure(vim, recovery_method, faulty_vnf, None)

            end = time.time()
            runtime += end-start-pause_time

        elif recovery_method == '1R-AA':
            # stop and remove "master" VNF
            print "deleting %s" % faulty_vnf['device_id']
            vim.delete_virtual_device(faulty_vnf['device_id'])

            start = time.time()

            # TODO: create new backup in background

            self.reconfigure(vim, recovery_method, faulty_vnf, None)

            end = time.time()
            runtime += end-start

        elif recovery_method == 'MR-AA':

            start = time.time()

            # reconfigure
            self.reconfigure(vim, recovery_method, faulty_vnf, None)

            end = time.time()
            runtime += end-start

        return runtime

    def reconfigure(self, recovery_method, faulty_vnf, new_device):
        """After fault recovery, reconfigure VNF and SFC."""

        if recovery_method == '0R':
            # update VNF
            faulty_vnf['short_id'] = new_device['short_id']
            faulty_vnf['device_id'] = new_device['id']
            faulty_vnf['ip'] = new_device['ip']

            update_db('replace', 'vnf', faulty_vnf['id'], faulty_vnf)

        elif recovery_method in ['1R-AS', '1R-AA']:
            # replace VNF backup device
            backup_device = faulty_vnf['recovery']['backups'][0]

            # remove used backup
            del faulty_vnf['recovery']['backups'][0]

            faulty_vnf['short_id'] = backup_device['short_id']
            faulty_vnf['device_id'] = backup_device['id']

            if recovery_method == '1R-AS':
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

        elif recovery_method == 'MR-AA':
            backup_device = faulty_vnf['recovery']['backups'][0]
            # remove used backup
            del faulty_vnf['recovery']['backups'][0]
            update_db('replace', 'vnf', faulty_vnf['id'], faulty_vnf)

    def mainloop(self):
        """Periodically monitors each virtual device."""

        while True:
            self.update_devices()
            self.monitor()
            time.sleep(3)

if __name__ == '__main__':
    fms = FaultManagementSystem()
    fms.mainloop()
