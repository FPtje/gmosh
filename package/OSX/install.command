#!/usr/bin/env /bin/bash
[ "$UID" -eq 0 ] || exec sudo bash "$0" "$@"
cd `dirname $0`

echo "Install log:" > install.log

if [ ! -d /opt/gmosh ]; then mkdir -p /opt/gmosh >> install.log 2>> install.log; fi
cp bin/* /opt/gmosh >> install.log 2>> install.log
cp required/gmpublish_osx /opt/gmosh >> install.log 2>> install.log
cp required/libsteam_api.dylib /opt/gmosh >> install.log 2>> install.log

ln -sf /opt/gmosh/libsteam_api.dylib /usr/lib/libsteam_api.dylib >> install.log 2>> install.log
ln -sf /opt/gmosh/gmpublish_osx /usr/bin/gmpublish_osx >> install.log 2>> install.log
ln -sf /opt/gmosh/gmosh /usr/bin/gmosh >> install.log 2>> install.log

cp required/steam_appid.txt /opt/gmosh/steam_appid.txt >> install.log  2>> install.log # Has to be in same folder as gmpublish_linux
chmod +x /opt/gmosh/gmpublish_osx >> install.log 2>> install.log
chmod +x /opt/gmosh/gmosh >> install.log 2>> install.log

echo "" >> install.log
echo "Installation completed" >> install.log

cat install.log
rm install.log