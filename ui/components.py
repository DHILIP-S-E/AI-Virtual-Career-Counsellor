import streamlit as st
import pandas as pd
import time
from datetime import datetime
import json
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from database.career_db import CareerDatabase

def render_chat_interface():
    """Render the chat interface with message history and input box"""
    st.header("💬 Chat with AI Career Counselor")
    
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    

def render_career_cards(careers, on_view_roadmap=None, on_download_pdf=None):
    """Render career suggestion cards"""
    st.header("🎯 Recommended Careers")
    
    # Get career database
    db = CareerDatabase()
    
    for career_title in careers:
        career = db.get_career_by_title(career_title)
        if not career:
            continue
            
        with st.expander(f"**{career['title']}**", expanded=True):
            st.markdown(f"**Average Salary:** ${career['salary']:,}/year")
            st.markdown("**Required Skills:**")
            for skill in career['skills']:
                st.markdown(f"- {skill}")
            
            col1, col2 = st.columns(2)
            with col1:
                if on_view_roadmap:
                    if st.button(f"View Roadmap", key=f"roadmap_{career['title']}"):
                        on_view_roadmap(career['title'])
            with col2:
                if on_download_pdf:
                    if st.button(f"Download Plan (PDF)", key=f"pdf_{career['title']}"):
                        on_download_pdf(career['title'])

def render_roadmap(career):
    """Render a career roadmap with steps"""
    st.header(f"🗺️ Career Roadmap: {career['title']}")
    
    st.markdown(f"""
    ### About this Career
    {career['description']}
    
    **Average Salary:** ${career['salary']:,}/year
    
    **Required Skills:** {', '.join(career['skills'])}
    """)
    
    st.markdown("### Your Learning Path")
    
    for i, step in enumerate(career['roadmap']):
        with st.container():
            col1, col2 = st.columns([1, 10])
            with col1:
                st.markdown(f"### {i+1}")
            with col2:
                st.markdown(f"### {step['title']}")
                st.markdown(step['description'])
                
                if 'resources' in step and step['resources']:
                    st.markdown("**Resources:**")
                    for resource in step['resources']:
                        st.markdown(f"- [{resource['title']}]({resource['url']})")
    
    st.markdown("---")
    st.markdown("### Next Steps")
    st.markdown("""
    1. Set specific goals for each step in the roadmap
    2. Join communities related to this field
    3. Find mentors who can guide you
    4. Start building a portfolio of projects
    """)

def render_personality_quiz():
    """Render the personality quiz interface"""
    st.header("🧠 Career Personality Quiz")
    
    st.markdown("""
    This quiz will help identify career paths that match your personality and preferences.
    Answer the following questions to get personalized career recommendations.
    """)
    
    with st.form("personality_quiz"):
        st.markdown("### Work Style")
        work_style = st.radio(
            "How do you prefer to work?",
            ["Independently with focus on personal tasks", 
             "Collaboratively in a team environment",
             "Mix of both independent and team work",
             "Leading and directing others"]
        )
        
        st.markdown("### Problem Solving")
        problem_solving = st.radio(
            "When faced with a problem, you typically:",
            ["Analyze data and facts methodically",
             "Brainstorm creative solutions",
             "Seek input from others before deciding",
             "Trust your intuition and experience"]
        )
        
        st.markdown("### Work Environment")
        work_environment = st.radio(
            "What type of work environment energizes you?",
            ["Structured with clear rules and processes",
             "Creative and flexible",
             "Fast-paced with changing priorities",
             "Stable and predictable"]
        )
        
        st.markdown("### Career Values")
        career_values = st.multiselect(
            "Select the values most important to you in a career (choose up to 3):",
            ["Financial security", "Work-life balance", "Making a difference", 
             "Recognition and prestige", "Continuous learning", "Creativity and innovation",
             "Leadership opportunities", "Independence and autonomy"],
            max_selections=3
        )
        
        st.markdown("### Skills Assessment")
        technical_skills = st.slider("Rate your technical/analytical skills:", 1, 10, 5)
        creative_skills = st.slider("Rate your creative/artistic skills:", 1, 10, 5)
        people_skills = st.slider("Rate your interpersonal/communication skills:", 1, 10, 5)
        
        submitted = st.form_submit_button("Get Career Recommendations")
        
        if submitted:
            st.success("Quiz completed! Based on your responses, here are your recommended career paths:")

            # This would normally use a more sophisticated algorithm
            # For now, we'll use a simple mapping based on highest skills
            skills = {
                "technical": technical_skills,
                "creative": creative_skills,
                "people": people_skills
            }

            top_skill = max(skills, key=skills.get)

            if top_skill == "technical":
                careers = ["Data Scientist", "Software Engineer", "Systems Analyst"]
            elif top_skill == "creative":
                careers = ["UX Designer", "Content Creator", "Digital Marketing Specialist"]
            else:  # people skills
                careers = ["Human Resources Manager", "Sales Executive", "Customer Success Manager"]

            # Update session state with suggested careers
            st.session_state.user_profile['suggested_careers'] = careers

    # Display career cards outside of the form if there are suggested careers
    if st.session_state.user_profile.get('suggested_careers'):
        render_career_cards(
            st.session_state.user_profile['suggested_careers'],
            on_view_roadmap=lambda career: st.session_state.update({"selected_career": career, "current_view": "chat"}),
            on_download_pdf=lambda career: st.write(f"Download PDF for {career} (functionality to be implemented)")
        )

def render_weekly_tracker():
    """Render the weekly learning goal tracker"""
    st.header("📅 Weekly Learning Tracker")
    
    # Initialize weekly goals in session state if not present
    if 'weekly_goals' not in st.session_state:
        st.session_state.weekly_goals = []
    
    # Form to add new goals
    with st.form("add_goal"):
        st.subheader("Add New Learning Goal")
        goal_title = st.text_input("Goal Title")
        goal_description = st.text_area("Description")
        goal_deadline = st.date_input("Target Completion Date")
        goal_category = st.selectbox(
            "Category",
            ["Technical Skill", "Soft Skill", "Education", "Project", "Other"]
        )
        
        submitted = st.form_submit_button("Add Goal")
        if submitted and goal_title:
            # Add new goal to the list
            st.session_state.weekly_goals.append({
                "title": goal_title,
                "description": goal_description,
                "deadline": goal_deadline.strftime("%Y-%m-%d"),
                "category": goal_category,
                "completed": False,
                "created_at": datetime.now().strftime("%Y-%m-%d")
            })
            st.success(f"Goal '{goal_title}' added successfully!")
    
    # Display existing goals
    if st.session_state.weekly_goals:
        st.subheader("Your Learning Goals")
        
        # Filter options
        filter_status = st.radio("Filter by status:", ["All", "Completed", "In Progress"], horizontal=True)
        
        # Apply filters
        filtered_goals = st.session_state.weekly_goals
        if filter_status == "Completed":
            filtered_goals = [g for g in filtered_goals if g["completed"]]
        elif filter_status == "In Progress":
            filtered_goals = [g for g in filtered_goals if not g["completed"]]
        
        # Display goals
        for i, goal in enumerate(filtered_goals):
            with st.expander(f"{goal['title']} ({goal['category']})", expanded=True):
                st.write(f"**Description:** {goal['description']}")
                st.write(f"**Deadline:** {goal['deadline']}")
                
                # Toggle completion status
                completed = st.checkbox("Mark as completed", value=goal["completed"], key=f"goal_{i}")
                
                # Update the goal's completion status
                if completed != goal["completed"]:
                    st.session_state.weekly_goals[i]["completed"] = completed
                    st.experimental_rerun()
                
                # Delete goal
                if st.button("Delete Goal", key=f"delete_{i}"):
                    st.session_state.weekly_goals.pop(i)
                    st.experimental_rerun()
    else:
        st.info("You haven't added any learning goals yet. Use the form above to add your first goal!")

def render_voice_chat():
    """Render the voice chat interface"""
    st.header("🎙️ Voice Chat Mode")
    
    st.markdown("""
    Use voice commands to interact with the AI Career Counselor.
    Click the microphone button and speak your question or request.
    """)
    
    # This is a placeholder for the actual voice chat functionality
    # In a real implementation, this would use browser APIs for speech recognition
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.text_area("Recognized Speech", value="", height=100, disabled=True, 
                    key="speech_text", placeholder="Your speech will appear here...")
    
    with col2:
        st.button("🎙️ Start Recording", use_container_width=True)
        st.button("⏹️ Stop Recording", use_container_width=True)
    
    st.info("Note: Voice chat functionality requires browser permissions and is currently a placeholder. In a full implementation, this would use the Web Speech API or a similar technology.")

def render_resume_builder():
    """Render the resume builder interface"""
    st.header("📄 Resume Builder")
    
    st.markdown("""
    Build a professional resume tailored to your target career.
    Fill in the sections below and get keyword suggestions based on your chosen career path.
    """)
    
    # Career selection for keyword targeting
    target_career = st.selectbox(
        "Target Career (for keyword optimization)",
        ["Software Developer", "Data Scientist", "UX Designer", "Product Manager", 
         "Digital Marketing Specialist", "Business Analyst", "Other"]
    )
    
    # Resume sections
    with st.form("resume_form"):
        st.subheader("Personal Information")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name")
            email = st.text_input("Email")
        with col2:
            phone = st.text_input("Phone")
            location = st.text_input("Location")
        
        st.subheader("Professional Summary")
        summary = st.text_area("Write a brief professional summary")
        
        # Show keyword suggestions based on selected career
        if target_career:
            st.info(f"Suggested keywords for {target_career}: " + get_resume_keywords(target_career))
        
        st.subheader("Work Experience")
        exp_company = st.text_input("Company Name")
        exp_title = st.text_input("Job Title")
        exp_dates = st.text_input("Employment Dates (e.g., Jan 2020 - Present)")
        exp_description = st.text_area("Job Description and Achievements")
        
        st.subheader("Education")
        edu_institution = st.text_input("Institution Name")
        edu_degree = st.text_input("Degree/Certificate")
        edu_dates = st.text_input("Dates (e.g., 2016 - 2020)")
        
        st.subheader("Skills")
        skills = st.text_area("List your relevant skills (comma separated)")
        
        submitted = st.form_submit_button("Generate Resume")
        
        if submitted:
            st.success("Resume generated! In a full implementation, this would create a formatted PDF resume.")
            
            # Display a preview of the resume
            st.subheader("Resume Preview")
            st.markdown(f"""
            # {name}
            {email} | {phone} | {location}
            
            ## Professional Summary
            {summary}
            
            ## Work Experience
            **{exp_title}** at {exp_company}  
            {exp_dates}  
            {exp_description}
            
            ## Education
            **{edu_degree}**  
            {edu_institution}, {edu_dates}
            
            ## Skills
            {skills}
            """)

def get_resume_keywords(career):
    """Return suggested keywords for a specific career"""
    keywords = {
        "Software Developer": "Python, JavaScript, API development, Git, CI/CD, agile methodology, full-stack, problem-solving",
        "Data Scientist": "Python, R, machine learning, statistical analysis, data visualization, SQL, big data, predictive modeling",
        "UX Designer": "user research, wireframing, prototyping, usability testing, Figma, Adobe XD, user-centered design, information architecture",
        "Product Manager": "product strategy, roadmapping, user stories, market research, stakeholder management, agile, KPIs, product lifecycle",
        "Digital Marketing Specialist": "SEO, SEM, content marketing, social media, Google Analytics, email campaigns, conversion optimization, A/B testing",
        "Business Analyst": "requirements gathering, data analysis, SQL, process modeling, stakeholder interviews, documentation, problem-solving, JIRA"
    }
    
    return keywords.get(career, "leadership, communication, teamwork, problem-solving, analytical thinking")