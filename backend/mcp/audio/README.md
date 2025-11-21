# MCP Audio Service

## Endpoints exposés
POST /audio/transcribe
POST /audio/speech
POST /audio/analyze

## Fonctionnalités
- Transcription audio → texte
- Synthèse vocale (TTS)
- Analyse audio basique

## Module interne utilisé
backend/connectors/audio/audio_manager.py

## Format de sortie
{
  "text": "...",
  "confidence": 0.95,
  "metadata": {...}
}