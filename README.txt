Compiling prerequisites (all platforms):
	Make sure python 3.3 is installed. 3.4 is untested.

	Make sure the module six is installed. The construct module depends on it.
		https://pypi.python.org/pypi/six

	Make sure the module construct is installed.
		https://pypi.python.org/pypi/construct

	cx_freeze for Python 3.3. cx_freeze for Python 3.4 appears not to work on Windows at least.
		Note: the cx_freeze package on the Ubuntu repositories is for Python 2.7. Compile the right version from source.


Compiling on Linux:
	cd to the root of the repository
	enter "make" in the terminal
	enter "sudo make install" in the terminal to install it on your system

Compiling on Windows:
	Open the command prompt in the root of the repository
	run compile_windows.bat.
		Note: You might have to change the path of cxfreeze in the batch file. Currently it's C:\Python33\Scripts\cxfreeze.

FAQ:
	Any: error about "construct" missing when running executable
		The modules six and/or construct were not installed properly at the time of compiling

	Windows: Error about zip or something when running compiled executable
		This happened to me when I tried to compile with Python 3.4 and cx_freeze for 3.4. Roll back to Python 3.3 and cx_freeze for 3.4

	Windows: Error during compiling: C:\Python33\Scripts\cxfreeze not found
		Open the batch file and change the path of cxfreeze to the real path. For some strange reason cxfreeze wasn't added to $PATH for me.

	Linux: All sorts of exceptions when running the compiled program
		You might have compiled with cx_freeze for Python 2.7, which is the default cx_freeze in some package repositories.
