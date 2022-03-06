# File for managing convenient access to the pimsgboard configuration
# file, handling default values.

import configparser
import os

_cf = None

def _getconfig():
    global _cf

    if _cf is None:
        print("Reading configuration\n")
        _cf = configparser.ConfigParser({
            'dbfile': "/tmp/pimsgboard.db",
            'scrollspeed':2.0,
            'pollinterval':5.0,
            'webhost':'',
            'webport':8080,
            'lowlight':True,
            'autoplay':False,
            'directionplugin':''})
        _cf.add_section('pimsgboard')
        if os.path.isfile(os.path.expanduser("~/.pimsgboard")):
            _cf.read(os.path.expanduser("~/.pimsgboard")) 

    return _cf

def getstr(opt):
    return _getconfig().get('pimsgboard', opt)

def getint(opt):
    return _getconfig().getint('pimsgboard', opt)

def getfloat(opt):
    return _getconfig().getfloat('pimsgboard', opt)

def getbool(opt):
    return _getconfig().getboolean('pimsgboard', opt)
