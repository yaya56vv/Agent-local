import base64
import sys
import os
from fastapi import FastAPI, UploadFile, File

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

from backend.connectors.audio.audio_manager import AudioManager

app = FastAPI(title="MCP Audio Service")
audio = AudioManager()

@app.post("/audio/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    content = await file.read()
    return audio.transcribe(content)

@app.post("/audio/speech")
async def audio_speech(payload: dict):
    text = payload.get("text", "")
    audio_bytes = audio.text_to_speech(text)
    return {
        "audio_base64": base64.b64encode(audio_bytes).decode()
    }

@app.post("/audio/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    content = await file.read()
    return audio.analyze(content)