#!/usr/bin/env python3

class GMad:
	"""Class to verify files for, create and extract Garry's Mod Addon (gma) files"""

	def __init__(self, path, addon = None):
		self.path = path
		self.addon = addon

	def getfiles(self):
		"""Return a list of files in the addon
		all files are relative to the addon path
		"""
		ignore = []
		if self.addon is not None:
			ignore = self.addon.getignored()


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