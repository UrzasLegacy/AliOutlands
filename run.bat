@echo off

:: Navigate to the script's directory
cd /d %~dp0

if not exist "venv\Scripts\activate" (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b
)

call venv\Scripts\activate

python main.py

:: Keep the command prompt open for error messages
pause