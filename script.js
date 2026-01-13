const statusBox = document.getElementById("status");
const speakBtn = document.getElementById("speakBtn");
const audioPlayer = document.getElementById("audioPlayer");

let apiKey = null;

// Load config.json
fetch("config.json")
  .then(res => res.json())
  .then(json => {
    apiKey = json.api_key;
    if (!apiKey) {
      throw new Error("API key not found in config.json");
    }
    statusBox.innerText = "API key loaded.";
  })
  .catch(err => {
    statusBox.innerText = "Error loading config.json";
    console.error(err);
  });

// Map emotions → SSML prosody style
function emotionToSSML(text, emotion, prompt) {

  text = applyPrompt(text, prompt);

  const wrap = (p) => `<speak><prosody ${p}>${text}</prosody></speak>`;

  switch (emotion) {
    case "happy":
      return wrap(`pitch="+6st" rate="115%"`);
    case "sad":
      return wrap(`pitch="-4st" rate="85%" volume="x-soft"`);
    case "angry":
      return `<speak><emphasis level="strong">${text}</emphasis></speak>`;
    case "calm":
      return wrap(`rate="90%" volume="soft"`);
    case "excited":
      return wrap(`pitch="+8st" rate="130%"`);
    case "neutral":
      return `<speak>${text}</speak>`;
    case "none":
      return `<speak>${text}</speak>`;
  }
}


// Get API key
function getApiKey() {
  if (!apiKey) {
    throw new Error("API key not loaded. Please check config.json");
  }
  return apiKey;
}

function applyPrompt(text, prompt) {
  if (!prompt || prompt.trim() === "") return text;

  return `(${prompt}) ${text}`;
}


// Main speak handler
speakBtn.onclick = async () => {
  try {
    const text = document.getElementById("textInput").value.trim();
    const voice = document.getElementById("voiceSelect").value;
    const model = document.getElementById("modelSelect").value;
    const prompt = document.getElementById("promptInput").value.trim();

    if (!text) {
      statusBox.innerText = "Please enter text.";
      return;
    }

    statusBox.innerText = "Generating token...";
    const token = await getAccessToken();

    statusBox.innerText = "Calling Generative TTS API...";

    const ttsResponse = await fetch(
      "https://texttospeech.googleapis.com/v1beta1/text:synthesize",
      {
        method: "POST",
        headers: {
          "Authorization": "Bearer " + token,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          input: {
            text: text,
            prompt: prompt
          },
          voice: {
            languageCode: "en-US",
            name: voice,
            modelName: model
          },
          audioConfig: {
            audioEncoding: "MP3",
            pitch: 0,
            speakingRate: 1
          }
        })
      }
    );

    const ttsData = await ttsResponse.json();

    if (!ttsData.audioContent) {
      console.error(ttsData);
      statusBox.innerText = "TTS request failed. Check console for details.";
      return;
    }

    statusBox.innerText = "Playing audio...";
    audioPlayer.src = "data:audio/mp3;base64," + ttsData.audioContent;
    audioPlayer.play();

  } catch (e) {
    console.error(e);
    statusBox.innerText = "Error: " + e.message;
  }
};

