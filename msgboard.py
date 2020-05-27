#!/usr/bin/env python3

import sense_hat
import sqlite3
import time
import threading
import os
import sys

# Location of the database we will read from
db_file = "test.db"

# How fast to scroll. 1 is default. 2 is twice as fast, etc.
msg_speed = 1.5

# How frequently to poll for new messages, in seconds
poll_interval = 3.0

######################################################

# Check for a database that looks like we need
def check_db(filename):
    try:
        # Connect to db (creating it if it doesn't exist)
        conn = sqlite3.connect(os.path.normpath(filename))
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


# This function waits for joystick input and calls appropriate functions
def handle_joystick_input(sense, led_lock, db_file, msg_speed=1):
    while True:
        # Clear any events that occurred while processing the most
        # recent event. I.e. simulate a "ready" period, or a "not accepting
        # input" period of time.
        _ = sense.stick.get_events()
        # Get the next event from the joystick
        event = sense.stick.wait_for_event()
        
        if event.action == sense_hat.ACTION_RELEASED:
            with led_lock:
                sense.show_message(
                        text_string="Message: {}".format(event.direction),
                        scroll_speed=0.1/msg_speed)


# This thread periodically polls the message database and alerts for available
# new messages
def check_inbox(sense, led_lock, db_file, poll_interval=5.0):
    count = 0
    while True:
        if led_lock.acquire(blocking=False):
            try:
                sense.show_letter(str(count % 10))
            finally:
                led_lock.release()
        time.sleep(poll_interval)
        count += 1


def main(argv):
    # Check if the database exists and is in the correct format
    if not check_db(db_file):
        sys.exit("Error reading database file {}".format(dbfile))
    
    # Create the sense hat object: shared by all threads
    sense = sense_hat.SenseHat()
    
    # Lock to coordinate access to the sense's LED display
    led_lock = threading.RLock()
    
    # Set low light mode to protect retinas
    sense.low_light = True
    
    # Start both threads
    input_thread = threading.Thread(
            target=handle_joystick_input,
            args=(sense, led_lock, db_file),
            kwargs={'msg_speed':msg_speed})
    inbox_thread = threading.Thread(
            target=check_inbox,
            args=(sense, led_lock, db_file),
            kwargs={'poll_interval':poll_interval})
    input_thread.start()
    inbox_thread.start()
    print("Ready")
    
    # Wait indefinitely for them to end
    input_thread.join()
    inbox_thread.join()

#######################################################################

if __name__ == "__main__":
    import sys
    main(sys.argv)
