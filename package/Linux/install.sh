#!/usr/bin/env /bin/bash
tty -s; if [ $? -ne 0 ]; then
	[ "$UID" -eq 0 ] || exec gksu bash "$0" "$@"
else
	[ "$UID" -eq 0 ] || exec sudo bash "$0" "$@"
fi

echo "Install log:" > install.log

if [ ! -d /opt/gmosh ]; then mkdir /opt/gmosh >> install.log 2>> install.log; fi
cp bin/* /opt/gmosh >> install.log 2>> install.log
cp required/gmpublish_linux /opt/gmosh >> install.log 2>> install.log
cp required/libsteam_api.so /opt/gmosh >> install.log 2>> install.log

ln -sf /opt/gmosh/gmosh /usr/bin/gmosh >> install.log 2>> install.log

cp required/steam_appid.txt /opt/gmosh/steam_appid.txt >> install.log  2>> install.log # Has to be in same folder as gmpublish_linux
chmod +x /opt/gmosh/gmpublish_linux >> install.log 2>> install.log
chmod +x /opt/gmosh/gmosh >> install.log 2>> install.log

echo "Checking existence of libsteam.so" >> install.log
if [ ! -f ~/.steam/linux32/libsteam.so ]; then
	echo "    libsteam does not exist" >> install.log
	echo "    Attempting to copy libsteam to ~/.steam/linux32/" >> install.log
	echo "    If this fails you should copy it yourself. Gmosh will not work otherwise" >> install.log
	echo "    cp required/libsteam.so ~/.steam/linux32/" >> install.log
	mkdir -p ~/.steam/linux32/ 2>> install.log
	cp required/libsteam.so ~/.steam/linux32/ >> install.log 2>> install.log
else
	echo "    libsteam exists. " >> install.log
fi

echo "" >> install.log
echo "Installation completed" >> install.log

tty -s; if [ $? -ne 0 ]; then
	xmessage -file install.log
	rm install.log
else
	cat install.log
	rm install.log
fi