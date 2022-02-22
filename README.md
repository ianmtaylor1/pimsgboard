# pimsgboard
Small message board based on the Raspberry Pi sense hat

This program serves a web interface where messages can be submitted, which 
are then displayed on the Raspberry Pi sense hat.

## Web Interface

![Screenshot of web interface](pimsgboard-interface-screenshot.PNG?raw=true)

Once `pimsgboard` is running, it will serve a web interface (by default on all
addresses, port 8080). You can leave a message by going there in any browser.
For example, if your Raspberry Pi has the IP 192.168.0.123, visiting
`http://192.168.0.123:8080/` will bring up the web interface. See the
"Configuration" and "Listening on Port 80" sections for info about how to
change this behavior.

## Sense Hat Controls

Once `pimsgboard` is running, the sense hat will display the number of messages
that are in the inbox (a single digit 1-9; "+" means 10 or more messages, and a
blank screen means no messages). Pressing the middle button on the sense hat
joystick will display all new messages. Pressing left on the joystick will
replay the most recent group of past messages.

The color of the notification digit is determined pseudorandomly by the timestamp
of the oldest unread message. It will stay the same until the messages are read,
then it will (probably) be different when the next message is received.

## Installing

1. On a Raspberry Pi running [Raspberry Pi OS](https://www.raspberrypi.org/downloads/raspberry-pi-os/)
with a sense hat attached, run:

```
sudo apt-get install sense-hat python3-pip
```

2. Then fetch the sources from this repository and install by running:

```
git clone https://github.com/ianmtaylor1/pimsgboard.git
cd pimsgboard
pip3 install --user .
```

3. The server can then be started by running the command:

```
pimsgboard
```

## Configuration

Configuration is read in from the file `.pimsgboard` in your home directory.
This file in in a `.ini` format. Here is an example file with the defaults
filled in.
```
[pimsgboard]
DBFile = /tmp/pimsgboard.db
ScrollSpeed = 2.0
PollInterval = 5.0
WebHost = 
WebPort = 8080
LowLight = yes
AutoPlay = no
DirectionPlugin = 
```

To override any of these defaults create a file `.pimsgboard` in your home
directory with the `[pimsgboard]` header and any desired options below it.

The options are

* `DBFile` is the location of the SQLite database. You will probably never need to set this yourself.
* `ScrollSpeed` is the speed at which messages scroll across the LED matrix. Higher is faster, and 1.0 is the default speed of the sense hat.
* `PollInterval` is how often to check for new messages, in seconds.
* `WebHost` is an IP address for the web server to listen on. By default, it listens on all interfaces.
* `WebPort` is the port for the web server to listen on.
* `LowLight` is whether to use the sense hat's "low light" mode.
* `AutoPlay` - if true, messages will automatically scroll when received, instead of waiting for a button push. The buttons are unresponsive in this mode.
* `DirectionPlugin` - A function to call in the event of other direction buttons (up, right, down) being pressed. Should be a string representing a callable in another Python module installed on the same device, e.g., 'mypackage.mymodule.myfunction'. See section 'Plugins' for more details.

The configuration is read once at startup. If any options are changed, restart
the pimsgboard program.

## Plugins

Certain features allow the use of plugins to enhance this software. Here is
documentation of how to write and use these plugins.

### Direction Plugin

This plugin is a callable defined in an outside Python module that can perform
actions depending on which button has been pressed. The function should take
two positional arguments:

1. The sense hat object created by SenseHat()
2. The direction pressed as a string ("up", "right", or "down")

This means that the plugin can write directly to the sense hat display, read
the sense hat's sensors, and perform different actions based on the direction
pressed. However, the plugin will have no access to messages. A very simple 
plugin could be the following:

```
def myplugin(sense, direction):
    if direction == "up":
        sense.show_message("Temperature: %s C" % sense.get_temperature())
    elif direction == "right":
        sense.show_message("Humidity: %s %%" % sense.get_humidity())
    elif direction == "down":
        sense.show_message("Pressure: %s millibars" % sense.get_pressure())
```

When the function returns, the screen is cleared and normal message polling
resumes. Any return value is discarded.

## Starting automatically

To start `pimsgboard` automatically on Raspberry Pi boot, add this line to the pi
user's crontab (by running `crontab -e`)
```
@reboot /home/pi/.local/bin/pimsgboard >/dev/null 2>&1
```

## Listening on Port 80

By default, the `pimsgboard` web interface listens on port 8080. It's not possible
to listen on port 80 without root privileges, and I would advise against running
this script as root. Instead, install a standard web server and set up a reverse
proxy. I've done this with `nginx`, with these simple steps.

1. Install `nginx`
```
sudo apt-get install nginx
```

2. Create the reverse proxy configuration. 

As root, edit the file `/etc/nginx/sites-available/pimsgboard`:
```
sudo nano /etc/nginx/sites-available/pimsgboard
```

Copy-paste the following content, then save and close the file:
```
server {
	listen 80;
	listen [::]:80 ipv6only=on;
	location / {
		proxy_pass http://127.0.0.1:8080;
	}
}
```

3. Enable the configuration.
```
sudo ln -s /etc/nginx/sites-available/pimsgboard /etc/nginx/sites-enabled/pimsgboard
```
