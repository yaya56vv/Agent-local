# Control MCP API

## Outils exposés
- `move_mouse(x, y)`: Déplacer la souris.
- `click_mouse(button, clicks)`: Cliquer.
- `type_text(text)`: Simuler la frappe au clavier.
- `press_key(key)`: Simuler une touche spéciale (Enter, Esc...).
- `take_screenshot()`: Capturer l'écran actuel.
- `get_mouse_position()`: Obtenir les coordonnées actuelles.

## Schéma d’appel
### Requête
```json
{
  "tool": "type_text",
  "params": {
    "text": "Hello World"
  }
}
```

### Réponse
```json
{
  "status": "success",
  "data": {
    "action": "typed",
    "length": 11
  }
}
```

## Dépendances requises
- `pyautogui`
- `Pillow` (PIL)
- `keyboard` (optionnel)

## Interaction avec l’orchestrateur
- Permet à l'agent d'agir physiquement sur l'interface utilisateur.
- **Vigilance**: Mécanisme de "Fail-safe" (arrêt d'urgence) indispensable si l'agent perd le contrôle de la souris/clavier.
