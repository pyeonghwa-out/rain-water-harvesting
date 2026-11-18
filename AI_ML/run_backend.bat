@echo off
echo Activating virtual environment...
call newenv\Scripts\activate

echo Starting backend server...
cd ..
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
cd AI_ML
pause
