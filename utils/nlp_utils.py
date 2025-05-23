import re
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from typing import List, Dict, Any, Set

# Download required NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Career-related keyword sets
TECH_KEYWORDS = {
    'programming', 'coding', 'developer', 'software', 'web', 'app', 'computer', 
    'technology', 'data', 'science', 'machine learning', 'ai', 'artificial intelligence',
    'python', 'javascript', 'java', 'c++', 'algorithm', 'database', 'cloud', 'cybersecurity',
    'network', 'it', 'information technology', 'tech', 'engineering', 'system', 'frontend',
    'backend', 'fullstack', 'devops', 'security', 'hacking', 'blockchain', 'automation'
}

CREATIVE_KEYWORDS = {
    'design', 'art', 'creative', 'visual', 'graphic', 'ui', 'ux', 'user experience',
    'user interface', 'illustration', 'animation', 'drawing', 'photography', 'video',
    'film', 'music', 'writing', 'content', 'storytelling', 'branding', 'fashion',
    'architecture', 'interior design', 'game design', 'advertising', 'marketing'
}

BUSINESS_KEYWORDS = {
    'business', 'management', 'marketing', 'sales', 'finance', 'accounting', 'economics',
    'entrepreneurship', 'startup', 'leadership', 'strategy', 'consulting', 'project management',
    'product management', 'operations', 'hr', 'human resources', 'recruitment', 'analytics',
    'market research', 'ecommerce', 'digital marketing', 'seo', 'social media', 'advertising'
}

HEALTHCARE_KEYWORDS = {
    'healthcare', 'medical', 'doctor', 'nurse', 'physician', 'therapy', 'therapist',
    'clinical', 'health', 'patient', 'hospital', 'pharmacy', 'medicine', 'dental',
    'dentist', 'psychology', 'psychiatry', 'nutrition', 'fitness', 'wellness',
    'public health', 'research', 'biology', 'anatomy', 'physiology'
}

EDUCATION_KEYWORDS = {
    'education', 'teaching', 'teacher', 'professor', 'academic', 'school', 'university',
    'college', 'learning', 'student', 'curriculum', 'instruction', 'training', 'coaching',
    'mentoring', 'e-learning', 'online learning', 'educational technology', 'edtech'
}

# Combine all keywords
ALL_CAREER_KEYWORDS = TECH_KEYWORDS | CREATIVE_KEYWORDS | BUSINESS_KEYWORDS | HEALTHCARE_KEYWORDS | EDUCATION_KEYWORDS

def preprocess_text(text: str) -> str:
    """
    Preprocess text by converting to lowercase, removing punctuation,
    and standardizing whitespace.
    
    Args:
        text: Input text to preprocess
        
    Returns:
        Preprocessed text
    """
    if not text:
        return ""
        
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Standardize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def tokenize_text(text: str) -> List[str]:
    """
    Tokenize text into words, remove stopwords, and lemmatize.
    
    Args:
        text: Input text to tokenize
        
    Returns:
        List of processed tokens
    """
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    
    # Lemmatize
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    
    return tokens

def extract_keywords(text: str) -> Dict[str, List[str]]:
    """
    Extract career-related keywords from text and categorize them.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Dictionary with categorized keywords
    """
    # Preprocess and tokenize
    processed_text = preprocess_text(text)
    tokens = tokenize_text(processed_text)
    
    # Check for bigrams (two-word phrases)
    bigrams = [' '.join(tokens[i:i+2]) for i in range(len(tokens)-1)]
    
    # Combine tokens and bigrams
    all_terms = tokens + bigrams
    
    # Extract keywords by category
    found_keywords = {
        'tech': [kw for kw in all_terms if kw in TECH_KEYWORDS],
        'creative': [kw for kw in all_terms if kw in CREATIVE_KEYWORDS],
        'business': [kw for kw in all_terms if kw in BUSINESS_KEYWORDS],
        'healthcare': [kw for kw in all_terms if kw in HEALTHCARE_KEYWORDS],
        'education': [kw for kw in all_terms if kw in EDUCATION_KEYWORDS]
    }
    
    # Add general category with all found keywords
    all_found = []
    for category_keywords in found_keywords.values():
        all_found.extend(category_keywords)
    found_keywords['all'] = all_found
    
    return found_keywords

def detect_intent(text: str) -> str:
    """
    Detect the primary intent of the user's message.
    
    Args:
        text: User's message
        
    Returns:
        Intent category: tech_interest, creative_mind, dream_job, confused_state, goal_oriented, or general
    """
    processed_text = preprocess_text(text)
    
    # Check for confusion or uncertainty
    confusion_indicators = ['confused', 'not sure', 'dont know', 'uncertain', 'help me', 'lost', 'guidance']
    if any(indicator in processed_text for indicator in confusion_indicators):
        return 'confused_state'
    
    # Check for goal-oriented language
    goal_indicators = ['want to become', 'goal', 'plan', 'roadmap', 'steps', 'how to', 'achieve', 'career path']
    if any(indicator in processed_text for indicator in goal_indicators):
        return 'goal_oriented'
    
    # Check for dream job language
    dream_indicators = ['dream job', 'always wanted', 'passion', 'love to', 'aspire', 'ideal career']
    if any(indicator in processed_text for indicator in dream_indicators):
        return 'dream_job'
    
    # Extract keywords to determine interest area
    keywords = extract_keywords(text)
    
    # Determine primary interest area based on keyword count
    category_counts = {
        'tech_interest': len(keywords['tech']),
        'creative_mind': len(keywords['creative']),
        'business_interest': len(keywords['business']),
        'healthcare_interest': len(keywords['healthcare']),
        'education_interest': len(keywords['education'])
    }
    
    # Get the category with the most keywords
    if max(category_counts.values()) > 0:
        primary_intent = max(category_counts, key=category_counts.get)
        return primary_intent
    
    # Default to general if no specific intent is detected
    return 'general'

def get_career_recommendations(keywords: Dict[str, List[str]], sentiment: str, limit: int = 3) -> List[str]:
    """
    Get career recommendations based on extracted keywords and sentiment.
    This is a simplified version - in production, this would query the database.
    
    Args:
        keywords: Dictionary of extracted keywords by category
        sentiment: Detected sentiment (positive, neutral, negative)
        limit: Maximum number of recommendations to return
        
    Returns:
        List of recommended career titles
    """
    # This is a simplified mapping - in production, this would use the database
    career_matches = {
        'tech': ['Software Developer', 'Data Scientist', 'Cybersecurity Analyst'],
        'creative': ['UX Designer', 'Graphic Designer', 'Content Creator'],
        'business': ['Product Manager', 'Digital Marketing Specialist', 'Financial Analyst'],
        'healthcare': ['Healthcare Administrator', 'Medical Researcher', 'Health Informatics Specialist'],
        'education': ['Instructional Designer', 'Education Technology Specialist', 'Curriculum Developer']
    }
    
    # Count keywords in each category
    category_counts = {
        category: len(kws) for category, kws in keywords.items() 
        if category != 'all'  # Exclude the 'all' category
    }
    
    # Sort categories by keyword count (descending)
    sorted_categories = sorted(category_counts.keys(), key=lambda k: category_counts[k], reverse=True)
    
    # Get recommendations from top categories
    recommendations = []
    for category in sorted_categories:
        if category in career_matches and len(recommendations) < limit:
            # Add careers from this category that aren't already in recommendations
            for career in career_matches[category]:
                if career not in recommendations and len(recommendations) < limit:
                    recommendations.append(career)
    
    # If we still don't have enough recommendations, add from other categories
    if len(recommendations) < limit:
        all_careers = [career for careers in career_matches.values() for career in careers]
        for career in all_careers:
            if career not in recommendations and len(recommendations) < limit:
                recommendations.append(career)
    
    return recommendations[:limit]