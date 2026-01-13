# Quick Start Guide - FastAPI Text-to-Speech Backend

## 🚀 Quick Start (5 minutes)

### Step 1: Activate Virtual Environment
```powershell
# Navigate to your project directory
cd c:\programming\ai_teacher\ai-teach-old

# Activate Python virtual environment
.\venv39\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Run the Backend Server
```powershell
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Test the API (in a new PowerShell window)
```powershell
python test_api.py
```

### Step 5: Open Frontend
Open your browser and go to:
```
http://localhost:8000/docs
```

Or replace `index.html` with `index_new.html`:
```powershell
# Open in browser
start index_new.html
```

---

## 📁 What's New

### New Files Created:
- **main.py** - FastAPI backend server
- **client.js** - JavaScript client library
- **requirements.txt** - Python dependencies
- **index_new.html** - Updated HTML frontend
- **test_api.py** - API testing script
- **FASTAPI_SETUP.md** - Detailed setup guide
- **QUICKSTART.md** - This file

### How They Work Together:

```
User Browser (index_new.html)
    ↓
    ├─→ client.js (JavaScript client)
    ↓
    └─→ FastAPI Backend (main.py:8000)
    ↓
    └─→ Google TTS API
    ↓
    ← Audio Response
```

---

## 🧪 Testing the API

### Using PowerShell/curl:
```powershell
# Test health
curl http://localhost:8000/health

# Test synthesis
$body = @{
    text = "Hello, this is a test"
    prompt = "Read aloud naturally"
    voice_name = "Achernar"
} | ConvertTo-Json

curl -X POST http://localhost:8000/synthesize `
  -ContentType "application/json" `
  -Body $body
```

### Using the Test Script:
```powershell
python test_api.py
```

### Using Swagger UI (Interactive Docs):
```
http://localhost:8000/docs
```

---

## 🎯 API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check |
| `/health` | GET | Service status |
| `/synthesize` | POST | Convert text to speech (returns base64) |
| `/synthesize/stream` | POST | Convert text to speech (streams audio) |

---

## 💡 Example Usage in JavaScript

```javascript
// Basic usage
const result = await synthesizeText(
  "Hello world",
  "Read aloud in a warm tone",
  {
    voice_name: "Achernar",
    speaking_rate: 1.0
  }
);

if (result.success) {
  playAudio(result.audio_content);
}
```

---

## 🛠️ Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fastapi'"
```powershell
# Solution: Install dependencies
pip install -r requirements.txt
```

### Issue: "Connection refused" when testing
```powershell
# Solution: Make sure backend is running
python main.py
```

### Issue: "401 Unauthorized" from Google API
- Check that `config.json` has valid credentials
- Verify Google Cloud project has Text-to-Speech API enabled
- Check that the service account has the correct permissions

### Issue: CORS errors in browser
- CORS is already enabled in `main.py`
- Clear browser cache and reload
- Check browser console for more details

---

## 📊 Project Structure

```
ai-teach-old/
├── main.py                    # FastAPI application ⭐ NEW
├── client.js                  # JavaScript client ⭐ NEW
├── index_new.html            # Updated frontend ⭐ NEW
├── test_api.py               # Test script ⭐ NEW
├── QUICKSTART.md             # This file ⭐ NEW
├── FASTAPI_SETUP.md          # Detailed setup ⭐ NEW
├── requirements.txt          # Dependencies ⭐ NEW
├── config.json               # Google credentials ✅ EXISTING
├── index.html                # Original frontend
├── script.jsp                # Original scripts
├── styles.css                # Styling
└── venv39/                   # Python environment
```

---

## 🔄 Next Steps

1. **Test the API**: Run `python test_api.py`
2. **Open the Web UI**: Navigate to `index_new.html`
3. **Customize Styles**: Edit `styles.css` as needed
4. **Add Features**: 
   - Hand raise with voice recording (Web Audio API)
   - Automatic emotion detection
   - Question answering with web search
5. **Deploy**: 
   - Use production ASGI server (Gunicorn + Uvicorn)
   - Set up environment variables for credentials
   - Enable HTTPS

---

## 📚 Documentation Files

- **FASTAPI_SETUP.md** - Detailed technical setup
- **main.py** - Backend code with docstrings
- **client.js** - Frontend client with examples
- **test_api.py** - Testing examples

---

## ⚡ Performance Tips

1. **Caching**: Consider caching frequently used synthesizations
2. **Streaming**: Use `/synthesize/stream` for large texts
3. **Batch Processing**: Process multiple texts in parallel
4. **Error Handling**: Implement retry logic for API failures

---

## 🔒 Security Considerations

1. **Never commit** `config.json` to version control
2. **Use environment variables** for credentials in production
3. **Validate all inputs** on the backend
4. **Implement rate limiting** to prevent abuse
5. **Use HTTPS** in production deployments

---

## 📞 Support Resources

- Google Cloud Text-to-Speech: https://cloud.google.com/text-to-speech/docs
- FastAPI Documentation: https://fastapi.tiangolo.com
- Uvicorn: https://www.uvicorn.org/
- Pydantic: https://docs.pydantic.dev/

---

## ✅ Verification Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `config.json` present with valid credentials
- [ ] Backend running (`python main.py`)
- [ ] Tests passing (`python test_api.py`)
- [ ] Frontend accessible (`http://localhost:8000/docs`)
- [ ] Audio playback working

---

You're all set! 🎉 The FastAPI backend is now ready to serve your text-to-speech needs!
