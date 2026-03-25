@echo off
setlocal
call .venv\Scripts\activate.bat
cd /d %~dp0backend_service
python -m uvicorn backend.main:app --reload
