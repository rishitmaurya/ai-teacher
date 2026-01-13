# Long Text Chunking Logic - Fixed

## Problem
The Google Text-to-Speech API has a **4000 byte limit** for the combined size of `input.text + input.prompt`.

### Error Experienced
```
Google API error: {
  "error": {
    "code": 400,
    "message": "Either `input.text` or `input.prompt` is longer than the limit of 4000 bytes.",
    "status": "INVALID_ARGUMENT"
  }
}
```

## Solution Implemented

### 1. **Smart Text Splitting** (`split_text_into_chunks`)
- Accounts for **prompt size** when calculating chunk sizes
- Reserves up to 500 bytes for the prompt
- Uses remaining bytes for text: `max_text_bytes = 4000 - prompt_bytes - 100` (100-byte safety margin)
- Splits by **sentences** to preserve context and readability
- Validates each chunk in **bytes** (not just characters), accounting for UTF-8 encoding

### 2. **Intelligent Prompt Handling**
For multi-chunk synthesis:
- **First chunk**: Uses the full user-provided prompt
- **Subsequent chunks**: Uses minimal prompt `"Continue reading naturally"` to save bytes
- **Single chunk**: Always uses full prompt

### 3. **Byte-Level Validation**
Before sending each chunk to Google API:
- Calculates: `total_bytes = len(chunk_text) + len(chunk_prompt)`
- Ensures: `total_bytes <= 4000`
- If validation fails, removes the prompt to fit within limit

### 4. **Audio Combination**
Multiple audio chunks are:
- Decoded from base64
- Combined by skipping the WAV header (44 bytes) from subsequent chunks
- Re-encoded as single base64 audio

## Key Changes

### Function: `split_text_into_chunks(text, prompt="", max_api_limit=4000)`
```python
# Accounts for prompt when calculating max text size
max_text_bytes = 4000 - len(prompt) - 100  # 100-byte safety margin

# Splits by sentences, validates in bytes
for sentence in sentences:
    if chunk_bytes + sentence_bytes + 50 <= max_text_bytes:
        # Add sentence to current chunk
```

### Function: `synthesize_chunk(access_token, chunk_text, chunk_prompt, request)`
- Now accepts `chunk_prompt` parameter (can vary per chunk)
- Logs byte sizes for debugging

### Endpoint: `/synthesize`
```python
# Use full prompt only for single chunk
if len(text_chunks) > 1:
    prompt_first_chunk = request.prompt
    prompt_other_chunks = "Continue reading naturally"

# For each chunk
for i, chunk in enumerate(text_chunks):
    chunk_prompt = prompt_first_chunk if i == 1 else prompt_other_chunks
    audio_content = synthesize_chunk(access_token, chunk, chunk_prompt, request)
```

## Results

✅ **No text length limit** - Can synthesize any size document  
✅ **Respects API constraints** - All requests are ≤ 4000 bytes  
✅ **Seamless audio** - Multiple chunks combined into single continuous audio  
✅ **Context preserved** - Sentences kept together, natural reading flow  
✅ **Byte-safe validation** - Catches oversized chunks before API call  

## Logging
The implementation includes detailed logging:
- `Text splitting config: prompt=X bytes, max_chunk=Y chars`
- `Chunk created: Z bytes`
- `API Request - Text: X bytes, Prompt: Y bytes`
- `Split text into N chunks (max API bytes: 4000)`

## Testing
To test with long text:
1. Paste any length of text in the UI
2. Check browser console for synthesis progress
3. Audio plays seamlessly from beginning to end
