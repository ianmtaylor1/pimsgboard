import sense_hat
import time
import threading
import sys

from . import db
from . import web

######################################################


# Displays a message in the standard message format
# If running in a multi-threaded environment, the led_lock should be acquired
# before calling this function
def display_message(sense, msg, idx, count, speed=1):
    fullmsg = 'Msg {}/{}: {}'.format(idx, count, msg)
    sense.show_message(text_string=fullmsg, text_colour=msg.rgb(), 
            scroll_speed=0.1/speed)


# This function waits for joystick input and calls appropriate functions
def handle_joystick_input(sense, led_lock, db_file, msg_speed=1):
    # Start out with a blank list of messages
    msgs = []
    while True:
        # Clear any events that occurred while processing the most
        # recent event. I.e. simulate a "ready" period, or a "not accepting
        # input" period of time.
        _ = sense.stick.get_events()
        # Get the next event from the joystick
        event = sense.stick.wait_for_event()
        if event.action == sense_hat.ACTION_RELEASED:
            if event.direction == sense_hat.DIRECTION_MIDDLE:
                # Middle button = display all messages
                msgs = db.get_all_messages(db_file)
                with led_lock:
                    for i,m in enumerate(msgs):
                        display_message(sense, m, i+1, len(msgs),
                                speed=msg_speed)
                        db.delete_message(db_file, m)
            if event.direction == sense_hat.DIRECTION_LEFT:
                # Left button = display last set of messages
                with led_lock:
                    for i,m in enumerate(msgs):
                        display_message(sense, m, i+1, len(msgs),
                                speed=msg_speed)
                        db.delete_message(db_file, m)


# This thread periodically polls the message database and alerts for available
# new messages
def check_inbox(sense, led_lock, db_file, poll_interval=5.0):
    while True:
        # How many messages do we currently have?
        count = db.count_messages(db_file)
        if count > 0:
            # If the count is one digit, show it. If not, show a +
            if count < 10:
                showchar = str(count)
            else:
                showchar = "+"
            # Try to acquire the lock for the display and display the count
            if led_lock.acquire(blocking=False):
                try:
                    sense.show_letter(showchar)
                finally:
                    led_lock.release()
        # Wait until next check
        time.sleep(poll_interval)


def main():
    # Global parameters. Future: read from config?
    # Location of the database we will read from
    db_file = "/tmp/test.db"
    # How fast to scroll. 1 is default. 2 is twice as fast, etc.
    msg_speed = 2.25
    # How frequently to poll for new messages, in seconds
    poll_interval = 3.0
    # Where to serve the webpage
    web_host = ''
    web_port = 8080
    
    # Check if the database exists and is in the correct format
    if not db.check_db(db_file):
        sys.exit("Error reading database file {}".format(dbfile))
    
    # Create the sense hat object: shared by all threads
    sense = sense_hat.SenseHat()
    
    # Lock to coordinate access to the sense's LED display
    led_lock = threading.RLock()
    
    # Set low light mode to protect retinas
    sense.low_light = True
    
    # Start threads for handling joystick input, idle inbox display,
    # and web interface
    input_thread = threading.Thread(
            target=handle_joystick_input,
            args=(sense, led_lock, db_file),
            kwargs={'msg_speed':msg_speed})
    inbox_thread = threading.Thread(
            target=check_inbox,
            args=(sense, led_lock, db_file),
            kwargs={'poll_interval':poll_interval})
    web_thread = threading.Thread(
            target=web.start_server,
            args=(web_host, web_port, db_file),
            kwargs={})
    input_thread.start()
    inbox_thread.start()
    web_thread.start()
    print("Ready")
    
    # Wait indefinitely for them to end
    web_thread.join()
    inbox_thread.join()
    input_thread.join()

    # Clear sense hat display
    sense.clear()


