; Zobvia Studio - Inno Setup script
; Build on Windows with Inno Setup 6:  ISCC.exe zobvia-studio.iss
; Produces dist\ZobviaStudio-Setup.exe - a real Windows installer:
; users download it, double-click, and Zobvia Studio is installed
; with a Desktop shortcut. (Prerequisite tools are installed by
; INSTALL.bat, which the installer runs once at the end.)

[Setup]
AppName=Zobvia Studio
AppVersion=1.0
AppPublisher=Zobaerio
DefaultDirName={autopf}\ZobviaStudio
DefaultGroupName=Zobvia Studio
OutputDir=dist
OutputBaseFilename=ZobviaStudio-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "zobvia-studio\*"; DestDir: "{app}\zobvia-studio"; Flags: recursesubdirs ignoreversion
Source: "zobvia\*"; DestDir: "{app}\zobvia"; Flags: recursesubdirs ignoreversion
Source: "ZobviaStudio.bat"; DestDir: "{app}"
Source: "INSTALL.bat"; DestDir: "{app}"
Source: "README-WINDOWS.md"; DestDir: "{app}"

[Icons]
Name: "{commondesktop}\Zobvia Studio"; Filename: "{app}\ZobviaStudio.bat"; WorkingDir: "{app}"
Name: "{group}\Zobvia Studio"; Filename: "{app}\ZobviaStudio.bat"; WorkingDir: "{app}"

[Run]
Filename: "{app}\INSTALL.bat"; Description: "Install required tools (Python, Node.js, ffmpeg) and the video engine"; Flags: postinstall runascurrentuser
