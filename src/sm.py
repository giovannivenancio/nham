import os
import time
from subprocess import check_output
from vnfm import *
from utils import *

class StateManager():
    """
    Implementation of the State Manager.

    This module offers an API to manage the internal state of VNFs:
    import_vnf_state
    export_vnf_state
    """

    def __init__(self):
        self._vnfm = VNFManager()
        self._vim = VirtualizedInfrastructureManager()
        self._db_path = '/tmp/'

    def export_vnf_state(self, vnf_id):
        """Export a VNF internal state to a tarball."""

        vnf = self._vnfm.get_vnf(vnf_id)
        virtual_device = self._vim.get_virtual_device(vnf['device_id'])

        checkpoint_name = 'checkpoint_%s' % generate_id()

        checkpoint_cmd = 'docker checkpoint create --leave-running=true %s %s' % (vnf['device_id'], checkpoint_name)

        try:
            res = check_output(
                ['docker', 'checkpoint', 'create', '--leave-running=true', vnf['device_id'], checkpoint_name],
                stderr=open(os.devnull, 'w'))
            print "checkpoint %s created for VNF %s" % (checkpoint_name, vnf_id)
        except:
            print "no new checkpoint required for VNF %s" % vnf_id
            return

        state_entry = {
            'checkpoint': checkpoint_name,
            'timestamp': get_current_time()
        }

        if not self.get_states(vnf_id):
            insert_db('state', vnf['id'], state_entry)
        else:
            update_db('state', vnf['id'], str(state_entry))

        # save VNF state to database
        pack_name = self._db_path + checkpoint_name + '_' + vnf_id + '.tar.gz'
        pack_cmd = 'sudo tar cvzf %s -C /var/lib/docker/containers/%s/checkpoints/%s . >/dev/null 2>&1' % (pack_name, virtual_device['id'], checkpoint_name)
        os.system(pack_cmd)

    def import_vnf_state(self, destination, source, epoch):
        """Import a state to a VNF. If epoch is None, the latest will be used.
        If new_vnf contains a VNFD, then a new VNF is created, otherwise an existent VNF
        will receive the imported state."""


        vnf = self._vnfm.get_vnf(destination)
        self._vnfm.stop_vnf(destination)
        states = self.get_states(source)

        if epoch:
            for state in states:
                if state['timestamp'] == epoch:
                    checkpoint_name = state['checkpoint']
        else:
            checkpoint_name = states[-1]['checkpoint']

        pack_name = self._db_path + checkpoint_name + '_' + source + '.tar.gz'

        target_dir = '/var/lib/docker/containers/%s/checkpoints/%s' % (vnf['device_id'], checkpoint_name)
        unpack_cmd = 'sudo mkdir -p %s && sudo tar -C %s -xvf %s >/dev/null 2>&1' % (target_dir, target_dir, pack_name)
        os.system(unpack_cmd)

        restore_cmd = "docker start --checkpoint %s %s" % (checkpoint_name, vnf['device_id'])
        os.system(restore_cmd)

    def list_states(self):
        """List all saved states from all VNFs."""

        states = load_db('state')

        for vnf_id in states:
            print vnf_id
            for state in states[vnf_id]:
                print "%s [%s] [%s]" % (" "*2, state['checkpoint'], state['timestamp'])

    def get_states(self, vnf_id):
        """Get all saved states from a specific VNF."""

        states = load_db('state')

        for id in states:
            if id == vnf_id:
                return states[id]
        return None

sm = StateManager()

sm.export_vnf_state('teLjcOSIDdSKIgFm')
time.sleep(3)
sm.export_vnf_state('teLjcOSIDdSKIgFm')
time.sleep(3)
sm.export_vnf_state('teLjcOSIDdSKIgFm')

#sm.import_vnf_state('4yafwsHN7HVEwUZK', 'siI347bgaq6mGayO', epoch="12/11/2019 10:40:19", new_vnf=False)
#sm.import_vnf_state('M7VvLQ9rTuSh3egl', 'OVkTxWVWaYIRdJwp', epoch=False)
