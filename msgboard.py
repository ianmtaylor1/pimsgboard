#!/usr/bin/env python3

import sense_hat
import sqlite3
import time
import threading

# Location of the database we will read from
db_file = "test.db"

######################################################

# Check for a database that looks like we need
def check_db(filename):
    # Todo: stub
    return True

# This function waits for joystick input and calls appropriate functions
def handle_joystick_input(sense, led_lock, db_file):
    while True:
        # Clear any events that occurred while processing the most
        # recent event. I.e. simulate a "ready" period, or a "not accepting
        # input" period of time.
        _ = sense.stick.get_events()
        # Get the next event from the joystick
        event = sense.stick.wait_for_event()
        
        if event.action == sense_hat.ACTION_RELEASED:
            with led_lock:
                sense.show_message("Message: {}".format(event.direction))

# This thread periodically polls the message database and alerts for available
# new messages
def check_inbox(sense, led_lock, db_file):
    count = 0
    while True:
        if led_lock.acquire(blocking=False):
            try:
                sense.show_letter(str(count % 10))
            finally:
                led_lock.release()
        time.sleep(2.5)
        count += 1


def main(argv):
    # Check if the database exists and is in the correct format
    check_db(db_file)
    
    # Create the sense hat object: shared by all threads
    sense = sense_hat.SenseHat()
    
    # Lock to coordinate access to the sense's LED display
    led_lock = threading.RLock()
    
    # Set low light mode to protect retinas
    sense.low_light = True
    
    # Start both threads
    input_thread = threading.Thread(
            target=handle_joystick_input,
            args=(sense, led_lock, db_file))
    inbox_thread = threading.Thread(
            target=check_inbox,
            args=(sense, led_lock, db_file))
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
