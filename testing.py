import base64
import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

API_KEY = "MY_ID"
TTS_URL = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={API_KEY}"

app = FastAPI(title="Prompt-based TTS API")

# -------- Request schema --------
class TTSRequest(BaseModel):
    text: str
    style: str = "Speak in a warm and friendly tone."
    language: str = "en-US"

# -------- API endpoint --------
@app.post("/speak")
def synthesize_speech(req: TTSRequest):
    payload = {
        "input": {
            "text": req.text
        },
        "voice": {
            "languageCode": "en-US",
            "name": "en-US-Neural2-J"
        },
        "audioConfig": {
            "audioEncoding": "MP3"
        }
    }


    try:
        r = requests.post(TTS_URL, json=payload, timeout=30)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

    data = r.json()

    if "audioContent" not in data:
        raise HTTPException(status_code=500, detail="No audio returned from Google TTS")

    # Decode base64 audio
    audio_bytes = base64.b64decode(data["audioContent"])

    # Save file
    output_file = "output.mp3"
    with open(output_file, "wb") as f:
        f.write(audio_bytes)

    return {
        "message": "Speech generated successfully",
        "file": output_file
    }
