#!/usr/bin/env python3

import os.path
import os
import json

class AddonNotFoundError(Exception):
    def __init__(self, path):
        self.value = path

    def __str__(self):
        return "Addon not found in " + os.path.abspath(self.value)

def findAddon(location):
    """Try to find an addon.json file at location or any of the parents
        e.g. findAddon("a/b/c/") will try to find the following files in order:
         - a/b/c/addon.json
         - a/b/addon.json
         - a/addon.json
         - /addon.json

        An exception will be thrown if the addon.json is not found.
        >>> findAddon("/etc/")
        Traceback (most recent call last):
        ...
        AddonNotFoundError: Addon not found in /etc
    """
    curLocation = location

    # Try at most 10 levels up
    for k in range(1, 10):
        filename = os.path.join(curLocation, "addon.json")

        if os.path.isfile(filename):
            return filename

        curLocation = os.path.dirname(curLocation)
    else:
        raise AddonNotFoundError(location)

def getAddonInfo(file):
    """Get the contents of addon.json in a dictionary"""
    with open(file, 'r') as f:
        data = json.load(f)

    return data

if __name__ == '__main__':
    import doctest
    doctest.testmod()