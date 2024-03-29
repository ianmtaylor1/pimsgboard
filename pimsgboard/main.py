import sense_hat
import time
import threading
import sys
import colorsys
import math
import os

from . import db
from . import web
from . import plugin
from . import config

######################################################


# Displays a message in the standard message format, or a plain format.
# If running in a multi-threaded environment, the led_lock should be acquired
# before calling this function
def display_message(sense, msg, idx, count, speed=1):
    fullmsg = 'Msg {}/{}: {}'.format(idx, count, msg)
    sense.show_message(text_string=fullmsg, text_colour=msg.rgb(), 
            scroll_speed=0.1/speed)

def display_message_plain(sense, msg, speed=1):
    sense.show_message(text_string=msg.tostring(plain=True),
            text_colour=msg.rgb(),
            scroll_speed=0.1/speed)

# This function waits for joystick input and calls appropriate functions
def handle_joystick_input(sense, led_lock):
    db_file = config.getstr('dbfile')
    msg_speed = config.getfloat('scrollspeed')
    direction_plugin = plugin.get_plugin_by_name(config.getstr('directionplugin'))

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
            elif event.direction == sense_hat.DIRECTION_LEFT:
                # Left button = display last set of messages
                with led_lock:
                    for i,m in enumerate(msgs):
                        display_message(sense, m, i+1, len(msgs),
                                speed=msg_speed)
                        db.delete_message(db_file, m)
            else:
                # TBD
                with led_lock:
                    direction_plugin(sense, event.direction)
                    sense.clear()


# This thread periodically polls the message database and alerts for available
# new messages
def check_inbox(sense, led_lock):
    db_file = config.getstr('dbfile')
    poll_interval = config.getfloat('pollinterval')

    while True:
        # How many messages do we currently have?
        count = db.count_messages(db_file)
        if count > 0:
            # How old is the oldest message?
            firsttime = db.oldest_message(db_file)
            # If the count is one digit, show it. If not, show a +
            if count < 10:
                showchar = str(count)
            else:
                showchar = "+"
            # Determine the color based on the time of the oldest message
            hue = (hash(firsttime) % 1024) / 1024
            minsat = 0.33
            satraw = ((hash(firsttime) // 1024) % 1024) / 1024
            sat = math.sqrt(minsat**2 + (1.0 - minsat**2) * satraw)
            rgb = [math.floor(x * 255.99) for x in colorsys.hsv_to_rgb(hue, sat, 1.0)]
            # Try to acquire the lock for the display and display the count
            if led_lock.acquire(blocking=False):
                try:
                    sense.show_letter(showchar, text_colour=rgb)
                finally:
                    led_lock.release()
        # Wait until next check
        time.sleep(poll_interval)


# This thread periodically checks the message database and automatically
# scrolls messages across the display
def check_and_autoplay(sense, led_lock):
    db_file = config.getstr('dbfile')
    poll_interval = config.getfloat('pollinterval')
    msg_speed = config.getfloat('scrollspeed')

    while True:
        # How many messages do we currently have?
        msgs = db.get_all_messages(db_file)
        with led_lock:
            for i,m in enumerate(msgs):
                display_message_plain(sense, m, speed=msg_speed)
                db.delete_message(db_file, m)
        # Wait until next check
        time.sleep(poll_interval)


def main():
    # Location of the database we will read from
    db_file = config.getstr("dbfile")
    # Set low light mode to protect retinas
    low_light = config.getbool("lowlight")
    # Should messages automatically scroll or wait for buttons?
    auto_play = config.getbool("autoplay") 
    # What function should be used for remaining directional buttons?
    direction_plugin_name = config.getstr("directionplugin")

    # Check if the database exists and is in the correct format
    if not db.check_db(db_file):
        sys.exit("Error reading database file {}".format(db_file))
    
    # Create the sense hat object: shared by all threads
    sense = sense_hat.SenseHat()
    sense.low_light = low_light

    # Lock to coordinate access to the sense's LED display
    led_lock = threading.RLock()

    # Load plugin module and retrieve callable
    direction_plugin = plugin.get_plugin_by_name(direction_plugin_name)
    
    # Start threads for handling joystick input, idle inbox display,
    # and web interface. If autoplay is on, start thread for autoplaying
    if auto_play:
        auto_thread = threading.Thread(target=check_and_autoplay, args=(sense, led_lock))
        auto_thread.start()
    else:
        input_thread = threading.Thread(target=handle_joystick_input, args=(sense, led_lock))
        inbox_thread = threading.Thread(target=check_inbox, args=(sense, led_lock))
        input_thread.start()
        inbox_thread.start()
    web_thread = threading.Thread(target=web.start_server)
    web_thread.start()
    
    print("Ready")
    
    # Wait indefinitely for them to end
    web_thread.join()
    if auto_play:
        auto_thread.join()
    else:
        inbox_thread.join()
        input_thread.join()

    # Clear sense hat display
    sense.clear()


