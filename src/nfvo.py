from vnfm import *
from utils import generate_id

class NFVOrchestrator():
    """
    NFV Orchestrator implementation.
    """

    def __init__(self):
        self._bd_path = '../db/sfcs'

    def sfc_create(self, num_vnfs, vnfd):
        """Create a SFC."""

        for i in range(num_vnfs):
            vnfm.create(vnfd)

        # create routes
        #ip route add src via dest

        sfc_id = generate_id()

        # TODO: implement a real database
        with open(self._db_path, 'r') as db:
            db.write(sfc_id, chain, '\n')

    def list_sfcs(self):
        """."""

    def sfc_delete(sfc_id):
        """Delete a sfc."""
        pass

        # remove vnfs from chain
        # delete from file
