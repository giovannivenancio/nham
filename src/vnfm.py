import yaml

from vim import *
from resil import *
from utils import *

class VNFManager():
    """
    VNF Manager implementation.
    """

    def __init__(self):
        self._vim = VirtualizedInfrastructureManager()

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
        mem_size = resources['mem_size']
        num_cpus = resources['num_cpus']
        num_backups = resil_requirements['num_backups']

        if num_backups >= 1:
            vnf_level = resil_requirements['vnf_level']
            infra_level = resil_requirements['infra_level']

            if vnf_level['type'] == 'active-active':
                cooldown = vnf_level['cooldown']

            if infra_level['type'] == 'remote':
                remote_site = infra_level['remote_site']

        # main virtual device for VNF
        device = self._vim.create_virtual_device(
            virtual_device_type,
            image,
            num_cpus,
            mem_size)

        # create backups
        if num_backups >= 1:
            backups = []
            for i in range(num_backups):
                backup = self._vim.create_virtual_device(
                    virtual_device_type,
                    image,
                    num_cpus,
                    mem_size)
                backups.append(device['short_id'])

        vnf = {
            'id': generate_id(),
            'short_id': device['short_id'],
            'device_id': device['id'],
            'ip': device['ip'],
            'network_function': 'forwarder',
            'recovery_mode': vnf_level['type'],
            'backups': backups,
            'timestamp': get_current_time()
        }

        insert_db('vnf', vnf['id'], vnf)

        print "VNF created: %s" % vnf['id']

        return vnf

    def list_vnfs(self):
        """List all VNFs."""

        vnfs = load_db('vnf')

        for id in vnfs:
            print "[VNF] [%s] [%s] [%s] [%s]" % (id, vnfs[id]['network_function'], self._vim.get_status(vnfs[id]['device_id']), vnfs[id]['timestamp'])
            print "%s backups: %s" % (" "*2, vnfs[id]['backups'])
        print ""

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

        for id in vnfs:
            try:
                remove_db('state', id)
                remove_db('vnf', id)
            except:
                pass
