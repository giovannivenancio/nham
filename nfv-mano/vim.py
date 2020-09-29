#!/usr/bin/env python

"""
Virtualized Infrastructure Manager implementation.
This VIM is based on containers.
"""

import docker
from eve import Eve
from flask import request, jsonify
from utils import *

app = Eve()
dkr = docker.from_env()

@app.route('/vim/create', methods=['POST'])
def create_virtual_device():
    """Create a virtual device."""

    type = request.json['type']
    image = request.json['image']
    num_cpus = request.json['num_cpus']
    mem_size = request.json['mem_size']

    container = dkr.containers.run(
        image,
        detach=True,
        cap_add=['NET_ADMIN'],
        stdin_open=True,
        cpu_count=num_cpus,
        mem_limit=mem_size)

    device = {
        'id': container.id,
        'short_id': container.short_id,
        'image': container.image.tags[0],
        'ip': get_updated_ip(container.id),
        'num_cpus': num_cpus,
        'mem_size': mem_size
    }

    insert_db('device', device['id'], device)

    return "ok!"

def get_updated_ip(device_id):
    """Get updated IP address."""

    return dkr.containers.get(device_id).attrs['NetworkSettings']['IPAddress']

@app.route('/vim/list', methods=['GET'])
def list_virtual_devices():
    """List all virtual devices."""

    devices = load_db('device')

    list_devices = ''

    for id in devices:
        list_devices += "[container] [%s] [%s] [%s] [%s]\n" % (devices[id]['image'], id, devices[id]['ip'], dkr.containers.get(id).status)

    return list_devices

@app.route('/vim/show', methods=['GET'])
def get_virtual_device():
    """Get information from a specific device."""

    devices = load_db('device')

    v_id = request.json['id']

    for id in devices:
        if id == v_id:
            return devices[id]

@app.route('/vim/status', methods=['GET'])
def get_status():
    """Get status of a virtual device."""

    v_id = request.json['id']

    return dkr.containers.get(v_id).status

@app.route('/vim/delete', methods=['DELETE'])
def delete_virtual_device():
    """Delete a virtual device."""

    v_id = request.json['id']

    container = dkr.containers.get(v_id)
    container.stop()
    container.remove()

    remove_db('device', v_id)

    return "ok!"

@app.route('/vim/stop', methods=['POST'])
def stop_virtual_device():
    """Stop a virtual device."""

    v_id = request.json['id']

    container = dkr.containers.get(v_id)
    container.stop()

    return "ok!"

@app.route('/vim/purge', methods=['DELETE'])
def purge_devices():
    """Stop and delete all virtual devices."""

    for container in dkr.containers.list():
        container.stop()

    dkr.containers.prune()

    devices = load_db('device')

    for id in devices:
        try:
            remove_db('device', id)
        except:
            pass

    return "ok!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
