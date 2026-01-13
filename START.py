#!/usr/bin/env python3
"""
START HERE - FastAPI Text-to-Speech Backend
Quick setup and verification script
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_header():
    print("\n" + "="*70)
    print("  🎙️  AI TEACHER - FastAPI TEXT-TO-SPEECH BACKEND")
    print("="*70 + "\n")

def check_requirements():
    """Check if all requirements are met"""
    print("📋 CHECKING REQUIREMENTS...\n")
    
    checks = {
        "Python 3.8+": check_python(),
        "config.json present": check_config(),
        "venv39 exists": check_venv(),
        "requirements.txt present": check_requirements_file(),
        "main.py present": check_main_py(),
        "client.js present": check_client_js(),
    }
    
    all_pass = all(checks.values())
    
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")
    
    return all_pass

def check_python():
    try:
        version = sys.version_info
        return version.major == 3 and version.minor >= 8
    except:
        return False

def check_config():
    return os.path.exists("config.json")

def check_venv():
    return os.path.exists("venv39")

def check_requirements_file():
    return os.path.exists("requirements.txt")

def check_main_py():
    return os.path.exists("main.py")

def check_client_js():
    return os.path.exists("client.js")

def print_quick_start():
    print("\n" + "="*70)
    print("🚀 QUICK START (5 MINUTES)")
    print("="*70)
    print("""
1️⃣  Activate Virtual Environment:
    .\venv39\Scripts\Activate.ps1

2️⃣  Install Dependencies:
    pip install -r requirements.txt

3️⃣  Start Backend Server:
    python main.py

4️⃣  Test API (in new terminal):
    python test_api.py

5️⃣  Open Frontend:
    http://localhost:8000/docs
    or open index_new.html

✅ Done! Your Text-to-Speech API is ready!
    """)

def print_file_guide():
    print("\n" + "="*70)
    print("📁 IMPORTANT FILES")
    print("="*70)
    print("""
BACKEND:
  • main.py              - FastAPI server (▶️ Run this!)
  • client.js            - JavaScript client library
  • test_api.py          - Test suite (✅ Test this!)
  • requirements.txt     - Python dependencies

FRONTEND:
  • index_new.html       - Modern web UI (🌐 Open this!)
  • index.html           - Original UI (reference)

DOCUMENTATION:
  📖 QUICKSTART.md              - Start here! (5 min read)
  📖 README_BACKEND.md          - Complete guide
  📖 FASTAPI_SETUP.md          - Detailed setup
  📖 DEPLOYMENT.md             - Production deployment
  📖 VISUAL_GUIDE.md           - Architecture diagrams
  📖 PROJECT_SUMMARY.md        - Everything created

CREDENTIALS:
  🔑 config.json                - Google service account
                                 (⚠️  Keep secret!)

CONFIGURATION:
  ⚙️  .env.example              - Environment template
    """)

def print_documentation_index():
    print("\n" + "="*70)
    print("📚 DOCUMENTATION INDEX")
    print("="*70)
    print("""
START HERE:
  1. QUICKSTART.md           - Get running in 5 minutes
                             (Essential first read!)

FOR DEVELOPMENT:
  2. README_BACKEND.md       - Comprehensive backend guide
                             (Reference + examples)
  
  3. VISUAL_GUIDE.md         - Architecture & diagrams
                             (Understand the flow)
  
  4. FASTAPI_SETUP.md        - Technical details
                             (Configuration & params)

FOR PRODUCTION:
  5. DEPLOYMENT.md           - Production deployment
                             (Windows/Linux/Docker/Cloud)
  
  6. PROJECT_SUMMARY.md      - Overview of all files
                             (File relationships)

CONFIGURATION:
  7. .env.example            - Environment settings
                             (Copy to .env for prod)
    """)

def print_api_reference():
    print("\n" + "="*70)
    print("🔌 API ENDPOINTS")
    print("="*70)
    print("""
GET  /health
  Purpose: Health check
  Response: {"status": "healthy"}

POST /synthesize
  Purpose: Convert text to speech (returns base64)
  Request Body:
    {
      "text": "Hello world",
      "prompt": "Read aloud naturally",
      "voice_name": "Achernar",
      ...
    }

POST /synthesize/stream
  Purpose: Stream audio directly

GET  /docs
  Purpose: Interactive API documentation (Swagger UI)
  URL: http://localhost:8000/docs
    """)

def print_voice_options():
    print("\n" + "="*70)
    print("🎤 VOICE OPTIONS")
    print("="*70)
    print("""
Voices:
  • Achernar  - Warm, approachable voice
  • Altair    - Professional, clear voice
  • Vega      - Calm, soothing voice

Languages:
  • en-US, en-GB, es-ES, fr-FR, de-DE, and 35+ more

Audio Formats:
  • LINEAR16  - WAV format (best quality)
  • MP3       - MP3 format (best compression)
  • ALAW      - A-law format
  • MULAW     - Mu-law format
  • OGG_OPUS  - Ogg Opus format

Parameters:
  • pitch:        -20 to 20 (semitones)
  • speaking_rate: 0.25 to 4.0 (1.0 = normal)
    """)

def print_troubleshooting():
    print("\n" + "="*70)
    print("🔧 TROUBLESHOOTING")
    print("="*70)
    print("""
Problem: ModuleNotFoundError
Solution: pip install -r requirements.txt

Problem: Connection refused
Solution: Make sure backend is running: python main.py

Problem: 401 Unauthorized from Google
Solution: 
  - Verify config.json has valid credentials
  - Enable Text-to-Speech API in Google Cloud
  - Check service account permissions

Problem: CORS errors
Solution:
  - CORS is enabled in main.py
  - Clear browser cache and reload
  - Check browser console (F12)

Problem: Text exceeds maximum length
Solution: Maximum is 5000 characters per request

More help: See FASTAPI_SETUP.md Troubleshooting section
    """)

def print_next_steps():
    print("\n" + "="*70)
    print("✅ NEXT STEPS")
    print("="*70)
    print("""
1. Read: QUICKSTART.md (15 minutes)
2. Run: python main.py
3. Test: python test_api.py
4. Explore: http://localhost:8000/docs
5. Build: Customize the frontend
6. Deploy: Follow DEPLOYMENT.md when ready

📚 Full documentation in *.md files
📖 Start with: QUICKSTART.md
    """)

def print_project_structure():
    print("\n" + "="*70)
    print("📁 PROJECT STRUCTURE")
    print("="*70)
    print("""
ai-teach-old/
│
├─ BACKEND (NEW)
│  ├─ main.py              ⭐ FastAPI server
│  ├─ client.js            ⭐ JavaScript client
│  ├─ test_api.py          ⭐ Test suite
│  ├─ requirements.txt     ⭐ Dependencies
│  └─ .env.example         ⭐ Config template
│
├─ FRONTEND (NEW/UPDATED)
│  ├─ index_new.html       ⭐ Modern UI
│  └─ styles.css           (existing)
│
├─ DOCUMENTATION (NEW)
│  ├─ QUICKSTART.md        ⭐ Start here!
│  ├─ README_BACKEND.md    ⭐ Full guide
│  ├─ FASTAPI_SETUP.md     ⭐ Technical details
│  ├─ DEPLOYMENT.md        ⭐ Production guide
│  ├─ VISUAL_GUIDE.md      ⭐ Architecture
│  ├─ PROJECT_SUMMARY.md   ⭐ Overview
│  └─ README.md            (original)
│
├─ CREDENTIALS
│  └─ config.json          🔑 Google account (SECRET!)
│
├─ ENVIRONMENT
│  └─ venv39/              🐍 Python 3.9
│
└─ REFERENCE
   ├─ index.html           (original)
   ├─ script.jsp           (original)
   └─ ai_teacher_req.txt   (specs)
    """)

def main():
    print_header()
    
    # Check requirements
    if not check_requirements():
        print("\n⚠️  Some requirements are missing!")
        print("See QUICKSTART.md for setup instructions.")
        return 1
    
    print("\n✅ All requirements met!\n")
    
    # Print guides
    print_quick_start()
    print_file_guide()
    print_documentation_index()
    print_api_reference()
    print_voice_options()
    print_troubleshooting()
    print_next_steps()
    
    print("\n" + "="*70)
    print("🎉 YOU'RE READY!")
    print("="*70)
    print("""
Command to start:
  1. Activate venv: .\venv39\Scripts\Activate.ps1
  2. Run server: python main.py
  3. Test API: python test_api.py (new terminal)
  4. Open UI: http://localhost:8000/docs

📖 Documentation: Read QUICKSTART.md first!

Questions? Check the *.md documentation files!
    """)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
