@echo off
title Fluxora - Backend API Service
cd /d "%~dp0backend"
echo ========================================================
echo Starting Fluxora FastAPI Backend Server...
echo Master Spec: PS08 - Energy for the Next Billion
echo API Documentation: http://127.0.0.1:8000/docs
echo ========================================================
venv\Scripts\python.exe run.py
pause
