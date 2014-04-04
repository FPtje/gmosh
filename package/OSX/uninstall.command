#!/usr/bin/env /bin/bash
[ "$UID" -eq 0 ] || exec sudo bash "$0" "$@"
cd `dirname $0`

echo "Uninstall log:" > uninstall.log

if [ -L /usr/bin/gmosh ]; then rm /usr/bin/gmosh >> uninstall.log 2>> uninstall.log; fi
if [ -d /opt/gmosh ]; then rm -r /opt/gmosh >> uninstall.log 2>> uninstall.log; fi
if [ -L /usr/lib/libsteam_api.dylib ]; then rm /usr/lib/libsteam_api.dylib >> uninstall.log 2>> uninstall.log; fi
if [ -L /usr/bin/gmpublish_osx ]; then rm /usr/bin/gmpublish_osx >> uninstall.log 2>> uninstall.log; fi

echo "" >> uninstall.log
echo "Uninstallation completed" >> uninstall.log

cat uninstall.log
rm uninstall.log