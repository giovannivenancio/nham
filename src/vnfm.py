import yaml

from vim import *
from utils import *

class VNFManager():
    """
    VNF Manager implementation.
    """

    def __init__(self):
        self._vim = VirtualizedInfrastructureManager()
        #self._sm = StateManager()

    def create_vnf(self, vnfd_file):
        """Create a VNF."""

        with open(vnfd_file, 'r') as stream:
            try:
                vnfd = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print "error", exc
                return

        vdu = vnfd['topology_template']['node_templates']['VDU1']
        resil_requirements = vnfd['topology_template']['node_templates']['resiliency']
        resources = vdu['capabilities']['nfv_compute']['properties']

        virtual_device_type = vdu['properties']['type']
        image = vdu['properties']['image']
        num_cpus = resources['num_cpus']
        mem_size = resources['mem_size']
        num_backups = resil_requirements['num_backups']
        cooldown = resil_requirements['cooldown']

        if num_backups >= 1:
            vnf_level = resil_requirements['vnf_level']
            infra_level = resil_requirements['infra_level']
            vnf_level_type = vnf_level['type']

            if infra_level['type'] == 'remote':
                remote_site = infra_level['remote_site']
        else:
            vnf_level_type = None

        # main virtual device for VNF
        device = self._vim.create_virtual_device(
            virtual_device_type,
            image,
            num_cpus,
            mem_size)

        # create backups
        backups = []
        if num_backups >= 1:
            for i in range(num_backups):
                backup = self._vim.create_virtual_device(
                    virtual_device_type,
                    image,
                    num_cpus,
                    mem_size)
                backups.append(backup)

        vnf = {
            'id': generate_id(),
            'short_id': device['short_id'],
            'device_id': device['id'],
            'ip': device['ip'],
            'properties': {
                'image': image,
                'num_cpus': num_cpus,
                'mem_size': mem_size
            },
            'network_function': 'forwarder',
            'recovery': {
                'method': vnf_level_type,
                'cooldown': cooldown,
                'backups': backups
            },
            'timestamp': get_current_time()
        }

        insert_db('vnf', vnf['id'], vnf)

        print "VNF created: %s" % vnf['id']

        return vnf

    def list_vnfs(self):
        """List all VNFs."""

        vnfs = load_db('vnf')

        for id in vnfs:
            try:
                status = self._vim.get_status(vnfs[id]['device_id'])
            except:
                status = 'exited'

            print "[VNF] [%s] [%s] [%s] [%s]" % (id, vnfs[id]['network_function'], status, vnfs[id]['timestamp'])
            print "%s virtual device: %s" % (" "*2, vnfs[id]['short_id'])
            print "%s IP: %s" % (" "*2, vnfs[id]['ip'])

            backups = vnfs[id]['recovery']['backups']
            backups_short_ids = []
            if len(backups) >= 1:
                for backup in backups:
                    backups_short_ids.append(backup['short_id'])
                backup_msg = ' ,'.join(backups_short_ids)
            else:
                backup_msg = 'None'

            print "%s backups (%s): %s" % (" "*2, vnfs[id]['recovery']['method'], backup_msg)

    def get_vnf(self, vnf_id):
        """Get information from a specific device."""

        vnfs = load_db('vnf')

        for id in vnfs:
            if id == vnf_id:
                return vnfs[id]

    def delete_vnf(self, vnf_id):
        """Delete a VNF."""

        vnf = self.get_vnf(vnf_id)
        self._vim.delete_virtual_device(vnf['device_id'])

        remove_db('vnf', vnf_id)

        print "VNF deleted: %s" % vnf_id

    def stop_vnf(self, vnf_id):
        """Stop a VNF."""

        vnf = self.get_vnf(vnf_id)
        self._vim.stop_virtual_device(vnf['device_id'])

        print "VNF stopped: %s" % vnf_id

    def purge_vnfs(self):
        """Delete all VNFs."""

        self._vim.purge_devices()

        vnfs = load_db('vnf')
        states = load_db('state')
        recovering = load_db('recovering')

        for id in vnfs:
            try:
                remove_db('vnf', id)
            except:
                pass

        for id in states:
            try:
                remove_db('state', id)
            except:
                pass

        for id in recovering:
            try:
                remove_db('recovering', id)
            except:
                pass
