@ECHO OFF
rmdir "%ProgramFiles%\gmosh" /Q /S
pathed.exe -r "%ProgramFiles%\gmosh\bin"

echo Uninstall complete
PAUSE
