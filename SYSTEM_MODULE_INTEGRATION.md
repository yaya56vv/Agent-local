# Intégration du Module System Actions

## Fichiers créés

### Backend

1. **backend/connectors/system/__init__.py**
   - Fichier d'initialisation du package

2. **backend/connectors/system/system_actions.py**
   - Classe `SystemActions` avec toutes les méthodes système
   - Gestion de la sécurité avec `allow=True` obligatoire
   - Support Windows, macOS, Linux

3. **backend/connectors/system/README.md**
   - Documentation complète du module

4. **backend/routes/system_route.py**
   - Routes FastAPI pour exposer les fonctionnalités
   - Modèles Pydantic pour validation
   - Gestion des erreurs HTTP

### Tests

5. **test_system_actions.py**
   - Tests unitaires du module SystemActions
   - Exécutable directement : `python test_system_actions.py`

6. **test_system_routes.py**
   - Tests des routes API HTTP
   - Nécessite serveur FastAPI en cours d'exécution

## Intégration dans l'application principale

Pour intégrer les routes système dans votre application FastAPI, ajoutez dans votre fichier principal (ex: `main.py` ou `app.py`) :

```python
from fastapi import FastAPI
from backend.routes import system_route

app = FastAPI()

# Inclure les routes système
app.include_router(
    system_route.router,
    prefix="/system",
    tags=["system"]
)
```

## Endpoints disponibles

Une fois intégré, les endpoints suivants seront disponibles :

### Lecture seule
- `GET /system/health` - Vérifier l'état du service
- `GET /system/info` - Obtenir les informations système

### Actions système (nécessitent `allow=True`)
- `POST /system/open` - Ouvrir fichier ou dossier automatiquement
- `POST /system/open/file` - Ouvrir un fichier spécifiquement
- `POST /system/open/folder` - Ouvrir un dossier spécifiquement
- `POST /system/run` - Lancer un programme
- `POST /system/list` - Lister les processus (nécessite psutil)
- `POST /system/kill` - Terminer un processus (nécessite psutil)
- `POST /system/exists` - Vérifier l'existence d'un chemin

## Exemples d'utilisation

### Avec curl

```bash
# Health check
curl http://localhost:8000/system/health

# Informations système
curl http://localhost:8000/system/info

# Vérifier si un fichier existe
curl -X POST http://localhost:8000/system/exists \
  -H "Content-Type: application/json" \
  -d '{"path": "C:\\Windows", "allow": true}'

# Lister les processus
curl -X POST http://localhost:8000/system/list \
  -H "Content-Type: application/json" \
  -d '{"allow": true}'

# Ouvrir un fichier
curl -X POST http://localhost:8000/system/open/file \
  -H "Content-Type: application/json" \
  -d '{"path": "C:\\test.txt", "allow": true}'
```

### Avec Python requests

```python
import requests

# Health check
response = requests.get("http://localhost:8000/system/health")
print(response.json())

# Vérifier existence
response = requests.post(
    "http://localhost:8000/system/exists",
    json={"path": "C:\\Windows", "allow": True}
)
print(response.json())

# Lister processus
response = requests.post(
    "http://localhost:8000/system/list",
    json={"allow": True}
)
data = response.json()
print(f"Found {data['count']} processes")
```

### Avec JavaScript (fetch)

```javascript
// Health check
fetch('http://localhost:8000/system/health')
  .then(r => r.json())
  .then(data => console.log(data));

// Vérifier existence
fetch('http://localhost:8000/system/exists', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    path: 'C:\\Windows',
    allow: true
  })
})
  .then(r => r.json())
  .then(data => console.log(data));
```

## Sécurité

### Protection par `allow=True`

Toutes les actions nécessitent explicitement `allow=True` dans la requête :

```python
# ✅ Autorisé
{"path": "C:\\test.txt", "allow": true}

# ❌ Refusé (HTTP 403)
{"path": "C:\\test.txt", "allow": false}

# ❌ Refusé (HTTP 403)
{"path": "C:\\test.txt"}
```

### Codes d'erreur HTTP

- `200` - Succès
- `400` - Erreur dans la requête (fichier introuvable, etc.)
- `403` - Permission refusée (`allow=True` non fourni)
- `500` - Erreur serveur interne

## Dépendances optionnelles

### psutil (recommandé)

Pour la gestion des processus :

```bash
pip install psutil
```

Sans psutil :
- ✅ `open_file`, `open_folder`, `run_program`, `exists` fonctionnent
- ❌ `list_processes`, `kill_process` ne sont pas disponibles

## Tests

### Tests unitaires

```bash
cd "C:\AGENT LOCAL"
python test_system_actions.py
```

### Tests API

1. Démarrer le serveur :
```bash
uvicorn main:app --reload
```

2. Lancer les tests :
```bash
python test_system_routes.py
```

## Documentation API interactive

Une fois le serveur démarré, accédez à :
- Swagger UI : http://localhost:8000/docs
- ReDoc : http://localhost:8000/redoc

## Notes importantes

1. **Ne modifie pas les autres modules** - Le module est totalement indépendant
2. **Compatible multiplateforme** - Fonctionne sur Windows, macOS, Linux
3. **Sécurisé par défaut** - Toutes les actions nécessitent confirmation explicite
4. **Gestion d'erreurs robuste** - Exceptions claires et messages informatifs
5. **Code propre** - Type hints, docstrings, commentaires en français

## Structure du projet

```
backend/
├── connectors/
│   ├── files/          # Module existant (non modifié)
│   └── system/         # Nouveau module
│       ├── __init__.py
│       ├── system_actions.py
│       └── README.md
└── routes/
    ├── files_route.py  # Route existante (non modifiée)
    └── system_route.py # Nouvelle route

test_system_actions.py    # Tests unitaires
test_system_routes.py     # Tests API
SYSTEM_MODULE_INTEGRATION.md  # Ce fichier
```

## Support

Pour toute question ou problème :
1. Consultez [README.md](backend/connectors/system/README.md)
2. Vérifiez les tests pour des exemples d'utilisation
3. Consultez la documentation interactive (Swagger UI)
