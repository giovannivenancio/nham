import requests
import time
import os
import sys

sys.path.append("../nfv-mano/")

from utils import *

VIM_URL = 'http://0.0.0.0:9000/vim/'
VNF_URL = 'http://0.0.0.0:9001/vnf/'
SFC_URL = 'http://0.0.0.0:9002/sfc/'
SM_URL  = 'http://0.0.0.0:9003/state/'

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

        fault = False

        for id in self.devices:
            device = self.devices[id]

            # verify if device is (i) up and running and; (ii) if it is reachable
            status, networking = self.check_health(device['id'], device['ip'])

            if status in ['paused', 'exited', 'dead'] or not networking:
               print "Fault found on device %s: status = %s networking = %s" % (id, status, networking)
               fault = True
               break

        if fault:
            self.alarm(id)
            del self.devices[id]

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

        # locate VNF that has a faulty device
        faulty_vnf = None
        for vnf_id in vnfs:
            if vnfs[vnf_id]['device_id'] == device_id:
                faulty_vnf = vnfs[vnf_id]
                break

        if not faulty_vnf:
            return "VNF not found!"

        # recovery from failure
        recovery_time = self.recovery(faulty_vnf)
        recovery_time = "%s\n" % str(recovery_time).replace('.', ',')

        with open('../eval/recovery.log', 'a') as f:
            f.write(recovery_time)

    def remove_async(self, faulty_device_id):
        """Remove faulty virtual device.
        Doing it asynchronously, since removing a container consumes a lot of time.
        """

        try:
            requests.delete(VIM_URL + 'delete', json={'id': faulty_device_id})
        except requests.exceptions.ReadTimeout:
            pass

    def recovery(self, faulty_vnf):
        """Recover VNF from fault.
        Recovery methods supported by NHAM are:
        1)    0R: no resiliency; create a new instance, recover state from DB, and reconfigure.
        2) 1R-AS: one replica in standby mode; import last state from DB, and reconfigure.
        3) 1R-AA: one replica in active mode; just reconfiguration.
        4) MR-AA: multiple replicas in active mode; just check if it has any more backups.
        """

        recovery_method = faulty_vnf['recovery']['method']

        # asynchronously remove faulty virtual device
        self.remove_async(faulty_vnf['device_id'])

        # remove corresponding process responsible for synchronizing the VNF
        # MR-AA has other replicas to synchronize, doesn't need to restart
        if recovery_method in ['0R', '1R-AS', '1R-AA']:
            requests.post(SM_URL + 'desync', json={'id': faulty_vnf['id']})

        start = time.time()

        if recovery_method == '0R':
            # get virtual device configuration from faulty VNF to create a new virtual device
            image = faulty_vnf['properties']['image']
            num_cpus = faulty_vnf['properties']['num_cpus']
            mem_size = faulty_vnf['properties']['mem_size']

            # create new virtual device for VNF
            r = requests.post(VIM_URL + 'create', json = {
                'type': 'container',
                'image': image,
                'num_cpus': num_cpus,
                'mem_size': mem_size
            })

            new_device = r.json()['device']

            self.reconfigure(recovery_method, faulty_vnf, new_device)

            # TODO: for now, just recreating the sync worker. After worker code rework, send immediately a request
            # to import VNF state
            requests.post(SM_URL + 'sync', json={'id': faulty_vnf['id']})

            end = time.time()

        elif recovery_method == '1R-AS':
            self.reconfigure(recovery_method, faulty_vnf, None)

            # TODO: for now, just recreating the sync worker. After worker code rework, send immediately a request
            # to import VNF state
            requests.post(SM_URL + 'sync', json={'id': faulty_vnf['id']})

            end = time.time()

            # asynchronously create new backup
            requests.post(VNF_URL + 'backup', json={'id': faulty_vnf['id']})

        elif recovery_method == '1R-AA':
            self.reconfigure(recovery_method, faulty_vnf, None)

            # TODO: for now, just recreating the sync worker. After worker code rework, send immediately a request
            # to import VNF state
            requests.post(SM_URL + 'sync', json={'id': faulty_vnf['id']})

            end = time.time()

            # asynchronously create new backup
            requests.post(VNF_URL + 'backup', json={'id': faulty_vnf['id']})

        elif recovery_method == 'MR-AA':
            self.reconfigure(recovery_method, faulty_vnf, None)

            end = time.time()

        return end-start

    def reconfigure(self, recovery_method, faulty_vnf, new_device):
        """After fault recovery, reconfigure VNF and SFC."""

        if recovery_method == '0R':
            # update VNF
            faulty_vnf['short_id'] = new_device['short_id']
            faulty_vnf['device_id'] = new_device['id']
            faulty_vnf['ip'] = new_device['ip']

        elif recovery_method in ['1R-AS', '1R-AA', 'MR-AA']:
            # replace VNF backup device
            backup_device = faulty_vnf['recovery']['backups'][0]

            # remove used backup
            del faulty_vnf['recovery']['backups'][0]

            faulty_vnf['short_id'] = backup_device['short_id']
            faulty_vnf['device_id'] = backup_device['id']
            faulty_vnf['ip'] = backup_device['ip']

        update_db('replace', 'vnf', faulty_vnf['id'], faulty_vnf)

    def mainloop(self):
        """Periodically monitors each VNF."""

        while True:
            self.update_devices()
            self.monitor()
            time.sleep(2)

if __name__ == '__main__':
    fms = FaultManagementSystem()
    fms.mainloop()
