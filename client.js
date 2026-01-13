/**
 * JavaScript client for FastAPI Text-to-Speech backend
 * Use this to call the FastAPI endpoints from your frontend
 * Now with auto-prompt generation based on text content
 */

const API_BASE_URL = "http://localhost:8000";

/**
 * Analyze text and get auto-generated prompt
 * @param {string} text - Text to analyze
 * @returns {Promise} Response with analysis and generated prompt
 */
async function analyzeText(text) {
  try {
    if (!text.trim()) {
      throw new Error("Text cannot be empty");
    }

    const requestBody = {
      text: text,
      auto_prompt: true
    };

    console.log("Analyzing text for auto-prompt generation...");

    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Analysis failed");
    }

    const result = await response.json();
    console.log("Analysis Result:", result);
    
    return result;

  } catch (error) {
    console.error("Error analyzing text:", error);
    throw error;
  }
}

/**
 * Synthesize speech and return audio content
 * @param {string} text - Text to synthesize
 * @param {string} prompt - Style/emotion prompt (optional, will auto-generate if not provided)
 * @param {Object} options - Additional options
 * @returns {Promise} Response with audio content
 */
async function synthesizeText(text, prompt = null, options = {}) {
  try {
    const requestBody = {
      text: text,
      prompt: prompt,
      auto_prompt: options.auto_prompt !== false,  // Default to true
      voice_name: options.voice_name || "Achernar",
      language_code: options.language_code || "en-US",
      model_name: options.model_name || "gemini-2.5-pro-tts",
      audio_encoding: options.audio_encoding || "LINEAR16",
      pitch: options.pitch !== undefined ? options.pitch : null,  // null = auto-adjust
      speaking_rate: options.speaking_rate !== undefined ? options.speaking_rate : null,  // null = auto-adjust
      fast_mode: options.fast_mode || false,  // NEW: Use single upfront analysis for all chunks (fastest)
      single_prompt: options.single_prompt || false  // NEW: Reuse one prompt for all chunks (fast)
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
  const autoPromptToggle = document.getElementById("autoPromptToggle");
  const suggestedPromptBox = document.getElementById("suggestedPrompt");

  if (!speakBtn) return;

  // Debounce timer for auto-generation
  let autoGenerateTimer = null;

  // Handle auto-prompt toggle
  if (autoPromptToggle) {
    autoPromptToggle.addEventListener("change", async () => {
      if (autoPromptToggle.checked) {
        // Enable auto-prompt mode
        promptInput?.setAttribute("disabled", "disabled");
        promptInput?.setAttribute("placeholder", "Auto-generating based on your text...");
        updateStatus("Auto-prompt mode: enabled. Prompts will auto-generate as you type.", "info");
        
        // Trigger immediate generation if text exists
        const text = textInput?.value || "";
        if (text.trim()) {
          clearTimeout(autoGenerateTimer);
          autoGeneratePrompt(text);
        }
      } else {
        // Disable auto-prompt mode
        promptInput?.removeAttribute("disabled");
        promptInput?.setAttribute("placeholder", "Enter your custom prompt here");
        clearTimeout(autoGenerateTimer);
      }
    });
  }

  // Auto-generate prompt with 2-second debounce when text changes
  if (textInput && autoPromptToggle?.checked) {
    textInput.addEventListener("input", () => {
      const text = textInput.value || "";
      
      // Clear previous timer
      clearTimeout(autoGenerateTimer);
      
      // Show loading status
      if (text.trim()) {
        updateStatus("Analyzing text...", "info");
        
        // Set new timer for 2-second delay
        autoGenerateTimer = setTimeout(async () => {
          await autoGeneratePrompt(text);
        }, 2000);
      } else {
        // Clear prompt and analysis if text is empty
        if (promptInput) promptInput.value = "";
        if (suggestedPromptBox) suggestedPromptBox.style.display = "none";
      }
    });
  }

  // Auto-generate prompt function
  async function autoGeneratePrompt(text) {
    try {
      if (!text.trim()) return;
      
      const analysis = await analyzeText(text);
      
      if (suggestedPromptBox) {
        suggestedPromptBox.style.display = "block";
        suggestedPromptBox.innerHTML = `
          <strong>📊 Auto-Generated Analysis:</strong><br/>
          <small>
            <strong>Sentiment:</strong> ${analysis.analysis.sentiment.dominant_sentiment}<br/>
            <strong>Tone:</strong> ${analysis.analysis.tone.tone_type}<br/>
            <strong>Content:</strong> ${analysis.analysis.content_type.primary_type}<br/>
            <br/>
            <strong>🎭 Prompt:</strong><br/>
            <em>"${analysis.generated_prompt}"</em>
          </small>
        `;
      }

      if (promptInput) {
        promptInput.value = analysis.generated_prompt;
      }

      updateStatus("✓ Prompt auto-generated!", "success");
    } catch (error) {
      console.error("Error auto-generating prompt:", error);
      updateStatus(`Auto-generation: ${error.message}`, "error");
    }
  }

  // Handle speak button
  speakBtn.addEventListener("click", async () => {
    try {
      const text = textInput?.value || "";
      let prompt = promptInput?.value || null;
      const voice = voiceSelect?.value || "Achernar";
      const model = modelSelect?.value || "gemini-2.5-pro-tts";
      const useAutoPrompt = autoPromptToggle?.checked ?? true;

      if (!text.trim()) {
        updateStatus("Please enter text", "error");
        return;
      }

      // If auto-prompt is enabled and prompt is empty or default, don't send it
      if (useAutoPrompt && (!prompt || prompt.trim() === "")) {
        prompt = null;
      }

      updateStatus("Synthesizing...", "info");
      speakBtn.disabled = true;

      const result = await synthesizeText(text, prompt, {
        voice_name: voice,
        model_name: model,
        auto_prompt: useAutoPrompt
      });

      if (result.success && result.audio_content) {
        updateStatus("✓ Playing audio...", "success");
        playAudio(result.audio_content);

        // Show generated prompts if available
        if (result.generated_prompts && result.generated_prompts.length > 1) {
          console.log("Prompts used for each chunk:", result.generated_prompts);
          updateStatus(
            `✓ Audio ready! (${result.generated_prompts.length} sections with custom prompts)`,
            "success"
          );
        }
      } else {
        updateStatus("Failed to synthesize", "error");
      }

    } catch (error) {
      updateStatus(`Error: ${error.message}`, "error");
    } finally {
      speakBtn.disabled = false;
    }
  });
}

// Helper function to update status
function updateStatus(message, type = "info") {
  const statusBox = document.getElementById("status");
  if (statusBox) {
    statusBox.textContent = message;
    statusBox.className = type;
  }
}

// Auto-setup when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", setupTTSControls);
} else {
  setupTTSControls();
}
