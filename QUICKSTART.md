# 🚀 Quick Start - System Actions Module

Guide de démarrage en 5 minutes.

## ⚡ Installation Rapide

```bash
# 1. Installer psutil (optionnel mais recommandé)
pip install psutil

# 2. Tester le module
python test_system_actions.py

# 3. Lancer le serveur
python example_integration.py
```

## 🎯 Premiers Tests

### Option 1 : Python Direct

```python
from backend.connectors.system.system_actions import SystemActions

system = SystemActions()

# Vérifier si Windows existe
result = system.exists("C:\\Windows", allow=True)
print(result)
# {'success': True, 'exists': True, 'is_dir': True, ...}

# Lister les processus
result = system.list_processes(allow=True)
print(f"Processus: {result['count']}")
```

### Option 2 : API HTTP

```bash
# Démarrer le serveur
python example_integration.py

# Dans un autre terminal :
curl http://localhost:8000/system/health
curl -X POST http://localhost:8000/system/list \
  -H "Content-Type: application/json" \
  -d '{"allow": true}'
```

### Option 3 : Swagger UI

1. Lancer : `python example_integration.py`
2. Ouvrir : http://localhost:8000/docs
3. Tester les endpoints interactivement

## 📚 Documentation

| Fichier | Description |
|---------|-------------|
| [SYSTEM_ACTIONS_SUMMARY.md](SYSTEM_ACTIONS_SUMMARY.md) | **Commencer ici** - Vue d'ensemble complète |
| [backend/connectors/system/README.md](backend/connectors/system/README.md) | Documentation technique |
| [backend/connectors/system/EXAMPLES.md](backend/connectors/system/EXAMPLES.md) | Exemples de code |
| [backend/connectors/system/API_RESPONSES.md](backend/connectors/system/API_RESPONSES.md) | Format des réponses API |
| [SYSTEM_MODULE_INTEGRATION.md](SYSTEM_MODULE_INTEGRATION.md) | Guide d'intégration |

## 🔑 Points Clés

### Sécurité
```python
# ✅ Bon
system.exists("C:\\Windows", allow=True)

# ❌ Refusé
system.exists("C:\\Windows", allow=False)
```

### 6 Actions Disponibles
1. `exists(path, allow)` - Vérifier existence
2. `open_file(path, allow)` - Ouvrir fichier
3. `open_folder(path, allow)` - Ouvrir dossier
4. `run_program(path, args, allow)` - Lancer programme
5. `list_processes(allow)` - Lister processus
6. `kill_process(name, allow)` - Terminer processus

### 9 Endpoints API
- `GET /system/health` - Health check
- `GET /system/info` - Infos système
- `POST /system/exists` - Vérifier existence
- `POST /system/open` - Ouvrir auto
- `POST /system/open/file` - Ouvrir fichier
- `POST /system/open/folder` - Ouvrir dossier
- `POST /system/run` - Lancer programme
- `POST /system/list` - Lister processus
- `POST /system/kill` - Terminer processus

## 💻 Exemples Ultra-Rapides

### Vérifier Windows
```python
from backend.connectors.system.system_actions import SystemActions
system = SystemActions()
print(system.exists("C:\\Windows", allow=True))
```

### Lister Processus Chrome
```python
result = system.list_processes(allow=True)
chrome = [p for p in result['processes'] if 'chrome' in p['name'].lower()]
print(f"Chrome: {len(chrome)} processus, {sum(p['memory_mb'] for p in chrome):.2f} MB")
```

### Ouvrir un fichier
```python
system.open_file("C:\\test.txt", allow=True)
```

## 🧪 Tests

```bash
# Tests unitaires
python test_system_actions.py

# Tests API (serveur doit être lancé)
python example_integration.py  # Terminal 1
python test_system_routes.py   # Terminal 2
```

## 🎉 C'est Prêt !

Le module est maintenant :
- ✅ Installé
- ✅ Testé
- ✅ Documenté
- ✅ Prêt à l'emploi

## 🆘 Besoin d'Aide ?

1. Voir [SYSTEM_ACTIONS_SUMMARY.md](SYSTEM_ACTIONS_SUMMARY.md) pour la vue d'ensemble
2. Voir [EXAMPLES.md](backend/connectors/system/EXAMPLES.md) pour les exemples
3. Lancer les tests : `python test_system_actions.py`

---

**Prochaine étape :** Intégrer dans votre application avec [SYSTEM_MODULE_INTEGRATION.md](SYSTEM_MODULE_INTEGRATION.md)
