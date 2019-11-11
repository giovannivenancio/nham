import yaml
from vim import *
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
                print exc
                return

        type = vnfd['topology_template']['node_templates']['VDU1']['properties']['type']
        image = vnfd['topology_template']['node_templates']['VDU1']['properties']['image']
        resources = vnfd['topology_template']['node_templates']['VDU1']['capabilities']['nfv_compute']['properties']
        mem_size = resources['mem_size']
        num_cpus = resources['num_cpus']

        device = self._vim.create_virtual_device(type, image, num_cpus, mem_size)

        vnf = {
            'id': generate_id(),
            'short_id': device['short_id'],
            'device_id': device['id'],
            'ip': device['ip'],
            'network_function': 'forwarder',
            'timestamp': get_current_time()
        }

        insert_db('vnf', vnf['id'], vnf)

        print "VNF created: %s" % vnf['short_id']

        return vnf

    def list_vnfs(self):
        """List all VNFs."""

        vnfs = load_db('vnf')

        for id in vnfs:
            print "[VNF] [%s] [%s] [%s] [%s]" % (id, vnfs[id]['network_function'], self._vim.get_status(vnfs[id]['device_id']), vnfs[id]['timestamp'])
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

    def purge_vnfs(self):
        """Delete all VNFs."""

        self._vim.purge_devices()

        vnfs = load_db('vnf')

        for id in vnfs:
            try:
                remove_db('vnf', id)
            except:
                pass
