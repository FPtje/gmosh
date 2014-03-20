#!/usr/bin/env python3
import os
from functools import partial
from fnmatch import fnmatch

class GMad:
	"""Class to verify files for, create and extract Garry's Mod Addon (gma) files"""

	def __init__(self, path, addon = None):
		self.path = path
		self.addon = addon

	def getfiles(self):
		"""Return a list of files in the addon
		all files are relative to the addon path
		"""
		ignore = ['*addon.json']
		if self.addon is not None:
			ignore += self.addon.getignored()

		file_list = []
		for dir, _, files in os.walk(self.path):
			rel = os.path.relpath(dir, self.path)
			file_list += list(map(partial(os.path.join, rel), files))

		return list(filter(partial(self._file_nomatch, ignore), file_list))

	def _file_nomatch(self, ignore, f):
		"""Whether a given file is in the ignore list"""
		for pattern in ignore:
			if fnmatch(f, pattern):
				return False

		return True

	def verify_files(self):
		"""Check if all files in the path are allowed in a GMA file.
		>>> from addoninfo import *;GMad("test", addon_info_from_path("test")).verify_files()
		(True, [])
		"""
		file_list = self.getfiles()
		disallowed = list(filter(partial(self._file_nomatch, addon_whitelist), file_list))
		return not disallowed, disallowed

	def compress(self, addon):
		"""Compress the contents of a folder into a .gma file"""
		pass

	def decompress(self, file):
		"""Decompress a .gma file to the working path"""
		pass

addon_whitelist = ["maps/*.bsp",
			"maps/*.png",
			"maps/*.nav",
			"maps/*.ain",
			"sound/*.wav",
			"sound/*.mp3",
			"lua/*.lua",
			"materials/*.vmt",
			"materials/*.vtf",
			"materials/*.png",
			"models/*.mdl",
			"models/*.vtx",
			"models/*.phy",
			"models/*.ani",
			"models/*.vvd",
			"gamemodes/*.txt",
			"gamemodes/*.lua",
			"scenes/*.vcd",
			"particles/*.pcf",
			"gamemodes/*/backgrounds/*.jpg",
			"gamemodes/*/icon24.png",
			"gamemodes/*/logo.png",
			"scripts/vehicles/*.txt",
			"resource/fonts/*.ttf"]

if __name__ == '__main__':
    import doctest
    doctest.testmod()