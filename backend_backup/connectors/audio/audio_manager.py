import whisper
import librosa
import numpy as np
from TTS.api import TTS
import tempfile
import os
import base64


class AudioManager:
    def __init__(self):
        # Load Whisper model
        self.asr = whisper.load_model("small")

        # Load XTTS v2 TTS model
        self.tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

    # -----------------------
    #  TRANSCRIPTION (Whisper)
    # -----------------------
    def transcribe(self, audio_bytes: bytes) -> dict:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            temp_path = tmp.name

        result = self.asr.transcribe(temp_path)

        try:
            os.remove(temp_path)
        except:
            pass

        return {"text": result["text"], "confidence": 1.0}

    # -----------------------
    #  SYNTHESE VOCALE (XTTS)
    # -----------------------
    def text_to_speech(self, text: str) -> bytes:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            temp_out = tmp.name

        # Generate speech to temp file
        self.tts.tts_to_file(text=text, file_path=temp_out, speaker="female", language="fr")

        # Read as bytes
        audio_bytes = open(temp_out, "rb").read()

        try:
            os.remove(temp_out)
        except:
            pass

        return audio_bytes

    # -----------------------
    #  ANALYSE AUDIO
    # -----------------------
    def analyze(self, audio_bytes: bytes) -> dict:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            temp_path = tmp.name

        y, sr = librosa.load(temp_path)
        duration = librosa.get_duration(y=y, sr=sr)

        try:
            os.remove(temp_path)
        except:
            pass

        return {
            "duration_seconds": duration,
            "amplitude_mean": float(np.mean(y)),
            "amplitude_std": float(np.std(y))
        }
