@echo off
title AI Firewall - Backend API Server
echo ========================================================
echo   AI Firewall: Secure Middleware with Intelligent DLP
echo   COMSATS University Islamabad - Department of CE
echo ========================================================
echo Starting FastAPI Backend on http://localhost:8000 ...
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload
pause
