Set-Location "C:\AGENT LOCAL"

Write-Host "=== Agent Local ===" -ForegroundColor Cyan

# Kill old python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Activate venv
& "C:\AGENT LOCAL\venv\Scripts\Activate.ps1"

# Start backend
Write-Host "Starting backend on http://127.0.0.1:8000" -ForegroundColor Yellow

Start-Job -ScriptBlock {
    Start-Sleep -Seconds 3
    Start-Process "http://127.0.0.1:8000/ui"
} | Out-Null

# Utiliser python du venv explicitement
& "C:\AGENT LOCAL\venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

Write-Host "Server stopped." -ForegroundColor Red
Read-Host "Press Enter to exit"
