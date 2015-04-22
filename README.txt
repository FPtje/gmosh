Installation:
	Please see HOW TO INSTALL.txt

IMPORTANT:
	On Linux, gmoshui will NOT work and throw a big nasty ImportError if you don't have python3-pyside installed!
	I currently have no way of circumventing this. Sorry for the inconvenience!

How to use gmosh:
	gmosh is a command line interface (cli) program. This means that the program has no visual interface.
	Rather, it is run from the command prompt/terminal. This might sound frightening, but it makes sense:
	Typing is faster than pointing and clicking, this program was made so updates can be pushed to the workshop /super fast/.
	Gmosh was loosely inspired by the git cli. Pushing an update to a git repository is as easy as entering "git push" in the terminal.
	Likewise, publishing an update to the workshop is as easy as entering "gmosh" in the terminal.

	Cli justification aside, you can do many things with gmosh. When you don't know how to do something,
	you can run gmosh --help in the terminal. Here are some examples:

	-- Publish an addon to the workshop
	gmosh --logo test.jpg
	or just
	gmosh

	Note: If the addon has been published to the workshop before, gmosh will ask for the workshop ID once (and only once!)
	This workshop ID can be found in the URL of the workshop addon.

	-- Extract a gma file:
	gmosh -e SomeGMAFile.gma out/directory/
	or
	gmosh --extract SomeGMAFile.gma out/directory/

	-- Create a gma file from an addon
	gmosh -c addon_directory --out output.gma
	or
	gmosh --create-gma # creates out.gma based on the current directory

	-- Check for "illegal" files in the current folder.
	-- Illegal files are files that are not allowed to be in a gma file.
	gmosh -v
	or
	gmosh --verify directory

	-- List the contents of a gma file
	gmosh -l SomeGMAFile.gma
	or
	gmosh --list SomeGMAFile.gma

	-- Generate an addon.json file
	gmosh --new
	or
	gmosh --new-addon addons/MyAddon

Extra fields in addon.json
	The addon.json file contains the necessary information to publish addons to the workshop.
	In addition to the default fields, gmosh understands some more.

	default_changelog, string: When you're too lazy to type a new changelog every time you update your addon,
	the default changelog is the right thing for you.
	"default_changelog": "All changes can be found on my website"

	workshopid, int: The ID of the addon on the workshop. gmosh uses this ID to know where to upload the addon to.
	If you do not enter this yourself, gmosh will ask it once and then store it in the addon.json file.
	"workshopid": 123456789

	The following fields are read and then put in the GMA, but I am unsure what they do.
	They might cause problems when you fill them in.

	steamid64, int
	description, string
	author, string

Compiling prerequisites (all platforms):
	Make sure python 3.3 is installed. 3.4 is untested.

	Make sure the module six is installed. The construct module depends on it.
		https://pypi.python.org/pypi/six

	Make sure the module construct is installed.
		https://pypi.python.org/pypi/construct

	cx_freeze for Python 3.3. cx_freeze for Python 3.4 appears not to work on Windows.
		Note: the cx_freeze package on the Ubuntu repositories is for Python 2.7. Compile the right version from source.

Compiling on Linux:
	cd to the root of the repository
	enter "make" in the terminal
	enter "sudo make install_linux" in the terminal to install it on your system

Compiling on OS X:
	cd to the root of the repository
	enter "make osx" in the terminal
	enter "sudo make install_osx" in the terminal to install it on your system
		Note: You may have to change the path of cxfreeze in the makefile. Currently it's /Library/Frameworks/Python.framework/Versions/3.3/bin/cxfreeze

Compiling on Windows:
	Open the command prompt in the root of the repository
	run compile_windows.bat.
		Note: You might have to change the path of cxfreeze in the batch file. Currently it's C:\Python33\Scripts\cxfreeze.

FAQ:
	Compiling any: Errors about "No module named 'addoninfo'"
		You're trying to compile the pre-built version. Please download the source.

	Compiling any: error about "construct" missing when running executable
		The modules six and/or construct were not installed properly at the time of compiling

	Compiling Windows: Error about zip or something when running compiled executable
		This happened to me when I tried to compile with Python 3.4 and cx_freeze for 3.4. Roll back to Python 3.3 and cx_freeze for 3.4

	Compiling Windows: Error during compiling: C:\Python33\Scripts\cxfreeze not found
		Open the batch file and change the path of cxfreeze to the real path. For some strange reason cxfreeze wasn't added to $PATH for me.

	Compiling Linux: All sorts of exceptions when running the compiled program
		You might have compiled with cx_freeze for Python 2.7, which is the default cx_freeze in some package repositories.
