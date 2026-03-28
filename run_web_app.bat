@echo off
setlocal
set "ROOT=%~dp0"
set "WEB_DIR=%ROOT%frontend\web"
set "NEXT_BIN=%WEB_DIR%\node_modules\.bin\next.cmd"

cd /d "%WEB_DIR%"
if not exist "%NEXT_BIN%" (
  echo Missing Next.js executable at "%NEXT_BIN%".
  echo Install frontend dependencies with: cd frontend\web ^&^& npm install
  exit /b 1
)
if exist ".next" powershell -NoProfile -Command "Remove-Item -Recurse -Force .next"
set "NODE_OPTIONS="
set "NODE_ENV="
"%NEXT_BIN%" dev --webpack --hostname 127.0.0.1 --port 3000
