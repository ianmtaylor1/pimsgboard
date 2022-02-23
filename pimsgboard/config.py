# File for managing convenient access to the pimsgboard configuration
# file, handling default values.

import configparser
import os

def getconfig():
    cf = configparser.ConfigParser({
        'dbfile': "/tmp/pimsgboard.db",
        'scrollspeed':2.0,
        'pollinterval':5.0,
        'webhost':'',
        'webport':8080,
        'lowlight':True,
        'autoplay':False,
        'directionplugin':''})
    cf.add_section('pimsgboard')
    if os.path.isfile(os.path.expanduser("~/.pimsgboard")):
        cf.read(os.path.expanduser("~/.pimsgboard")) 

    return cf
