# Auto-Prompt Generation Feature

## Overview
The AI Teacher now automatically generates optimized prompts as students type their study material. This makes the experience seamless - no need to click buttons or wait for manual configuration.

---

## How It Works

### 1. **Automatic Prompt Generation (2-Second Delay)**
- When a student pastes or types study material, the system waits 2 seconds
- After the 2-second delay, it automatically analyzes the text
- A customized teacher prompt is generated and displayed in the "Style Prompt" field
- The analysis shows:
  - **Sentiment**: Emotional tone of the material
  - **Tone Type**: Formal, casual, technical, etc.
  - **Content Type**: Educational, narrative, dialogue, etc.
  - **Generated Prompt**: The exact voice instruction for the AI teacher

### 2. **Education-Focused Prompts**
The prompt generator prioritizes **educational content** since this app is designed for students:

#### Educational Positive (Exciting Content)
> "You're an enthusiastic and engaging teacher reading study material to students. Use a warm, encouraging, and energetic tone. Speak with clear articulation and natural pauses between concepts..."

#### Educational Neutral (Standard Content)
> "You're a clear, professional teacher reading study material to students. Maintain a calm, patient, and authoritative tone. Speak at a steady, easy-to-follow pace..."

#### Educational Negative/Complex (Difficult Content)
> "You're a compassionate, supportive teacher reading difficult or complex study material. Use a reassuring, calm tone despite any challenging content. Speak slowly and deliberately..."

### 3. **Smart Content Detection**
The system defaults to **educational templates** because:
- Most text input is study material from students
- If content type is uncertain, it assumes educational context
- This ensures the AI teacher speaks in an appropriate, student-friendly manner

---

## Key Features

### ✅ **Zero-Click Auto-Generation**
- No need to click a "Generate" button
- No need to manually enter prompts
- Prompts appear automatically as you type

### ✅ **2-Second Smart Delay**
- Waits 2 seconds after you stop typing
- Prevents excessive API calls
- Provides time for natural typing/pasting

### ✅ **Visual Feedback**
- Status messages show "Analyzing text..." while processing
- Success confirmation: "✓ Prompt auto-generated!"
- Analysis results displayed in the suggestion box

### ✅ **Toggle Control**
- Students can enable/disable auto-generation
- When disabled, they can type custom prompts
- Toggle clearly labeled in the UI

### ✅ **Per-Chunk Optimization**
- Each chunk of text gets its own optimized prompt
- Long texts are split intelligently
- Each section uses context-appropriate instructions

---

## Technical Implementation

### Backend (`text_analyzer.py`)
```python
# Prioritizes educational content
if content_type == "educational" and content_confidence > 0.3:
    # Use educational template
else:
    # Default to educational template for student materials
```

### Frontend (`client.js`)
```javascript
// Debounced auto-generation
textInput.addEventListener("input", () => {
  clearTimeout(autoGenerateTimer);
  autoGenerateTimer = setTimeout(async () => {
    await autoGeneratePrompt(text);  // Calls after 2 seconds
  }, 2000);
});
```

### UI (`index_new.html`)
- Auto-prompt checkbox (enabled by default)
- Real-time analysis display
- Disabled prompt field (shows auto-generated text)

---

## User Experience Flow

### For Students Studying:
1. **Open AI Teacher app**
2. **Copy study material** from textbook/notes
3. **Paste into text box** → Auto-analysis begins
4. **Wait 2 seconds** → Prompt auto-generates
5. **Click "Speak"** → AI teacher reads it aloud
6. **Adjust settings** (voice, pitch, speed) if needed
7. **Listen & learn** with perfect teacher tone

### For Custom Prompts:
1. **Toggle "Enable" off**
2. **Type custom prompt** (e.g., "Read like a friendly tutor")
3. **Toggle back on** for auto-generation
4. **Click "Speak"**

---

## Performance Benefits

- **⚡ Fast**: 2-second analysis is quick enough to not feel sluggish
- **🎯 Accurate**: Detects educational vs other content types
- **📚 Smart**: Defaults to teacher voice for student learning
- **🔄 Smooth**: Debouncing prevents unnecessary API calls
- **✨ Professional**: AI teacher voice matches content perfectly

---

## Audio Parameters Auto-Adjustment

Based on sentiment analysis, the system also auto-adjusts:
- **Pitch**: +4 for positive content, -3 for negative
- **Speaking Rate**: 0.85x for complex text, 1.1x for simple
- **Volume**: Adjusted based on emotional tone

---

## Example Analyses

### Example 1: Biology Study Material
**Input**: "Photosynthesis is the process by which plants convert light energy into chemical energy. It occurs in two stages: the light-dependent reactions in the thylakoid membrane and the light-independent reactions (Calvin cycle) in the stroma."

**Analysis**:
- Sentiment: Neutral
- Tone: Technical
- Content: Educational
- **Prompt**: "You're a clear, professional teacher reading study material to students..."

### Example 2: History Lesson
**Input**: "The French Revolution was a pivotal moment in world history! It fundamentally changed society, politics, and culture across Europe. The ideals of liberty, equality, and fraternity inspired generations..."

**Analysis**:
- Sentiment: Positive
- Tone: Formal but engaging
- Content: Educational
- **Prompt**: "You're an enthusiastic and engaging teacher reading study material to students..."

### Example 3: Complex Concept
**Input**: "Quantum entanglement is a phenomenon where particles become correlated in such a way that the quantum state of each particle cannot be described independently. This defies classical intuition and troubled even Einstein."

**Analysis**:
- Sentiment: Neutral (slightly complex/concerned)
- Tone: Technical
- Content: Educational
- **Prompt**: "You're a clear, professional teacher reading study material to students. Maintain a calm, patient tone..."

---

## Customization

Students can still customize by:
- **Disabling auto-generation** and entering custom prompts
- **Adjusting pitch/speed sliders** in Advanced Settings
- **Selecting different voices** (Achernar, Altair, Vega)
- **Choosing audio format** (WAV, MP3, etc.)

---

## Future Enhancements

- [ ] Save favorite prompts for similar content
- [ ] Learn student preferences over time
- [ ] Support for different languages
- [ ] Integration with popular note-taking apps
- [ ] Voice recognition to detect speaking style preference
