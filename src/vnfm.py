import yaml
from vim import *

class VNFManager():
    """
    VNF Manager implementation.
    """

    def __init__(self):
        self._vim = VirtualizedInfrastructureManager()

    def vnf_create(self, vnfd_file):
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

        self._vim.create_virtual_device(type, image, num_cpus, mem_size)

        # fazer os requisitos de HA no NHAM

    def list_vnfs(self):
        """."""
        pass

    def vnf_delete(vnf_id):
        """Delete a VNF."""
        pass

        # remove pelo vim
        # remove backups
