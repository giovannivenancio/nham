from vnfm import *
from utils import *

class NFVOrchestrator():
    """
    NFV Orchestrator implementation.
    """

    def __init__(self):
        self._vnfm = VNFManager()

    def sfc_create(self, num_vnfs, vnfd):
        """Create a SFC."""

        chain = []
        for i in range(num_vnfs):
            vnf = self._vnfm.vnf_create(vnfd)
            chain.append(vnf['id'])

        sfc = {
            'id': generate_id(),
            'chain': chain,
            'timestamp': get_current_time()
        }

        insert_db('sfc', sfc['id'], sfc)

        return sfc

    def list_sfcs(self):
        """List all SFCs."""

        sfcs = load_db('sfc')

        for id in sfcs:
            print "[SFC] [%s] [%s]" % (id, sfcs[id]['timestamp'])
            for vnf in sfcs[id]['chain']:
                print "  %s" % vnf

    def get_sfc(self, sfc_id):
        """Get information from a specific SFC."""

        sfcs = load_db('sfc')

        for id in sfcs:
            if id == sfc_id:
                return sfcs[id]

    def sfc_delete(self, sfc_id):
        """Delete a SFC."""

        sfc = self.get_sfc(sfc_id)

        for vnf_id in sfc['chain']:
            self._vnfm.vnf_delete(vnf_id)

        remove_db('sfc', sfc_id)

    def purge_sfcs(self):
        """Delete all SFCs."""

        self._vnfm.purge_vnfs()

        sfcs = load_db('sfc')

        for id in sfcs:
            try:
                remove_db('sfc', id)
            except:
                pass
