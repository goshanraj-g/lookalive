; LookAlive Installer Script for Inno Setup
; Download Inno Setup from: https://jrsoftware.org/isinfo.php

[Setup]
AppName=LookAlive
AppVersion=1.0
AppPublisher=Your Name
DefaultDirName={autopf}\LookAlive
DefaultGroupName=LookAlive
OutputDir=installer
OutputBaseFilename=LookAlive-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "dist\LookAlive.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\LookAlive"; Filename: "{app}\LookAlive.exe"
Name: "{autodesktop}\LookAlive"; Filename: "{app}\LookAlive.exe"; Tasks: desktopicon
Name: "{userstartup}\LookAlive"; Filename: "{app}\LookAlive.exe"; Tasks: startupicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"
Name: "startupicon"; Description: "Start LookAlive when Windows starts"; GroupDescription: "Additional options:"

[Run]
Filename: "{app}\LookAlive.exe"; Description: "Launch LookAlive"; Flags: nowait postinstall skipifsilent
