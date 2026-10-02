@echo off
echo ========================================================
echo Launching AlgoLens Full-Stack Development Environment...
echo ========================================================
start "AlgoLens Backend (FastAPI)" cmd /k "%~dp0start-backend.bat"
start "AlgoLens Frontend (Vite + React)" cmd /k "%~dp0start-frontend.bat"
echo.
echo AlgoLens services are starting in dedicated terminal windows!
echo - Backend API:  http://localhost:8000 (Swagger docs at http://localhost:8000/docs)
echo - Frontend App: http://localhost:5173
echo ========================================================
