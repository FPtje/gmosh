#!/usr/bin/env python3
import sys
import subprocess
import re
import os

class GmPublish:
	"""Wrapper for the GMPublish program"""

	def __init__(self, addon):
		self.addon = addon

	def create(self):
		"""Upload to the workshop as a new addon. Returns (succeeded, strResult)
		precondition: Assumes that the files of the addon have been verified.
		"""
		outfile = os.path.join(self.addon.getpath(), 'temp.gma')
		logo = self.addon.getlogo()

		print("Compressing to temporary GMA file...")
		self.addon.compress(outfile)

		print("Publishing GMA file to workshop...\n")

		# Call gmpublish to create the addon
		try:
			output = subprocess.check_output([self._get_executable(), 'create',
						'-addon', outfile,
						'-icon', logo
					])
		except subprocess.CalledProcessError as e:
			os.remove(outfile)
			return False, e.output.decode('utf-8')

		# Remove the temporary file
		os.remove(outfile)

		output = output.decode('utf-8')
		match = re.search('UID: ([0-9]+)', output)

		# Try to find the addon ID
		if match and match.group(1):
			self.addon.set_workshopid(int(match.group(1)))
			return True, match.group(1)

		# Assumption: something must have gone wrong when no addon ID could be found
		return False, output


	def update(self, message=None):
		"""Push an update of the addon to the workshop"""
		message = message or self.addon.getdefault_changelog()
		outfile = os.path.join(self.addon.getpath(), 'temp.gma')
		print("Compressing to temporary GMA file...")
		self.addon.compress(outfile)

		print("Publishing GMA file to workshop...\n")

		# Call GMPublish to update
		try:
			params = [self._get_executable(), 'update',
						'-addon', outfile,
						'-id', str(self.addon.getworkshopid()),
						'-changes', message
					]
			if self.addon.getlogo():
				params.append('-icon')
				params.append(self.addon.getlogo())

			output = subprocess.check_output(params)
			print(output.decode('utf-8'))
		except subprocess.CalledProcessError as e:
			print(e.output.decode('utf-8'))
			print("Upload to workshop failed!")

		os.remove(outfile)

	def _get_executable(self):
		"""Retrieve the path of the gmpublish executable"""
		platform = sys.platform
		if platform == 'linux':
			return 'gmpublish_linux'
		elif platform == 'windows' or platform == "win32":
			return 'gmpublish.exe'
		elif platform == 'darwin': #untested
			return 'gmpublish_osx'

		raise NameError("Could not find executable for platform " + platform)
