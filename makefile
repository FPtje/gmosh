MODULES=addoninfo,gmafile,gmpublish

linux:
	if [ ! -d bin ]; then mkdir bin; fi
	cxfreeze gmosh.py --target-dir=bin --include-modules=$(MODULES)

install:
	cp bin/gmosh /usr/bin

uninstall:
	if [ -f /usr/bin/gmosh ]; then rm /usr/bin/gmosh; fi

clean:
	if [ -d bin ]; then rm -r bin; fi
	if ls *.pyc 2> /dev/null; then rm *.pyc; fi
	if [ -d __pycache__ ]; then rm -r __pycache__; fi