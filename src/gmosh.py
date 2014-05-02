#!/usr/bin/env python3
import argparse
import sys
import os
import addoninfo
import gmafile
from gmpublish import GmPublish
from glob import glob
from itertools import chain

# Define command line parameters
parser = argparse.ArgumentParser(description = "Garry's mod workshop cli wrapper.")
parser.add_argument('--logo', '--icon', nargs=1, help='Path of the logo image.', metavar='path')
parser.add_argument('-d', '--dir', '--path', nargs=1, help='Path where the addon is located.', metavar='path')
parser.add_argument('out', metavar='path', type=str, nargs='*', help='The output file or directory (used when creating or extracting gma files).')
parser.add_argument('-p', '--publish', action='store_true', help='Publish the addon to the workshop.')
parser.add_argument('-v', '--verify', action='store_true', help='Verify the contents of the current folder and exit.')
parser.add_argument('--new', '--new-addon', action='store_true', help='Create a new addon.json at the current location. This is required before an addon can be uploaded to the workshop.')
parser.add_argument('-c', '--create-gma', action='store_true', help='Create a GMA file of the addon and exit.')
parser.add_argument('--dump', '--dump-gma', action='store_true', help='Dump a textual representation of a gma file to console.')
parser.add_argument('-x', '-e', '--extract', action='store_true', help='Extract a GMA file and exit.')
parser.add_argument('-l', '--list', action='store_true', help='List the files contained in a GMA file.')
parser.add_argument('-m', '--message', nargs=1, help='Update message when updating the addon.', metavar='msg')
parser.add_argument('-i', '--interactive', action='store_true', help='Run GMosh interactively')

def main(args):
	# working directory
	curdir = args.dir and args.dir[0] or os.getcwd()
	# directory to output things to
	out = args.out and args.out or [curdir]
	file_list = list(filter(os.path.isfile, chain.from_iterable(map(glob, out))))
	# include folders that do not exist yet:
	folder_list = list(filter(lambda x: not os.path.isfile(x), out))

	if args.extract:
		# Extract a GMA file
		extract(file_list, folder_list or ['out'])
		return
	elif args.dump:
		# Dump the contents of GMA files
		dump_gma(file_list)
		return
	elif args.list:
		# List the files contained in a GMA file(s)
		list_files(file_list)
		return
	elif args.new:
		# Wizard for creating an addon.json file
		new_addon(curdir)
		return

	# Try to get the addon information
	try:
		addon = addoninfo.addon_info_from_path(curdir)
	except addoninfo.AddonNotFoundError as err:
		print(err)
		return

	if args.verify:
		# Verify the addon files
		verify_files(curdir, addon)
	elif args.create_gma:
		# Create a GMA file from an existing addon
		creategma(addon, out)
	else:
		# Publish the addon
		message = args.message and args.message[0] or addon.getdefault_changelog()
		publish(addon, args.logo and args.logo[0], message)

def request_uploaded():
	"""Ask whether the addon exists on the workshop"""
	try:
		uploaded = input("No workshop ID found in the addon. Has this addon been uploaded to the workshop yet? (y/n)\n")
		return uploaded == 'y' or uploaded == 'yes' or uploaded == '\n'
	except EOFError:
		print("Setup cancelled")
		return None

def request_workshopid(addon):
	"""The addon is uploaded, but the workshop ID hasn't been registered yet
		This function requests the workshop ID
	"""
	try:
		inp = input("Please enter the workshop ID of the addon: ")
		addon.set_workshopid(int(inp))
	except ValueError:
		print("Not a valid workshop ID.")
		request_workshopid(addon)

#
# Actions that can be called from the command line
#

def verify_files(dir, addon):
	"""Verify if the files in the path can be compressed in a gma"""
	verified, disallowed = addon.verify_files()

	if verified:
		print("No illegal files were found.")
	else:
		print("Illegal files were found:")
		for f in disallowed: print('\t' + f)
		print("Please remove these files or add them to the ignore list of your addon.")

	return verified, disallowed

possible_types = ["gamemode", "map", "weapon", "vehicle", "npc", "tool", "effects", "model"]
possible_tags =  ["fun", "roleplay", "scenic", "movie", "realism", "cartoon", "water", "comic", "build"]
def new_addon(path):
	print("Turning \"%s\" into a workshoppable addon. Press Ctrl+C at any time to cancel." % path)
	data = dict()
	data['title'] = input("What will be the name of your addon?\n")

	print()

	# Choosing the type
	print("What will be the type of your addon? You can choose only one.")
	for i in range(0, len(possible_types)):
		print("%s: %s" % (str(i), possible_types[i]))

	while 'type' not in data or data['type'] < 0 or data['type'] >= len(possible_types):
		try:
			data['type'] = int(input("? "))
		except ValueError:
			print("Not a number")

	data['type'] = possible_types[data['type']]

	print()

	# Choosing tags
	print("Your addon can have up to two tags. You can choose from the following:")
	for i in range(0, len(possible_tags)):
		print("%s: %s" % (str(i), possible_tags[i]))

	data['tags'] = []
	for i in range(0, 2):
		if i > 0 and data['tags'][i-1] == -1: break

		while len(data['tags']) <= i or data['tags'][i] >= len(possible_tags):
			try:
				data['tags'].append(int(input("Choose tag #%s. Enter -1 to stop adding tags.\n" % str(i + 1))))
			except ValueError:
				print("Not a number")

	pop = data['tags'].pop()
	if pop != -1: data['tags'].append(pop)
	for i in range(0, len(data['tags'])): data['tags'][i] = possible_tags[data['tags'][i]]

	print()

	# Ignore list
	data['ignore'] = []
	print("Now it's time to select which files you do NOT want to ship with your addon!")
	print("Please list the file names of the files you want to ignore in the addon. Use wildcards!")
	print("Checking current directory for files that are not allowed to be in a workshop addon...")
	allowed, disallowed = addoninfo.GModAddon(data, path).verify_files()
	if allowed:
		print("No illegal files found. But maybe you still have ideas for files to ignore?")
	else:
		print("The following illegal files were found:")
		for k in disallowed: print(k)

	print("Please enter the files you want to ignore. Enter nothing or -1 to continue to the next step.")
	while True:
		ignore = input("? ")
		if ignore == "-1" or ignore == "": break
		data['ignore'].append(ignore)

	print()

	# Default changelog
	print("When updating the addon on the workshop. Do you want to have a default changelog? Leave this field empty or enter -1 if you don't.")
	default_changelog = input("? ")
	if default_changelog != "" and default_changelog != "-1":
		data['default_changelog'] = default_changelog
	else:
		print("No default changelog chosen")

	print()

	# Store to addon
	addoninfo.GModAddon(data, path).save_changes()

	print("Alright! That's it! This is the data:")
	print(data)
	print("Don't worry if you've made a mistake. You can either run this wizard again or edit the addon.json file with an editor.")
	print("Addon.json saved successfully")

def dump_gma(input_files):
	for f in input_files:
		if not os.path.isfile(f):
			print("\"%s\" is not a GMA file!" % f)
			continue

		try:
			print(gmafile.dump(f))
		except:
			print("Unable to parse \"%s\"" % f)

def creategma(addon, files):
	output_file = files[0]
	allowed, illegal_files = addon.compress(output_file)
	if not allowed:
		print("Illegal files were found:")
		for f in illegal_files: print('\t' + f)
		print("Please remove these files or add them to the ignore list of your addon.")

def extract(gma_files, directories):
	for file in gma_files:
		for output_dir in directories:
			gmafile.extract(file, output_dir)

def list_files(files):
	for gma_file in files:
		lst = gmafile.getfiles(gma_file)
		for f in lst:
			print(f)

def publish(addon, logo, message):
	publisher = GmPublish(addon)

	# Verify files first
	allowed, _ = verify_files(addon.getpath(), addon)
	if not allowed: return

	# Update if workshop ID exists in addon.json
	if addon.has_workshop_id():
		publisher.update(message)
		return

	# Ask whether the addon has been uploaded before
	uploaded = request_uploaded()

	if uploaded == None:
		return
	elif uploaded:
		request_workshopid(addon)
		publisher.update(message)
		return

	# New addons require a logo file
	while True:
		if not logo:
			print("Please provide a 512x512 logo jpg file for the initial upload.")
		elif not os.path.isfile(logo):
			print("The file \"%s\" does not exist." % logo)
		else:
			break

		logo = input("What is the path of the logo file?\n")

	succeeded, result = publisher.create(logo)
	if succeeded:
		print("Publishing to workshop succeeded!")
		print("Workshop ID set to", result)
	else:
		print("Publishing to workshop failed!")
		print(result)

if __name__ == '__main__':
	try:
		args = parser.parse_args()
		# Prevent "pipe closed" exceptions
		if sys.platform == 'linux':
			from signal import signal, SIGPIPE, SIG_DFL
			signal(SIGPIPE, SIG_DFL)

		main(args)
		if args.interactive:
			input("Press Enter to continue")
	except KeyboardInterrupt:
		# keyboard interrupts are allowed, print a newline
		print()