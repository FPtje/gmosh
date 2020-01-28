#!/usr/bin/env python3
"""Represents the Garry's mod folder"""

import os
import lzma
import re

commonGModPaths = [
    "C:/Program Files/Steam/SteamApps/common/GarrysMod/garrysmod",
    "C:/Program Files (x86)/Steam/SteamApps/common/GarrysMod/garrysmod",
    "D:/Program Files/Steam/SteamApps/common/GarrysMod/garrysmod",
    "D:/Program Files (x86)/Steam/SteamApps/common/GarrysMod/garrysmod",
    "~/.steam/steam/SteamApps/common/GarrysMod/garrysmod",
    "~/.local/share/Steam/SteamApps/common/GarrysMod/garrysmod",
    "~/Library/Application Support/Steam/SteamApps/common/GarrysMod/garrysmod",
]


class GModFolder:
    """Represents GMod folder"""

    def __init__(self, path=None):
        self.path = path

    def find_gmod_folder(self):
        for f in commonGModPaths:
            f = os.path.expanduser(f)
            if os.path.isdir(f):
                self.path = f
                return True

        return False

    def get_cache_folder(self):
        if not self.path:
            return False

        cachepath = os.path.join(self.path, "cache/lua")

        if not os.path.isdir(cachepath):
            return False

        return cachepath

    def extract_cache_file(self, f):
        with open(f, 'rb') as ff:
            contents = ff.read()
            # First 32 bytes as base
            decompressed = lzma.decompress(contents[32:])
            # Last byte is \0
            return decompressed[:-1]

    def extract_cache_files(self, out, fil=None):
        if not self.path:
            return False

        cachedir = self.get_cache_folder()

        it = os.listdir(cachedir)
        print("Unpacking %i files..." % (fil and len(fil) or len(it)))
        for f in it:
            ff = os.path.join(cachedir, f)

            ff = os.path.normpath(ff)
            if not f.endswith(".lua") or (fil and ff not in fil):
                continue

            data = self.extract_cache_file(ff)
            outfile = os.path.join(out, f)

            with open(outfile, 'wb') as of:
                of.write(data)
                of.close()

            del data

    def search_cache(self, regex):
        if not self.path:
            return []

        pattern = re.compile(regex)
        res = []
        cachedir = self.get_cache_folder()
        it = os.listdir(cachedir)

        print("Searching %i files..." % len(it))
        for f in it:
            ff = os.path.join(cachedir, f)
            if not f.endswith(".lua"):
                continue

            if re.search(pattern, self.extract_cache_file(ff).decode('utf-8', 'replace')):
                res.append(f)

        return res
