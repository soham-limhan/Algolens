@echo off
cd /d "%~dp0backend"
set "PATH=C:\Program Files\Eclipse Adoptium\jdk-21.0.12.101-hotspot\bin;%PATH%"
echo Starting AlgoLens Backend API on http://localhost:8000 ...
.\.venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8000
