#!/usr/bin/env python3
import sys
import subprocess

class GmPublish:
	"""Wrapper for the GMPublish program"""

	def __init__(self, addon):
		self.addon = addon

	def create(self, logo):
		"""Upload to the workshop as a new addon.
		precondition: Assumes that the files of the addon have been verified.
		"""
		outfile = 'temp.gma'
		self.addon.compress(outfile)

		output = subprocess.check_output([self._get_executable(), 'create', '-addon', outfile, '-icon', logo])
		output = output.decode('utf-8')
		print(output)

	def update(self, message=None):
		"""Push an update of the addon to the workshop"""
		message = message or self.addon.getdefault_changelog()

	def _get_executable(self):
		"""Retrieve the path of the gmpublish executable"""
		platform = sys.platform
		if platform == 'linux':
			return 'gmpublish_linux'
		elif platform == 'windows':
			return 'gmpublish.exe'
		elif platform == 'darwin': #untested
			return 'gmpublish_osx'

		raise NameError("Could not find executable for platform " + platform)