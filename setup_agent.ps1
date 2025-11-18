# ===============================================
# SETUP COMPLET DE L'AGENT LOCAL
# ===============================================

$base = "C:\AGENT LOCAL"

Write-Host "=== Création de la structure ==="

# --- Création des dossiers ---
$folders = @(
    "$base\backend",
    "$base\backend\actions",
    "$base\backend\connectors",
    "$base\backend\connectors\reasoning",
    "$base\backend\connectors\code",
    "$base\backend\connectors\vision",
    "$base\backend\connectors\search",
    "$base\backend\memory",
    "$base\backend\memory\sessions",
    "$base\backend\memory\vectors",
    "$base\backend\memory\graphs",
    "$base\backend\vision",
    "$base\backend\vision\captures",
    "$base\frontend",
    "$base\frontend\ui",
    "$base\frontend\static"
)

foreach ($f in $folders) {
    if (!(Test-Path $f)) {
        New-Item -ItemType Directory -Path $f | Out-Null
        Write-Host "Dossier créé: $f"
    }
}

# --- Création fichiers backend ---
function Create-File($path, $content) {
    if (!(Test-Path $path)) {
        $content | Out-File $path -Encoding utf8
        Write-Host "Fichier créé: $path"
    }
}

Create-File "$base\backend\main.py" @"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Agent Local")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Agent Local démarré."}
"@

Create-File "$base\backend\actions\file_operations.py" "# Gestion des fichiers"
Create-File "$base\backend\actions\n8n_connector.py" "# Connexion à n8n"
Create-File "$base\backend\actions\word_editing.py" "# Edition Word"

Create-File "$base\backend\vision\vision_handler.py" "# Vision"
Create-File "$base\backend\memory\memory_handler.py" "# Mémoire"
Create-File "$base\backend\memory\graph_builder.py" "# Graphe mémoire"

Create-File "$base\backend\connectors\active_config.py" @"
ACTIVE_REASONING = None
ACTIVE_CODE = None
ACTIVE_VISION = None
ACTIVE_SEARCH = None
"@

Create-File "$base\frontend\ui\index.html" @"
<!DOCTYPE html>
<html>
<head><title>Agent Local</title></head>
<body><h1>Interface Agent Local</h1></body>
</html>
"@

# --- Création .env.example ---
Create-File "$base\.env.example" @"
OPENAI_API_KEY=
QWEN_API_KEY=
DEEPSEEK_API_KEY=
SEARCH_API_KEY=
N8N_WEBHOOK_URL=
"@

# --- Création ENV Python ---
Write-Host "=== Installation de l'environnement Python ==="

if (!(Test-Path "$base\venv")) {
    python -m venv "$base\venv"
}

# --- Installer les dépendances ---
& "$base\venv\Scripts\pip.exe" install fastapi uvicorn python-multipart python-dotenv mss psutil requests pyautogui keyboard watchdog pywin32 pillow qdrant-client

Write-Host "=== Installation terminée ==="
Write-Host "Tu peux maintenant utiliser run_agent.ps1"
