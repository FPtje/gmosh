@ECHO OFF

:: Remove gmosh' directory in program files
rmdir "%ProgramFiles%\gmosh" /Q /S
:: Remove the path from the PATH variable
pathed.exe -r "%ProgramFiles%\gmosh\bin"

echo Uninstall complete
PAUSE
