@echo off

:: Check if Python is installed, >nul 2>nul silence error messages
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python could not be found. Please install Python.
    exit /b
)



:: Set up the virtual environment
python -m venv venv

:: Activate the virtual environment
call venv\Scripts\activate

:: Install dependencies
pip install -r requirements.txt

echo Setup complete. Use run.bat to start.