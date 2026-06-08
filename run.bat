@echo off
title Discord Member Parser

echo [*] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python not found! Install it from python.org
    pause
    exit /b 1
)

echo [*] Checking dependencies...
python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Installing requests...
    pip install -r "%~dp0requirements.txt"
    if %errorlevel% neq 0 (
        echo [!] Failed to install dependencies
        pause
        exit /b 1
    )
)

echo [*] Starting parser...
python "%~dp0discord_parser.py"
pause
