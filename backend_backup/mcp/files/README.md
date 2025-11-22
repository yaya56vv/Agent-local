# Files MCP API

## Outils exposés
- `read_file(path)`: Lire le contenu d'un fichier.
- `write_file(path, content)`: Écrire du contenu dans un fichier (écrase ou crée).
- `list_dir(path)`: Lister les fichiers et dossiers d'un répertoire.
- `mkdir(path)`: Créer un répertoire (récursif).
- `delete_file(path)`: Supprimer un fichier.
- `file_search(pattern, path)`: Rechercher des fichiers correspondant à un motif.
- `get_file_info(path)`: Obtenir les métadonnées d'un fichier (taille, dates).

## Schéma d’appel
### Requête
```json
{
  "tool": "read_file",
  "params": {
    "path": "/chemin/absolu/vers/fichier.txt"
  }
}
```

### Réponse
```json
{
  "status": "success",
  "data": {
    "content": "Contenu du fichier...",
    "encoding": "utf-8"
  }
}
```

## Dépendances requises
- `os`
- `shutil`
- `pathlib`
- `glob`

## Interaction avec l’orchestrateur
- L'orchestrateur appelle ce service via HTTP (POST /mcp/files) ou via un protocole MCP standard sur stdio/SSE.
- **Vigilance**: Validation stricte des chemins pour éviter l'accès hors du workspace autorisé (Path Traversal).
