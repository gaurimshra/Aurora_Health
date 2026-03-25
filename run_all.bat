@echo off
setlocal
cd /d %~dp0

echo Starting Aurora backend on http://127.0.0.1:8000
start "Aurora Backend" cmd /k "cd /d %~dp0 && call run_backend.bat"

echo Starting Aurora web app on http://127.0.0.1:3000
start "Aurora Web App" cmd /k "cd /d %~dp0 && call run_web_app.bat"

echo Starting Aurora studio on http://127.0.0.1:8501
start "Aurora Studio" cmd /k "cd /d %~dp0 && call run_frontend.bat"

echo.
echo Aurora stack launch requested.
echo Backend:  http://127.0.0.1:8000
echo Web app:  http://127.0.0.1:3000
echo Studio:   http://127.0.0.1:8501
