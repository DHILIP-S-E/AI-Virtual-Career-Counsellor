import streamlit as st
import streamlit_lottie
import requests
import json
from typing import Dict, Any, Optional

def load_lottie_animation(url: str) -> Optional[Dict[str, Any]]:
    """
    Load a Lottie animation from a URL
    
    Args:
        url: URL to the Lottie animation JSON
        
    Returns:
        Dictionary containing the Lottie animation data or None if loading fails
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to load animation from {url}: HTTP {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error loading animation: {str(e)}")
        return None

def get_animation_url(animation_type: str) -> str:
    """
    Get URL for a specific type of animation
    
    Args:
        animation_type: Type of animation to load
        
    Returns:
        URL to the Lottie animation JSON
    """
    # Dictionary mapping animation types to URLs
    animation_urls = {
        "welcome": "https://assets5.lottiefiles.com/packages/lf20_khzniaya.json",
        "thinking": "https://assets5.lottiefiles.com/packages/lf20_yd8fbnml.json",
        "success": "https://assets5.lottiefiles.com/packages/lf20_jvkzwk0t.json",
        "error": "https://assets5.lottiefiles.com/packages/lf20_rbtawnwz.json",
        "loading": "https://assets5.lottiefiles.com/packages/lf20_p8bfn5to.json",
        "career": "https://assets5.lottiefiles.com/packages/lf20_vvmkgfp3.json",
        "education": "https://assets5.lottiefiles.com/packages/lf20_jtbfg2nb.json",
        "roadmap": "https://assets5.lottiefiles.com/packages/lf20_cmaqoazd.json"
    }
    
    return animation_urls.get(animation_type, animation_urls["welcome"])

def display_career_animation(career_field: str) -> None:
    """
    Display an animation related to a specific career field
    
    Args:
        career_field: The career field to display an animation for
    """
    # Map career fields to animation types
    field_to_animation = {
        "technology": "https://assets5.lottiefiles.com/packages/lf20_vvmkgfp3.json",
        "design": "https://assets5.lottiefiles.com/packages/lf20_jtbfg2nb.json",
        "business": "https://assets5.lottiefiles.com/packages/lf20_cmaqoazd.json",
        "healthcare": "https://assets5.lottiefiles.com/packages/lf20_p8bfn5to.json",
        "education": "https://assets5.lottiefiles.com/packages/lf20_yd8fbnml.json"
    }
    
    # Get the animation URL for the career field
    animation_url = field_to_animation.get(
        career_field.lower(), 
        "https://assets5.lottiefiles.com/packages/lf20_khzniaya.json"  # Default animation
    )
    
    # Load and display the animation
    animation_data = load_lottie_animation(animation_url)
    if animation_data:
        streamlit_lottie.st_lottie(animation_data, height=200)