#!/usr/bin/env python

"""
Implementation of the State Manager.

This module offers an API to manage the internal state of VNFs:
import_vnf_state
export_vnf_state
"""

import os
import re
import requests
import subprocess
import sys
import time

sys.path.append("../nfv-mano/")

from eve import Eve
from subprocess import check_output, Popen
from multiprocessing import Process, Queue
from flask import request, jsonify
from utils import *

app = Eve()

VIM_URL = 'http://0.0.0.0:9000/vim/'
VNF_URL = 'http://0.0.0.0:9001/vnf/'
SFC_URL = 'http://0.0.0.0:9002/sfc/'

_db_path = '/tmp/'

def dump(pid):
    """Dump the contents of memory to DB or another VNF."""

    memory_permissions = 'rw'
    dump = ''

    with open('/proc/%d/maps' % pid, 'r') as maps_file:
        with open('/proc/%d/mem' % pid, 'r', 0) as mem_file:
            # for each mapped region
            for line in maps_file.readlines():
                m = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+) ([-r][-w])', line)

                if m.group(3) == memory_permissions:
                    #sys.stderr.write("\nOK : \n" + line+"\n")
                    start = int(m.group(1), 16)

                    if start > 0xFFFFFFFFFFFF:
                        continue

                    end = int(m.group(2), 16)

                    #sys.stderr.write( "start = " + str(start) + "\n")

                    # seek to region start
                    mem_file.seek(start)

                    # read region contents
                    chunk = mem_file.read(end - start)
                    dump += chunk
                else:
                    pass
                    #sys.stderr.write("\nPASS : \n" + line+"\n")
    return dump

def get_pid(container_id):
    """Given a VNF ID, search for the corresponding container and the returns the application PID."""

    # get VNF master device PID (parent pid)
    ps = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE).communicate()[0]
    processes = ps.split('\n')
    nfields = len(processes[0].split()) - 1

    for proc in processes[1:]:
        if container_id in proc:
            vnf_container_pid = proc.split(None, nfields)[1]

    # get VNFs processes PIDs
    try:
        processes_pids = check_output(
            ['pgrep', '-P', vnf_container_pid],
            stderr=open(os.devnull, 'w'))
    except subprocess.CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

    processes_pids = processes_pids.split('\n')[:-1]
    return int(processes_pids[1])

def sync_db(vnf_id, vnf_function_pid, cooldown):
    """Sync mechanism used by 0R (0 replicas) and 1R-AS (1 Replica Active-Standby).
    Periodically dump VNF memory and send directly to DB.
    """

    while True:
        try:
            state = dump(vnf_function_pid)
            write_state(vnf_id, state)
        except Exception as e:
            print e

        time.sleep(cooldown)

def sync_1RAA(vnf_id, vnf_function_pid, backup_pids, cooldown):
    """Sync mechanism used by 1R-AA (1 Replica Active-Active).
    Periodically dump VNF memory and send directly to the replica.
    """

    while True:
        try:
            pass
        except:
            pass

        sleep(cooldown)

def sync_MRAA(vnf_id, vnf_function_pid, backup_pids, cooldown):
    """Sync mechanism used by MR-AA (M Replicas Active-Active).
    Periodically dump VNF memory and send to each replica.
    """

    while True:
        try:
            pass
        except:
            pass

        sleep(cooldown)

@app.route('/state/sync', methods=['POST'])
def sync_state():
    """Create a new process to sync internal state of active-active replication VNFs."""

    vnf_id = request.json['id']
    r = requests.get(VNF_URL + 'show', json={'vnf_id': vnf_id})
    vnf = r.json()

    recovery_method = vnf['recovery']['method']
    cooldown = int(vnf['recovery']['cooldown'])

    print "received VNF %s with recovery %s and cooldown %s" % (vnf_id, recovery_method, cooldown)

    try:
        vnf_function_pid = get_pid(vnf['short_id'])
    except:
        return "error: couldn't get container PID."

    # If a VNF has any backups, get the PIDs too
    backup_pids = []
    if recovery_method != '0R':
        for vnf_backup in vnf['recovery']['backups']:
            vnf_backup_id = vnf_backup['short_id']
            backup_pids.append(get_pid(vnf_backup_id))

    print "vnf pid: ", vnf_function_pid
    print "backups pids: ", backup_pids

    if recovery_method == '0R':
        sync_vnf = Process(
            target=sync_db,
            args=(vnf_id,vnf_function_pid,cooldown))

    elif recovery_method == '1R-AS':
        sync_vnf = Process(
            target=sync_db,
            args=(vnf_id,vnf_function_pid,cooldown))

    elif recovery_method == '1R-AA':
        sync_vnf = Process(
            target=sync_1RAA,
            args=(vnf_id,vnf_function_pid,backup_pids,cooldown))

    elif recovery_method == 'MR-AA':
        sync_vnf = Process(
            target=sync_MRAA,
            args=(vnf_id,vnf_function_pid,backup_pids,cooldown))

    sync_vnf.daemon = True
    sync_vnf.start()

    return "ok"

@app.route('/state/list', methods=['GET'])
def list_states(self):
    """List all saved states from all VNFs."""

    pass

@app.route('/state/get', methods=['GET'])
def get_states(self, vnf_id):
    """Get all saved states from a specific VNF."""

    pass



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9003)
