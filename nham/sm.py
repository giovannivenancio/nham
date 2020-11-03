#!/usr/bin/env python

"""
Implementation of the State Manager.

This module offers an API to manage the internal state of VNFs:
import_vnf_state
export_vnf_state
"""

import ctypes
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

## ptrace(2) interface
c_ptrace = ctypes.CDLL("libc.so.6").ptrace
c_pid_t = ctypes.c_int32
c_ptrace.argtypes = [ctypes.c_int, c_pid_t, ctypes.c_void_p, ctypes.c_void_p]

app = Eve()

VIM_URL = 'http://0.0.0.0:9000/vim/'
VNF_URL = 'http://0.0.0.0:9001/vnf/'
SFC_URL = 'http://0.0.0.0:9002/sfc/'

memory_permissions = 'rw'
global sync_workers
sync_workers = {}

def ptrace(attach, pid):
    """ATTACH or DETACH a process.
    Used to stop/resume execution when a checkpoint is being performed.
    """

    # PTRACE_ATTACH or PTRACE_DETACH
    op = ctypes.c_int(16 if attach else 17)
    c_pid = c_pid_t(pid)
    null = ctypes.c_void_p()

    err = c_ptrace(op, c_pid, null, null)

    if err != 0:
        print err

def dump(pid):
    """Dump the contents of memory to DB or another VNF."""

    memory_dump = ''

    # sequentially read memory map
    with open('/proc/%d/maps' % pid, 'r') as maps_file:
        with open('/proc/%d/mem' % pid, 'r', 0) as mem_file:
            # for each mapped region
            for line in maps_file.readlines():
                m = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+) ([-r][-w])', line)

                if m.group(3) == memory_permissions:
                    start = int(m.group(1), 16)

                    if start > 0xFFFFFFFFFFFF:
                        continue

                    end = int(m.group(2), 16)

                    # seek to region start
                    mem_file.seek(start)

                    # read region contents
                    chunk = mem_file.read(end - start)
                    memory_dump += chunk

    return memory_dump

def restore(pid, dump_mem):
    """Read memory map and replace with dump_mem contents."""

    dump_mem_fd = open(dump_mem, 'r')

    # sequentially read memory map
    with open('/proc/%d/maps' % pid, 'r') as maps_file:
        with open('/proc/%d/mem' % pid, 'rb+', 0) as mem_file:
            # for each mapped region
            for line in maps_file.readlines():
                m = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+) ([-r][-w])', line)

                if m.group(3) == memory_permissions:
                    start = int(m.group(1), 16)

                    if start > 0xFFFFFFFFFFFF:
                        continue

                    end = int(m.group(2), 16)

                    # seek to region start
                    mem_file.seek(start)

                    # read dumped memory contents
                    chunk = dump_mem_fd.read(end - start)

                    # replace actual memory with readed content
                    #mem_file.write(chunk)

    dump_mem_fd.close()

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

def export_vnf_state(vnf_function_pid):
    """ptrace and memory dump to export VNF state."""

    ptrace(True, vnf_function_pid)    # stop process
    state = dump(vnf_function_pid)    # dump memory
    ptrace(False, vnf_function_pid)   # resume process

    return state

def import_vnf_state(vnf_function_pid, dump_mem):
    """ptrace and replace process memory with dumped memory to import VNF state."""

    ptrace(True, vnf_function_pid)      # stop process
    restore(vnf_function_pid, dump_mem) # restore memory into VNF
    ptrace(False, vnf_function_pid)     # resume process

def sync_to_db(vnf_id, vnf_function_pid, cooldown):
    """Sync mechanism used by 0R (0 replicas) and 1R-AS (1 Replica Active-Standby).
    Periodically dump VNF memory and send directly to DB.
    """

    while True:
        try:
            state = export_vnf_state(vnf_function_pid) # export VNF state
            write_state(vnf_id, state) # save state to DB
        except Exception as e:
            print e

        time.sleep(cooldown)

def sync_to_replica(vnf_id, vnf_function_pid, backup_pids, cooldown):
    """Sync mechanism used by 1R-AA (1 Replica Active-Active) and MR-AA (M Replicas Active-Active).
    Periodically dump VNF memory and send directly to the replica(s).
    """

    while True:
        try:
            state = export_vnf_state(vnf_function_pid) # export VNF state

            for backup_pid in backup_pids:
                import_vnf_state(backup_pid, state)
        except Exception as e:
            print e

        sleep(cooldown)

@app.route('/state/sync', methods=['POST'])
def sync_state():
    """Create a new process to sync internal state of VNFs."""

    vnf_id = request.json['id']
    r = requests.get(VNF_URL + 'show', json={'vnf_id': vnf_id})
    vnf = r.json()

    recovery_method = vnf['recovery']['method']
    cooldown = int(vnf['recovery']['cooldown'])

    try:
        vnf_function_pid = get_pid(vnf['short_id'])
    except:
        return "error: couldn't get container PID."

    # If a VNF has any backups, get the PIDs too
    backup_pids = []
    if recovery_method in ['1R-AA', 'MR-AA']:
        for vnf_backup in vnf['recovery']['backups']:
            vnf_backup_id = vnf_backup['short_id']
            backup_pids.append(get_pid(vnf_backup_id))

    if recovery_method in ['0R', '1R-AS']:
        sync_vnf = Process(
            target=sync_to_db,
            args=(vnf_id,vnf_function_pid,cooldown))

    elif recovery_method in ['1R-AA', 'MR-AA']:
        sync_vnf = Process(
            target=sync_to_replica,
            args=(vnf_id,vnf_function_pid,backup_pids,cooldown))

    sync_vnf.daemon = True
    sync_vnf.start()

    insert_db('sync', vnf_id, sync_vnf.pid)

    return "ok"

@app.route('/state/desync', methods=['POST'])
def desync_state():
    """Remove (kill) VNF sync worker."""

    vnf_id = request.json['id']

    sync = load_db('sync')

    for id in sync:
        if id == vnf_id:
            worker_pid = str(sync[id])

    Popen(['kill', '-9', worker_pid])
    remove_db('sync', vnf_id)

    return "ok"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9003)
