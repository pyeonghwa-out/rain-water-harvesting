@echo off
cd %~dp0

echo Cleaning up old environments...
rmdir /S /Q myenv
rmdir /S /Q __pycache__
if exist myenv rmdir /S /Q myenv
if exist __pycache__ rmdir /S /Q __pycache__
if exist newenv rmdir /S /Q newenv


echo Creating virtual environment 'newenv'...
python -m venv newenv

echo Activating environment...
call newenv\Scripts\activate

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing requirements...
pip install -r requirements.txt

echo Fixing .gitignore...
if not exist .gitignore (
    echo.>.gitignore
)
findstr /C:"newenv/" .gitignore >nul || echo newenv/>>.gitignore
findstr /C:"__pycache__/" .gitignore >nul || echo __pycache__/>>.gitignore
findstr /C:"*.pyc" .gitignore >nul || echo *.pyc>>.gitignore

echo Setup complete. Run "call newenv\Scripts\activate" to use the environment.
pause
