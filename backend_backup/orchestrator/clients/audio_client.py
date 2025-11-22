"""
Audio MCP Client
Handles communication with the Audio MCP server
"""
import httpx
from typing import Dict, Any, Optional


class AudioClient:
    """Client for MCP Audio Service"""
    
    def __init__(self, base_url: str = "http://localhost:8010"):
        self.base_url = base_url.rstrip('/')
        self.timeout = 30.0
    
    async def transcribe(self, audio_bytes: bytes) -> Dict[str, Any]:
        """
        Transcrit un fichier audio
        
        Args:
            audio_bytes: Données audio brutes
            
        Returns:
            Transcription
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
            response = await client.post(
                f"{self.base_url}/audio/transcribe",
                files=files
            )
            response.raise_for_status()
            return response.json()
    
    async def text_to_speech(self, text: str) -> Dict[str, Any]:
        """
        Convertit du texte en audio
        
        Args:
            text: Texte à convertir
            
        Returns:
            Audio encodé en base64
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/audio/speech",
                json={"text": text}
            )
            response.raise_for_status()
            return response.json()
    
    async def analyze(self, audio_bytes: bytes) -> Dict[str, Any]:
        """
        Analyse un fichier audio
        
        Args:
            audio_bytes: Données audio brutes
            
        Returns:
            Analyse audio
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
            response = await client.post(
                f"{self.base_url}/audio/analyze",
                files=files
            )
            response.raise_for_status()
            return response.json()
    
    async def get_audio_context(self) -> Dict[str, Any]:
        """
        Récupère le contexte audio actif
        
        Returns:
            Contexte audio (dernières transcriptions, etc.)
        """
        # Pour l'instant, retourne un contexte vide
        # À implémenter selon les besoins
        return {
            "status": "active",
            "recent_transcriptions": [],
            "audio_state": "ready"
        }
