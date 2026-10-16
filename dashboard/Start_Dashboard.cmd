@echo off
cd /d "%~dp0"
if exist "..\.venv-dashboard\Scripts\python.exe" (
  "..\.venv-dashboard\Scripts\python.exe" -m streamlit run app.py
) else (
  python -m streamlit run app.py
)
pause
