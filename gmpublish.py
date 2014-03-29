#!/usr/bin/env python3
import sys

class GmPublish:
	"""Wrapper for the GMPublish program"""

	def __init__(self, addon):
		self.addon = addon

	def create(self, logo):
		"""Upload to the workshop as a new addon"""
		pass

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