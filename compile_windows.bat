mkdir bin > NUL
mkdir package\Windows\bin > NUL
mkdir package\Windows\required > NUL

python C:/Python34/Scripts/cxfreeze src/gmosh.py --target-dir=bin --include-modules=addoninfo,gmafile,gmpublish,workshoputils

xcopy bin\* package\Windows\bin\ /y
xcopy README.txt package\Windows\ /y
xcopy required\gmpublish.exe package\Windows\required\ /y
xcopy required\steam_api.dll package\Windows\required\ /y
xcopy required\steam_appid.txt package\Windows\required\ /y
PAUSE
