@echo off
setlocal
call .venv\Scripts\activate.bat
cd /d %~dp0frontend\studio
streamlit run app.py --server.address 127.0.0.1 --server.port 8501
