MODULES=addoninfo,gmafile,gmpublish

linux:
	if [ ! -d bin ]; then mkdir bin; fi
	cxfreeze src/gmosh.py --target-dir=bin --include-modules=$(MODULES)

install:
	cp bin/gmosh /usr/bin
	cp required/gmpublish_linux /usr/bin
	cp required/libsteam_api.so /usr/lib/

	cp required/steam_appid.txt /usr/bin/steam_appid.txt # Has to be in same folder as gmpublish_linux
	chmod +x /usr/bin/gmpublish_linux

	@echo "Checking existence of libsteam.so"
	if [ ! -f ~/.steam/linux32/libsteam.so ]; then mkdir -p ~/.steam/linux32/ && cp required/libsteam.so ~/.steam/linux32/; fi

uninstall:
	if [ -f /usr/bin/gmosh ]; then rm /usr/bin/gmosh; fi
	if [ -f /usr/bin/gmpublish_linux ]; then rm /usr/bin/gmpublish_linux; fi
	if [ -f /usr/bin/steam_appid.txt ]; then rm /usr/bin/steam_appid.txt; fi
	if [ -f /usr/lib/libsteam_api.so ]; then rm /usr/lib/libsteam_api.so; fi

# Make a Linux distributable package
package: linux
	if [ ! -d package ]; then mkdir package; fi
	if [ ! -d package/bin ]; then mkdir package/bin; fi
	cp makefile package/
	cp bin/gmosh package/bin/

	echo "Installation: open a terminal in this folder and use \"sudo make install\"" > package/README.txt

	if [ ! -d package/required ]; then mkdir package/required; fi
	cp required/gmpublish_linux package/required/
	cp required/libsteam_api.so package/required/
	cp required/libsteam.so package/required/


clean:
	if [ -d bin ]; then rm -r bin; fi
	if ls *.pyc 2> /dev/null; then rm *.pyc; fi
	if [ -d __pycache__ ]; then rm -r __pycache__; fi