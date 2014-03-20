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

		return list(filter(partial(_file_ignored, ignore), file_list))

	def _file_ignored(ignore, f):
		"""Whether a given file is in the ignore list"""
		for pattern in ignore:
			if fnmatch(f, pattern):
				return False

		return True

	def verify_files(self):
		"""Check if all files in the path are allowed in a GMA file.
		#>>> GMad("test").verify_files()
		True
		"""
		pass

	def file_allowed(self, file):
		"""Whether a certain file is allowed to be in a GMA file.
		Note: the file path is relative to the addon.
		#>>> file_allowed("notRelative/lua/stubborn.lua")
		False
		#>>> file_allowed("lua/correct.lua")
		True
		"""
		pass

	def compress(self, addon):
		"""Compress the contents of a folder into a .gma file"""
		pass

	def decompress(self, file):
		"""Decompress a .gma file to the working path"""
		pass

if __name__ == '__main__':
    import doctest
    doctest.testmod()