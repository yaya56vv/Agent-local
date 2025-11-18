# ======================================
#   SETUP COMPLET DE LA STRUCTURE AGENT
# ======================================

$base = "C:\AGENT LOCAL"

# Création des dossiers principaux
$folders = @(
    "$base\backend",
    "$base\backend\connectors",
    "$base\backend\connectors\reasoning",
    "$base\backend\connectors\code",
    "$base\backend\connectors\vision",
    "$base\backend\connectors\search",
    "$base\backend\rag",
    "$base\backend\local_agent",
    "$base\frontend",
    "$base\frontend\ui",
    "$base\memory",
    "$base\captures"
)

foreach ($f in $folders) {
    if (!(Test-Path $f)) {
        New-Item -ItemType Directory -Path $f | Out-Null
    }
}

# Création des fichiers backend
$files = @{
    "$base\backend\main.py"                          = "# FastAPI / Routes principales";
    "$base\backend\connectors\reasoning\api.py"      = "# API raisonnement";
    "$base\backend\connectors\code\api.py"           = "# API code";
    "$base\backend\connectors\vision\api.py"         = "# API vision";
    "$base\backend\connectors\search\api.py"         = "# API recherche";
    "$base\backend\rag\rag_engine.py"                = "# RAG LanceDB portable";
    "$base\backend\local_agent\actions.py"           = "# Actions locales Windows sécurisées";
    "$base\backend\local_agent\toolkit.py"           = "# Toolkit de gestion fichiers";
}

foreach ($path in $files.Keys) {
    if (!(Test-Path $path)) {
        $files[$path] | Out-File $path -Encoding UTF8
    }
}

# Fichiers frontend minimaux
$front_files = @{
    "$base\frontend\ui\index.html" = "<!-- Interface agent -->";
    "$base\frontend\ui\style.css"  = "/* CSS */";
    "$base\frontend\ui\app.js"     = "// JS agent";
}

foreach ($path in $front_files.Keys) {
    if (!(Test-Path $path)) {
        $front_files[$path] | Out-File $path -Encoding UTF8
    }
}

Write-Host "=== STRUCTURE COMPLETE CRÉÉE ==="
