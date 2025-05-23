import streamlit as st
import streamlit_lottie
import requests
import json
import pandas as pd
import time
from datetime import datetime
import os
import sys

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import project modules
from ui.components import (
    render_chat_interface,
    render_career_cards,
    render_roadmap,
    render_personality_quiz,
    render_weekly_tracker,
    render_voice_chat,
    render_resume_builder
)
from ui.animations import load_lottie_animation
from database.career_db import CareerDatabase
from utils.nlp_utils import preprocess_text
from utils.sentiment import analyze_sentiment
from utils.pdf_generator import generate_career_plan_pdf

# Page configuration
st.set_page_config(
    page_title="AI Career Counselor",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        'name': '',
        'interests': [],
        'sentiment': 'neutral',
        'suggested_careers': []
    }
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'chat'
if 'selected_career' not in st.session_state:
    st.session_state.selected_career = None

# Initialize database connection
@st.cache_resource
def init_database():
    return CareerDatabase()

db = init_database()

# Sidebar navigation
with st.sidebar:
    st.title("🧠 AI Career Counselor")
    
    # Load and display animation
    lottie_animation = load_lottie_animation("https://assets5.lottiefiles.com/packages/lf20_khzniaya.json")
    streamlit_lottie.st_lottie(lottie_animation, height=200)
    
    st.markdown("### Navigation")
    nav_option = st.radio(
        "Choose a feature:",
        ["💬 Chat", "🧠 Personality Quiz", "📅 Weekly Tracker", "🎙️ Voice Chat", "📄 Resume Builder"]
    )
    
    # Map radio options to view names
    view_mapping = {
        "💬 Chat": "chat",
        "🧠 Personality Quiz": "quiz",
        "📅 Weekly Tracker": "tracker",
        "🎙️ Voice Chat": "voice",
        "📄 Resume Builder": "resume"
    }
    st.session_state.current_view = view_mapping[nav_option]
    
    # Display user profile if available
    if st.session_state.user_profile['name']:
        st.markdown("---")
        st.markdown("### Your Profile")
        st.markdown(f"**Name:** {st.session_state.user_profile['name']}")
        if st.session_state.user_profile['interests']:
            st.markdown(f"**Interests:** {', '.join(st.session_state.user_profile['interests'])}")
        
        # Reset button
        if st.button("Reset Session"):
            st.session_state.messages = []
            st.session_state.user_profile = {
                'name': '',
                'interests': [],
                'sentiment': 'neutral',
                'suggested_careers': []
            }
            st.session_state.selected_career = None
            st.experimental_rerun()

# Main content area
def main():
    # Display different views based on navigation
    if st.session_state.current_view == "chat":
        render_chat_view()
    elif st.session_state.current_view == "quiz":
        render_personality_quiz()
    elif st.session_state.current_view == "tracker":
        render_weekly_tracker()
    elif st.session_state.current_view == "voice":
        render_voice_chat()
    elif st.session_state.current_view == "resume":
        render_resume_builder()

def render_chat_view():
    # If a career is selected, show its roadmap
    if st.session_state.selected_career:
        career = db.get_career_by_title(st.session_state.selected_career)
        if career:
            render_roadmap(career)
            if st.button("← Back to Chat"):
                st.session_state.selected_career = None
                st.experimental_rerun()
        else:
            st.error(f"Could not find career details for '{st.session_state.selected_career}'. Please select a different career or try again.")
            if st.button("← Back to Chat"):
                st.session_state.selected_career = None
                st.experimental_rerun()
        return
    
    # Chat interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_chat_interface()
    
    with col2:
        # Show career cards if there are suggested careers
        if st.session_state.user_profile['suggested_careers']:
            render_career_cards(
                st.session_state.user_profile['suggested_careers'],
                on_view_roadmap=lambda career: set_selected_career(career),
                on_download_pdf=lambda career: download_career_plan(career)
            )

    # Accept user input outside of columns
    if prompt := st.chat_input("What's on your mind about your career?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            # Simulate stream of response with a typing indicator
            # In production, this would be replaced with the actual response from Rasa
            # response = send_message_to_rasa(prompt)

            # For now, we'll use a placeholder response
            response = "I understand you're interested in exploring career options. Could you tell me more about your interests and skills? This will help me provide more personalized guidance."

            # Simulate typing
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(0.05)
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

def set_selected_career(career_title):
    st.session_state.selected_career = career_title
    st.experimental_rerun()

def download_career_plan(career_title):
    career = db.get_career_by_title(career_title)
    pdf_path = generate_career_plan_pdf(career, st.session_state.user_profile)
    
    with open(pdf_path, "rb") as file:
        btn = st.download_button(
            label="Download Career Plan",
            data=file,
            file_name=f"{career_title.replace(' ', '_')}_career_plan.pdf",
            mime="application/pdf"
        )
    
    # Remove the temporary file
    os.remove(pdf_path)

def send_message_to_rasa(message_text):
    """Send a message to the Rasa server and get the response"""
    try:
        # Preprocess the text
        processed_text = preprocess_text(message_text)
        
        # Analyze sentiment
        sentiment = analyze_sentiment(message_text)
        st.session_state.user_profile['sentiment'] = sentiment
        
        # Send to Rasa
        rasa_url = "http://localhost:5005/webhooks/rest/webhook"
        response = requests.post(
            rasa_url,
            json={"sender": "user", "message": processed_text}
        )
        
        if response.status_code == 200:
            rasa_responses = response.json()
            if rasa_responses:
                # Extract the text responses
                texts = [resp.get("text", "") for resp in rasa_responses if "text" in resp]
                
                # Check for any custom payloads (like career suggestions)
                for resp in rasa_responses:
                    if "custom" in resp:
                        custom_data = json.loads(resp["custom"])
                        if "careers" in custom_data:
                            st.session_state.user_profile['suggested_careers'] = custom_data["careers"]
                        if "interests" in custom_data:
                            st.session_state.user_profile['interests'] = custom_data["interests"]
                        if "name" in custom_data:
                            st.session_state.user_profile['name'] = custom_data["name"]
                
                return " ".join(texts)
            return "I'm sorry, I didn't get a response. Could you try again?"
        else:
            return f"Error: Received status code {response.status_code} from Rasa server. Make sure the Rasa server is running."
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to the Rasa server. Make sure it's running at http://localhost:5005."
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    main()