@echo off
chcp 65001 >nul
title Zobvia Studio
cd /d "%~dp0zobvia-studio"
echo Starting Zobvia Studio...
start "Zobvia Studio Server" /min python server.py
timeout /t 3 /nobreak >nul
start http://localhost:8770
echo.
echo Zobvia Studio is running at http://localhost:8770
echo Keep the small server window open while you work.
echo Close that window to stop Zobvia Studio.
pause
