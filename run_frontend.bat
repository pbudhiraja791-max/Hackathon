@echo off
title Fluxora - Executive React Dashboard
cd /d "%~dp0frontend"
echo ========================================================
echo Starting Fluxora React Dashboard (Vite)...
echo Dashboard URL: http://localhost:5173
echo ========================================================
cmd /c npm run dev -- --host
pause
