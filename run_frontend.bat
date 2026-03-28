@echo off
setlocal
set "ROOT=%~dp0"
set "VENV_PYTHON=%ROOT%.venv\Scripts\python.exe"

if not exist "%VENV_PYTHON%" (
  echo Missing virtual environment Python at "%VENV_PYTHON%".
  echo Create it with: python -m venv .venv
  echo Then install backend dependencies with: .venv\Scripts\python.exe -m pip install -r backend_service\requirements.txt
  exit /b 1
)

cd /d "%ROOT%frontend\studio"
"%VENV_PYTHON%" -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
