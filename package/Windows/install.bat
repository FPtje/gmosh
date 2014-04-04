@ECHO OFF
@setlocal enableextensions
@cd /d "%~dp0"

mkdir "%ProgramFiles%\gmosh\bin\" > NUL
xcopy "bin\*" "%ProgramFiles%\gmosh\bin\" /Y
xcopy "required\*" "%ProgramFiles%\gmosh\bin\" /Y
xcopy "README.txt" "%ProgramFiles%\gmosh\" /Y
:: https://code.google.com/p/pathed/
:: Add the gmosh bin directory to %PATH% so you can run it from the command prompt
pathed.exe -a "%ProgramFiles%\gmosh\bin"

echo Install complete
PAUSE
