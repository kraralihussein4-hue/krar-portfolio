@echo off
cd /d "%~dp0backend"
echo Starting KrarAli Portfolio...
python -m uvicorn main:app --host 0.0.0.0 --port 8000
pause