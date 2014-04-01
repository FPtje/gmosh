MODULES=addoninfo,gmafile,gmpublish

linux:
	if [ ! -d bin ]; then mkdir bin; fi
	cxfreeze src/gmosh.py --target-dir=bin --include-modules=$(MODULES)

osx:
	if [ ! -d bin ]; then mkdir bin; fi
	/Library/Frameworks/Python.framework/Versions/3.3/bin/cxfreeze src/gmosh.py --target-dir=bin --include-modules=$(MODULES)

install_linux:
	if [ ! -d /opt/gmosh ]; then mkdir /opt/gmosh; fi
	cp bin/* /opt/gmosh
	cp required/gmpublish_linux /opt/gmosh
	cp required/libsteam_api.so /opt/gmosh

	ln -sf /opt/gmosh/gmosh /usr/bin/gmosh

	cp required/steam_appid.txt /opt/gmosh/steam_appid.txt # Has to be in same folder as gmpublish_linux
	chmod +x /opt/gmosh/gmpublish_linux
	chmod +x /opt/gmosh/gmosh

	@echo "Checking existence of libsteam.so"
	if [ ! -f ~/.steam/linux32/libsteam.so ]; then mkdir -p ~/.steam/linux32/ && cp required/libsteam.so ~/.steam/linux32/; fi
	@echo "Installation completed successfully"

install_osx:
	if [ ! -d /opt/gmosh ]; then mkdir /opt/gmosh; fi
	cp bin/* /opt/gmosh
	cp required/gmpublish_osx /opt/gmosh
	cp required/libsteam_api.dylib /opt/gmosh

	ln -sf /opt/gmosh/gmosh /usr/bin/gmosh

	cp required/steam_appid.txt /opt/gmosh/steam_appid.txt # Has to be in same folder as gmpublish_osx
	chmod +x /opt/gmosh/gmpublish_osx
	chmod +x /opt/gmosh/gmosh

	@echo "Installation completed successfully"

uninstall_linux:
	if [ -L /usr/bin/gmosh ]; then rm /usr/bin/gmosh; fi
	if [ -d /opt/gmosh ]; then rm -r /opt/gmosh; fi

uninstall_osx: uninstall_linux

# Make a Linux distributable package
package_linux: linux
	if [ ! -d package ]; then mkdir package; fi
	if [ ! -d package/Linux ]; then mkdir package/Linux; fi
	if [ ! -d package/Linux/bin ]; then mkdir package/Linux/bin; fi

	cp bin/* package/Linux/bin/

	if [ ! -d package/Linux/required ]; then mkdir package/Linux/required; fi
	cp required/gmpublish_linux package/Linux/required/
	cp required/steam_appid.txt package/Linux/required/
	cp required/libsteam_api.so package/Linux/required/
	cp required/libsteam.so package/Linux/required/

	cp README.txt package/Linux/

	@echo "Packaging completed successfully"

package_osx: osx
	if [ ! -d package ]; then mkdir package; fi
	if [ ! -d package/OSX ]; then mkdir package/OSX; fi
	if [ ! -d package/OSX/bin ]; then mkdir package/OSX/bin; fi

	cp bin/* package/OSX/bin/

	if [ ! -d package/OSX/required ]; then mkdir package/OSX/required; fi
	cp required/gmpublish_osx package/OSX/required/
	cp required/steam_appid.txt package/OSX/required/
	cp required/libsteam_api.dylib package/OSX/required/

	cp README.txt package/OSX/

	@echo "Packaging completed successfully"


clean:
	if [ -d bin ]; then rm -r bin; fi
	if ls *.pyc 2> /dev/null; then rm *.pyc; fi
	if [ -d __pycache__ ]; then rm -r __pycache__; fi