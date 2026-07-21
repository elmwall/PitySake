@echo off
chcp 65001 > nul
echo Clear __pycache__ ...


set "FOLDER_1=.\app"
set "FOLDER_2=.\project_utilities"
set "FOLDER_3=.\project_utilities\src"
set "FOLDER_4=.\project_utilities\utils"


call :CleanRoot
call :CleanFolder "%FOLDER_1%"
call :CleanFolder "%FOLDER_2%"
call :CleanFolder "%FOLDER_3%"
call :CleanFolder "%FOLDER_4%"

echo.
echo __pycache__ cleared!
pause
exit /b


:CleanRoot
echo Clearing root
if exist "%~1.\__pycache__" (
    attrib -R -S -H "%~1.\__pycache__" >nul 2>&1
    rd /s /q "%~1.\__pycache__" && echo   Removed from root: %~1.\__pycache__
)


:CleanFolder
if "%~1"=="" exit /b
if not exist "%~1" (
    echo [FEL] Could not find folder: %~1
    exit /b
)

echo Clearing: %~1

for /f "delims=" %%i in ('dir /b /s /ad "%~1\*__pycache__*" 2^>nul') do (
    attrib -R -S -H "%%i" >nul 2>&1
    rd /s /q "%%i" && echo   Removed: %%i
)
exit /b