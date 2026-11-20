; The installer.
;
; Per-user by default (PrivilegesRequired=lowest), so installing needs no administrator and the app
; lands in the person's own AppData. An astrology app has no business asking for the whole machine, and
; most people who would be put off by a UAC prompt are exactly the people this is for.
;
; There is no code-signing certificate, so Windows SmartScreen will warn on first run. That is honest:
; it is unsigned software. Buying a certificate is the only fix and it is the author's decision.

#define AppName "Gaurav Jyotish"
; The build passes this in with ISCC /DAppVersion=x.y.z. Without it the filename and the version shown
; in Windows would say 1.0.0 whatever the release was tagged - which is how you end up testing a build
; you did not mean to, because two files called Setup-1.0.0.exe look identical in a Downloads folder.
#ifndef AppVersion
  #define AppVersion "0.0.0-dev"
#endif
#define AppPublisher "Gaurav Mishra"
#define AppURL "https://authorgaurav.com"
#define AppExe "GauravJyotish.exe"

[Setup]
AppId={{8E2D6A1C-4F7B-4E25-9C3A-7B5E1D9A4C62}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputBaseFilename=GauravJyotish-Setup-{#AppVersion}
SetupIconFile=app.ico
UninstallDisplayIcon={app}\{#AppExe}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\..\dist\GauravJyotish\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Registry]
; A saved backup opens the app rather than nothing. Per-user keys only, matching the install.
Root: HKCU; Subkey: "Software\Classes\.gjb"; ValueType: string; ValueName: ""; ValueData: "GauravJyotish.Backup"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\GauravJyotish.Backup"; ValueType: string; ValueName: ""; ValueData: "Gaurav Jyotish backup"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\GauravJyotish.Backup\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#AppExe},0"
Root: HKCU; Subkey: "Software\Classes\GauravJyotish.Backup\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExe}"" ""%1"""

[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; What the app wrote stays. Saved people and reports are the person's, not the installer's, and an
; uninstall that deleted them would be a nasty surprise for anybody reinstalling.
Type: dirifempty; Name: "{app}"
