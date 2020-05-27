#!/usr/bin/env python3

import sense_hat
import sqlite3
import time
import threading

# Location of the database we will read from
db_file = "test.db"

# Create the sense hat object: shared by all threads
sense = sense_hat.SenseHat()

# Locks to coordinate access to resources
led_lock = threading.RLock()
input_lock = threading.RLock()

# Set low light mode to protect retinas
sense.low_light = True

# This function waits for joystick input and calls appropriate functions
def handle_joystick_input():
    while True:
        # Get the next event from the joystick
        with input_lock:
            # Clear any events that occurred while processing the most
            # recent event. I.e. simulate a "ready" period, or a "not accepting
            # input" period of time.
            _ = sense.stick.get_events()
            event = sense.stick.wait_for_event()
        if event.action == sense_hat.ACTION_RELEASED:
            with led_lock:
                sense.show_message("Message: {}".format(event.direction))

# This thread periodically polls the message database and alerts for available
# new messages
def check_inbox():
    count = 0
    while True:
        if led_lock.acquire(blocking=False):
            try:
                sense.show_letter(str(count % 10))
            finally:
                led_lock.release()
        time.sleep(2.5)
        count += 1

# Start both threads
input_thread = threading.Thread(target=handle_joystick_input)
inbox_thread = threading.Thread(target=check_inbox)
input_thread.start()
inbox_thread.start()
print("Ready")

# Wait indefinitely for them to end
input_thread.join()
inbox_thread.join()
