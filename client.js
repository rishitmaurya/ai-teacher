/**
 * JavaScript client for FastAPI Text-to-Speech backend
 * Use this to call the FastAPI endpoints from your frontend
 */

const API_BASE_URL = "http://localhost:8000";

/**
 * Synthesize speech and return audio content
 * @param {string} text - Text to synthesize
 * @param {string} prompt - Style/emotion prompt
 * @param {Object} options - Additional options
 * @returns {Promise} Response with audio content
 */
async function synthesizeText(text, prompt = "Read aloud naturally", options = {}) {
  try {
    const requestBody = {
      text: text,
      prompt: prompt,
      voice_name: options.voice_name || "Achernar",
      language_code: options.language_code || "en-US",
      model_name: options.model_name || "gemini-2.5-pro-tts",
      audio_encoding: options.audio_encoding || "LINEAR16",
      pitch: options.pitch || 0.0,
      speaking_rate: options.speaking_rate || 1.0
    };

    console.log("Sending request to TTS API:", requestBody);

    const response = await fetch(`${API_BASE_URL}/synthesize`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "API request failed");
    }

    const result = await response.json();
    console.log("TTS API Response:", result);
    
    return result;

  } catch (error) {
    console.error("Error calling TTS API:", error);
    throw error;
  }
}

/**
 * Play audio from base64 content
 * @param {string} audioContent - Base64 encoded audio content
 * @param {HTMLAudioElement} audioElement - Audio element to play on
 */
function playAudio(audioContent, audioElement) {
  try {
    if (!audioElement) {
      audioElement = document.getElementById("audioPlayer");
    }

    // Convert base64 to blob
    const binaryString = atob(audioContent);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    const blob = new Blob([bytes], { type: "audio/wav" });

    // Create blob URL and set as audio source
    const audioUrl = URL.createObjectURL(blob);
    audioElement.src = audioUrl;
    audioElement.play();
  } catch (error) {
    console.error("Error playing audio:", error);
    throw error;
  }
}

/**
 * Stream audio directly
 * @param {string} text - Text to synthesize
 * @param {string} prompt - Style/emotion prompt
 * @param {Object} options - Additional options
 */
async function streamAudio(text, prompt = "Read aloud naturally", options = {}) {
  try {
    const requestBody = {
      text: text,
      prompt: prompt,
      voice_name: options.voice_name || "Achernar",
      language_code: options.language_code || "en-US",
      model_name: options.model_name || "gemini-2.5-pro-tts",
      audio_encoding: options.audio_encoding || "LINEAR16",
      pitch: options.pitch || 0.0,
      speaking_rate: options.speaking_rate || 1.0
    };

    const response = await fetch(`${API_BASE_URL}/synthesize/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      throw new Error("Stream request failed");
    }

    const audioBlob = await response.blob();
    const audioUrl = URL.createObjectURL(audioBlob);
    
    const audioElement = document.getElementById("audioPlayer");
    audioElement.src = audioUrl;
    audioElement.play();

  } catch (error) {
    console.error("Error streaming audio:", error);
    throw error;
  }
}

/**
 * Example usage with HTML controls
 */
function setupTTSControls() {
  const textInput = document.getElementById("textInput");
  const promptInput = document.getElementById("promptInput");
  const voiceSelect = document.getElementById("voiceSelect");
  const modelSelect = document.getElementById("modelSelect");
  const speakBtn = document.getElementById("speakBtn");
  const statusBox = document.getElementById("status");

  if (!speakBtn) return;

  speakBtn.addEventListener("click", async () => {
    try {
      const text = textInput?.value || "";
      const prompt = promptInput?.value || "Read aloud naturally";
      const voice = voiceSelect?.value || "Achernar";
      const model = modelSelect?.value || "gemini-2.5-pro-tts";

      if (!text.trim()) {
        statusBox.innerText = "Please enter text";
        return;
      }

      statusBox.innerText = "Synthesizing...";
      speakBtn.disabled = true;

      const result = await synthesizeText(text, prompt, {
        voice_name: voice,
        model_name: model
      });

      if (result.success && result.audio_content) {
        statusBox.innerText = "Playing audio...";
        playAudio(result.audio_content);
      } else {
        statusBox.innerText = "Failed to synthesize";
      }

    } catch (error) {
      statusBox.innerText = `Error: ${error.message}`;
    } finally {
      speakBtn.disabled = false;
    }
  });
}

// Auto-setup when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", setupTTSControls);
} else {
  setupTTSControls();
}
