@echo off
REM Assistant Windows - Launch Script
REM Run this script as Administrator for hotkey support

echo ========================================
echo   Assistant Windows - Mission 6
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo WARNING: Not running as Administrator!
    echo Hotkeys may not work properly.
    echo Please right-click and "Run as Administrator"
    echo.
    pause
)

REM Check if backend is running
echo Checking backend status...
curl -s http://localhost:8000/health >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ERROR: Backend is not running!
    echo Please start the backend first:
    echo   python -m uvicorn backend.main:app --reload --port 8000
    echo.
    pause
    exit /b 1
)

echo Backend is running ✓
echo.

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import PySide6" >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ERROR: PySide6 not installed!
    echo Installing dependencies...
    pip install -r requirements.txt
    if %errorLevel% neq 0 (
        echo Failed to install dependencies!
        pause
        exit /b 1
    )
)

echo Dependencies OK ✓
echo.

REM Launch the assistant
echo Starting Assistant Windows...
echo.
echo Hotkeys:
echo   F1  = Show window (no capture)
echo   F8  = Show window + start auto capture
echo   F9  = Stop auto capture
echo   F10 = Single screenshot
echo.
echo Press Ctrl+C to stop
echo.

python main.py

pause