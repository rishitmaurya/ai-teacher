AI TEACHING ASSISTANT - SETUP INSTRUCTIONS
==========================================

Prerequisite : Create the config.json using the service account credentials of the google account 

1. GET A GOOGLE CLOUD API KEY:
   - Go to: https://console.cloud.google.com/
   - Create new project or select existing
   - Enable "Text-to-Speech API"
   - Go to Credentials → Create Credentials → API Key
   - Copy the API key

2. CONFIGURE THE APP:
   - Open js/config.js
   - Find: const GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY_HERE";
   - Replace with your actual API key
   - Save the file

3. RUN THE APPLICATION:
   - Open index.html in a web browser
   - OR use a local server:
     python -m http.server 8000
     Then open: http://localhost:8000

4. TROUBLESHOOTING:
   - If you get CORS errors, use a local server
   - Check browser console for errors (F12)
   - Ensure API key is correct and Text-to-Speech API is enabled

5. TEST THE APP:
   - Select a lesson from dropdown
   - Choose narration style
   - Click Play button
   - Use Raise Hand to ask questions

