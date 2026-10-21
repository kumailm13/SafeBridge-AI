@echo off
title AI Firewall System
echo ==================================================================
echo   AI Firewall: A Secure Middleware with Intelligent Filtering
echo   COMSATS University Islamabad - BCE Final Year Project
echo ==================================================================
echo Starting Backend API Server...
start "AI Firewall Backend (FastAPI)" cmd /c "run_backend.bat"

echo Waiting 2 seconds for backend initialization...
timeout /t 2 /nobreak >nul

echo Starting Frontend Security Dashboard...
start "AI Firewall Dashboard (React)" cmd /c "run_frontend.bat"

echo.
echo Both servers launched!
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
timeout /t 3 /nobreak >nul
start http://localhost:5173
