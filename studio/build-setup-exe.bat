@echo off
REM ============================================================
REM  Build a true single-file installer: ZobviaStudio-Setup.exe
REM  Run this ON A WINDOWS PC (cannot be built on Linux).
REM  Needs: Inno Setup 6 (https://jrsoftware.org/isdl.php)
REM  Output: dist\ZobviaStudio-Setup.exe
REM ============================================================
chcp 65001 >nul
cd /d "%~dp0"
if not exist dist mkdir dist
echo Building ZobviaStudio-Setup.exe with Inno Setup...
"%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" zobvia-studio.iss
if errorlevel 1 (
  echo ISCC failed. Is Inno Setup 6 installed?
  pause
  exit /b 1
)
echo.
echo Done: dist\ZobviaStudio-Setup.exe
pause
