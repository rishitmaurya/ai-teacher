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
import base64
import re
import time

# Import text analyzer for auto-prompt generation
from text_analyzer import analyze_text, generate_prompt, get_audio_adjustments

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


def split_text_into_chunks(text: str, prompt: str = "", max_api_limit: int = 4000) -> list:
    """
    Split text into chunks respecting Google API's 4000 byte limit for (text + prompt).
    Uses smaller chunks (1200 bytes) to improve API performance and reduce timeouts.
    
    The Google API requires: len(text) + len(prompt) <= 4000 bytes
    Smaller chunks = faster API responses and fewer timeouts.
    
    Args:
        text: Text to split
        prompt: The prompt that will be sent with each chunk
        max_api_limit: Google API limit (4000 bytes for input.text + input.prompt)
    
    Returns:
        List of text chunks
    """
    # Use smaller chunks (1200 bytes) for better API performance and timeout avoidance
    # Reserve 300 bytes for prompt, use 1200 bytes for text per chunk
    max_text_bytes = 1200
    
    # Convert max bytes to approximate characters (most UTF-8 chars are 1-2 bytes)
    max_chunk_chars = max_text_bytes // 2
    
    logger.info(f"Text splitting config: chunk_size={max_text_bytes} bytes, estimated chars={max_chunk_chars}")
    
    if len(text) <= max_chunk_chars:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Try splitting by sentences first (period + space)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    for sentence in sentences:
        sentence_bytes = len(sentence.encode('utf-8'))
        chunk_bytes = len(current_chunk.encode('utf-8'))
        
        # Check if adding this sentence would exceed the limit
        if chunk_bytes + sentence_bytes + 50 <= max_text_bytes:  # 50 byte buffer for spaces
            current_chunk += (" " if current_chunk else "") + sentence
        else:
            # Current chunk is full, save it
            if current_chunk:
                chunks.append(current_chunk.strip())
                logger.info(f"Chunk created: {len(current_chunk.encode('utf-8'))} bytes")
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
        logger.info(f"Final chunk created: {len(current_chunk.encode('utf-8'))} bytes")
    
    logger.info(f"Split text into {len(chunks)} chunks (max API bytes: {max_api_limit})")
    return chunks


def synthesize_chunk(access_token: str, chunk_text: str, chunk_prompt: str, request: 'TextToSpeechRequest', max_retries: int = 3) -> str:
    """
    Synthesize a single chunk of text and return base64 audio content.
    Includes retry logic with exponential backoff for timeout resilience.
    
    Args:
        access_token: Google OAuth2 access token
        chunk_text: Text chunk to synthesize
        chunk_prompt: Prompt for this specific chunk
        request: Original request object
        max_retries: Maximum number of retry attempts
    
    Returns:
        Base64 encoded audio content
    """
    api_request_body = {
        "input": {
            "text": chunk_text,
            "prompt": chunk_prompt
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
    
    chunk_text_bytes = len(chunk_text.encode('utf-8'))
    chunk_prompt_bytes = len(chunk_prompt.encode('utf-8'))
    logger.info(f"API Request - Text: {chunk_text_bytes} bytes, Prompt: {chunk_prompt_bytes} bytes, Total: {chunk_text_bytes + chunk_prompt_bytes} bytes")
    
    # Retry logic with exponential backoff
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries} - Sending to Google TTS API (timeout: 120s)")
            response = requests.post(
                url,
                json=api_request_body,
                headers=headers,
                timeout=120  # Increased from 30 to 120 seconds
            )

            if response.status_code != 200:
                error_details = response.json() if response.headers.get('content-type') == 'application/json' else response.text
                logger.error(f"Google API error (status {response.status_code}): {error_details}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Google API error: {error_details}"
                )

            result = response.json()
            
            if "audioContent" not in result:
                logger.error(f"No audioContent in API response. Response keys: {result.keys()}")
                raise ValueError("No audio content received from API")
            
            logger.info(f"✓ Synthesis succeeded on attempt {attempt + 1}. Audio size: {len(result['audioContent'])} bytes")
            return result["audioContent"]
            
        except HTTPException:
            raise  # Don't retry HTTP errors
        except requests.exceptions.Timeout as e:
            logger.warning(f"⏱ Timeout on attempt {attempt + 1}/{max_retries}: {str(e)}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                logger.info(f"⏳ Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error(f"✗ Failed after {max_retries} attempts - timeout")
                raise ValueError(f"Synthesis timeout after {max_retries} attempts. Try shorter text or simpler prompts.")
        except Exception as e:
            logger.warning(f"⚠ Error on attempt {attempt + 1}/{max_retries}: {type(e).__name__}: {str(e)}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"⏳ Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error(f"✗ Failed after {max_retries} attempts")
                raise


def combine_audio_chunks(audio_chunks: list, encoding: str = "LINEAR16") -> str:
    """
    Combine multiple base64 audio chunks into a single audio file.
    For LINEAR16 and similar PCM formats, concatenates the raw bytes.
    
    Args:
        audio_chunks: List of base64 encoded audio chunks
        encoding: Audio encoding type
    
    Returns:
        Base64 encoded combined audio
    """
    try:
        if not audio_chunks:
            raise ValueError("No audio chunks to combine")
        
        if len(audio_chunks) == 1:
            return audio_chunks[0]
        
        # For PCM formats (LINEAR16, ALAW, MULAW), we can concatenate the raw audio
        if encoding in ["LINEAR16", "ALAW", "MULAW"]:
            combined_bytes = b""
            
            for i, chunk in enumerate(audio_chunks):
                try:
                    # Decode base64 to bytes
                    audio_bytes = base64.b64decode(chunk)
                    logger.info(f"Chunk {i+1}: Decoded {len(audio_bytes)} bytes from base64")
                    
                    # For the first chunk, include the WAV header
                    if i == 0:
                        combined_bytes += audio_bytes
                        logger.info(f"Chunk {i+1}: Added full audio (including WAV header)")
                    else:
                        # For WAV files, skip the RIFF header (typically 44 bytes)
                        # But be safe and check for the RIFF signature first
                        if audio_bytes.startswith(b'RIFF') and len(audio_bytes) > 44:
                            # This is a WAV file, skip header
                            combined_bytes += audio_bytes[44:]
                            logger.info(f"Chunk {i+1}: Appended {len(audio_bytes) - 44} bytes (skipped WAV header)")
                        else:
                            # Not a standard WAV or too short, append as-is
                            combined_bytes += audio_bytes
                            logger.info(f"Chunk {i+1}: Appended {len(audio_bytes)} bytes (no header detected)")
                except Exception as e:
                    logger.error(f"Error processing chunk {i+1}: {str(e)}")
                    raise ValueError(f"Failed to process audio chunk {i+1}: {str(e)}")
            
            # Encode back to base64
            result = base64.b64encode(combined_bytes).decode('utf-8')
            logger.info(f"Successfully combined {len(audio_chunks)} chunks. Total size: {len(combined_bytes)} bytes")
            return result
        
        # For MP3, return first chunk (MP3 doesn't concatenate well without special handling)
        if encoding == "MP3":
            logger.warning(f"MP3 concatenation not supported. Using first chunk only.")
            return audio_chunks[0]
        
        # Default: return first chunk for unknown formats
        logger.warning(f"Unsupported encoding '{encoding}'. Using first chunk only.")
        return audio_chunks[0]
        
    except Exception as e:
        logger.error(f"Error in combine_audio_chunks: {str(e)}")
        raise ValueError(f"Failed to combine audio chunks: {str(e)}")



# Request/Response models
class TextToSpeechRequest(BaseModel):
    text: str
    prompt: Optional[str] = None  # None = auto-generate per chunk
    auto_prompt: Optional[bool] = True  # Enable auto-prompt generation
    voice_name: Optional[str] = "Achernar"
    language_code: Optional[str] = "en-US"
    model_name: Optional[str] = "gemini-2.5-pro-tts"
    audio_encoding: Optional[str] = "LINEAR16"
    pitch: Optional[float] = None  # None = auto-adjust based on analysis
    speaking_rate: Optional[float] = None  # None = auto-adjust based on analysis


class TextToSpeechResponse(BaseModel):
    success: bool
    message: str
    generated_prompts: Optional[list] = None  # List of prompts used for each chunk
    audio_content: Optional[str] = None  # Base64 encoded
    audio_duration: Optional[float] = None


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "AI Teacher TTS API is running",
        "endpoints": {
            "synthesize": "/synthesize",
            "analyze": "/analyze",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Text-to-Speech"}


@app.post("/analyze")
async def analyze_text_endpoint(request: TextToSpeechRequest):
    """
    Analyze text and generate optimal prompt
    Useful for previewing the auto-generated prompt before synthesis
    """
    try:
        if not request.text.strip():
            raise ValueError("Text cannot be empty")
        
        logger.info(f"Analyzing text of {len(request.text)} characters")
        
        # Analyze the text
        analysis = analyze_text(request.text)
        generated_prompt = generate_prompt(analysis)
        adjustments = get_audio_adjustments(analysis)
        
        logger.info(f"Analysis complete - Generated prompt will be used for synthesis")
        
        return {
            "success": True,
            "analysis": analysis,
            "generated_prompt": generated_prompt,
            "audio_adjustments": adjustments
        }
    
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing text: {str(e)}")


@app.post("/synthesize", response_model=TextToSpeechResponse)
async def synthesize_speech(request: TextToSpeechRequest):
    """
    Synthesize speech from text using Google's Generative AI TTS API
    Automatically handles long text by splitting into chunks and combining audio.
    Respects Google's 4000 byte limit for (input.text + input.prompt).
    
    Args:
        request: TextToSpeechRequest containing:
            - text: The text to convert to speech (no length limit)
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
        
        logger.info(f"Synthesizing text of length {len(request.text)} characters")
        prompt_bytes = len(request.prompt.encode('utf-8')) if request.prompt else 0
        logger.info(f"Prompt length: {prompt_bytes} bytes (auto_prompt={request.auto_prompt})")
        logger.info(f"Voice: {request.voice_name}, Encoding: {request.audio_encoding}")

        # Get access token
        try:
            access_token = get_access_token()
            logger.info("Successfully obtained access token")
        except Exception as e:
            logger.error(f"Failed to get access token: {str(e)}")
            raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

        # Split text into chunks respecting Google API's 4000 byte limit
        # Use empty prompt for chunking if auto_prompt is enabled (we'll generate per chunk)
        chunking_prompt = "" if request.auto_prompt else (request.prompt or "")
        text_chunks = split_text_into_chunks(request.text, chunking_prompt, max_api_limit=4000)
        logger.info(f"Split text into {len(text_chunks)} chunk(s)")

        # Generate prompts for each chunk or use provided prompt
        generated_prompts = []
        if request.auto_prompt and request.prompt is None:
            # Auto-generate a unique prompt for each chunk based on its content
            logger.info("Auto-prompt enabled: Generating unique prompt for each chunk")
            for i, chunk in enumerate(text_chunks, 1):
                try:
                    chunk_analysis = analyze_text(chunk)
                    chunk_prompt = generate_prompt(chunk_analysis)
                    generated_prompts.append(chunk_prompt)
                    logger.info(f"Chunk {i}: Generated prompt - {chunk_prompt[:80]}...")
                except Exception as e:
                    logger.warning(f"Error analyzing chunk {i}, using fallback: {str(e)}")
                    generated_prompts.append("Read naturally and clearly")
        else:
            # Use provided prompt for all chunks, or default
            default_prompt = request.prompt or "Read aloud naturally"
            for i in range(len(text_chunks)):
                generated_prompts.append(default_prompt)
        
        # Also auto-adjust audio parameters if not provided
        if request.pitch is None or request.speaking_rate is None:
            logger.info("Auto-adjusting audio parameters based on text analysis")
            full_text_analysis = analyze_text(request.text)
            adjustments = get_audio_adjustments(full_text_analysis)
            
            if request.pitch is None:
                request.pitch = adjustments["pitch"]
            if request.speaking_rate is None:
                request.speaking_rate = adjustments["speaking_rate"]
            
            logger.info(f"Auto-adjusted: pitch={request.pitch}, speaking_rate={request.speaking_rate}")

        # Synthesize each chunk with its unique prompt
        audio_chunks = []
        for i, chunk in enumerate(text_chunks, 1):
            try:
                chunk_bytes = len(chunk.encode('utf-8'))
                logger.info(f"\n{'='*60}")
                logger.info(f"CHUNK {i}/{len(text_chunks)} - {chunk_bytes} bytes")
                logger.info(f"{'='*60}")
                
                # Use the generated prompt for this chunk
                chunk_prompt = generated_prompts[i - 1]
                
                # Validate that text + prompt fits within API limit
                total_bytes = chunk_bytes + len(chunk_prompt.encode('utf-8'))
                if total_bytes > 4000:
                    logger.warning(f"Chunk {i} exceeds 4000 bytes ({total_bytes}). Reducing prompt.")
                    # Use shorter version if available
                    chunk_prompt = "Continue reading naturally"
                
                logger.info(f"Text: {chunk_bytes} bytes | Prompt: {len(chunk_prompt.encode('utf-8'))} bytes | Total: {total_bytes} bytes")
                logger.info(f"Using prompt: {chunk_prompt[:100]}...")
                
                audio_content = synthesize_chunk(access_token, chunk, chunk_prompt, request, max_retries=3)
                audio_chunks.append(audio_content)
                logger.info(f"✓ Chunk {i}/{len(text_chunks)} completed successfully\n")
            except HTTPException as e:
                logger.error(f"✗ HTTP error on chunk {i}: {str(e.detail)}")
                raise
            except ValueError as e:
                logger.error(f"✗ Validation error on chunk {i}: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error on chunk {i}: {str(e)}")
            except Exception as e:
                logger.error(f"✗ Unexpected error on chunk {i}: {str(e)}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error synthesizing chunk {i}/{len(text_chunks)}: {str(e)}"
                )

        # Combine audio chunks
        try:
            logger.info(f"Combining {len(audio_chunks)} audio chunk(s)...")
            combined_audio = combine_audio_chunks(audio_chunks, request.audio_encoding)
            logger.info(f"Successfully combined all {len(audio_chunks)} chunk(s)")
        except ValueError as e:
            logger.error(f"Error combining chunks: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error combining chunks: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error combining audio: {str(e)}")
        
        return TextToSpeechResponse(
            success=True,
            message=f"Speech synthesized successfully ({len(text_chunks)} chunk(s))",
            audio_content=combined_audio,
            audio_duration=None,
            generated_prompts=generated_prompts if request.auto_prompt else None
        )


    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in synthesize_speech: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error synthesizing speech: {str(e)}")


@app.post("/synthesize/stream")
async def synthesize_speech_stream(request: TextToSpeechRequest):
    """
    Stream audio response directly as audio file
    Handles long text automatically by synthesizing chunks and combining them.
    Respects Google's 4000 byte limit for (input.text + input.prompt).
    Useful for immediate playback without base64 encoding
    """
    try:
        if not request.text.strip():
            raise ValueError("Text cannot be empty")

        access_token = get_access_token()

        # Split text into chunks respecting Google API's 4000 byte limit
        chunking_prompt = "" if request.auto_prompt else (request.prompt or "")
        text_chunks = split_text_into_chunks(request.text, chunking_prompt, max_api_limit=4000)
        logger.info(f"Split text into {len(text_chunks)} chunk(s) for streaming")

        # Generate prompts for each chunk (same logic as synthesize endpoint)
        generated_prompts = []
        if request.auto_prompt and request.prompt is None:
            logger.info("Auto-prompt enabled for stream: Generating unique prompt for each chunk")
            for i, chunk in enumerate(text_chunks, 1):
                try:
                    chunk_analysis = analyze_text(chunk)
                    chunk_prompt = generate_prompt(chunk_analysis)
                    generated_prompts.append(chunk_prompt)
                except Exception as e:
                    logger.warning(f"Error analyzing chunk {i}, using fallback: {str(e)}")
                    generated_prompts.append("Read naturally and clearly")
        else:
            default_prompt = request.prompt or "Read aloud naturally"
            for i in range(len(text_chunks)):
                generated_prompts.append(default_prompt)
        
        # Auto-adjust audio parameters if needed
        if request.pitch is None or request.speaking_rate is None:
            full_text_analysis = analyze_text(request.text)
            adjustments = get_audio_adjustments(full_text_analysis)
            
            if request.pitch is None:
                request.pitch = adjustments["pitch"]
            if request.speaking_rate is None:
                request.speaking_rate = adjustments["speaking_rate"]

        # Synthesize each chunk
        audio_chunks = []
        for i, chunk in enumerate(text_chunks, 1):
            try:
                chunk_bytes = len(chunk.encode('utf-8'))
                logger.info(f"Stream chunk {i}/{len(text_chunks)}: {chunk_bytes} bytes")
                
                # Use the generated prompt for this chunk
                chunk_prompt = generated_prompts[i - 1]
                
                # Validate that text + prompt fits within API limit
                total_bytes = chunk_bytes + len(chunk_prompt.encode('utf-8'))
                if total_bytes > 4000:
                    logger.warning(f"Stream chunk {i} exceeds 4000 bytes ({total_bytes}). Reducing prompt.")
                    chunk_prompt = "Continue reading naturally"
                
                audio_content = synthesize_chunk(access_token, chunk, chunk_prompt, request, max_retries=3)
                audio_chunks.append(audio_content)
            except Exception as e:
                logger.error(f"Error synthesizing stream chunk {i}: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error on chunk {i}: {str(e)}")

        # Combine audio chunks
        combined_audio_b64 = combine_audio_chunks(audio_chunks, request.audio_encoding)
        
        # Decode back to bytes for streaming
        audio_bytes = base64.b64decode(combined_audio_b64)

        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/wav" if request.audio_encoding == "LINEAR16" else "audio/mpeg",
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
