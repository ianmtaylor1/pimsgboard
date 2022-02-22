# This file contains functions to handle plugin functionality,
# including retrieving plugin functions specified by strings,
# default actions, etc.

import importlib

def get_plugin_by_name(name):
    if name == '':
        return default_direction_plugin
    
    namelist = name.split(".")
    funname = namelist[-1]
    modname = ".".join(namelist[:-1])
    
    if modname == '':
        raise Exception("Plugin name must be fully specified, e.g. pkg.module.fun")

    mod = importlib.import_module(modname)
    fun = getattr(mod, funname)
    
    return fun


def default_direction_plugin(sense, direction):
    sense.show_message(text_string='{}'.format(direction))

