-- Schema for AI Career Counselor Database

-- Users table to store user profiles
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User interests table
CREATE TABLE IF NOT EXISTS user_interests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    interest TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- User sentiment history
CREATE TABLE IF NOT EXISTS user_sentiment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    sentiment TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Chat history
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message TEXT,
    role TEXT,  -- 'user' or 'assistant'
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Career fields
CREATE TABLE IF NOT EXISTS career_fields (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    description TEXT
);

-- Careers table
CREATE TABLE IF NOT EXISTS careers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT UNIQUE,
    field_id INTEGER,
    description TEXT,
    salary INTEGER,
    growth_rate REAL,
    education_level TEXT,
    FOREIGN KEY (field_id) REFERENCES career_fields(id)
);

-- Career skills
CREATE TABLE IF NOT EXISTS career_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    career_id INTEGER,
    skill TEXT,
    importance INTEGER,  -- 1-10 scale
    FOREIGN KEY (career_id) REFERENCES careers(id)
);

-- Career roadmap steps
CREATE TABLE IF NOT EXISTS roadmap_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    career_id INTEGER,
    step_order INTEGER,
    title TEXT,
    description TEXT,
    duration TEXT,  -- e.g., "3 months", "1 year"
    FOREIGN KEY (career_id) REFERENCES careers(id)
);

-- Learning resources for roadmap steps
CREATE TABLE IF NOT EXISTS learning_resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    step_id INTEGER,
    title TEXT,
    url TEXT,
    resource_type TEXT,  -- e.g., "course", "book", "video"
    is_free BOOLEAN,
    FOREIGN KEY (step_id) REFERENCES roadmap_steps(id)
);

-- User career suggestions
CREATE TABLE IF NOT EXISTS user_career_suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    career_id INTEGER,
    suggested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    relevance_score REAL,  -- 0-1 scale
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (career_id) REFERENCES careers(id)
);

-- Weekly learning goals
CREATE TABLE IF NOT EXISTS learning_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT,
    description TEXT,
    category TEXT,
    deadline DATE,
    completed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Personality quiz results
CREATE TABLE IF NOT EXISTS personality_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    technical_score INTEGER,
    creative_score INTEGER,
    people_score INTEGER,
    analytical_score INTEGER,
    leadership_score INTEGER,
    detail_oriented_score INTEGER,
    taken_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);