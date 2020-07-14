# pimsgboard
Small message board based on the Raspberry Pi sense hat

This program serves a web interface where messages can be submitted, then
they are displayed on the Raspberry Pi sense hat.

## Sense Hat Controls

Once `pimsgboard` is running, the sense hat will display the number of messages
that are in the inbox ("+" means 10 or more messages, and a blank screen means
no messages). Pressing the middle button on the sense hat joystick will
display all new messages. Pressing left on the joystick will replay the most
recent group of past messages.

## Installing

1. On a Raspberry Pi with a sense hat attached, run:

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

Configuration TBD. At the moment, configurable values are hard-coded.

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
