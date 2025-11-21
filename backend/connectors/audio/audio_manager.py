class AudioManager:
    def __init__(self):
        pass

    def transcribe(self, audio_bytes: bytes) -> dict:
        # TODO : intégrer Whisper ou API OpenAI plus tard
        return {
            "text": "Transcription non implémentée",
            "confidence": 0.0
        }

    def text_to_speech(self, text: str) -> bytes:
        # TODO : intégrer TTS local ou API
        return b"FAKE_AUDIO_DATA"

    def analyze(self, audio_bytes: bytes) -> dict:
        return {
            "analysis": "Analyse non implémentée",
            "duration": None
        }