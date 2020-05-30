"""This module holds the Message class, which contains representations of
messages."""

import datetime
import math

def _reltimestr(then, now):
    """Return a sensible string representing the relative time of then compared
    to now (e.g. 'yesterday 2:03pm' or '35 minutes ago')"""
    delta = now - then
    if delta.days < 0:
        # Assume negatives are due to clocks slightly out of sync
        return "just now"
    minutes = delta.days * 24 * 60 + (delta.seconds + delta.microseconds / 1000000) / 60
    if minutes < 1:
        return "1 minute ago"
    elif minutes < 60:
        return "{} minutes ago".format(math.ceil(minutes))
    elif then.date() == now.date():
        return then.strftime("%I:%M %p")
    elif then.date() == now.date() - datetime.timedelta(days=1):
        return "yesterday {}".format(then.strftime("%I:%M %p"))
    elif minutes < 60 * 24 * 6:
        return then.strftime('%a %I:%M %p')
    elif minutes < 60 * 24 * 180:
        return then.strftime('%a %b %d %I:%M %p')
    else:
        return then.strftime('%c')


class Message:
    """Contains the representation of a message."""

    def __init__(self, id_, text, timestamp=None, color=[255,255,255]):
        self.id = id_
        if timestamp is None:
            timestamp = datetime.datetime.now()
        self.timestamp = timestamp
        self.text = text
        self.color = color

    def __str__(self):
        return self.tostring()
    
    def tostring(self, reltime=True, now=None):
        """Convert the message to a string for display. If reltime is true,
        report the time as relative (e.g. '5 minutes ago'). Relative time
        is relative to 'now', which defaults to datetime.datetime.now()"""
        if reltime:
            if now is None:
                now = datetime.datetime.now()
            displaytime = _reltimestr(self.timestamp, now)
        else:
            displaytime = self.timestamp.strftime('%c')
        return '"{}" ({})'.format(self.text, displaytime)
