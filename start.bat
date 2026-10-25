@echo off
chcp 65001 >nul 2>&1
title Zh2En Translator

cd /d "%~dp0"

echo [INFO] Checking Python installation...
py -3.12 --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.12 not found!
    pause
    exit /b 1
)

if not exist "venv\Scripts\activate" (
    echo [INFO] First run: creating virtual environment...
    py -3.12 -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

call venv\Scripts\activate

if not exist "venv\.installed" (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt --quiet
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        echo [INFO] Note: keyboard package may not support Python 3.14 yet
        echo [INFO] Try using Python 3.11 or 3.12 instead
        pause
        exit /b 1
    )
    echo. > venv\.installed
)

echo [INFO] Starting Zh2En Translator...
echo.
set PYTHONIOENCODING=utf-8
python main.py

echo.
echo [INFO] Program exited
pause
