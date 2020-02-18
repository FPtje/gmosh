MODULES=addoninfo,gmafile,gmpublish,workshoputils

gui:
	uic -g python ui/mainwindow.ui -o src/view/mainwindow.py
	uic -g python ui/progressdialog.ui -o src/view/progressdialog.py

linux: gui
	if [ ! -d bin ]; then mkdir bin; fi
	cxfreeze src/gmosh.py --target-dir=bin --include-modules=$(MODULES)
	cxfreeze src/gmoshui.py --target-dir=bin --include-modules=$(MODULES),atexit

osx: gui
	if [ ! -d bin ]; then mkdir bin; fi
	/Library/Frameworks/Python.framework/Versions/3.8/bin/cxfreeze src/gmosh.py --target-dir=bin --include-modules=$(MODULES)
	/Library/Frameworks/Python.framework/Versions/3.8/bin/cxfreeze src/gmoshui.py --target-dir=bin --include-modules=$(MODULES),atexit

install_linux: uninstall_linux
	if [ ! -d /opt/gmosh ]; then mkdir -p /opt/gmosh; fi
	cp -r bin/* /opt/gmosh
	cp required/gmpublish_linux /opt/gmosh
	cp required/libsteam_api.so /opt/gmosh

	# Copy desktop and mime files
	cp res/gmoshui.desktop /usr/share/applications/
	cp res/icon.png /usr/share/pixmaps/gmosh_256.png
	xdg-mime install --mode system res/x-gma.xml
	xdg-mime default gmoshui.desktop application/x-gma

	ln -sf /opt/gmosh/gmosh /usr/local/bin/gmosh
	ln -sf /opt/gmosh/gmoshui /usr/local/bin/gmoshui
	ln -sf /opt/gmosh/libsteam_api.so /usr/lib/libsteam_api.so
	ln -sf /opt/gmosh/gmpublish_linux /usr/local/bin/gmpublish_linux

	cp required/steam_appid.txt /opt/gmosh/steam_appid.txt # Has to be in same folder as gmpublish_linux
	chmod +x /opt/gmosh/gmpublish_linux
	chmod +x /opt/gmosh/gmosh

	@echo "Checking existence of libsteam.so"
	if [ ! -f ~/.steam/linux32/libsteam.so ]; then mkdir -p ~/.steam/linux32/ && cp required/libsteam.so ~/.steam/linux32/; fi
	@echo "Installation completed successfully"

	@echo "NOTE! IMPORTANT! gmoshui WILL NOT WORK if python3-pyside isn't installed."

install_osx: uninstall_osx
	if [ ! -d /opt/gmosh ]; then mkdir -p /opt/gmosh; fi
	cp -r bin/* /opt/gmosh
	cp required/gmpublish_osx /opt/gmosh
	cp required/libsteam_api.dylib /opt/gmosh

	ln -sf /opt/gmosh/libsteam_api.dylib /usr/lib/libsteam_api.dylib
	ln -sf /opt/gmosh/gmpublish_osx /usr/local/bin/gmpublish_osx

	ln -sf /opt/gmosh/gmosh /usr/local/bin/gmosh
	ln -sf /opt/gmosh/gmoshui /usr/local/bin/gmoshui

	cp required/steam_appid.txt /opt/gmosh/steam_appid.txt # Has to be in same folder as gmpublish_osx
	chmod +x /opt/gmosh/gmpublish_osx
	chmod +x /opt/gmosh/gmosh

	@echo "Installation completed successfully"

uninstall_linux:
	# Desktop and mime files
	if [ -L /usr/share/applications/gmoshui.desktop ]; then rm /usr/share/applications/gmoshui.desktop; fi
	if [ -L /usr/share/pixmaps/gmosh_256.png ]; then rm /usr/share/pixmaps/gmosh_256.png; fi

	if [ -L /usr/bin/gmosh ]; then rm /usr/bin/gmosh; fi
	if [ -L /usr/local/bin/gmosh ]; then rm /usr/local/bin/gmosh; fi
	if [ -d /opt/gmosh ]; then rm -r /opt/gmosh; fi
	if [ -L /usr/lib/libsteam_api.so ]; then rm /usr/lib/libsteam_api.so; fi
	if [ -L /usr/lib/libsteam_api.dylib ]; then rm /usr/lib/libsteam_api.dylib; fi
	if [ -L /usr/bin/gmpublish_linux ]; then rm /usr/bin/gmpublish_linux; fi
	if [ -L /usr/local/bin/gmpublish_linux ]; then rm /usr/local/bin/gmpublish_linux; fi
	if [ -L /usr/bin/gmpublish_osx ]; then rm /usr/bin/gmpublish_osx; fi
	if [ -L /usr/local/bin/gmpublish_osx ]; then rm /usr/local/bin/gmpublish_osx; fi

uninstall_osx: uninstall_linux

# Make a Linux distributable package
package_linux: linux
	if [ ! -d package ]; then mkdir package; fi
	if [ ! -d package/Linux ]; then mkdir package/Linux; fi
	if [ ! -d package/Linux/bin ]; then mkdir package/Linux/bin; fi

	cp -r bin/* package/Linux/bin/

	cp -r res package/Linux/

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

	cp -r bin/* package/OSX/bin/
	cp -r res package/OSX/

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
