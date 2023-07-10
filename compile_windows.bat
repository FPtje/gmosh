mkdir bin > NUL
mkdir package\Windows\bin > NUL
mkdir package\Windows\required > NUL

pyside-uic.exe ui/mainwindow.ui -o src/gmosh/view/mainwindow.py
pyside-uic.exe ui/progressdialog.ui -o src/gmosh/view/progressdialog.py
python C:/Python34/Scripts/cxfreeze src/gmosh/gmosh.py --target-dir=bin --include-modules=addoninfo,gmafile,gmpublish,workshoputils
python C:/Python34/Scripts/cxfreeze src/gmosh/gmoshui.py --target-dir=bin --base=Win32GUI --include-modules=addoninfo,gmafile,gmpublish,workshoputils,atexit --icon res/icon.ico

xcopy bin\* package\Windows\bin\ /y
xcopy README.txt package\Windows\ /y
xcopy required\gmpublish.exe package\Windows\required\ /y
xcopy required\steam_api.dll package\Windows\required\ /y
xcopy required\steam_appid.txt package\Windows\required\ /y

"C:\Program Files (x86)\Inno Setup 5\ISCC.exe" "installer\windows.iss"
xcopy installer\setup.exe package\Windows\ /y
PAUSE
