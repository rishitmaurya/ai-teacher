"""
FastAPI backend for Google Text-to-Speech with Generative AI
Handles text-to-speech synthesis with style prompts and emotion detection
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import json
import requests
import os
from typing import Optional
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Teacher Text-to-Speech API",
    description="Convert text to speech using Google's Generative AI Text-to-Speech API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load service account credentials
SERVICE_ACCOUNT_FILE = "config.json"
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

def get_access_token():
    """
    Get OAuth2 access token from service account credentials
    """
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        request = Request()
        credentials.refresh(request)
        return credentials.token
    except Exception as e:
        logger.error(f"Error getting access token: {str(e)}")
        raise


# Request/Response models
class TextToSpeechRequest(BaseModel):
    text: str
    prompt: Optional[str] = "Read aloud like an experienced teacher explaining to students"
    voice_name: Optional[str] = "Achernar"
    language_code: Optional[str] = "en-US"
    model_name: Optional[str] = "gemini-2.5-pro-tts"
    audio_encoding: Optional[str] = "LINEAR16"
    pitch: Optional[float] = 0.0
    speaking_rate: Optional[float] = 1.0


class TextToSpeechResponse(BaseModel):
    success: bool
    message: str
    audio_content: Optional[str] = None  # Base64 encoded
    audio_duration: Optional[float] = None


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "AI Teacher TTS API is running",
        "endpoints": {
            "synthesize": "/synthesize",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Text-to-Speech"}


@app.post("/synthesize", response_model=TextToSpeechResponse)
async def synthesize_speech(request: TextToSpeechRequest):
    """
    Synthesize speech from text using Google's Generative AI TTS API
    
    Args:
        request: TextToSpeechRequest containing:
            - text: The text to convert to speech
            - prompt: Style/emotion prompt (e.g., "warm, welcoming tone")
            - voice_name: Voice to use (Achernar, Altair, Vega)
            - language_code: Language code (en-US, en-GB, etc.)
            - model_name: Model to use
            - audio_encoding: Audio format (LINEAR16, MP3, etc.)
            - pitch: Voice pitch adjustment (-20.0 to 20.0)
            - speaking_rate: Speaking rate (0.25 to 4.0)
    
    Returns:
        TextToSpeechResponse with base64 encoded audio content
    """
    try:
        # Validate inputs
        if not request.text.strip():
            raise ValueError("Text cannot be empty")
        
        if len(request.text) > 10000:
            raise ValueError("Text exceeds maximum length of 10000 characters")

        # Get access token
        access_token = get_access_token()

        # Prepare the request body for Google API
        api_request_body = {
            "input": {
                "text": request.text,
                "prompt": request.prompt
            },
            "voice": {
                "languageCode": request.language_code,
                "name": request.voice_name,
                "modelName": request.model_name
            },
            "audioConfig": {
                "audioEncoding": request.audio_encoding,
                "pitch": request.pitch,
                "speakingRate": request.speaking_rate
            }
        }

        # Make API request to Google
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        url = "https://texttospeech.googleapis.com/v1beta1/text:synthesize"

        logger.info(f"Making request to Google TTS API for text: {request.text[:50]}...")
        response = requests.post(
            url,
            json=api_request_body,
            headers=headers,
            timeout=30
        )

        # Handle API response
        if response.status_code != 200:
            error_details = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            logger.error(f"Google API error: {error_details}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Google API error: {error_details}"
            )

        result = response.json()
        
        if "audioContent" not in result:
            raise ValueError("No audio content received from API")

        logger.info("Successfully synthesized speech")
        
        return TextToSpeechResponse(
            success=True,
            message="Speech synthesized successfully",
            audio_content=result["audioContent"],
            audio_duration=result.get("audioDuration", None)
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error synthesizing speech: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error synthesizing speech: {str(e)}")


@app.post("/synthesize/stream")
async def synthesize_speech_stream(request: TextToSpeechRequest):
    """
    Stream audio response directly as audio file
    Useful for immediate playback without base64 encoding
    """
    try:
        if not request.text.strip():
            raise ValueError("Text cannot be empty")

        access_token = get_access_token()

        api_request_body = {
            "input": {
                "text": request.text,
                "prompt": request.prompt
            },
            "voice": {
                "languageCode": request.language_code,
                "name": request.voice_name,
                "modelName": request.model_name
            },
            "audioConfig": {
                "audioEncoding": request.audio_encoding,
                "pitch": request.pitch,
                "speakingRate": request.speaking_rate
            }
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        url = "https://texttospeech.googleapis.com/v1beta1/text:synthesize"
        response = requests.post(url, json=api_request_body, headers=headers, timeout=30)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Google API error")

        result = response.json()
        audio_bytes = bytes(result["audioContent"].encode('latin1'))

        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=speech.wav"}
        )

    except Exception as e:
        logger.error(f"Error in stream endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
