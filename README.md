# Gmosh

A CLI interface for publishing packages, and a simple graphical interface for inspecting GMA files.

**WARNING** Unmaintained! Unsupported! Publishing packages no longer works because the included `gmpublish` is out-of-date!

## Installation

When you just want to install it, please download the binaries from here:
<https://github.com/FPtje/gmosh/releases>

## How to use gmosh

Gmosh is a command line interface (cli) program. This means that the program has no visual interface.
Rather, it is run from the command prompt/terminal. This might sound frightening, but it makes sense:
Typing is faster than pointing and clicking, this program was made so updates can be pushed to the workshop /super fast/.
Gmosh was loosely inspired by the git cli. Pushing an update to a git repository is as easy as entering "git push" in the terminal.
Likewise, publishing an update to the workshop is as easy as entering "gmosh" in the terminal.

Cli justification aside, you can do many things with gmosh. When you don't know how to do something,
you can run gmosh --help in the terminal. Here are some examples:

### Publish an addon to the workshop/Update an addon on the workshop

If you're publishing the addon for the first time, run the following command:

```bash
gmosh --logo test.jpg
```

When updating you can just run

```bash
gmosh
```

Note: If the addon has been published to the workshop before, gmosh will ask for the workshop ID once (and only once!)
This workshop ID can be found in the URL of the workshop addon.

### Extract a gma file

```bash
gmosh -e SomeGMAFile.gma out/directory/
```

or

```bash
gmosh --extract SomeGMAFile.gma out/directory/
```

### Create a gma file from an addon

```bash
gmosh -c --dir addon_directory output.gma
```

or

```bash
gmosh --create-gma # creates `out.gma` from the addon in `addon_directory`
```

### Check for "illegal" files in the current folder

Illegal files are files that are not allowed to be in a gma file.

```bash
gmosh -v
```

or

```bash
gmosh --verify directory
```

### List the contents of a gma file

```bash
gmosh -l SomeGMAFile.gma
```

or

```bash
gmosh --list SomeGMAFile.gma
```

### Generate an addon.json file

This is an easy way to turn your addon into a workshoppable one.

```bash
gmosh --new
```

or

```bash
gmosh --new-addon addons/MyAddon
```

## Extra fields in addon.json

The addon.json file contains the necessary information to publish addons to the workshop.
In addition to the default fields, gmosh understands some more.

### default_changelog, string

When you're too lazy to type a new changelog every time you update your addon,
the default changelog is the right thing for you.

```bash
"default_changelog": "All changes can be found on my website"
```

### workshopid, int

The ID of the addon on the workshop. gmosh uses this ID to know where to upload the addon to.
If you do not enter this yourself, gmosh will ask it once and then store it in the addon.json file.

```bash
"workshopid": 123456789
```

### Other

The following fields are read and then put in the GMA, but I am unsure what they do.
They might cause problems when you fill them in.

- steamid64, int
- description, string
- author, string

## Compiling

### Compiling prerequisites (all platforms)

Make sure python 3.8 or 3.7 is installed.

Make sure the module construct is installed. <https://pypi.org/project/construct/>
If you want to compile binaries, then make sure to install cx_freeze: <https://pypi.org/project/cx-Freeze/>

### Compiling on Linux

cd to the root of the repository
enter "make" in the terminal
enter "sudo make install_linux" in the terminal to install it on your system

### Compiling on OS X

cd to the root of the repository
enter "make osx" in the terminal
enter "sudo make install_osx" in the terminal to install it on your system
Note: You may have to change the path of cxfreeze in the makefile. Currently it's /Library/Frameworks/Python.framework/Versions/3.8/bin/cxfreeze

### Compiling on Windows

Open the command prompt in the root of the repository
run compile_windows.bat.
Note: You might have to change the path of cxfreeze in the batch file. Currently it's C:\Python33\Scripts\cxfreeze.

## FAQ

### Compiling any: Errors about "No module named 'addoninfo'"

You're trying to compile the pre-built version. Please download the source.

### Compiling any: error about "construct" missing when running executable

The modules six and/or construct were not installed properly at the time of compiling

### Compiling Windows: Error about zip or something when running compiled executable

This happened to me when I tried to compile with Python 3.4 and cx_freeze for 3.4. Roll back to Python 3.3 and cx_freeze for 3.4

### Compiling Windows: Error during compiling: C:\Python33\Scripts\cxfreeze not found

Open the batch file and change the path of cxfreeze to the real path. For some strange reason cxfreeze wasn't added to $PATH for me.

### Compiling Linux: All sorts of exceptions when running the compiled program

You might have compiled with cx_freeze for Python 2.7, which is the default cx_freeze in some package repositories.

### Compiling Windows: You get this cx-freeze exception when trying to run the compiled version

```bash
$ gmosh --help
Traceback (most recent call last):
  File "C:\Python34\lib\site-packages\cx_Freeze\initscripts\Console.py", line 27, in <module>
    exec(code, m.__dict__)
  File "src/gmosh/gmosh.py", line 5, in <module>
  File "c:\Python\64-bit\3.4\lib\importlib\_bootstrap.py", line 2214, in _find_and_load
  File "c:\Python\64-bit\3.4\lib\importlib\_bootstrap.py", line 2203, in _find_and_load_unlocked
  File "c:\Python\64-bit\3.4\lib\importlib\_bootstrap.py", line 1191, in _load_unlocked
  File "c:\Python\64-bit\3.4\lib\importlib\_bootstrap.py", line 1161, in _load_backward_compatible
AttributeError: 'module' object has no attribute '_fix_up_module'
```

Please see this link:
<http://stackoverflow.com/questions/23920073/cx-freeze-error-python-34>
