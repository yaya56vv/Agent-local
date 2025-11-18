# Exemples d'utilisation du module System Actions

## Table des matières
1. [Vérification d'existence](#vérification-dexistence)
2. [Ouverture de fichiers](#ouverture-de-fichiers)
3. [Ouverture de dossiers](#ouverture-de-dossiers)
4. [Lancement de programmes](#lancement-de-programmes)
5. [Gestion des processus](#gestion-des-processus)
6. [Cas d'usage pratiques](#cas-dusage-pratiques)

---

## Vérification d'existence

### Python (Direct)

```python
from backend.connectors.system.system_actions import SystemActions

system = SystemActions()

# Vérifier un fichier
result = system.exists("C:\\Windows\\System32\\notepad.exe", allow=True)
print(f"Existe: {result['exists']}")
print(f"Type: {'Fichier' if result['is_file'] else 'Dossier'}")
print(f"Taille: {result['size_bytes']} bytes")

# Vérifier un dossier
result = system.exists("C:\\Users", allow=True)
print(result)
# Output: {
#   'success': True,
#   'exists': True,
#   'path': 'C:\\Users',
#   'is_file': False,
#   'is_dir': True,
#   ...
# }
```

### API (HTTP)

```bash
curl -X POST http://localhost:8000/system/exists \
  -H "Content-Type: application/json" \
  -d '{
    "path": "C:\\Windows",
    "allow": true
  }'
```

---

## Ouverture de fichiers

### Python (Direct)

```python
from backend.connectors.system.system_actions import SystemActions

system = SystemActions()

# Ouvrir un fichier texte
result = system.open_file("C:\\Users\\Public\\Documents\\test.txt", allow=True)
print(result)
# Output: {
#   'success': True,
#   'message': 'File opened: C:\\Users\\Public\\Documents\\test.txt',
#   'path': 'C:\\Users\\Public\\Documents\\test.txt'
# }

# Ouvrir une image
result = system.open_file("C:\\Pictures\\photo.jpg", allow=True)

# Ouvrir un PDF
result = system.open_file("C:\\Documents\\report.pdf", allow=True)
```

### API (HTTP)

```bash
# Ouvrir un fichier
curl -X POST http://localhost:8000/system/open/file \
  -H "Content-Type: application/json" \
  -d '{
    "path": "C:\\test.txt",
    "allow": true
  }'
```

### JavaScript

```javascript
async function openFile(filePath) {
  const response = await fetch('http://localhost:8000/system/open/file', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      path: filePath,
      allow: true
    })
  });

  const result = await response.json();
  console.log(result);
}

openFile('C:\\Users\\Public\\Documents\\test.txt');
```

---

## Ouverture de dossiers

### Python (Direct)

```python
from backend.connectors.system.system_actions import SystemActions

system = SystemActions()

# Ouvrir un dossier dans l'explorateur
result = system.open_folder("C:\\Users\\Public\\Documents", allow=True)
print(result)

# Ouvrir le dossier utilisateur
import os
user_folder = os.path.expanduser("~")
result = system.open_folder(user_folder, allow=True)
```

### API (HTTP)

```bash
curl -X POST http://localhost:8000/system/open/folder \
  -H "Content-Type: application/json" \
  -d '{
    "path": "C:\\Users\\Public",
    "allow": true
  }'
```

---

## Lancement de programmes

### Python (Direct)

```python
from backend.connectors.system.system_actions import SystemActions

system = SystemActions()

# Lancer Notepad
result = system.run_program("C:\\Windows\\System32\\notepad.exe", allow=True)
print(f"PID: {result['pid']}")

# Lancer avec arguments
result = system.run_program(
    path="C:\\Windows\\System32\\cmd.exe",
    args=["/c", "echo", "Hello World"],
    allow=True
)
print(f"Programme lancé avec PID: {result['pid']}")

# Lancer un script Python
result = system.run_program(
    path="python",
    args=["script.py", "--arg1", "value"],
    allow=True
)
```

### API (HTTP)

```bash
# Lancer Notepad
curl -X POST http://localhost:8000/system/run \
  -H "Content-Type: application/json" \
  -d '{
    "path": "C:\\Windows\\System32\\notepad.exe",
    "allow": true
  }'

# Avec arguments
curl -X POST http://localhost:8000/system/run \
  -H "Content-Type: application/json" \
  -d '{
    "path": "C:\\Windows\\System32\\cmd.exe",
    "args": ["/c", "echo", "Hello"],
    "allow": true
  }'
```

---

## Gestion des processus

### Python (Direct)

```python
from backend.connectors.system.system_actions import SystemActions

system = SystemActions()

# Lister tous les processus
result = system.list_processes(allow=True)
print(f"Total: {result['count']} processus")

for proc in result['processes']:
    print(f"{proc['name']:30} PID: {proc['pid']:6} Mem: {proc['memory_mb']:6.2f} MB")

# Filtrer les processus Chrome
chrome_procs = [p for p in result['processes'] if 'chrome' in p['name'].lower()]
print(f"\nProcessus Chrome: {len(chrome_procs)}")

# Terminer un processus
result = system.kill_process("notepad.exe", allow=True)
if result['success']:
    print(f"Terminé {result['killed_count']} processus")
    print(f"PIDs: {result['killed_pids']}")
else:
    print(result['message'])
```

### API (HTTP)

```bash
# Lister les processus
curl -X POST http://localhost:8000/system/list \
  -H "Content-Type: application/json" \
  -d '{"allow": true}'

# Terminer un processus
curl -X POST http://localhost:8000/system/kill \
  -H "Content-Type: application/json" \
  -d '{
    "name": "notepad.exe",
    "allow": true
  }'
```

### Python (avec filtrage)

```python
def find_process_by_name(name):
    """Trouve un processus par son nom"""
    system = SystemActions()
    result = system.list_processes(allow=True)

    return [p for p in result['processes']
            if name.lower() in p['name'].lower()]

# Utilisation
chrome_processes = find_process_by_name("chrome")
for proc in chrome_processes:
    print(f"{proc['name']} - {proc['memory_mb']} MB")

def get_total_memory_by_process(name):
    """Calcule la mémoire totale utilisée par un processus"""
    processes = find_process_by_name(name)
    total = sum(p['memory_mb'] for p in processes)
    return total

memory = get_total_memory_by_process("chrome")
print(f"Chrome utilise {memory:.2f} MB")
```

---

## Cas d'usage pratiques

### 1. Vérifier et ouvrir un fichier

```python
from backend.connectors.system.system_actions import SystemActions

def open_if_exists(file_path):
    """Ouvre un fichier seulement s'il existe"""
    system = SystemActions()

    # Vérifier existence
    check = system.exists(file_path, allow=True)

    if check['exists'] and check['is_file']:
        # Ouvrir le fichier
        result = system.open_file(file_path, allow=True)
        print(f"✓ Fichier ouvert: {file_path}")
        return True
    else:
        print(f"✗ Fichier introuvable: {file_path}")
        return False

# Utilisation
open_if_exists("C:\\Users\\Public\\Documents\\rapport.pdf")
```

### 2. Moniteur de mémoire

```python
from backend.connectors.system.system_actions import SystemActions
import time

def monitor_memory(process_name, duration=60, interval=5):
    """Surveille la mémoire d'un processus"""
    system = SystemActions()

    print(f"Surveillance de {process_name} pendant {duration}s...")

    for i in range(duration // interval):
        result = system.list_processes(allow=True)

        # Filtrer le processus
        procs = [p for p in result['processes']
                if process_name.lower() in p['name'].lower()]

        if procs:
            total_mem = sum(p['memory_mb'] for p in procs)
            print(f"[{i*interval}s] {process_name}: {total_mem:.2f} MB ({len(procs)} instances)")
        else:
            print(f"[{i*interval}s] {process_name}: Processus non trouvé")

        time.sleep(interval)

# Utilisation
monitor_memory("chrome", duration=30, interval=5)
```

### 3. Nettoyeur de processus

```python
from backend.connectors.system.system_actions import SystemActions

def cleanup_processes(process_names):
    """Termine plusieurs processus"""
    system = SystemActions()
    results = []

    for name in process_names:
        try:
            result = system.kill_process(name, allow=True)
            results.append({
                'name': name,
                'success': result['success'],
                'killed': result.get('killed_count', 0)
            })
        except Exception as e:
            results.append({
                'name': name,
                'success': False,
                'error': str(e)
            })

    return results

# Utilisation
to_cleanup = ["notepad.exe", "calc.exe"]
results = cleanup_processes(to_cleanup)

for r in results:
    if r['success']:
        print(f"✓ {r['name']}: {r['killed']} processus terminés")
    else:
        print(f"✗ {r['name']}: {r.get('error', 'Aucun processus trouvé')}")
```

### 4. Lanceur d'applications

```python
from backend.connectors.system.system_actions import SystemActions
import time

def launch_workspace():
    """Lance un espace de travail complet"""
    system = SystemActions()

    apps = [
        {
            "name": "VS Code",
            "path": "C:\\Users\\USER\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
            "args": ["C:\\Projects\\MyProject"]
        },
        {
            "name": "Chrome",
            "path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "args": ["https://github.com"]
        }
    ]

    for app in apps:
        try:
            result = system.run_program(
                path=app['path'],
                args=app.get('args'),
                allow=True
            )
            print(f"✓ {app['name']} lancé (PID: {result['pid']})")
            time.sleep(1)  # Pause entre les lancements
        except Exception as e:
            print(f"✗ {app['name']}: {str(e)}")

# Utilisation
launch_workspace()
```

### 5. API Wrapper complet

```python
from backend.connectors.system.system_actions import SystemActions
from typing import Dict, List, Optional

class SystemManager:
    """Wrapper avancé pour SystemActions"""

    def __init__(self):
        self.system = SystemActions()

    def safe_open(self, path: str) -> Dict:
        """Ouvre un fichier ou dossier de manière sécurisée"""
        check = self.system.exists(path, allow=True)

        if not check['exists']:
            return {'success': False, 'error': 'Path not found'}

        if check['is_file']:
            return self.system.open_file(path, allow=True)
        else:
            return self.system.open_folder(path, allow=True)

    def get_process_info(self, name: str) -> List[Dict]:
        """Récupère les infos d'un processus"""
        result = self.system.list_processes(allow=True)
        return [p for p in result['processes']
                if name.lower() in p['name'].lower()]

    def is_running(self, process_name: str) -> bool:
        """Vérifie si un processus est en cours"""
        procs = self.get_process_info(process_name)
        return len(procs) > 0

    def launch_if_not_running(self, process_name: str, path: str,
                             args: Optional[List[str]] = None) -> Dict:
        """Lance un programme seulement s'il n'est pas déjà lancé"""
        if self.is_running(process_name):
            return {
                'success': False,
                'message': f'{process_name} is already running'
            }

        return self.system.run_program(path, args, allow=True)

# Utilisation
manager = SystemManager()

# Ouvrir intelligemment
manager.safe_open("C:\\Users\\Public\\Documents")

# Vérifier et lancer
if not manager.is_running("notepad.exe"):
    manager.launch_if_not_running(
        "notepad.exe",
        "C:\\Windows\\System32\\notepad.exe"
    )
```

---

## Gestion des erreurs

### Pattern recommandé

```python
from backend.connectors.system.system_actions import (
    SystemActions,
    SystemActionsError,
    PermissionDeniedError
)

system = SystemActions()

try:
    result = system.open_file("C:\\test.txt", allow=True)
    print(f"✓ Succès: {result['message']}")

except PermissionDeniedError as e:
    print(f"✗ Permission refusée: {e}")
    print("Conseil: Ajoutez allow=True")

except SystemActionsError as e:
    print(f"✗ Erreur système: {e}")

except Exception as e:
    print(f"✗ Erreur inattendue: {e}")
```

---

## Notes de sécurité

### ✅ Bonnes pratiques

```python
# Toujours utiliser allow=True explicitement
result = system.open_file(path, allow=True)

# Vérifier l'existence avant d'ouvrir
check = system.exists(path, allow=True)
if check['exists']:
    result = system.open_file(path, allow=True)

# Gérer les erreurs proprement
try:
    result = system.kill_process("process.exe", allow=True)
except PermissionDeniedError:
    print("Permission required")
```

### ❌ À éviter

```python
# Ne jamais oublier allow=True
result = system.open_file(path)  # ❌ Sera refusé

# Ne pas ignorer les erreurs
system.open_file(path, allow=True)  # ❌ Pas de gestion d'erreur

# Ne pas supposer qu'un fichier existe
system.open_file(path, allow=True)  # ❌ Peut échouer si n'existe pas
```
