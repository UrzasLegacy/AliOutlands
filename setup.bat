@echo off

:: Check if Git is installed TEST
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
    echo Repository already exists. Resetting and pulling latest changes.
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
    echo Cloning the repository.
    git clone %REPO_URL% "%REPO_DIR%" >nul 2>&1
    if %errorlevel% neq 0 (
        echo Failed to clone the repository. Please check the repository URL and your internet connection.
        exit /b
    )
)

:: Change to the repository directory
cd "%REPO_DIR%"

:: Set up the virtual environment if it does not exist
if not exist "venv\" (
    python -m venv venv
)

:: Activate the virtual environment
call venv\Scripts\activate

:: Install dependencies
pip install -r requirements.txt

echo Setup complete!
echo Use run.bat to start.
echo Press Enter to close this window.
pause