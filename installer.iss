; ─────────────────────────────────────────────────────────────
;  News Editor — Inno Setup Script
;  Compile dengan Inno Setup 6: https://jrsoftware.org/isinfo.php
; ─────────────────────────────────────────────────────────────

#define AppName      "News Editor"
#define AppVersion   "3.0"
#define AppPublisher "Portal Berita"
#define AppURL       "https://github.com/username/portal-berita"
#define AppExeName   "NewsEditor.exe"
#define BuildDir     "dist\NewsEditor"

[Setup]
; ── Info aplikasi ──────────────────────────────────────────────
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}

; ── Folder install default ─────────────────────────────────────
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes

; ── Output installer ───────────────────────────────────────────
OutputDir=installer_output
OutputBaseFilename=NewsEditor_Setup_v{#AppVersion}
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\{#AppExeName}

; ── Kompresi ───────────────────────────────────────────────────
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes

; ── Tampilan installer ─────────────────────────────────────────
WizardStyle=modern
WizardResizable=no
DisableWelcomePage=no
DisableDirPage=no
DisableProgramGroupPage=no

; ── Hak akses ──────────────────────────────────────────────────
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; ── Arsitektur ─────────────────────────────────────────────────
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
english.WelcomeLabel2=Selamat datang di installer {#AppName} v{#AppVersion}.%n%nAplikasi ini memungkinkan Anda membuat, mengedit, dan mempublish berita ke GitHub Pages secara otomatis.%n%nKlik Berikutnya untuk melanjutkan.
english.FinishedHeadingLabel=Instalasi {#AppName} Selesai!
english.FinishedLabel=Terima kasih telah menginstall {#AppName}.%n%nKlik Selesai untuk menutup installer.

[Tasks]
Name: "desktopicon";     Description: "Buat shortcut di Desktop";          GroupDescription: "Shortcut:"; Flags: unchecked
Name: "quicklaunchicon"; Description: "Buat shortcut di Quick Launch bar"; GroupDescription: "Shortcut:"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; ── Semua file hasil build PyInstaller ─────────────────────────
Source: "{#BuildDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; ── File pendukung portal berita ───────────────────────────────
Source: "generate_list.py"; DestDir: "{app}";  Flags: ignoreversion; Components: portal
Source: "index.html";       DestDir: "{app}";  Flags: ignoreversion; Components: portal
Source: "file-list.json";   DestDir: "{app}";  Flags: ignoreversion; Components: portal
Source: "README.md";        DestDir: "{app}";  Flags: ignoreversion; DestName: "README.txt"

[Components]
Name: "main";   Description: "News Editor (Wajib)"; Types: full compact custom; Flags: fixed
Name: "portal"; Description: "File Portal Berita (index.html, generate_list.py)"; Types: full

[Icons]
; ── Start Menu ─────────────────────────────────────────────────
Name: "{group}\{#AppName}";              Filename: "{app}\{#AppExeName}";         IconFilename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall {#AppName}";    Filename: "{uninstallexe}"

; ── Desktop ────────────────────────────────────────────────────
Name: "{autodesktop}\{#AppName}";        Filename: "{app}\{#AppExeName}";         IconFilename: "{app}\{#AppExeName}"; Tasks: desktopicon

; ── Quick Launch ───────────────────────────────────────────────
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: quicklaunchicon

[Run]
; Tawarkan jalankan aplikasi setelah install selesai
Filename: "{app}\{#AppExeName}"; Description: "Jalankan {#AppName} sekarang"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Hapus file yang dibuat oleh aplikasi saat uninstall
Type: files;     Name: "{app}\kategori.json"
Type: files;     Name: "{app}\file-list.json"
Type: filesandordirs; Name: "{app}"

[Code]
// ── Cek apakah sudah ada versi sebelumnya ─────────────────────
function InitializeSetup(): Boolean;
var
  OldVersion: String;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Buat folder 'berita' kosong di dalam app dir
    CreateDir(ExpandConstant('{app}\berita'));
  end;
end;
