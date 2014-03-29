#!/usr/bin/env python3
import sys
import subprocess
import re
import os

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

		# Call gmpublish to create the addon
		output = subprocess.check_output([self._get_executable(), 'create',
			'-addon', outfile,
			'-icon', logo
		])

		output = output.decode('utf-8')
		match = re.search('UID: ([0-9]+)', output)

		# Try to find the addon ID
		if match and match.group(1):
			self.addon.set_workshopid(int(match.group(1)))
			print("Publishing to workshop succeeded!")
			print("Workshop ID set to", match.group(1))
		else:
			print("Publishing to workshop failed!")
			print(output)

		os.remove(outfile)

	def update(self, message=None):
		"""Push an update of the addon to the workshop"""
		message = message or self.addon.getdefault_changelog()
		outfile = 'temp.gma'
		self.addon.compress(outfile)

		# Call GMPublish to update
		output = subprocess.check_output([self._get_executable(), 'update',
			'-addon', outfile,
			'-id', str(self.addon.getworkshopid()),
			'-changes', message
		])

		print(output.decode('utf-8'))

		os.remove(outfile)

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