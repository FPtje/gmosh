#!/usr/bin/env python3

import os.path
import os
import json

class GModAddon:
    """Represents a Garry's mod addon based on the addon.json data
    """
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

    def gettitle(self):
        return "title" in self.data and self.data["title"] or "No title"

    def getignored(self):
        """Get the list of files to be ignored in this addon
        Always returns a list, even if the addon does not provide a list of ignored files
        """
        if u'ignore' not in self.data:
            return []
        return self.data[u'ignore']

    def getsteamid(self):
        return "steamid64" in self.data and self.data.steamid64 or 0

    def get_description_json(self):
        a_description = "description" in self.data and self.data.description or "Description"
        a_type = self.data["type"]
        a_tags = self.data["tags"]
        return json.dumps({"description": a_description, "type": a_type, "tags": a_tags})

    def getauthor(self):
        return "author" in self.data and self.data.author or "Author Name"

    def getversion(self):
        return 1

    def set_workshopid(self, id):
        """Set the workshop ID of the addon to id and store in addon.json"""
        self.data[u'workshopid'] = id
        self.save_changes()

    def save_changes(self):
        """Store the current state of the GModAddon to addon.json"""
        serialized = json.dumps(self.data, indent = 4, sort_keys = True)
        with open(os.path.join(self.file, "addon.json"), "w") as f:
            f.write(serialized)



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
        >>> find_addon("test")
        'test/addon.json'

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

def get_addon_info(addon_info_path):
    """Get the contents of addon.json in a dictionary
    >>> isinstance(addon_info_from_path("test"), GModAddon)
    True

    >>> get_addon_info("WrongPath")
    """
    if not os.path.isfile(addon_info_path):
        return

    with open(addon_info_path, 'r') as f:
        data = json.load(f)

    return GModAddon(data, os.path.dirname(addon_info_path))

def addon_info_from_path(path):
    """Get the addon info from a folder path."""
    return get_addon_info(find_addon(path))

if __name__ == '__main__':
    import doctest
    doctest.testmod()