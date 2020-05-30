# pimsgboard
Small message board based on the Raspberry Pi sense hat

This program serves a web interface where messages can be submitted, then
they are displayed on the Raspberry Pi sense hat.

## Sense Hat Controls

Once pimsgboard is running, the sense hat will display the number of messages
that are in the inbox ("+" means 10 or more messages, and a blank screen means
no messages). Pressing the middle button on the sense hat joystick will
display all new messages. Pressing left on the joystick will replay the most
recent group of past messages.

## Installing

On a Raspberry Pi with a sense hat installed, run

```
sudo apt-get install sense-hat python3-pip
```

Then  fetch the sources from this repository and install

```
git clone https://github.com/ianmtaylor1/pimsgboard.git
cd pimsgboard
pip3 install --user .
```

The server can then be started by running the command

```
pimsgboard
```

## Configuration

Configuration TBD. At the moment, configurable values are hard-coded.
