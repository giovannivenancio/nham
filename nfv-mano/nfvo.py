#!/usr/bin/env python

"""
NFV Orchestrator implementation.
"""

import requests
from eve import Eve
from flask import request, jsonify
from utils import *

app = Eve()
VIM_URL = 'http://0.0.0.0:9000/vim/'
VNF_URL = 'http://0.0.0.0:9001/vim/'

@app.route('/sfc/create', methods=['POST'])
def create_sfc():
    """Create a SFC."""

    num_vnfs = request.json['num_vnfs']
    vnfd_file = request.json['vnfd_file']

    chain = []
    for i in range(num_vnfs):
        r = requests.post(VNF_URL + 'create', json={'vnfd_file': vnfd_file})
        vnf = r.json()['vnf']
        chain.append(vnf['id'])

    sfc = {
        'id': generate_id(),
        'chain': chain,
        'timestamp': get_current_time()
    }

    # Create forwarding rules
    # for i in range(len(chain[:-1])):
    #     vnf = self._vnfm.get_vnf(chain[i])
    #     next_hop = self._vnfm.get_vnf(chain[i+1])['ip']
    #     forward_rule = 'iptables -t nat -A PREROUTING -p icmp -j DNAT --to-destination %s' % next_hop
    #
    #     device = self._vim.exec_cmd(vnf['device_id'], forward_rule)

    insert_db('sfc', sfc['id'], sfc)

    return sfc

@app.route('/sfc/list', methods=['GET'])
def list_sfcs():
    """List all SFCs."""

    sfcs = load_db('sfc')

    sfc_list = ''

    for id in sfcs:
        sfc_list += "[SFC] [%s] [%s]\n" % (id, sfcs[id]['timestamp'])
        for vnf in sfcs[id]['chain']:
            sfc_list += "  %s\n" % vnf
        sfc_list += "\n"

    return sfc_list

@app.route('/sfc/show', methods=['GET'])
def get_sfc():
    """Get information from a specific SFC."""

    sfc_id = requests.json['sfc_id']

    sfcs = load_db('sfc')

    for id in sfcs:
        if id == sfc_id:
            return sfcs[id]

@app.route('/sfc/delete', methods=['DELETE'])
def delete_sfc():
    """Delete a SFC."""

    sfc_id = requests.json['sfc_id']

    sfcs = load_db('sfc')

    # search for SFC
    for id in sfcs:
        if id == sfc_id:
            sfc = sfcs[id]

    for vnf_id in sfc['chain']:
        r = requests.delete(VNF_URL + 'delete', json={'vnf_id': vnf_id})

    remove_db('sfc', sfc_id)

    return "SFC deleted: %s" % sfc_id

@app.route('/sfc/purge', methods=['DELETE'])
def purge_sfcs():
    """Delete all SFCs."""

    r = requests.delete(VNF_URL + 'purge')

    sfcs = load_db('sfc')

    for id in sfcs:
        try:
            remove_db('sfc', id)
        except:
            pass

    return "ok!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9002)
