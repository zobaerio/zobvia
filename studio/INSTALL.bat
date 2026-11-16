@echo off
chcp 65001 >nul
title Zobvia Studio - Installer
echo ============================================
echo   Zobvia Studio - One-time Install
echo ============================================
echo.
echo This installs the tools Zobvia Studio needs
echo (Python, Node.js, ffmpeg) if they are missing,
echo then prepares the video engine. Internet is
echo required this one time only.
echo.
pause

REM --- Python ---
python --version >nul 2>&1
if errorlevel 1 (
  echo Installing Python...
  winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
)

REM --- Node.js ---
node --version >nul 2>&1
if errorlevel 1 (
  echo Installing Node.js...
  winget install -e --id OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements
)

REM --- ffmpeg ---
ffmpeg -version >nul 2>&1
if errorlevel 1 (
  echo Installing ffmpeg...
  winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
)

echo.
echo Refreshing PATH for this session...
set "PATH=%PATH%;%LocalAppData%\Programs\Python\Python312;%LocalAppData%\Programs\Python\Python312\Scripts;C:\Program Files\nodejs"

echo Installing the video engine packages (one time, a few minutes)...
cd /d "%~dp0zobvia-studio\render-app"
call npm install --no-audit --no-fund
if errorlevel 1 (
  echo.
  echo npm install failed. Check your internet connection and run INSTALL.bat again.
  pause
  exit /b 1
)

echo.
echo Access password setup - Zobvia Studio asks for a password
echo the first time it is used on this machine. Enter it now:
python "%~dp0zobvia\scripts\access_check.py"
echo (If you skipped it, the app will simply ask when it opens.)

echo.
echo Setting up the voice-to-subtitle AI (Whisper)...
echo One-time download of about 250 MB - please wait.
python -m venv "%~dp0whisper-venv"
"%~dp0whisper-venv\Scripts\python.exe" -m pip install --quiet --upgrade pip
"%~dp0whisper-venv\Scripts\python.exe" -m pip install --quiet faster-whisper "av==13.1.0"
if errorlevel 1 (
  echo Whisper setup did not finish - no problem: SRT upload and the
  echo Script box inside the app will still work.
) else (
  echo Whisper ready - the speech model downloads on first use.
)

echo Creating Desktop shortcut...
powershell -NoProfile -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Zobvia Studio.lnk'); $s.TargetPath='%~dp0ZobviaStudio.bat'; $s.WorkingDirectory='%~dp0'; $s.Description='Zobvia Studio - SRT + Voice to Video'; $s.Save()"

echo.
echo ============================================
echo   Install complete!
echo   Double-click "Zobvia Studio" on your Desktop,
echo   or run ZobviaStudio.bat from this folder.
echo ============================================
pause
