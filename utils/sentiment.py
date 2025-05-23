from textblob import TextBlob
import re
from typing import Dict, Any, Tuple

# Emotion indicators
POSITIVE_EMOTIONS = [
    'happy', 'excited', 'passionate', 'enthusiastic', 'confident', 'optimistic',
    'eager', 'motivated', 'inspired', 'determined', 'hopeful', 'love', 'enjoy',
    'interested', 'curious', 'fascinated', 'thrilled', 'delighted', 'pleased'
]

NEGATIVE_EMOTIONS = [
    'confused', 'uncertain', 'worried', 'anxious', 'stressed', 'overwhelmed',
    'frustrated', 'disappointed', 'discouraged', 'unsure', 'lost', 'afraid',
    'scared', 'concerned', 'doubtful', 'hesitant', 'unhappy', 'sad', 'depressed'
]

NEUTRAL_EMOTIONS = [
    'thinking', 'considering', 'wondering', 'pondering', 'contemplating',
    'evaluating', 'assessing', 'analyzing', 'exploring', 'learning',
    'understanding', 'seeking', 'looking', 'searching', 'trying'
]

def analyze_sentiment(text: str) -> str:
    """
    Analyze the sentiment of the given text.
    
    Args:
        text: The text to analyze
        
    Returns:
        Sentiment category: 'positive', 'negative', or 'neutral'
    """
    if not text:
        return 'neutral'
    
    # Use TextBlob for sentiment analysis
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    
    # Check for explicit emotion words
    text_lower = text.lower()
    
    # Count emotion indicators
    positive_count = sum(1 for word in POSITIVE_EMOTIONS if word in text_lower)
    negative_count = sum(1 for word in NEGATIVE_EMOTIONS if word in text_lower)
    
    # Adjust polarity based on explicit emotion words
    if positive_count > negative_count:
        polarity += 0.2
    elif negative_count > positive_count:
        polarity -= 0.2
    
    # Determine sentiment category
    if polarity > 0.1:
        return 'positive'
    elif polarity < -0.1:
        return 'negative'
    else:
        return 'neutral'

def get_response_tone(sentiment: str) -> Dict[str, Any]:
    """
    Get appropriate response tone based on detected sentiment.
    
    Args:
        sentiment: Detected sentiment ('positive', 'negative', or 'neutral')
        
    Returns:
        Dictionary with tone characteristics
    """
    if sentiment == 'positive':
        return {
            'tone': 'enthusiastic',
            'encouragement_level': 'moderate',
            'detail_level': 'high',
            'formality': 'conversational',
            'emoji_use': 'moderate'
        }
    elif sentiment == 'negative':
        return {
            'tone': 'supportive',
            'encouragement_level': 'high',
            'detail_level': 'moderate',
            'formality': 'warm',
            'emoji_use': 'minimal'
        }
    else:  # neutral
        return {
            'tone': 'informative',
            'encouragement_level': 'moderate',
            'detail_level': 'high',
            'formality': 'balanced',
            'emoji_use': 'minimal'
        }

def adjust_response(base_response: str, sentiment: str) -> str:
    """
    Adjust a response based on the detected sentiment.
    
    Args:
        base_response: The base response to adjust
        sentiment: Detected sentiment ('positive', 'negative', or 'neutral')
        
    Returns:
        Adjusted response
    """
    tone = get_response_tone(sentiment)
    
    if sentiment == 'positive':
        # For positive sentiment, match enthusiasm and provide detailed information
        encouragement = [
            "That's great enthusiasm! ",
            "I love your positive energy! ",
            "Your passion is inspiring! "
        ]
        
        if not any(phrase in base_response for phrase in encouragement):
            base_response = encouragement[0] + base_response
            
    elif sentiment == 'negative':
        # For negative sentiment, be supportive and encouraging
        support = [
            "I understand this can feel overwhelming. ",
            "It's completely normal to feel uncertain. ",
            "Many people share these concerns, and that's okay. "
        ]
        
        encouragement = [
            "I'm here to help you navigate this. ",
            "Let's break this down into manageable steps. ",
            "We'll figure this out together. "
        ]
        
        if not any(phrase in base_response for phrase in support + encouragement):
            base_response = support[0] + encouragement[0] + base_response
            
    # Add appropriate closing based on sentiment
    if sentiment == 'positive':
        if not base_response.endswith(('!', '?')):
            base_response += "!"
    elif sentiment == 'negative':
        if not base_response.endswith(('!', '?', '.')):
            base_response += "."
            
        # Add encouraging closing for negative sentiment
        base_response += " Remember, every career journey has its challenges, but with persistence and the right guidance, you'll find your path."
    
    return base_response

def extract_emotion_indicators(text: str) -> Dict[str, float]:
    """
    Extract emotion indicators from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with emotion scores
    """
    text_lower = text.lower()
    
    # Count emotion indicators
    positive_count = sum(1 for word in POSITIVE_EMOTIONS if word in text_lower)
    negative_count = sum(1 for word in NEGATIVE_EMOTIONS if word in text_lower)
    neutral_count = sum(1 for word in NEUTRAL_EMOTIONS if word in text_lower)
    
    # Calculate total and percentages
    total = positive_count + negative_count + neutral_count
    if total == 0:
        return {
            'positive': 0.33,
            'negative': 0.33,
            'neutral': 0.34
        }
    
    return {
        'positive': positive_count / total,
        'negative': negative_count / total,
        'neutral': neutral_count / total
    }