# AI Career Counselor

An intelligent virtual career counselor that provides personalized career guidance, roadmaps, and actionable next steps based on user interests, emotions, and personality.

## 🧰 Tech Stack

| Component | Technology |
|-----------|------------|
| 💬 Chat Engine | Rasa (NLP) |
| 🧠 Text Processing | NLTK, TextBlob |
| 🖥️ Frontend UI | Streamlit |
| 🗂️ Database | SQLite3 |
| 📊 Data Handling | Pandas |
| 🎨 UI Animations | Lottie / Icons8 |
| ☁️ Deployment | Streamlit Cloud |

## 🔥 Core Features

### 🗣️ NLP-Powered Conversation
- Detects user intents like tech_interest, creative_mind, dream_job, confused_state, etc.
- Analyzes sentiment to detect if the user is motivated, unsure, or needs encouragement.
- Adapts tone dynamically based on user sentiment.

### 🎯 Career Recommendation Engine
- Recommends top 3 careers tailored to user interest + sentiment.
- Displays career title, average salary, required skills, and a clickable learning roadmap.

### 📊 Integrated Career Database (SQLite3)
- Stores user profiles and career metadata
- Supports dynamic retrieval of career information

### 🎨 Interactive Streamlit UI
- Chat-like interface for user interaction
- Career suggestion cards with animations/icons
- "View Roadmap" button for step-by-step career journey
- "Download Career Plan (PDF)" feature

## 🧩 Bonus Innovations
- 🧠 Personality Quiz
- 📅 Weekly Tracker
- 🎙️ Voice Chat Mode
- 📄 Resume Builder

## Getting Started

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up the Rasa model: `cd rasa && rasa train`
4. Run the Streamlit app: `streamlit run app.py`
5. In a separate terminal, run the Rasa server: `cd rasa && rasa run --enable-api`

## Project Structure

```
.
├── app.py                  # Main Streamlit application
├── database/
│   ├── career_db.py        # Database operations
│   ├── schema.sql          # Database schema
│   └── career_data.csv     # Initial career data
├── rasa/
│   ├── actions/            # Custom Rasa actions
│   ├── data/               # Training data
│   ├── config.yml          # Rasa configuration
│   └── domain.yml          # Rasa domain
├── utils/
│   ├── nlp_utils.py        # NLP processing utilities
│   ├── sentiment.py        # Sentiment analysis
│   └── pdf_generator.py    # PDF generation for career plans
└── ui/
    ├── components.py       # UI components
    └── animations.py       # UI animations
```
