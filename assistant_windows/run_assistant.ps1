# Assistant Windows - Launch Script (PowerShell)
# Run this script as Administrator for hotkey support

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Assistant Windows - Mission 6" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "WARNING: Not running as Administrator!" -ForegroundColor Yellow
    Write-Host "Hotkeys may not work properly." -ForegroundColor Yellow
    Write-Host "Please right-click and 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to continue anyway or Ctrl+C to exit"
}

# Check if backend is running
Write-Host "Checking backend status..." -ForegroundColor Gray
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
    Write-Host "Backend is running ✓" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "ERROR: Backend is not running!" -ForegroundColor Red
    Write-Host "Please start the backend first:" -ForegroundColor Yellow
    Write-Host "  python -m uvicorn backend.main:app --reload --port 8000" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check if dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Gray
try {
    python -c "import PySide6" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "PySide6 not found"
    }
    Write-Host "Dependencies OK ✓" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "ERROR: PySide6 not installed!" -ForegroundColor Red
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install dependencies!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "Dependencies installed ✓" -ForegroundColor Green
}

Write-Host ""

# Launch the assistant
Write-Host "Starting Assistant Windows..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Hotkeys:" -ForegroundColor Yellow
Write-Host "  F1  = Show window (no capture)" -ForegroundColor White
Write-Host "  F8  = Show window + start auto capture" -ForegroundColor White
Write-Host "  F9  = Stop auto capture" -ForegroundColor White
Write-Host "  F10 = Single screenshot" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

# Change to assistant_windows directory
Set-Location $PSScriptRoot

# Run the assistant
python main.py

Write-Host ""
Read-Host "Press Enter to exit"