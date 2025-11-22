from fastapi import FastAPI, UploadFile, File
import requests
import base64
import os

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")


# ---------------------------
#  SPEECH TO TEXT (Whisper API)
# ---------------------------
@app.post("/audio/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    audio_bytes = await file.read()

    audio_b64 = base64.b64encode(audio_bytes).decode()

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini-tts",
        "input_audio": audio_b64
    }

    response = requests.post(
        "https://api.openai.com/v1/audio/transcriptions",
        json=payload,
        headers=headers
    )

    return response.json()



# ---------------------------
# TEXT TO SPEECH (OpenAI TTS)
# ---------------------------
@app.post("/audio/speak")
async def speak(text: str):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini-tts",
        "voice": "alloy",
        "input": text
    }

    r = requests.post(
        "https://api.openai.com/v1/audio/speech",
        json=payload,
        headers=headers,
    )

    return {"audio_b64": base64.b64encode(r.content).decode()}

