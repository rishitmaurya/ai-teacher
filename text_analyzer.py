"""
Fast Text Analyzer for Auto-Prompt Generation
Analyzes text across multiple dimensions to generate optimal TTS prompts
Uses lightweight libraries for speed (no heavy ML models)
"""

import re
from typing import Dict, Tuple, Optional
from collections import Counter
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# SENTIMENT & EMOTION KEYWORDS DICTIONARIES
# ============================================================================

POSITIVE_KEYWORDS = {
    "amazing": 0.9, "fantastic": 0.9, "wonderful": 0.9, "excellent": 0.9,
    "great": 0.8, "good": 0.7, "happy": 0.9, "joy": 0.9, "thrilled": 0.95,
    "excited": 0.9, "love": 0.85, "awesome": 0.85, "beautiful": 0.8,
    "perfect": 0.85, "brilliant": 0.9, "incredible": 0.9, "outstanding": 0.9,
    "superb": 0.85, "delighted": 0.9, "pleased": 0.75, "grateful": 0.8,
    "blessed": 0.85, "accomplished": 0.75, "successful": 0.8, "triumph": 0.85
}

NEGATIVE_KEYWORDS = {
    "terrible": 0.95, "awful": 0.95, "horrible": 0.95, "hate": 0.9,
    "angry": 0.9, "upset": 0.85, "sad": 0.85, "depressed": 0.9,
    "disappointed": 0.8, "frustrated": 0.8, "annoyed": 0.75, "scared": 0.85,
    "afraid": 0.85, "worried": 0.8, "anxious": 0.8, "stressed": 0.75,
    "disgusted": 0.9, "bad": 0.7, "poor": 0.7, "failed": 0.8,
    "crisis": 0.9, "emergency": 0.85, "dangerous": 0.85, "wrong": 0.7,
    "mistake": 0.6, "problem": 0.65, "issue": 0.55, "difficult": 0.6
}

URGENT_KEYWORDS = {
    "urgent": 0.95, "critical": 0.95, "must": 0.85, "immediately": 0.9,
    "now": 0.75, "important": 0.8, "essential": 0.8, "crucial": 0.9,
    "emergency": 0.9, "asap": 0.95, "alert": 0.9, "warning": 0.85,
    "immediate": 0.9, "imperative": 0.85, "required": 0.75, "mandatory": 0.8
}

CALM_KEYWORDS = {
    "peaceful": 0.9, "serene": 0.9, "calm": 0.9, "relaxed": 0.85,
    "gentle": 0.85, "soft": 0.8, "quiet": 0.8, "rest": 0.8,
    "meditation": 0.9, "tranquil": 0.9, "soothing": 0.9, "ease": 0.8,
    "comfort": 0.85, "cozy": 0.8, "safe": 0.8, "secure": 0.8,
    "cool": 0.75, "composed": 0.8, "collected": 0.75, "mindful": 0.85
}

FORMAL_KEYWORDS = {
    "furthermore": 0.9, "notwithstanding": 0.95, "subsequently": 0.9,
    "hence": 0.85, "thus": 0.85, "moreover": 0.85, "however": 0.75,
    "therefore": 0.8, "whereas": 0.85, "accordingly": 0.85, "hereby": 0.9,
    "thereby": 0.85, "thereof": 0.85, "concerning": 0.8, "regarding": 0.75,
    "pertaining": 0.85, "established": 0.8, "protocol": 0.9, "procedure": 0.85
}

CASUAL_KEYWORDS = {
    "gonna": 0.95, "wanna": 0.95, "kinda": 0.9, "sorta": 0.9,
    "awesome": 0.85, "cool": 0.8, "awesome": 0.85, "hey": 0.95,
    "yeah": 0.95, "nope": 0.95, "yep": 0.95, "gotta": 0.9,
    "dunno": 0.95, "lemme": 0.95, "gimme": 0.95, "ain't": 0.95,
    "ain't": 0.95, "stuff": 0.8, "thing": 0.75, "like": 0.7
}

TECHNICAL_KEYWORDS = {
    "algorithm": 0.9, "database": 0.9, "configuration": 0.9, "parameter": 0.85,
    "implementation": 0.85, "protocol": 0.85, "system": 0.75, "network": 0.8,
    "server": 0.8, "client": 0.8, "API": 0.9, "integration": 0.85,
    "optimization": 0.85, "cache": 0.85, "encryption": 0.9, "authentication": 0.85,
    "framework": 0.8, "library": 0.75, "module": 0.75, "function": 0.75,
    "variable": 0.8, "iteration": 0.8, "recursion": 0.85, "synchronous": 0.9
}

EDUCATIONAL_KEYWORDS = {
    "explain": 0.85, "understand": 0.8, "learn": 0.85, "teach": 0.85,
    "student": 0.8, "teacher": 0.8, "lesson": 0.8, "course": 0.8,
    "chapter": 0.8, "definition": 0.85, "concept": 0.8, "theory": 0.8,
    "principle": 0.8, "example": 0.75, "exercise": 0.75, "assignment": 0.75,
    "knowledge": 0.8, "skill": 0.75, "practice": 0.75, "study": 0.75,
    "education": 0.85, "academic": 0.85, "scholarly": 0.85, "pedagogy": 0.9
}

# ============================================================================
# TEXT ANALYSIS FUNCTIONS
# ============================================================================

def analyze_sentiment(text: str) -> Dict:
    """
    Fast sentiment analysis using keyword matching.
    Returns sentiment scores without external ML models.
    
    Returns:
        {
            "positive_score": 0-1,
            "negative_score": 0-1,
            "neutral_score": 0-1,
            "dominant_sentiment": "positive|negative|neutral",
            "emotion_markers": ["happy", "excited", ...]
        }
    """
    text_lower = text.lower()
    
    # Count emotional keywords
    positive_matches = sum(
        POSITIVE_KEYWORDS[word] for word in POSITIVE_KEYWORDS 
        if word in text_lower
    )
    negative_matches = sum(
        NEGATIVE_KEYWORDS[word] for word in NEGATIVE_KEYWORDS 
        if word in text_lower
    )
    urgent_matches = sum(
        URGENT_KEYWORDS[word] for word in URGENT_KEYWORDS 
        if word in text_lower
    )
    
    # Normalize scores (0-1 range)
    total_weight = max(positive_matches + negative_matches + urgent_matches, 1)
    positive_score = min(positive_matches / (total_weight * 0.5), 1.0)
    negative_score = min((negative_matches + urgent_matches) / (total_weight * 0.5), 1.0)
    
    # Determine dominant sentiment
    if positive_score > 0.6:
        dominant = "positive"
    elif negative_score > 0.6:
        dominant = "negative"
    else:
        dominant = "neutral"
    
    # Extract emotion markers
    emotion_markers = []
    for word in POSITIVE_KEYWORDS:
        if word in text_lower:
            emotion_markers.append(word)
    for word in NEGATIVE_KEYWORDS:
        if word in text_lower:
            emotion_markers.append(word)
    
    return {
        "positive_score": round(positive_score, 2),
        "negative_score": round(negative_score, 2),
        "neutral_score": round(1 - positive_score - negative_score, 2),
        "dominant_sentiment": dominant,
        "emotion_markers": emotion_markers[:5]  # Top 5 markers
    }


def analyze_tone(text: str) -> Dict:
    """
    Detect tone: formal vs casual, technical level
    
    Returns:
        {
            "formality_score": 0-1 (0=casual, 1=formal),
            "tone_type": "formal|casual|technical|conversational|balanced",
            "technical_level": 0-1 (0=lay, 1=highly technical),
            "markers": ["marker1", "marker2", ...]
        }
    """
    text_lower = text.lower()
    
    # Count tone markers
    formal_count = sum(1 for word in FORMAL_KEYWORDS if word in text_lower)
    casual_count = sum(1 for word in CASUAL_KEYWORDS if word in text_lower)
    technical_count = sum(1 for word in TECHNICAL_KEYWORDS if word in text_lower)
    
    # Calculate formality score
    total_tone_words = formal_count + casual_count
    if total_tone_words > 0:
        formality = formal_count / total_tone_words
    else:
        # Check for contractions (indicates casual)
        contraction_count = len(re.findall(r"n't|'ll|'ve|'re|'m|'d", text_lower))
        formality = max(0, 1 - (contraction_count / max(len(text.split()), 1) * 10))
    
    # Technical level
    technical_level = min(technical_count / max(len(text.split()) / 10, 1), 1.0)
    
    # Determine tone type
    if technical_level > 0.5:
        tone_type = "technical"
    elif formality > 0.6:
        tone_type = "formal"
    elif casual_count > formal_count:
        tone_type = "casual"
    elif technical_count > 0:
        tone_type = "technical"
    else:
        tone_type = "conversational"
    
    return {
        "formality_score": round(formality, 2),
        "tone_type": tone_type,
        "technical_level": round(technical_level, 2),
        "markers": {
            "formal": formal_count,
            "casual": casual_count,
            "technical": technical_count
        }
    }


def analyze_content_type(text: str) -> Dict:
    """
    Classify content type: educational, narrative, dialogue, instructions, etc.
    
    Returns:
        {
            "primary_type": "educational|narrative|dialogue|instructions|poetry|other",
            "confidence": 0-1,
            "characteristics": ["characteristic1", ...]
        }
    """
    text_lower = text.lower()
    lines = text.strip().split('\n')
    
    # Count content type indicators
    educational_count = sum(1 for word in EDUCATIONAL_KEYWORDS if word in text_lower)
    
    # Dialogue detection (speaker: text pattern or >)
    dialogue_pattern = r'^\s*[A-Z][a-z]+\s*[\:\-]|^>\s+|^"[^"]*"\s*(said|asked|replied)'
    dialogue_lines = sum(1 for line in lines if re.match(dialogue_pattern, line))
    dialogue_ratio = dialogue_lines / max(len(lines), 1)
    
    # Question pattern (for instructions/tutorials)
    question_count = len(re.findall(r'\?', text))
    question_ratio = question_count / max(len(text.split('.!?')), 1)
    
    # Imperative sentences (commands/instructions)
    imperative_count = len(re.findall(r'^\s*(Add|Remove|Create|Delete|Update|Copy|Paste|First|Next|Then|Finally|Step)\b', text, re.MULTILINE))
    
    # Poetry detection (line breaks, rhyming)
    avg_line_length = sum(len(line) for line in lines) / max(len(lines), 1)
    poetry_score = 1 if (avg_line_length < 50 and len(lines) > 3) else 0
    
    # Narrative detection (storytelling elements)
    narrative_words = ['once', 'upon', 'time', 'kingdom', 'tale', 'story', 'character', 'scene', 'happened', 'suddenly']
    narrative_count = sum(1 for word in narrative_words if word in text_lower)
    
    # Determine primary type
    scores = {
        "educational": educational_count * 2,
        "dialogue": dialogue_ratio * 10,
        "instructions": imperative_count * 3,
        "narrative": narrative_count * 2,
        "poetry": poetry_score * 5
    }
    
    if not any(scores.values()):
        primary_type = "other"
        confidence = 0.3
    else:
        primary_type = max(scores, key=scores.get)
        confidence = min(scores[primary_type] / 10, 1.0)
    
    return {
        "primary_type": primary_type,
        "confidence": round(confidence, 2),
        "characteristics": {
            "educational_markers": educational_count,
            "dialogue_ratio": round(dialogue_ratio, 2),
            "question_ratio": round(question_ratio, 2),
            "imperative_count": imperative_count,
            "narrative_markers": narrative_count
        }
    }


def analyze_pace(text: str) -> Dict:
    """
    Determine optimal speaking pace based on text complexity
    
    Returns:
        {
            "suggested_rate": 0.25-4.0 (1.0 = normal),
            "complexity": "simple|moderate|complex",
            "avg_word_length": float,
            "avg_sentence_length": int
        }
    """
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s for s in sentences if s.strip()]
    
    avg_word_length = sum(len(word) for word in words) / max(len(words), 1)
    avg_sentence_length = len(words) / max(len(sentences), 1)
    
    # Determine complexity
    if avg_word_length < 4 and avg_sentence_length < 12:
        complexity = "simple"
        suggested_rate = 1.1  # Slightly faster
    elif avg_word_length > 6 and avg_sentence_length > 20:
        complexity = "complex"
        suggested_rate = 0.85  # Slower for clarity
    else:
        complexity = "moderate"
        suggested_rate = 1.0  # Normal pace
    
    return {
        "suggested_rate": round(suggested_rate, 2),
        "complexity": complexity,
        "avg_word_length": round(avg_word_length, 1),
        "avg_sentence_length": round(avg_sentence_length, 1)
    }


def analyze_text(text: str) -> Dict:
    """
    Complete text analysis returning all dimensions
    """
    if not text.strip():
        return {}
    
    sentiment = analyze_sentiment(text)
    tone = analyze_tone(text)
    content = analyze_content_type(text)
    pace = analyze_pace(text)
    
    analysis = {
        "sentiment": sentiment,
        "tone": tone,
        "content_type": content,
        "pace": pace
    }
    
    logger.info(f"Text Analysis Complete - Sentiment: {sentiment['dominant_sentiment']}, "
                f"Tone: {tone['tone_type']}, Content: {content['primary_type']}")
    
    return analysis


# ============================================================================
# PROMPT GENERATION TEMPLATES
# ============================================================================

PROMPT_TEMPLATES = {
    # Educational Content - Focused on studying and learning
    "educational_positive": (
        "You're an enthusiastic and engaging teacher reading study material to students. "
        "Use a warm, encouraging, and energetic tone. Speak with clear articulation and natural pauses "
        "between concepts. Emphasize important points with appropriate inflection. Make the material "
        "interesting and help students feel excited about learning. Include slight emphasis on key terms."
    ),
    
    "educational_neutral": (
        "You're a clear, professional teacher reading study material to students. "
        "Maintain a calm, patient, and authoritative tone. Speak at a steady, easy-to-follow pace. "
        "Use natural pauses after important concepts to allow comprehension. Articulate clearly "
        "and emphasize definitions and key concepts slightly. Help students understand and retain the material."
    ),
    
    "educational_negative": (
        "You're a compassionate, supportive teacher reading difficult or complex study material. "
        "Use a reassuring, calm tone despite any challenging content. Speak slowly and deliberately "
        "to ensure clarity and understanding. Include thoughtful pauses for students to absorb information. "
        "Make the material feel approachable and less intimidating."
    ),
    
    # Narrative Content
    "narrative_positive": (
        "You're a skilled storyteller sharing an engaging narrative. "
        "Use a warm, expressive voice with natural emotional variation. "
        "Bring the story to life with enthusiasm and good pacing."
    ),
    
    "narrative_negative": (
        "You're a thoughtful storyteller sharing a poignant narrative. "
        "Use an expressive, emotionally aware voice. Slow your pace slightly "
        "for dramatic moments. Convey the gravity of the story."
    ),
    
    "narrative_neutral": (
        "You're a clear, engaging storyteller. Speak with natural variation "
        "in tone and pacing. Maintain listener engagement throughout. "
        "Use pauses for dramatic effect where appropriate."
    ),
    
    # Dialogue
    "dialogue": (
        "You're narrating dialogue between multiple speakers. "
        "Use distinct vocal characteristics for different characters. "
        "Pause between speaker changes. Maintain clear, engaging delivery."
    ),
    
    # Instructions
    "instructions_urgent": (
        "You're clearly delivering important step-by-step instructions. "
        "Speak with authority and clarity. Use emphasis on critical steps. "
        "Maintain a slightly elevated pace to convey importance. Pause after each step."
    ),
    
    "instructions_normal": (
        "You're clearly explaining step-by-step instructions. "
        "Speak at a steady, easy-to-follow pace. Pause between steps. "
        "Maintain clear articulation and professional tone."
    ),
    
    # Technical Content
    "technical": (
        "You're an expert explaining technical material with precision. "
        "Speak clearly and deliberately at a measured pace. Use proper "
        "pronunciation for technical terms. Maintain professional authority."
    ),
    
    # Conversational
    "conversational_friendly": (
        "Speak like a warm, approachable friend sharing thoughts. "
        "Be conversational and genuine. Use a natural, relaxed pace. "
        "Sound personable and easy to connect with."
    ),
    
    "conversational_professional": (
        "Maintain a professional but friendly conversational tone. "
        "Use clear articulation and measured pace. Sound businesslike yet personable. "
        "Create a sense of trust and reliability."
    ),
    
    # Urgent/Important
    "urgent": (
        "Convey urgency and importance. Speak with elevated energy and slightly "
        "faster pace, but maintain clarity. Use appropriate emphasis. Make it clear this matters."
    ),
    
    # Calm/Peaceful
    "calm": (
        "Speak in a calm, soothing voice with a slower pace. "
        "Use soft volume and gentle delivery. Create a peaceful, safe atmosphere. "
        "Include thoughtful pauses for reflection."
    ),
    
    # Default
    "balanced": (
        "You're a teacher reading study material aloud to help students learn. "
        "Speak clearly and naturally with good pacing. Emphasize important terms and concepts. "
        "Use natural pauses to allow students time to absorb information. "
        "Maintain an engaging but professional tone throughout."
    )
}


def generate_prompt(analysis: Dict, topic: str = "the material") -> str:
    """
    Generate an optimal prompt based on text analysis results
    Prioritizes educational content for student learning
    
    Args:
        analysis: Dict from analyze_text()
        topic: Optional topic description to include in prompt
    
    Returns:
        Generated prompt string
    """
    if not analysis:
        return PROMPT_TEMPLATES["balanced"]
    
    sentiment = analysis.get("sentiment", {})
    tone = analysis.get("tone", {})
    content = analysis.get("content_type", {})
    
    sentiment_val = sentiment.get("dominant_sentiment", "neutral")
    tone_type = tone.get("tone_type", "conversational")
    content_type = content.get("primary_type", "other")
    content_confidence = content.get("confidence", 0)
    technical_level = tone.get("technical_level", 0)
    
    # PRIORITY 1: If content is clearly educational, use educational templates
    if content_type == "educational" and content_confidence > 0.3:
        if sentiment_val == "positive":
            template_key = "educational_positive"
        elif sentiment_val == "negative":
            template_key = "educational_negative"
        else:
            template_key = "educational_neutral"
    
    # PRIORITY 2: If uncertain about content type but looks like study material, default to educational
    # (Most likely use case for this app - student study materials)
    elif content_confidence <= 0.3:
        # Use educational template by default since this is for students studying
        if sentiment_val == "positive":
            template_key = "educational_positive"
        elif sentiment_val == "negative":
            template_key = "educational_negative"
        else:
            template_key = "educational_neutral"
    
    # PRIORITY 3: Other content types
    elif content_type == "narrative":
        if sentiment_val == "positive":
            template_key = "narrative_positive"
        elif sentiment_val == "negative":
            template_key = "narrative_negative"
        else:
            template_key = "narrative_neutral"
    
    elif content_type == "dialogue":
        template_key = "dialogue"
    
    elif content_type == "instructions":
        if "urgent" in analysis.get("sentiment", {}).get("emotion_markers", []):
            template_key = "instructions_urgent"
        else:
            template_key = "instructions_normal"
    
    elif technical_level > 0.6:
        template_key = "technical"
    
    elif tone_type == "formal":
        template_key = "conversational_professional"
    elif tone_type == "casual":
        template_key = "conversational_friendly"
    elif tone_type == "technical":
        template_key = "technical"
    
    elif sentiment_val == "negative":
        template_key = "calm"
    elif sentiment_val == "positive":
        if "urgent" in analysis.get("sentiment", {}).get("emotion_markers", []):
            template_key = "urgent"
        else:
            template_key = "conversational_friendly"
    
    else:
        template_key = "balanced"
    
    # Format template with topic
    template = PROMPT_TEMPLATES.get(template_key, PROMPT_TEMPLATES["balanced"])
    prompt = template.replace("{topic}", topic)
    
    logger.info(f"Generated prompt using template: {template_key}")
    
    return prompt


# ============================================================================
# AUDIO PARAMETER ADJUSTMENT
# ============================================================================

def get_audio_adjustments(analysis: Dict) -> Dict:
    """
    Calculate audio parameter adjustments based on analysis
    
    Returns:
        {
            "pitch": -20.0 to 20.0,
            "speaking_rate": 0.25 to 4.0,
            "volume": -20.0 to 20.0
        }
    """
    if not analysis:
        return {"pitch": 0.0, "speaking_rate": 1.0, "volume": 0.0}
    
    sentiment = analysis.get("sentiment", {})
    pace = analysis.get("pace", {})
    
    sentiment_val = sentiment.get("dominant_sentiment", "neutral")
    suggested_rate = pace.get("suggested_rate", 1.0)
    
    # Pitch adjustment based on sentiment
    if sentiment_val == "positive":
        pitch = 4.0  # Slightly elevated
    elif sentiment_val == "negative":
        pitch = -3.0  # Slightly lowered
    else:
        pitch = 0.0
    
    # Speaking rate from pace analysis
    speaking_rate = float(suggested_rate)
    
    # Volume adjustment
    if sentiment_val == "negative":
        volume = -3.0  # Slightly softer
    elif sentiment_val == "positive":
        volume = 2.0  # Slightly louder
    else:
        volume = 0.0
    
    return {
        "pitch": round(pitch, 1),
        "speaking_rate": round(speaking_rate, 2),
        "volume": round(volume, 1)
    }
