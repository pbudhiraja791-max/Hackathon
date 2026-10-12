@echo off
title Fluxora - Complete Full-Stack Launcher
echo ========================================================
echo Launching Fluxora Energy Management System (PS08)
echo "Smarter Energy for a Sustainable Tomorrow"
echo ========================================================

start "Fluxora Backend" cmd /c "%~dp0run_backend.bat"
timeout /t 3 /nobreak >nul
start "Fluxora Frontend" cmd /c "%~dp0run_frontend.bat"

echo.
echo Fluxora services launched!
echo Backend API Docs: http://127.0.0.1:8000/docs
echo Executive Dashboard: http://localhost:5173
echo ========================================================
