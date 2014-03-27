#!/usr/bin/env python3
import argparse
import os
import addoninfo
import gmafile
from gmpublish import GmPublish

# Define command line parameters
parser = argparse.ArgumentParser(description = "Garry's mod workshop cli wrapper.")
parser.add_argument('-l', '--logo', nargs=1, help='Path of the logo image.', metavar='path')
parser.add_argument('-d', '--dir', '--path', nargs=1, help='Path where the addon is located.', metavar='path')
parser.add_argument('out', metavar='path', type=str, nargs='?', help='The output file or directory (used when creating or extracting gma files).')
parser.add_argument('-v', '--verify', action='store_true', help='Verify the contents of the current folder and exit.')
parser.add_argument('-c', '--create-gma', action='store_true', help='Create a GMA file of the addon and exit.')
parser.add_argument('-x', '-e', '--extract', nargs=1, help='Extract a GMA file and exit.', metavar='file')
parser.add_argument('-m', '--message', nargs=1, help='Update message when updating the addon.', metavar='msg')

def main():
	args = parser.parse_args()
	# working directory
	curdir = args.dir and args.dir[0] or os.getcwd()
	# directory to output things to
	out = args.out and args.out or curdir

	# Extract a GMA file
	if args.extract:
		extract(args.extract[0], out)
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
		publisher = GmPublish(addon)
		publish(addon, publisher, message)

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
	except NameError:
		print("Not a valid workshop ID.")
		request_workshopid()

#
# Actions that can be called from the command line
#

def verify_files(dir, addon):
	"""Verify if the files in the path can be compressed in a gma"""
	verified, disallowed = addon.verify_files()

	if verified:
		print("Current addon can be packed in a gma.\nNo illegal files were found.")
	else:
		print("Illegal files were found:")
		for f in disallowed: print('\t' + f)
		print("Please remove these files or add them to the ignore list of your addon.")

def creategma(addon, output_file):
	allowed, illegal_files = addon.compress(output_file)
	if not allowed:
		print("Illegal files were found:")
		for f in disallowed: print('\t' + f)
		print("Please remove these files or add them to the ignore list of your addon.")

def extract(gma_file, output_dir):
	gmafile.extract(gma_file, output_dir)

def publish(addon, publisher, message):
	if addon.has_workshop_id():
		publisher.update(message)
		return

	uploaded = request_uploaded()

	if uploaded == None:
		return
	elif uploaded:
		request_workshopid(addon)
		publisher.update(message)
		return

	publisher.create()

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		# keyboard interrupts are allowed, print a newline
		print()