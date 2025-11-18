# Assistant Windows - Mission 6

Mini-application Windows PySide6 avec hotkeys F1/F8/F9/F10 + capture d'écran + lien backend

## 🎯 Objectif

Application Windows locale en Python utilisant PySide6, indépendante du backend FastAPI, qui sert de "petite fenêtre copilote flottante".

**L'application ne tourne PAS en permanence** - elle se lance uniquement quand l'utilisateur appuie sur F1 ou F8.

## 🔑 Hotkeys Globales

| Touche | Action | Description |
|--------|--------|-------------|
| **F1** | Lancer/Afficher fenêtre | Ouvre la fenêtre sans démarrer la capture |
| **F8** | Lancer + Capture auto | Ouvre la fenêtre ET démarre la capture automatique |
| **F9** | Arrêter capture | Arrête la capture automatique (fenêtre reste ouverte) |
| **F10** | Capture unique | Fait un screenshot ponctuel |

## 📁 Architecture

```
assistant_windows/
│
├── main.py                # Point d'entrée principal
├── requirements.txt       # Dépendances Python
├── README.md             # Cette documentation
│
├── ui/
│   ├── __init__.py
│   └── floating_window.py # Fenêtre PySide6 flottante
│
└── services/
    ├── __init__.py
    ├── hotkeys.py         # Gestion des hotkeys F1/F8/F9/F10
    ├── screenshot.py      # Capture d'écran (dxcam/mss)
    └── api_client.py      # Communication avec backend
```

## 🚀 Installation

### 1. Installer les dépendances

```bash
cd assistant_windows
pip install -r requirements.txt
```

### 2. Vérifier que le backend est lancé

Le backend FastAPI doit être actif sur `http://localhost:8000`

```bash
# Dans le répertoire racine du projet
python -m uvicorn backend.main:app --reload --port 8000
```

### 3. Lancer l'assistant

```bash
python main.py
```

## 🎨 Interface Utilisateur

### Caractéristiques de la fenêtre

- **Always on top** - reste au-dessus des autres fenêtres
- **Taille** : 320x500 pixels
- **Thème sombre** avec coins arrondis
- **Déplaçable** à la souris
- **Opacité** : 95%

### Éléments UI

1. **Barre de titre** personnalisée avec bouton fermer
2. **Indicateur d'état** :
   - 🟠 Prêt / En attente
   - 🟢 Vision Active (capture automatique)
   - 🟡 Vision Arrêtée (mode manuel)
   - 🔴 Hors Ligne (backend indisponible)
3. **Zone de texte** pour afficher les résultats Vision
4. **Champ de saisie** (optionnel pour cette mission)
5. **Bouton Stop** pour fermer l'application

## 🔄 Comportement des Hotkeys

### F1 - Afficher la fenêtre

```
- Lance l'app si pas déjà lancée
- Affiche la fenêtre si cachée
- Ne déclenche PAS la capture
- État : 🟠 Prêt
```

### F8 - Démarrer capture automatique

```
- Lance l'app si pas déjà lancée
- Affiche la fenêtre si cachée
- Démarre la boucle de capture (toutes les 2 secondes)
- Envoie chaque frame à /vision/screenshot
- Affiche les résultats en temps réel
- État : 🟢 Vision Active
```

### F9 - Arrêter capture automatique

```
- Arrête immédiatement la capture continue
- La fenêtre RESTE ouverte
- L'assistant reste actif
- État : 🟡 Vision Arrêtée
```

### F10 - Capture unique

```
- Fait un screenshot ponctuel
- Envoie au backend pour analyse
- Affiche le résultat
- N'affecte pas la capture automatique
```

## 📸 Capture d'écran

### Méthodes supportées

1. **dxcam** (recommandé pour Windows) - Très rapide, utilise DirectX
2. **mss** (fallback) - Cross-platform, plus lent mais fiable

Le service choisit automatiquement la meilleure méthode disponible.

### Configuration

- **Intervalle de capture** : 2 secondes (configurable)
- **Format** : PNG
- **Limite** : 1 capture à la fois (évite la saturation)

## 🔌 Communication Backend

### Endpoint utilisé

```
POST /vision/screenshot
Content-Type: multipart/form-data
```

### Format de réponse attendu

```json
{
  "description": "Description de ce qui est visible",
  "suggested_actions": ["Action 1", "Action 2"],
  "detected_text": "Texte détecté dans l'image",
  "confidence": 0.95
}
```

### Gestion des erreurs

- **Timeout** : 7 secondes
- **Retry** : Non (pour éviter la saturation)
- **État offline** : Affiché si backend indisponible

## 🧪 Tests

### Test F1
```
1. Lancer l'app avec F1
2. Vérifier que la fenêtre s'ouvre
3. Vérifier l'état : 🟠 Prêt
```

### Test F8
```
1. Appuyer sur F8
2. Vérifier que la fenêtre s'ouvre
3. Vérifier l'état : 🟢 Vision Active
4. Vérifier que les captures s'affichent toutes les 2s
```

### Test F9
```
1. Avec F8 actif, appuyer sur F9
2. Vérifier que la capture s'arrête
3. Vérifier l'état : 🟡 Vision Arrêtée
4. Vérifier que la fenêtre reste ouverte
```

### Test F10
```
1. Appuyer sur F10
2. Vérifier qu'une capture unique est faite
3. Vérifier que le résultat s'affiche
4. Vérifier que l'état ne change pas
```

### Test Stop
```
1. Cliquer sur le bouton Stop
2. Vérifier que la fenêtre se ferme
3. Vérifier que les hotkeys sont désactivées
```

## 📝 Logs

Les logs sont affichés dans la console avec le format :

```
2024-01-18 16:30:00 - module_name - INFO - Message
```

Niveaux de log :
- **INFO** : Événements normaux
- **DEBUG** : Détails de capture
- **WARNING** : Problèmes non critiques
- **ERROR** : Erreurs avec stack trace

## ⚠️ Limitations (Mission 6)

- ❌ Pas de contrôle souris (Mission 7)
- ❌ Pas de reconnaissance vocale (Mission 8)
- ❌ Pas de synthèse vocale (Mission 8)

## 🔧 Dépannage

### L'application ne se lance pas

```bash
# Vérifier les dépendances
pip install -r requirements.txt

# Vérifier les permissions (keyboard nécessite admin sur Windows)
# Lancer en tant qu'administrateur si nécessaire
```

### Les hotkeys ne fonctionnent pas

- Vérifier que l'application tourne en tant qu'administrateur
- Vérifier qu'aucune autre application n'utilise ces touches

### La capture ne fonctionne pas

```bash
# Installer dxcam (recommandé)
pip install dxcam

# Ou utiliser mss (fallback)
pip install mss
```

### Le backend ne répond pas

```bash
# Vérifier que le backend est lancé
curl http://localhost:8000/health

# Vérifier les logs du backend
```

## 🚀 Prochaines étapes

- **Mission 7** : Contrôle souris automatique
- **Mission 8** : Reconnaissance et synthèse vocale

## 📄 Licence

Partie du projet Agent Local - Mission 6