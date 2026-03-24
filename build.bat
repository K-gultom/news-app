@echo off
title News Editor — Build Script
color 0A

echo.
echo  =====================================================
echo   NEWS EDITOR — BUILD TO .EXE
echo   Menggunakan PyInstaller
echo  =====================================================
echo.

:: ── Cek Python ──────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python tidak ditemukan!
    echo  Pastikan Python sudah terinstall dan ada di PATH.
    pause & exit /b 1
)

echo  [1/5] Menginstall / update dependencies...
pip install pyinstaller tkcalendar --quiet --upgrade
if errorlevel 1 (
    echo  [ERROR] Gagal install dependencies.
    pause & exit /b 1
)
echo        OK

echo.
echo  [2/5] Membersihkan folder build lama...
if exist "build"  rmdir /s /q "build"
if exist "dist"   rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"
echo        OK

echo.
echo  [3/5] Menjalankan PyInstaller...
pyinstaller ^
    --noconfirm ^
    --onedir ^
    --windowed ^
    --name "NewsEditor" ^
    --icon "assets\icon.ico" ^
    --add-data "assets;assets" ^
    --hidden-import "tkcalendar" ^
    --hidden-import "babel.numbers" ^
    --hidden-import "babel.dates" ^
    news_editor.py

if errorlevel 1 (
    echo.
    echo  [ERROR] PyInstaller gagal. Cek log di atas.
    pause & exit /b 1
)
echo        OK

echo.
echo  [4/5] Menyalin file pendukung ke dist\NewsEditor...
if exist "generate_list.py"  copy /y "generate_list.py"  "dist\NewsEditor\" >nul
if exist "index.html"        copy /y "index.html"        "dist\NewsEditor\" >nul
if exist "file-list.json"    copy /y "file-list.json"    "dist\NewsEditor\" >nul
if exist "README.md"         copy /y "README.md"         "dist\NewsEditor\" >nul
echo        OK

echo.
echo  [5/5] Build selesai!
echo.
echo  =====================================================
echo   Output ada di folder:  dist\NewsEditor\
echo   File exe:               dist\NewsEditor\NewsEditor.exe
echo.
echo   Langkah selanjutnya:
echo   Buka Inno Setup, compile installer.iss
echo   untuk membuat installer setup.exe
echo  =====================================================
echo.
pause
