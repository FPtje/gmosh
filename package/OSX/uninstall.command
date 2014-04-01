#!/usr/bin/env /bin/bash
[ "$UID" -eq 0 ] || exec sudo bash "$0" "$@"

echo "Uninstall log:" > uninstall.log

if [ -L /usr/bin/gmosh ]; then rm /usr/bin/gmosh >> uninstall.log 2>> uninstall.log; fi
if [ -d /opt/gmosh ]; then rm -r /opt/gmosh >> uninstall.log 2>> uninstall.log; fi

echo "" >> uninstall.log
echo "Uninstallation completed" >> uninstall.log

cat uninstall.log
rm uninstall.log