; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{4F5E5D42-3F61-411D-B38A-2A612586A8B5}
AppName=GMosh
AppVersion=2.0
;AppVerName=GMosh 2.0
AppPublisher=FPtje
AppPublisherURL=https://github.com/FPtje/gmosh
AppSupportURL=https://github.com/FPtje/gmosh
AppUpdatesURL=https://github.com/FPtje/gmosh
DefaultDirName={pf}\gmosh
DisableDirPage=yes
DefaultGroupName=gmoshui
AllowNoIcons=yes
OutputDir=C:\Users\falco\Documents\Programs\gmosh\installer
OutputBaseFilename=setup
SetupIconFile=C:\Users\falco\Documents\Programs\gmosh\res\icon.ico
Compression=lzma
SolidCompression=yes

[Setup]
ArchitecturesInstallIn64BitMode=x64 ia64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags:
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: ; OnlyBelowVersion: 0,6.1

[Files]
;Source: "C:\Program Files\gmosh\bin\gmoshui.exe"; DestDir: "{app}\bin"; Flags: ignoreversion
;Source: "C:\Program Files\gmosh\bin\gmosh.exe"; DestDir: "{app}\bin"; Flags: ignoreversion
Source: "..\package\Windows\uninstall.bat"; DestDir: "{app}"; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\GMosh"; Filename: "{app}\bin\gmoshui.exe"
Name: "{commondesktop}\GMosh"; Filename: "{app}\bin\gmoshui.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\GMosh"; Filename: "{app}\bin\gmoshui.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{src}\install.bat"
Filename: "{app}\bin\gmoshui.exe"; Description: "{cm:LaunchProgram,GMosh}"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKCR; Subkey: ".gma"; ValueType: string; ValueName: ""; ValueData: "gmoshui"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "gmoshui"; ValueType: string; ValueName: ""; ValueData: "gmoshui"; Flags: uninsdeletekey
Root: HKCR; Subkey: "gmoshui\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\bin\gmoshui.exe,0"
Root: HKCR; Subkey: "gmoshui\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\bin\gmoshui.exe"" ""%1"""

[UninstallRun]
Filename: "{app}\uninstall.bat"