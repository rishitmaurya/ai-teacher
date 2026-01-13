# FastAPI Text-to-Speech Backend Setup Guide

## Overview
This guide helps you set up a FastAPI backend that connects your frontend to Google's Generative AI Text-to-Speech API.

## Project Structure
```
ai-teach-old/
├── main.py                  # FastAPI backend application
├── client.js               # JavaScript client for frontend
├── requirements.txt        # Python dependencies
├── config.json            # Google service account credentials (already present)
├── index.html             # Frontend HTML
├── styles.css             # Frontend CSS
└── venv39/                # Python virtual environment
```

## Prerequisites
- Python 3.8+ (you have venv39)
- Google service account credentials (config.json - already present ✅)
- Google Cloud Project with Text-to-Speech API enabled

## Installation & Setup

### Step 1: Activate Virtual Environment
```powershell
# Windows PowerShell
.\venv39\Scripts\Activate.ps1

# If you get execution policy error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Verify config.json
Ensure your `config.json` file is in the root directory with valid Google service account credentials.

### Step 4: Run the FastAPI Backend
```powershell
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## API Endpoints

### 1. Health Check
```
GET http://localhost:8000/health
```
Response:
```json
{"status": "healthy", "service": "Text-to-Speech"}
```

### 2. Synthesize Speech (Returns Base64)
```
POST http://localhost:8000/synthesize
Content-Type: application/json

{
  "text": "Hello, this is a test",
  "prompt": "Read aloud in a warm, welcoming tone",
  "voice_name": "Achernar",
  "language_code": "en-US",
  "model_name": "gemini-2.5-pro-tts",
  "audio_encoding": "LINEAR16",
  "pitch": 0.0,
  "speaking_rate": 1.0
}
```

Response:
```json
{
  "success": true,
  "message": "Speech synthesized successfully",
  "audio_content": "SUQzBAAAAAAAI1NDVQAA...",
  "audio_duration": 2.5
}
```

### 3. Stream Audio (Direct Download)
```
POST http://localhost:8000/synthesize/stream
```
Same request body as above, but returns audio file directly.

## Frontend Integration

### Update your index.html
Add the client library:
```html
<script src="client.js"></script>
```

### Example Usage in JavaScript
```javascript
// Basic usage
async function speakText() {
  const result = await synthesizeText(
    "Hello world",
    "Read aloud naturally",
    {
      voice_name: "Achernar",
      model_name: "gemini-2.5-pro-tts"
    }
  );
  
  if (result.success) {
    playAudio(result.audio_content);
  }
}

// Or use streaming
async function streamText() {
  await streamAudio(
    "Hello world",
    "Read aloud naturally",
    { voice_name: "Achernar" }
  );
}
```

## Available Options

### Voice Names
- `Achernar`
- `Altair`
- `Vega`

### Models
- `gemini-2.5-pro-tts`
- `gemini-1`

### Language Codes
- `en-US` - English (US)
- `en-GB` - English (UK)
- `es-ES` - Spanish
- And many more...

### Audio Encodings
- `LINEAR16` - PCM WAV format
- `MP3` - MP3 format
- `ALAW` - A-law format
- `MULAW` - Mu-law format
- `OGG_OPUS` - Ogg Opus format

### Parameter Ranges
- `pitch`: -20.0 to 20.0 (semitones)
- `speaking_rate`: 0.25 to 4.0 (1.0 = normal)

## Common Prompt Examples

### For Stories
```
"Read aloud in a warm, storyteller's voice with emotion and expression"
```

### For Scientific Content
```
"Read aloud like an experienced scholar explaining complex topics clearly"
```

### For Educational Content
```
"Read aloud in a clear, engaging teacher's voice"
```

### For Casual Content
```
"Read aloud in a friendly, conversational tone"
```

### For News/Announcements
```
"Read aloud in a professional, authoritative news presenter's voice"
```

## Troubleshooting

### Issue: CORS Error
**Solution**: The FastAPI app already has CORS enabled for all origins. Ensure the API is running.

### Issue: 401 Unauthorized
**Solution**: Check that your `config.json` has valid Google service account credentials.

### Issue: 403 Forbidden
**Solution**: 
1. Go to Google Cloud Console
2. Enable the "Cloud Text-to-Speech API" for your project
3. Ensure the service account has necessary permissions

### Issue: Empty Response
**Solution**: Check that the text is not empty and doesn't exceed 5000 characters.

### Issue: Cannot import google modules
**Solution**: Ensure you've activated the virtual environment and installed requirements:
```powershell
pip install -r requirements.txt
```

## Next Steps

1. **Frontend Integration**: Update your HTML to use `client.js`
2. **Add Pause/Resume**: Use HTML5 audio controls on the audio element
3. **Add Hand Raise Feature**: Implement recording using Web Audio API
4. **Error Handling**: Add proper error messages for users
5. **Caching**: Consider caching repeated requests

## File Locations
- Backend: `main.py` (FastAPI)
- Frontend Client: `client.js` (JavaScript)
- Credentials: `config.json` (Google service account)
- Dependencies: `requirements.txt`

## Useful Commands

### Run Backend
```powershell
python main.py
```

### Check API Documentation (Swagger UI)
```
http://localhost:8000/docs
```

### Check ReDoc Documentation
```
http://localhost:8000/redoc
```

### Run Frontend with Live Server
```powershell
python -m http.server 8000
# Then open http://localhost:8000
```

## Security Notes
- Never commit `config.json` to public repositories
- Use environment variables for production deployments
- Validate all user inputs on the backend
- Implement rate limiting for API endpoints
- Use HTTPS in production

## Support
For issues with Google Cloud APIs, visit: https://cloud.google.com/support
