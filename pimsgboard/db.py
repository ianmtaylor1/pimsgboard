import sqlite3
import os

from . import message


# Take a filename and create a sqlite databae there if one does not exist.
# If one already exists there, make sure it has a 'messages' table.
def check_db(filename):
    try:
        # Connect to db (creating it if it doesn't exist)
        conn = sqlite3.connect(os.path.normpath(filename))
        with conn:
            cur = conn.cursor()
            # List all table names
            cur.execute("select name from sqlite_master where type='table';")
            names = [x[0] for x in cur.fetchall()]
            # Check for the table we need
            if 'messages' not in names:
                cur.execute("create table messages (id INTEGER PRIMARY KEY, timestamp TEXT, contents TEXT);")
                conn.commit()
            # To do: check for correct columns in table?
    except:
        return False
    finally:
        conn.close()
    return True


# Return all messages from the message table as a list of tuples
def get_all_messages(db_file):
    conn = sqlite3.connect(os.path.normpath(db_file))
    with conn:
        cur = conn.cursor()
        cur.execute("select id, timestamp, contents from messages order by timestamp;")
        msgs = cur.fetchall()
    conn.close()
    return [message.Message(id_=x[0], timestr=x[1], text=x[2]) for x in msgs]


# How many messages are currently waiting?
def count_messages(db_file):
    conn = sqlite3.connect(os.path.normpath(db_file))
    with conn:
        cur = conn.cursor()
        cur.execute("select id from messages;")
        count = len(cur.fetchall())
    conn.close()
    return count


# Deletes a message from the database by id
def delete_message(db_file, msg):
    conn = sqlite3.connect(os.path.normpath(db_file))
    with conn:
        cur = conn.cursor()
        cur.execute("delete from messages where id = ?;", (msg.id,))
    conn.close()

