import ast
import random
import string

DB_DEVICE = '../db/device'
DB_VNF = '../db/vnf'
DB_SFC = '../db/sfc'

def generate_id():
    """Generate a unique 16-byte ID."""

    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))

def get_db_path(db):
    """.Get database path."""

    if db == 'device':
        return DB_DEVICE
    elif db == 'vnf':
        return DB_VNF
    elif db == 'sfc':
        return DB_SFC

def insert_db(db, id, content):
    """Insert a new entry on database."""

    entry = "%s %s\n" % (id, content)

    with open(get_db_path(db), 'a+') as db_conn:
        db_conn.write(entry)

def remove_db(db, id):
    """Remove an entry from database."""

    with open(get_db_path(db), 'r') as old_db:
        old_data = old_db.readlines()

    with open(get_db_path(db), 'w') as db_conn:
        for entry in old_data:
            if id not in entry:
                db_conn.write(entry)

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
