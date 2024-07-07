@echo off

:: Check if Git is installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo Git could not be found. Please install Git.
    exit /b
)

:: Check if Python is installed, >nul 2>nul silence error messages
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python could not be found. Please install Python.
    exit /b
)

:: Set the repository URL here
set REPO_URL=https://github.com/UrzasLegacy/AliOutlands.git

:: Set the repository directory to the folder containing the setup.bat
set REPO_DIR=%~dp0

:: Check if the repository has already been cloned
if exist "%REPO_DIR%\.git" (
    echo Repository found. Resetting and pulling latest changes.
    cd "%REPO_DIR%"
    :: Discard local changes and clean untracked files
    git reset --hard >nul 2>&1
    git clean -fd >nul 2>&1
    :: Pull the latest changes and discard all output
    git pull --ff-only >nul 2>&1
    if %errorlevel% neq 0 (
        echo Failed to pull the latest changes. Please check your internet connection and repository permissions.
        exit /b
    )
) else (
    echo "Can't find repository files."
    pause
    exit /b
)

:: Change to the repository directory
cd "%REPO_DIR%"

:: Set up the virtual environment if it does not exist
if not exist "venv\" (
    python -m venv venv
)

:: Activate the virtual environment
call venv\Scripts\activate

:: Ensure pip and setuptools are installed
echo Ensuring pip and setuptools are installed...
python -m ensurepip
pip install --upgrade pip setuptools


:: Install dependencies
pip install -r requirements.txt

echo Setup complete!
echo.
echo Run start.bat as administrator to start the program. You can right click start.bat and create a shortcut and set it to open as admin.
echo Run update.bat as administrator to reset everything to the latest version on Github whenever I update it and remind you lol.
echo AFTER READING THE ABOVE:
pause