#!/usr/bin/env /bin/bash
tty -s; if [ $? -ne 0 ]; then
	[ "$UID" -eq 0 ] || exec gksu bash "$0" "$@"
else
	[ "$UID" -eq 0 ] || exec sudo bash "$0" "$@"
fi

echo "Uninstall log:" > uninstall.log

if [ -L /usr/bin/gmosh ]; then rm /usr/bin/gmosh >> uninstall.log 2>> uninstall.log; fi
if [ -d /opt/gmosh ]; then rm -r /opt/gmosh >> uninstall.log 2>> uninstall.log; fi
if [ -L /usr/lib/libsteam_api.so ]; then rm /usr/lib/libsteam_api.so >> uninstall.log 2>> uninstall.log; fi
if [ -L /usr/bin/gmpublish_linux ]; then rm /usr/bin/gmpublish_linux >> uninstall.log 2>> uninstall.log; fi

echo "" >> uninstall.log
echo "Uninstallation completed" >> uninstall.log

tty -s; if [ $? -ne 0 ]; then
	xmessage -file uninstall.log
	rm uninstall.log
else
	cat uninstall.log
	rm uninstall.log
fi