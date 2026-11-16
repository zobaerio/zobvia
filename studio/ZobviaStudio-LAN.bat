@echo off
chcp 65001 >nul
title Zobvia Studio (LAN - phone/tablet mode)
cd /d "%~dp0zobvia-studio"
echo Starting Zobvia Studio in LAN mode...
echo Watch the server window: it prints the address for your phone/tablet,
echo for example http://192.168.1.5:8770 - open THAT address in the
echo phone/tablet browser (same Wi-Fi). The access password still applies.
set ZOBVIA_LAN=1
start "Zobvia Studio Server" /min python server.py
timeout /t 3 /nobreak >nul
start http://localhost:8770
echo.
echo Zobvia Studio is running. Keep the small server window open.
pause
