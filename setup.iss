[Setup]
AppName=DTR Management System
AppVersion=1.0.0
DefaultDirName={autopf}\DTR Management System
DefaultGroupName=DTR Management System
UninstallDisplayIcon={app}\DTR_Management_System.exe
Compression=lzma2
SolidCompression=yes
OutputDir=dist
OutputBaseFilename=DTR_Management_System_Setup
SetupIconFile=icon.ico
; To allow installation without admin rights, uncomment the next line:
; PrivilegesRequired=lowest

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\DTR_Management_System\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\DTR Management System"; Filename: "{app}\DTR_Management_System.exe"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\DTR Management System"; Filename: "{app}\DTR_Management_System.exe"; Tasks: desktopicon; IconFilename: "{app}\icon.ico"
