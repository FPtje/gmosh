#!/usr/bin/env python3

import os.path
import os
import json
import gmafile
import re
from functools import partial
from fnmatch import fnmatch

class GModAddon:
    """Represents a Garry's mod addon based on the addon.json data
    """
    def __init__(self, data, path, addonFile = 'addon.json'):
        self.data = data
        self.file = os.path.join(path, addonFile)
        self.path = path

    def has_workshop_id(self):
        """Whether this addon has a workshop id (and thus exists on the workshop)"""
        return u'workshopid' in self.data

    def getworkshopid(self):
        return u'workshopid' in self.data and self.data[u'workshopid'] or 0

    def getdefault_changelog(self):
        """The default changelog of the addon.

            Used when the changelog is omitted from the command line.
        """
        return u'default_changelog' in self.data and self.data[u'default_changelog'] or ''

    def gettitle(self):
        """Get the title (name) of the addon"""
        return 'title' in self.data and self.data['title'] or "No title"

    def getignored(self):
        """Get the list of files to be ignored in this addon
        Always returns a list, even if the addon does not provide a list of ignored files
        """
        if u'ignore' not in self.data:
            return []
        return self.data[u'ignore']

    def getsteamid(self):
        """Unused. Get the SteamID64 of the addon as an int."""
        return 'steamid64' in self.data and self.data['steamid64'] or 0

    def get_description_json(self):
        """The "description" of this addon (includes description, type and tags)
        This description is used in the GMA file.
        """
        a_description = u'description' in self.data and self.data['description'] or u'Description'
        a_type = self.data['type']
        a_tags = self.data['tags']
        return json.dumps({'description': a_description, 'type': a_type, 'tags': a_tags})

    def getdescription(self):
        """Get the description of the addon"""
        return u'description' in self.data and self.data[u'description'] or u'Description'

    def gettype(self):
        """Get the type of the addon"""
        return u'type' in self.data and self.data[u'type'] or u'type'

    def gettags(self):
        """Get the tags of the addon"""
        return u'tags' in self.data and self.data[u'tags'] or []

    def getlogo(self):
        """Get the logo of the addon"""
        return u'logo' in self.data and self.data[u'logo'] or ''

    def getauthor(self):
        """The author of the addon"""
        return 'author' in self.data and self.data['author'] or "Author Name"

    def getversion(self):
        """The addon version. This field is not used and will always return 1."""
        return 1

    def set_workshopid(self, id):
        """Set the workshop ID of the addon to id and store in addon.json"""
        self.data['workshopid'] = id
        self.save_changes()

    def save_changes(self):
        """Store the current state of the GModAddon to addon.json"""
        serialized = json.dumps(self.data, indent = 4, sort_keys = True)
        with open(self.file, 'w') as f:
            f.write(serialized)

    def getfiles(self):
        """Return a list of files in the addon
        all files are relative to the addon path
        """
        ignore = ['*' + os.path.relpath(self.file, self.path)] # Always add the addon.json file
        ignore += self.getignored()

        file_list = []

        for dir, _, files in os.walk(self.path):
            rel = os.path.relpath(dir, self.path)
            file_list += list(map(partial(os.path.join, rel), files))

        # Remove './' at the start of some paths
        file_list = sorted(list(map(partial(re.sub, r'^\.[/\\]', ''), file_list)))
        # Replace backslashes with forward slashes (Windows)
        file_list = list(map(partial(re.sub, r'\\', '/'), file_list))
        return list(filter(partial(self._file_nomatch, ignore), file_list))

    def getpath(self):
        """The path of the addon folder"""
        return self.path

    def setfile(self, file):
        self.file = file
        self.path = os.path.dirname(file)

    def _file_nomatch(self, ignore, f):
        """Whether a given file is not in the blacklist
        >>> addon_info_from_path("test")._file_nomatch(['*.psd'], 'a/b/c.psd')
        False
        >>> addon_info_from_path("test")._file_nomatch(['*.psd', '*.svn*'], 'a/b/c.lua')
        True
        """
        for pattern in ignore:
            if fnmatch(f, pattern):
                return False

        return True

    def verify_files(self):
        """Check if all files in the path are allowed in a GMA file.
        >>> addon_info_from_path("test").verify_files()
        (True, [])
        """
        file_list = self.getfiles()
        disallowed = list(filter(partial(self._file_nomatch, addon_whitelist), file_list))
        return not disallowed, disallowed

    def compress(self, output):
        """Compress the contents of a folder into a .gma file"""
        allowed, illegal_files = self.verify_files()
        if not allowed:
            return False, illegal_files

        gmafile.write(self, output)

        return True, []



class AddonNotFoundError(Exception):
    def __init__(self, path):
        self.value = path

    def __str__(self):
        return "No GMod addon found in " + os.path.abspath(self.value)

def find_addon(location, addonFile = 'addon.json'):
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
        filename = os.path.join(curLocation, addonFile)

        if os.path.isfile(filename):
            return filename

        curLocation = os.path.dirname(curLocation)
    else:
        raise AddonNotFoundError(location)

def get_addon_info(addon_info_path):
    """Get the contents of addon.json in a dictionary
    >>> isinstance(addon_info_from_path('test'), GModAddon)
    True

    >>> get_addon_info('WrongPath')
    """
    if not os.path.isfile(addon_info_path):
        return

    with open(addon_info_path, 'r') as f:
        data = json.load(f)

    return GModAddon(data, os.path.dirname(addon_info_path), addon_info_path)

def addon_info_from_path(path, addonFile = 'addon.json'):
    """Get the addon info from a folder path."""
    return get_addon_info(find_addon(path, addonFile))


addon_whitelist = [
            "maps/*.bsp",
            "maps/*.png",
            "maps/*.nav",
            "maps/*.ain",
            "sound/*.wav",
            "sound/*.mp3",
            "sound/*.ogg",
            "lua/*.lua",
            "materials/*.vmt",
            "materials/*.vtf",
            "materials/*.png",
            "materials/*.jpeg",
            "materials/*.jpg",
            "models/*.mdl",
            "models/*.vtx",
            "models/*.phy",
            "models/*.ani",
            "models/*.vvd",
            "gamemodes/*.txt",
            "gamemodes/*/gamemode/*.lua",
            "gamemodes/*/entities/effects/*.lua",
            "gamemodes/*/entities/entities/*.lua",
            "gamemodes/*/entities/weapons/*.lua",
            "gamemodes/*/backgrounds/*.jpeg",
            "gamemodes/*/backgrounds/*.png",
            "gamemodes/*/*.fgd",
            "gamemodes/*/content/models/*.mdl",
            "gamemodes/*/content/models/*.vtx",
            "gamemodes/*/content/models/*.phy",
            "gamemodes/*/content/models/*.ani",
            "gamemodes/*/content/models/*.vvd",
            "gamemodes/*/content/materials/*.vmt",
            "gamemodes/*/content/materials/*.vtf",
            "gamemodes/*/content/materials/*.png",
            "gamemodes/*/content/materials/*.jpg",
            "gamemodes/*/content/materials/*.jpeg",
            "gamemodes/*/content/scenes/*.vcd",
            "gamemodes/*/content/particles/*.pcf",
            "gamemodes/*/content/resource/fonts/*.ttf",
            "gamemodes/*/content/scripts/vehicles/*.txt",
            "gamemodes/*/content/resource/localization/*/*.properties",
            "gamemodes/*/content/maps/*.bsp",
            "gamemodes/*/content/maps/*.nav",
            "gamemodes/*/content/maps/*.ain",
            "gamemodes/*/content/maps/thumb/*.png",
            "gamemodes/*/content/sound/*.wav",
            "gamemodes/*/content/sound/*.mp3",
            "gamemodes/*/content/sound/*.ogg",
            "scenes/*.vcd",
            "particles/*.pcf",
            "gamemodes/*/backgrounds/*.jpg",
            "gamemodes/*/icon24.png",
            "gamemodes/*/logo.png",
            "scripts/vehicles/*.txt",
            "resource/localization/*/*.properties",
            "resource/fonts/*.ttf"
            ]

if __name__ == '__main__':
    import doctest
    doctest.testmod()
