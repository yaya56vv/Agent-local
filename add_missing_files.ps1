$base = "C:\AGENT LOCAL"

Write-Host "=== Ajout des fichiers manquants ==="

function Create-File($path, $content) {
    if (!(Test-Path $path)) {
        $content | Out-File $path -Encoding utf8
        Write-Host "Fichier créé: $path"
    } else {
        Write-Host "Déjà présent: $path"
    }
}

# Connecteurs placeholders
$connectorFolders = @(
    "$base\backend\connectors\reasoning",
    "$base\backend\connectors\code",
    "$base\backend\connectors\vision",
    "$base\backend\connectors\search"
)

foreach ($folder in $connectorFolders) {
    if (!(Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder | Out-Null
        Write-Host "Dossier créé: $folder"
    }
}

Create-File "$base\backend\connectors\reasoning\placeholder.py" "# Placeholder reasoning"
Create-File "$base\backend\connectors\code\placeholder.py" "# Placeholder code"
Create-File "$base\backend\connectors\vision\placeholder.py" "# Placeholder vision"
Create-File "$base\backend\connectors\search\placeholder.py" "# Placeholder search"

# Fichiers frontend app.js et style.css
Create-File "$base\frontend\ui\app.js" "// JS principal"
Create-File "$base\frontend\ui\style.css" "/* Styles de l'interface */"

Write-Host "=== Ajout terminé ==="
