import ast
import os
import random
import shutil
import string

from datetime import datetime

DB_DEVICE = '../db/device'
DB_VNF = '../db/vnf'
DB_SFC = '../db/sfc'
DB_STATE = '../db/state'
DB_RECOVERING = '../db/recovering'
DB_SYNC = '../db/sync'

def generate_id():
    """Generate a unique 16-byte ID."""

    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))

def get_current_time():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def get_db_path(db):
    """Get database path."""

    if db == 'device':
        return DB_DEVICE
    elif db == 'vnf':
        return DB_VNF
    elif db == 'sfc':
        return DB_SFC
    elif db == 'state':
        return DB_STATE
    elif db == 'recovering':
        return DB_RECOVERING
    elif db == 'sync':
        return DB_SYNC

def insert_db(db, id, content):
    """Insert a new entry on the database."""

    entry = "%s %s\n" % (id, content)

    with open(get_db_path(db), 'a+') as db_conn:
        db_conn.write(entry)

def remove_db(db, id):
    """Remove an entry from a database."""

    with open(get_db_path(db), 'r') as old_db:
        old_data = old_db.readlines()

    with open(get_db_path(db), 'w') as db_conn:
        for entry in old_data:
            if id not in entry:
                db_conn.write(entry)

def update_db(action, db, entry_id, new_data):
    """Append an entry in a item from database.
    Mostly used by the State Manager."""

    with open(get_db_path(db), 'r') as old_db:
        data = old_db.readlines()

    for i in range(len(data)):
        entry = data[i].strip("\n")
        id, old_content = entry.split(' ', 1)

        if id == entry_id:
            if action == 'append':
                data[i] = id + ' ' + old_content + ',' + str(new_data) + '\n'
            elif action == 'replace':
                data[i] = id + ' ' + str(new_data) + '\n'

    with open(get_db_path(db), 'w') as db_conn:
        db_conn.writelines(data)

def load_db(db):
    """Load database on memory."""

    data = {}

    with open(get_db_path(db), 'r') as db_conn:
        entries = db_conn.readlines()

    for entry in entries:
        entry = entry.strip("\n")
        id, content = entry.split(' ', 1)

        content = ast.literal_eval(content)
        data[id] = content

    return data

def create_vnf_dir(vnf_id):
    """Create a directory to store VNF's checkpoints."""

    path = '../db/checkpoints/' + vnf_id

    try:
        os.mkdir(path)
    except OSError:
        return "error creating dir"

def delete_vnf_dir(vnf_id):
    """Create a directory to store VNF's checkpoints."""

    path = '../db/checkpoints/' + vnf_id

    try:
        shutil.rmtree(path)
    except Exception as e:
        return e

def write_state(vnf_id, state):
    """Write a dumped VNF state to DB."""

    path = '../db/checkpoints/' + vnf_id + '/checkpoint'

    with open(path, 'w') as db_conn:
        db_conn.write(state)
