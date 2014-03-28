MODULES=addoninfo,gmafile,gmpublish

linux:
	if [ ! -d bin ]; then mkdir bin; fi
	cxfreeze gmosh.py --target-dir=bin --include-modules=$(MODULES)

clean:
	rm -r bin
