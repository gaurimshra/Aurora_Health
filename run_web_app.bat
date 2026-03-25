@echo off
setlocal
cd /d %~dp0frontend\web
cmd /c "set NODE_OPTIONS= && set NODE_ENV=development && npm run dev -- --hostname 127.0.0.1 --port 3000"
