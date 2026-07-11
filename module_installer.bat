@echo off
SETLOCAL Enabledelayedexpansion

echo =========================
echo PITYSAKE MODULE INSTALLER
echo =========================
echo.
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found.
    echo Install Python before running this script.
    echo Go to: https://www.python.org/downloads/
    pause
    exit /b
)

for /f "tokens=2" %%I in ('python --version 2^>^&1') do set ver=%%I
for /f "tokens=1,2 delims=." %%a in ("%ver%") do (
    set major=%%a
    set minor=%%b
)

if %major% lss 3 (
    goto :bad_version
) else if %major% equ 3 (
    if %minor% lss 10 (
        goto :bad_version
    )
)

echo Python %ver% found
goto install_packages

:bad_version
echo Error: Python version too old
echo Version 3.10 or later required for Streamlit
echo Go to: https://www.python.org/downloads/
pause
exit /b

:install_packages
if not exist requirements.txt (
    echo Error: requirements.txt missing in folder.
    echo Collect the file here: https://github.com/elmwall/PitySake
    pause
    exit /b
)

echo.
echo Creating virtual environment for modules...
python -m venv .venv

echo Upgrading pip...
.venv\Scripts\python.exe -m pip install --upgrade pip

echo Checking modules...
.venv\Scripts\python.exe -m pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo Done, all modules ready.
) else (
    echo.
    echo Error: Something went wrong. Check messages above and contents of requirements.txt
)

echo Creating shortcuts...
.venv\Scripts\python.exe -m project_utilities.shortcut_maker

if %errorlevel% equ 0 (
    echo.
    echo =========================
    echo Installation done.
    echo PitySake can now be used.
    echo =========================
) else (
    echo.
    echo Error: Something went wrong. Check messages above and contents of requirements.txt
)

pause