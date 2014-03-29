MODULES=addoninfo,gmafile,gmpublish

linux:
	if [ ! -d bin ]; then mkdir bin; fi
	cxfreeze gmosh.py --target-dir=bin --include-modules=$(MODULES)

install:
	cp bin/gmosh /usr/bin
	cp required/gmpublish_linux /usr/bin
	cp required/libsteam_api.so /usr/lib/
	echo "4000" > /usr/bin/steam_appid.txt # Has to be in same folder as gmpublish_linux

	@echo "Checking existence of libsteam.so"
	if [ ! -f ~/.steam/linux32/libsteam.so ]; then mkdir -p ~/.steam/linux32/ && cp required/libsteam.so ~/.steam/linux32/; fi


uninstall:
	if [ -f /usr/bin/gmosh ]; then rm /usr/bin/gmosh; fi

clean:
	if [ -d bin ]; then rm -r bin; fi
	if ls *.pyc 2> /dev/null; then rm *.pyc; fi
	if [ -d __pycache__ ]; then rm -r __pycache__; fi