$base = "C:\AGENT LOCAL"

$folders = @(
    "$base\backend",
    "$base\backend\connectors",
    "$base\backend\connectors\reasoning",
    "$base\backend\connectors\code",
    "$base\backend\connectors\vision",
    "$base\backend\connectors\search",
    "$base\backend\rag",
    "$base\backend\local_agent"
)

foreach ($f in $folders) {
    $initPath = Join-Path $f "__init__.py"
    if (!(Test-Path $initPath)) {
        "" | Out-File $initPath -Encoding utf8
        Write-Host "Créé: $initPath"
    }
}

Write-Host "Fichiers __init__.py créés."
