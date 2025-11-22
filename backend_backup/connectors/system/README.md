# System Actions Module

Module permettant à l'agent d'interagir avec le système Windows de manière sécurisée.

## Sécurité

**IMPORTANT**: Toutes les actions nécessitent `allow=True` pour être exécutées. Cela évite les actions involontaires ou malveillantes.

## Installation

Pour bénéficier de toutes les fonctionnalités (gestion des processus), installez psutil :

```bash
pip install psutil
```

## Classes

### SystemActions

Classe principale pour effectuer des actions système.

#### Méthodes

##### `open_file(path: str, allow: bool = False)`

Ouvre un fichier avec l'application par défaut.

**Paramètres:**
- `path`: Chemin du fichier
- `allow`: Doit être True (sécurité)

**Retour:**
```json
{
  "success": true,
  "message": "File opened: path/to/file",
  "path": "path/to/file"
}
```

##### `open_folder(path: str, allow: bool = False)`

Ouvre un dossier dans l'explorateur Windows.

**Paramètres:**
- `path`: Chemin du dossier
- `allow`: Doit être True (sécurité)

**Retour:**
```json
{
  "success": true,
  "message": "Folder opened: path/to/folder",
  "path": "path/to/folder"
}
```

##### `run_program(path: str, args: List[str] = None, allow: bool = False)`

Lance un programme.

**Paramètres:**
- `path`: Chemin du programme
- `args`: Arguments optionnels
- `allow`: Doit être True (sécurité)

**Retour:**
```json
{
  "success": true,
  "message": "Program started: path/to/program",
  "path": "path/to/program",
  "pid": 12345
}
```

##### `list_processes(allow: bool = False)`

Liste tous les processus en cours (nécessite psutil).

**Paramètres:**
- `allow`: Doit être True (sécurité)

**Retour:**
```json
{
  "success": true,
  "message": "Found 250 processes",
  "count": 250,
  "processes": [
    {
      "pid": 1234,
      "name": "chrome.exe",
      "username": "USER",
      "memory_mb": 256.5
    }
  ]
}
```

##### `kill_process(name: str, allow: bool = False)`

Termine un processus par son nom (nécessite psutil).

**Paramètres:**
- `name`: Nom du processus (ex: "notepad.exe")
- `allow`: Doit être True (sécurité)

**Retour:**
```json
{
  "success": true,
  "message": "Killed 1 process(es) named: notepad.exe",
  "killed_count": 1,
  "killed_pids": [5678]
}
```

##### `exists(path: str, allow: bool = False)`

Vérifie si un chemin existe.

**Paramètres:**
- `path`: Chemin à vérifier
- `allow`: Doit être True (sécurité)

**Retour:**
```json
{
  "success": true,
  "exists": true,
  "path": "C:\\Users",
  "is_file": false,
  "is_dir": true,
  "size_bytes": 4096,
  "modified_timestamp": 1234567890.0
}
```

## Exceptions

### `SystemActionsError`
Exception générale pour les erreurs d'actions système.

### `PermissionDeniedError`
Levée quand `allow=True` n'est pas fourni.

## Exemple d'utilisation

```python
from backend.connectors.system.system_actions import SystemActions

system = SystemActions()

# Vérifier si un fichier existe
result = system.exists("C:\\Windows\\notepad.exe", allow=True)
print(result)

# Ouvrir un fichier
result = system.open_file("C:\\test.txt", allow=True)
print(result)

# Lister les processus
result = system.list_processes(allow=True)
for proc in result['processes']:
    print(f"{proc['name']}: {proc['memory_mb']} MB")
```

## Routes API

Voir [system_route.py](../../routes/system_route.py) pour les endpoints HTTP.

### Endpoints disponibles

- `POST /system/open` - Ouvrir fichier ou dossier
- `POST /system/open/file` - Ouvrir fichier
- `POST /system/open/folder` - Ouvrir dossier
- `POST /system/run` - Lancer programme
- `POST /system/list` - Lister processus
- `POST /system/kill` - Tuer processus
- `POST /system/exists` - Vérifier existence
- `GET /system/health` - Health check
- `GET /system/info` - Informations système

## Compatibilité

- **Windows**: Complètement supporté (os.startfile)
- **macOS**: Partiellement supporté (via 'open')
- **Linux**: Partiellement supporté (via 'xdg-open')

Pour la gestion des processus, psutil fonctionne sur toutes les plateformes.
