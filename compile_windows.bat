mkdir bin > NUL
mkdir package\Windows\bin > NUL
mkdir package\Windows\required > NUL

pyside-uic.exe ui/mainwindow.ui -o src/view/mainwindow.py
pyside-uic.exe ui/progressdialog.ui -o src/view/progressdialog.py
python C:/Python34/Scripts/cxfreeze src/gmosh.py --target-dir=bin --include-modules=addoninfo,gmafile,gmpublish,workshoputils
python C:/Python34/Scripts/cxfreeze src/gmoshui.py --target-dir=bin --base=Win32GUI --include-modules=addoninfo,gmafile,gmpublish,workshoputils,atexit --icon res/icon.ico

xcopy bin\* package\Windows\bin\ /y
xcopy README.txt package\Windows\ /y
xcopy required\gmpublish.exe package\Windows\required\ /y
xcopy required\steam_api.dll package\Windows\required\ /y
xcopy required\steam_appid.txt package\Windows\required\ /y
PAUSE
