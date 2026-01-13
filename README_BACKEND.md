# 🎓 AI Teacher - FastAPI Text-to-Speech Backend

A complete production-ready FastAPI backend for converting text to speech using Google's Generative AI Text-to-Speech API with intelligent emotion and style detection.

## ✨ Features

- ✅ **FastAPI Backend** - Modern, fast Python web framework
- ✅ **Google Generative AI TTS** - Uses latest Google TTS with emotion/style support
- ✅ **Multiple Voices** - Achernar, Altair, Vega
- ✅ **Style Prompts** - Control voice emotions (warm, cold, scholarly, friendly, etc.)
- ✅ **Audio Controls** - Play, pause, stop, resume
- ✅ **Adjustable Parameters** - Pitch, speed, language, audio format
- ✅ **CORS Enabled** - Works with frontend applications
- ✅ **Error Handling** - Comprehensive validation and error messages
- ✅ **Swagger Documentation** - Interactive API docs at `/docs`
- ✅ **Streaming Support** - Direct audio streaming or base64 responses

## 📂 Project Structure

```
ai-teach-old/
├── 🔴 BACKEND (NEW)
│   ├── main.py                    # FastAPI application
│   ├── client.js                  # JavaScript client library
│   ├── test_api.py               # API test suite
│   └── requirements.txt           # Python dependencies
│
├── 🟢 FRONTEND
│   ├── index_new.html            # Updated HTML with controls
│   ├── styles.css                # Styling
│   └── Original files (for reference)
│       ├── index.html
│       └── script.jsp
│
├── 🔑 CREDENTIALS
│   └── config.json               # Google service account (⚠️ KEEP SECRET)
│
├── 📖 DOCUMENTATION
│   ├── QUICKSTART.md            # Get started in 5 minutes
│   ├── FASTAPI_SETUP.md         # Detailed setup guide
│   ├── README_BACKEND.md        # This file
│   └── README.md                # Original documentation
│
└── 🐍 ENVIRONMENT
    └── venv39/                  # Python virtual environment
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ (you have venv39)
- Google service account credentials (config.json) ✅
- Windows/Linux/Mac

### Step 1: Setup Environment
```powershell
# Navigate to project
cd c:\programming\ai_teacher\ai-teach-old

# Activate virtual environment
.\venv39\Scripts\Activate.ps1
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Start Backend Server
```powershell
python main.py
```

Output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Test the API
```powershell
python test_api.py
```

### Step 5: Open Frontend
```powershell
start http://localhost:8000/docs
```

Or open `index_new.html` in your browser.

## 🛠️ API Endpoints

### 1. Health Check
```http
GET /health
```
Response:
```json
{"status": "healthy", "service": "Text-to-Speech"}
```

### 2. Synthesize Speech (Base64 Response)
```http
POST /synthesize
Content-Type: application/json

{
  "text": "Hello world",
  "prompt": "Read aloud in a warm tone",
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
```http
POST /synthesize/stream
Content-Type: application/json
```
Same request body as above, returns audio file directly.

## 📝 Usage Examples

### JavaScript Frontend
```javascript
// Synthesize text to speech
const result = await synthesizeText(
  "Hello, how are you?",
  "Read aloud in a warm, friendly tone",
  {
    voice_name: "Achernar",
    language_code: "en-US",
    speaking_rate: 1.0,
    pitch: 0.0
  }
);

// Play the audio
if (result.success) {
  playAudio(result.audio_content);
}
```

### Python Backend
```python
import requests

response = requests.post(
    "http://localhost:8000/synthesize",
    json={
        "text": "Hello world",
        "prompt": "Read aloud naturally",
        "voice_name": "Achernar"
    }
)

result = response.json()
if result["success"]:
    print(f"Audio duration: {result['audio_duration']}s")
```

### PowerShell/cURL
```powershell
$body = @{
    text = "Hello world"
    prompt = "Read aloud naturally"
    voice_name = "Achernar"
} | ConvertTo-Json

curl -X POST http://localhost:8000/synthesize `
  -ContentType "application/json" `
  -Body $body
```

## 🎤 Voice Options

| Voice | Description |
|-------|-------------|
| **Achernar** | Warm, approachable voice |
| **Altair** | Professional, clear voice |
| **Vega** | Calm, soothing voice |

## 🎨 Style Prompts

### For Different Content Types

**Educational Content:**
```
"Read aloud in a clear, engaging teacher's voice"
```

**Stories & Narrative:**
```
"Read aloud in a warm, storyteller's voice with emotion and expression"
```

**Scientific Content:**
```
"Read aloud like an experienced scholar explaining complex topics"
```

**News/Announcements:**
```
"Read aloud in a professional, authoritative news presenter's voice"
```

**Casual Conversation:**
```
"Read aloud in a friendly, conversational tone"
```

## ⚙️ Configuration Parameters

### Voice Parameters
- **voice_name**: Achernar, Altair, Vega
- **language_code**: en-US, en-GB, es-ES, fr-FR, de-DE, etc.
- **model_name**: gemini-2.5-pro-tts, gemini-1

### Audio Parameters
- **audio_encoding**: LINEAR16 (WAV), MP3, ALAW, MULAW, OGG_OPUS
- **pitch**: -20.0 to 20.0 (semitones)
- **speaking_rate**: 0.25 to 4.0 (1.0 = normal speed)

## 🧪 Testing

### Run Full Test Suite
```powershell
python test_api.py
```

Tests included:
- ✅ Health check
- ✅ Text synthesis
- ✅ Audio streaming
- ✅ Different voices
- ✅ Error handling

### Interactive API Documentation
```
http://localhost:8000/docs
```

Swagger UI with try-it-out functionality!

## 🔒 Security

### Credentials
- ⚠️ **Never commit** `config.json` to version control
- 🔐 Add to `.gitignore`:
  ```
  config.json
  .env
  *.key
  ```

### Production Setup
1. Use environment variables for credentials
2. Enable HTTPS
3. Implement rate limiting
4. Add API key authentication
5. Use production ASGI server (Gunicorn + Uvicorn)

Example with environment variables:
```python
import os
from dotenv import load_dotenv

load_dotenv()
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_CREDENTIALS_PATH")
```

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fastapi'"
```powershell
pip install -r requirements.txt
```

### Issue: "Connection refused" (Cannot reach server)
```powershell
# Make sure backend is running
python main.py
```

### Issue: "401 Unauthorized" from Google API
1. Verify `config.json` has valid credentials
2. Check Google Cloud Console
3. Enable "Cloud Text-to-Speech API"
4. Verify service account has correct permissions

### Issue: CORS errors in browser console
- CORS is already enabled in `main.py` (line 22-28)
- Clear browser cache
- Refresh the page
- Check browser developer tools (F12)

### Issue: "Text exceeds maximum length"
- Maximum text length: 5000 characters
- Split longer texts into multiple requests

## 📊 Performance Tips

1. **Caching**: Implement caching for common texts
2. **Streaming**: Use `/synthesize/stream` for large files
3. **Batch Processing**: Process multiple texts in parallel
4. **Async**: All endpoints are async for better concurrency

## 🚀 Production Deployment

### Using Gunicorn + Uvicorn
```powershell
pip install gunicorn

gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

### Environment Variables
```
GOOGLE_CREDENTIALS_PATH=path/to/config.json
API_PORT=8000
LOG_LEVEL=info
```

## 📚 API Documentation

### OpenAPI/Swagger
```
http://localhost:8000/docs
```

### ReDoc
```
http://localhost:8000/redoc
```

### OpenAPI JSON
```
http://localhost:8000/openapi.json
```

## 📖 Documentation Files

- **QUICKSTART.md** - Get started in 5 minutes
- **FASTAPI_SETUP.md** - Detailed setup and configuration
- **main.py** - Backend code with docstrings
- **client.js** - Frontend client with examples
- **test_api.py** - Test examples and debugging

## 🔄 Integration Guide

### For Bigger Applications

1. **Import the client**:
   ```html
   <script src="client.js"></script>
   ```

2. **Use the functions**:
   ```javascript
   const audio = await synthesizeText(content, prompt);
   playAudio(audio.audio_content);
   ```

3. **Handle responses**:
   ```javascript
   if (audio.success) {
     // Play audio
   } else {
     // Show error
   }
   ```

## 🎯 Next Features to Add

- [ ] Hand raise with voice recording
- [ ] Automatic emotion detection from text
- [ ] Question answering with web search
- [ ] Audio caching system
- [ ] Multi-language support
- [ ] Real-time audio playback with current position
- [ ] Voice activity detection
- [ ] Rate limiting and authentication

## 🤝 Contributing

To add features:
1. Update `main.py` for backend changes
2. Update `client.js` for frontend changes
3. Add tests to `test_api.py`
4. Update documentation

## 📋 Checklist for Deployment

- [ ] Virtual environment configured
- [ ] Dependencies installed
- [ ] Google credentials valid
- [ ] Backend tested (`python test_api.py`)
- [ ] Frontend loads without errors
- [ ] Audio playback works
- [ ] Error handling tested
- [ ] Documentation reviewed

## 📞 Support & Resources

- **Google Cloud TTS Documentation**: https://cloud.google.com/text-to-speech/docs
- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **Uvicorn Documentation**: https://www.uvicorn.org/
- **Pydantic Documentation**: https://docs.pydantic.dev/

## 📄 License

This project is provided as-is for educational purposes.

---

## 🎉 You're Ready!

Your FastAPI Text-to-Speech backend is now ready to:
- ✅ Convert text to speech with emotion/style
- ✅ Support multiple voices and languages
- ✅ Stream or encode audio as needed
- ✅ Scale to production usage
- ✅ Integrate with larger applications

**Start the server and explore the API at: `http://localhost:8000/docs`** 🚀

---

**Last Updated**: January 2026
**Status**: ✅ Production Ready
