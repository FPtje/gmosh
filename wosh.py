#!/usr/bin/env python3
import argparse
import os
import addoninfo
from gmpublish import GmPublish

def main():
	# Define command line parameters
	parser = argparse.ArgumentParser(description = "Garry's mod workshop cli wrapper.")
	args = parser.parse_args()
	curdir = os.getcwd()

	# Try to get the addon information
	try:
		addon = addoninfo.get_addon_info(addoninfo.find_addon(curdir))
		publisher = GmPublish(addon)
	except addoninfo.AddonNotFoundError as err:
		print(err)
		return

	# The addon can be updated if it has a workshop id
	if addon.has_workshop_id():
		publisher.update()
		return

	# otherwise the question must be asked whether it already exists
	try:
		uploaded = input("No workshop ID found in the addon. Has this addon been uploaded to the workshop yet? (y/n)")
		uploaded = uploaded == 'y' or uploaded == 'yes' or uploaded == '\n'
	except EOFError:
		print("Setup cancelled")
		return

	# The addon is uploaded, but the workshop ID hasn't been registered yet
	if uploaded:
		try:
			addon.set_workshopid(int(input("Please enter the workshop ID of the addon.")))
		except NameError:
			pass


if __name__ == '__main__':
	main()