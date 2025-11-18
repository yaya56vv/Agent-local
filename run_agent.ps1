# ======================================
#  Lancer AGENT LOCAL proprement
# ======================================

Write-Host "=== Démarrage de l'Agent Local ===" -ForegroundColor Green

# Se placer dans le bon répertoire
Set-Location "C:\AGENT LOCAL"

Write-Host "=== Activation de l'environnement virtuel ===" -ForegroundColor Cyan
& "C:\AGENT LOCAL\venv\Scripts\activate.ps1"

Write-Host "=== Démarrage du backend FastAPI ===" -ForegroundColor Cyan
Write-Host "Backend accessible sur : http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "Interface graphique : http://127.0.0.1:8000/ui" -ForegroundColor Yellow
Write-Host "Documentation API : http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host ""

# Ouvrir le navigateur après un court délai
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 3
    Start-Process "http://127.0.0.1:8000/ui"
} | Out-Null

# Lancer uvicorn avec python -m pour garantir le bon environnement
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

# Si uvicorn s'arrête, garder la fenêtre ouverte
Write-Host ""
Write-Host "=== Le serveur s'est arrêté ===" -ForegroundColor Red
Read-Host "Appuyez sur Entrée pour fermer cette fenêtre"
