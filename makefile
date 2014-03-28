MODULES=addoninfo,gmafile,gmpublish

linux:
	if [ ! -d bin ]; then mkdir bin; fi
	cxfreeze gmosh.py --target-dir=bin --include-modules=$(MODULES)

clean:
	if [ -d bin ]; then rm -r bin; fi
	if [ -f *.pyc ]; then rm *.pyc; fi
	if [ -d __pycache__ ]; then rm -r __pycache__; fi