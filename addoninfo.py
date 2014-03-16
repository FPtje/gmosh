#!/usr/bin/env python3

import os.path
import os

class AddonNotFoundError(Exception):
    def __init(self, path):
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



if __name__ == '__main__':
    import doctest
    doctest.testmod()