# System MCP API

## Outils exposés
- `get_system_info()`: Obtenir des infos sur l'OS, CPU, RAM, Disque.
- `list_processes()`: Lister les processus en cours.
- `execute_command(command)`: Exécuter une commande shell (avec précautions).
- `get_clipboard()`: Lire le presse-papier.
- `set_clipboard(text)`: Écrire dans le presse-papier.

## Schéma d’appel
### Requête
```json
{
  "tool": "get_system_info",
  "params": {}
}
```

### Réponse
```json
{
  "status": "success",
  "data": {
    "os": "Windows 10",
    "cpu_usage": 15.4,
    "ram_available": "8GB"
  }
}
```

## Dépendances requises
- `psutil`
- `platform`
- `subprocess`
- `pyperclip` (pour le presse-papier)

## Interaction avec l’orchestrateur
- Fournit la conscience de l'environnement d'exécution.
- **Vigilance**: `execute_command` est critique. Doit être sandboxé ou strictement validé pour éviter l'exécution de code malveillant.
