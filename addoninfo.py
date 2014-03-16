#!/usr/bin/env python3

import os.path
import os
import json

class GModAddon:
    """Represents a Garry's mod addon based on the addon.json data"""
    def __init__(self, data, path):
        self.data = data
        self.file = path

    def has_workshop_id(self):
        """Whether this addon has a workshop id (and thus exists on the workshop)"""
        return u'workshopid' in self.data

    def default_changelog(self):
        """The default changelog of the addon.

            Used when the changelog is omitted from the command line.
        """
        return u'default_changelog' in self.data and self.data[u'default_changelog'] or ''

class AddonNotFoundError(Exception):
    def __init__(self, path):
        self.value = path

    def __str__(self):
        return "No GMod addon found in " + os.path.abspath(self.value)

def find_addon(location):
    """Try to find an addon.json file at location or any of the parents
        e.g. find_addon("a/b/c/") will try to find the following files in order:
         - a/b/c/addon.json
         - a/b/addon.json
         - a/addon.json
         - /addon.json

        An exception will be thrown if the addon.json is not found.
        >>> find_addon("/etc/")
        Traceback (most recent call last):
        ...
        AddonNotFoundError: No GMod addon found in /etc
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

def get_addon_info(path):
    """Get the contents of addon.json in a dictionary"""
    with open(path, 'r') as f:
        data = json.load(f)

    return GModAddon(data, os.path.dirname(path))

if __name__ == '__main__':
    import doctest
    doctest.testmod()