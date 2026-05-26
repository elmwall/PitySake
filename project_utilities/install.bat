@echo off

echo Checking Python...

python --version >nul 2>&1
if errorlevel 1 (
echo Python not found.
echo Please install Python 3.12 or newer:
echo https://www.python.org/downloads/
pause
exit /b
)

echo Installing required packages...

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo Installation complete
echo You can now launch the application using the file run_project.bat
pause