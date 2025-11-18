# Réponses API - System Actions Module

Documentation complète des réponses JSON pour chaque endpoint.

## Table des matières
- [Health Check](#health-check)
- [System Info](#system-info)
- [Exists](#exists)
- [Open File](#open-file)
- [Open Folder](#open-folder)
- [Run Program](#run-program)
- [List Processes](#list-processes)
- [Kill Process](#kill-process)
- [Codes d'Erreur](#codes-derreur)

---

## Health Check

### `GET /system/health`

**Succès (200):**
```json
{
  "status": "healthy",
  "service": "system",
  "platform": "Windows",
  "is_windows": true,
  "psutil_available": true
}
```

**Sans psutil:**
```json
{
  "status": "healthy",
  "service": "system",
  "platform": "Windows",
  "is_windows": true,
  "psutil_available": false,
  "warning": "psutil not installed - process management unavailable"
}
```

**Erreur:**
```json
{
  "status": "unhealthy",
  "service": "system",
  "error": "Error message"
}
```

---

## System Info

### `GET /system/info`

**Succès (200):**
```json
{
  "status": "success",
  "info": {
    "platform": "Windows",
    "platform_release": "10",
    "platform_version": "10.0.19045",
    "architecture": "AMD64",
    "processor": "Intel64 Family 6 Model 142 Stepping 10, GenuineIntel",
    "python_version": "3.13.0",
    "psutil_available": true,
    "cpu_count": 4,
    "memory_total_gb": 31.43
  }
}
```

**Sans psutil:**
```json
{
  "status": "success",
  "info": {
    "platform": "Windows",
    "platform_release": "10",
    "platform_version": "10.0.19045",
    "architecture": "AMD64",
    "processor": "Intel64 Family 6 Model 142 Stepping 10, GenuineIntel",
    "python_version": "3.13.0",
    "psutil_available": false
  }
}
```

---

## Exists

### `POST /system/exists`

**Request:**
```json
{
  "path": "C:\\Windows",
  "allow": true
}
```

**Succès - Existe (200):**
```json
{
  "success": true,
  "exists": true,
  "path": "C:\\Windows",
  "is_file": false,
  "is_dir": true,
  "size_bytes": 16384,
  "modified_timestamp": 1763387110.3215418
}
```

**Succès - N'existe pas (200):**
```json
{
  "success": true,
  "exists": false,
  "path": "C:\\nonexistent"
}
```

**Erreur - Permission (403):**
```json
{
  "detail": "Action refused: allow=True required for security"
}
```

---

## Open File

### `POST /system/open/file`

**Request:**
```json
{
  "path": "C:\\Users\\Public\\Documents\\test.txt",
  "allow": true
}
```

**Succès (200):**
```json
{
  "success": true,
  "message": "File opened: C:\\Users\\Public\\Documents\\test.txt",
  "path": "C:\\Users\\Public\\Documents\\test.txt"
}
```

**Erreur - Fichier introuvable (400):**
```json
{
  "detail": "File not found: C:\\nonexistent.txt"
}
```

**Erreur - Pas un fichier (400):**
```json
{
  "detail": "Path is not a file: C:\\Windows"
}
```

**Erreur - Permission (403):**
```json
{
  "detail": "Action refused: allow=True required for security"
}
```

---

## Open Folder

### `POST /system/open/folder`

**Request:**
```json
{
  "path": "C:\\Users\\Public\\Documents",
  "allow": true
}
```

**Succès (200):**
```json
{
  "success": true,
  "message": "Folder opened: C:\\Users\\Public\\Documents",
  "path": "C:\\Users\\Public\\Documents"
}
```

**Erreur - Dossier introuvable (400):**
```json
{
  "detail": "Folder not found: C:\\nonexistent"
}
```

**Erreur - Pas un dossier (400):**
```json
{
  "detail": "Path is not a folder: C:\\Windows\\notepad.exe"
}
```

---

## Run Program

### `POST /system/run`

**Request simple:**
```json
{
  "path": "C:\\Windows\\System32\\notepad.exe",
  "allow": true
}
```

**Request avec arguments:**
```json
{
  "path": "C:\\Windows\\System32\\cmd.exe",
  "args": ["/c", "echo", "Hello World"],
  "allow": true
}
```

**Succès (200):**
```json
{
  "success": true,
  "message": "Program started: C:\\Windows\\System32\\notepad.exe",
  "path": "C:\\Windows\\System32\\notepad.exe",
  "pid": 12345
}
```

**Erreur - Programme introuvable (400):**
```json
{
  "detail": "Program not found: C:\\nonexistent.exe"
}
```

**Erreur - Permission (403):**
```json
{
  "detail": "Action refused: allow=True required for security"
}
```

---

## List Processes

### `POST /system/list`

**Request:**
```json
{
  "allow": true
}
```

**Succès (200):**
```json
{
  "success": true,
  "message": "Found 249 processes",
  "count": 249,
  "processes": [
    {
      "pid": 0,
      "name": "System Idle Process",
      "username": "NT AUTHORITY\\SYSTEM",
      "memory_mb": 0.01
    },
    {
      "pid": 4,
      "name": "System",
      "username": "NT AUTHORITY\\SYSTEM",
      "memory_mb": 0.11
    },
    {
      "pid": 488,
      "name": "chrome.exe",
      "username": "DOMAIN\\User",
      "memory_mb": 338.69
    },
    {
      "pid": 1234,
      "name": "python.exe",
      "username": "DOMAIN\\User",
      "memory_mb": 52.34
    }
  ]
}
```

**Erreur - psutil manquant (400):**
```json
{
  "detail": "psutil module not available. Install with: pip install psutil"
}
```

**Erreur - Permission (403):**
```json
{
  "detail": "Action refused: allow=True required for security"
}
```

---

## Kill Process

### `POST /system/kill`

**Request:**
```json
{
  "name": "notepad.exe",
  "allow": true
}
```

**Succès - Processus terminés (200):**
```json
{
  "success": true,
  "message": "Killed 2 process(es) named: notepad.exe",
  "killed_count": 2,
  "killed_pids": [5678, 5680]
}
```

**Succès - Aucun processus (200):**
```json
{
  "success": false,
  "message": "No process found with name: notepad.exe",
  "killed_count": 0
}
```

**Erreur - psutil manquant (400):**
```json
{
  "detail": "psutil module not available. Install with: pip install psutil"
}
```

**Erreur - Permission (403):**
```json
{
  "detail": "Action refused: allow=True required for security"
}
```

---

## Codes d'Erreur

### Codes HTTP

| Code | Signification | Cause |
|------|---------------|-------|
| 200 | OK | Succès |
| 400 | Bad Request | Fichier introuvable, module manquant, chemin invalide |
| 403 | Forbidden | `allow=True` non fourni |
| 500 | Internal Server Error | Erreur interne du serveur |

### Structure d'Erreur Standard

**403 - Forbidden:**
```json
{
  "detail": "Action refused: allow=True required for security"
}
```

**400 - Bad Request:**
```json
{
  "detail": "Specific error message"
}
```

Exemples de messages d'erreur 400 :
- `"File not found: {path}"`
- `"Folder not found: {path}"`
- `"Path is not a file: {path}"`
- `"Path is not a folder: {path}"`
- `"Program not found: {path}"`
- `"psutil module not available. Install with: pip install psutil"`
- `"Failed to open file: {error}"`
- `"Failed to run program: {error}"`
- `"Failed to list processes: {error}"`

**500 - Internal Server Error:**
```json
{
  "detail": "Failed to {action}: {error}"
}
```

---

## Exemples de Tests

### Test avec curl

```bash
# Exists - Succès
curl -X POST http://localhost:8000/system/exists \
  -H "Content-Type: application/json" \
  -d '{"path": "C:\\Windows", "allow": true}'

# Exists - Permission refusée
curl -X POST http://localhost:8000/system/exists \
  -H "Content-Type: application/json" \
  -d '{"path": "C:\\Windows", "allow": false}'

# List processes
curl -X POST http://localhost:8000/system/list \
  -H "Content-Type: application/json" \
  -d '{"allow": true}'
```

### Test avec Python requests

```python
import requests

# Exists - Succès
response = requests.post(
    "http://localhost:8000/system/exists",
    json={"path": "C:\\Windows", "allow": True}
)
print(response.status_code)  # 200
print(response.json())

# Exists - Permission refusée
response = requests.post(
    "http://localhost:8000/system/exists",
    json={"path": "C:\\Windows", "allow": False}
)
print(response.status_code)  # 403
print(response.json())

# List processes
response = requests.post(
    "http://localhost:8000/system/list",
    json={"allow": True}
)
data = response.json()
print(f"Found {data['count']} processes")
for proc in data['processes'][:5]:
    print(f"  - {proc['name']} ({proc['pid']})")
```

### Test avec JavaScript

```javascript
// Exists - Succès
fetch('http://localhost:8000/system/exists', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    path: 'C:\\Windows',
    allow: true
  })
})
  .then(r => r.json())
  .then(data => console.log(data));

// List processes
fetch('http://localhost:8000/system/list', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ allow: true })
})
  .then(r => r.json())
  .then(data => {
    console.log(`Found ${data.count} processes`);
    data.processes.slice(0, 5).forEach(p => {
      console.log(`  - ${p.name} (${p.pid})`);
    });
  });
```

---

## Validation des Requêtes

### Modèles Pydantic

Tous les endpoints utilisent des modèles Pydantic pour la validation :

**ExistsRequest:**
```python
{
  "path": str,      # Requis
  "allow": bool     # Défaut: False
}
```

**OpenFileRequest:**
```python
{
  "path": str,      # Requis
  "allow": bool     # Défaut: False
}
```

**RunProgramRequest:**
```python
{
  "path": str,           # Requis
  "args": List[str],     # Optionnel
  "allow": bool          # Défaut: False
}
```

**ListProcessesRequest:**
```python
{
  "allow": bool     # Défaut: False
}
```

**KillProcessRequest:**
```python
{
  "name": str,      # Requis
  "allow": bool     # Défaut: False
}
```

### Erreurs de Validation

Si un champ requis est manquant ou invalide :

```json
{
  "detail": [
    {
      "loc": ["body", "path"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Notes

1. **allow=True obligatoire** - Toutes les actions nécessitent cette confirmation
2. **JSON propre** - Tous les retours sont au format JSON
3. **Validation automatique** - Pydantic valide toutes les entrées
4. **Codes HTTP standard** - 200, 400, 403, 500
5. **Messages clairs** - Tous les messages sont explicites
