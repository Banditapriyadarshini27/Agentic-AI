@echo off
echo ========================================================
echo Starting NetCoop AI - FastAPI Backend Server
echo ========================================================
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
pause
