#!/usr/bin/env python

"""
VNF Manager implementation.
"""

import yaml
import requests
from eve import Eve
from flask import request, jsonify
from utils import *

app = Eve()

VIM_URL = 'http://0.0.0.0:9000/vim/'
SM_URL = 'http://0.0.0.0:9003/state/'

@app.route('/vnf/create', methods=['POST'])
def create_vnf():
    """Create a VNF."""

    vnfd_file = request.json['vnfd_file']

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
        vnf_level_type = '0R'

    # main virtual device for VNF
    r = requests.post(VIM_URL + 'create', json={
        'type': virtual_device_type,
        'image': image,
        'num_cpus': num_cpus,
        'mem_size': mem_size
    })

    device = r.json()['device']

    # create backups
    backups = []
    if num_backups >= 1 and vnf_level_type != '0R':
        for i in range(num_backups):
            r = requests.post(VIM_URL + 'create', json={
            'type': virtual_device_type,
                'image': image,
                'num_cpus': num_cpus,
                'mem_size': mem_size
            })

            backup = r.json()['device']
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
    create_vnf_dir(vnf['id'])

    # send VNF ID to State Manager to start synchronization
    r = requests.post(SM_URL + 'sync', json={'id': vnf['id']})

    return jsonify({'vnf': vnf})

@app.route('/vnf/list', methods=['GET'])
def list_vnfs():
    """List all VNFs."""

    vnfs = load_db('vnf')

    vnf_list = ''

    for id in vnfs:
        try:
            r = requests.get(VIM_URL + 'show', json={'id': vnfs[id]['device_id']})
            status = r.text
        except:
            status = 'exited'

        vnf_list += "[VNF] [%s] [%s] [%s] [%s]\n" % (id, vnfs[id]['network_function'], status, vnfs[id]['timestamp'])
        vnf_list += "%s virtual device: %s\n" % (" "*2, vnfs[id]['short_id'])

        if vnfs[id]['recovery']['method'] == 'multisync':
            vnf_list += "%s IP: %s\n" % (" "*2, vnfs[id]['ip'])
        else:
            vnf_list += "%s IP: %s\n" % (" "*2, vnfs[id]['ip'])

        backups = vnfs[id]['recovery']['backups']
        backups_short_ids = []

        if len(backups) >= 1:
            for backup in backups:
                backups_short_ids.append(backup['short_id'])
            backup_msg = ', '.join(backups_short_ids)
        else:
            backup_msg = 'None'

        vnf_list += "%s backups (%s): %s\n\n" % (" "*2, vnfs[id]['recovery']['method'], backup_msg)

    return vnf_list

@app.route('/vnf/show', methods=['GET'])
def get_vnf():
    """Get information from a specific device."""

    vnfs = load_db('vnf')

    vnf_id = request.json['vnf_id']

    for id in vnfs:
        if id == vnf_id:
            return vnfs[id]

@app.route('/vnf/delete', methods=['DELETE'])
def delete_vnf():
    """Delete a VNF."""

    vnfs = load_db('vnf')

    vnf_id = request.json['vnf_id']

    # search for VNF
    for id in vnfs:
        if id == vnf_id:
            vnf = vnfs[id]

    r = requests.delete(VIM_URL + 'delete', json={'id': vnf['device_id']})

    remove_db('vnf', vnf_id)
    delete_vnf_dir(vnf_id)

    return "VNF deleted: %s" % vnf_id

@app.route('/vnf/stop', methods=['POST'])
def stop_vnf():
    """Stop a VNF."""

    vnfs = load_db('vnf')

    vnf_id = request.json['vnf_id']

    # search for VNF
    for id in vnfs:
        if id == vnf_id:
            vnf = vnfs[id]

    r = requests.post(VIM_URL + 'stop', json={'id': vnf['device_id']})

    return "VNF stopped: %s" % vnf_id

@app.route('/vnf/purge', methods=['DELETE'])
def purge_vnfs():
    """Delete all VNFs."""

    r = requests.delete(VIM_URL + 'purge')

    vnfs = load_db('vnf')
    states = load_db('state')
    recovering = load_db('recovering')

    for id in vnfs:
        try:
            remove_db('vnf', id)
            delete_vnf_dir(id)
        except Exception as e:
            print e

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

    return "ok!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9001)
