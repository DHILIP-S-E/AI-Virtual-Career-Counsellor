import sqlite3
import os
import json
import pandas as pd
from typing import List, Dict, Any, Optional, Union
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CareerDatabase:
    """Class to handle all database operations for the AI Career Counselor"""
    
    def __init__(self, db_path: str = "database/career_counselor.db"):
        """
        Initialize the database connection
        
        Args:
            db_path: Path to the SQLite database file
        """
        # Ensure the database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.conn = None
        
        # Initialize the database
        self._initialize_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a connection to the database"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            # Enable foreign keys
            self.conn.execute("PRAGMA foreign_keys = ON")
            # Configure connection to return rows as dictionaries
            self.conn.row_factory = sqlite3.Row
        return self.conn
        
    def _initialize_db(self) -> None:
        """Initialize the database with schema and sample data"""
        try:
            conn = self._get_connection()
            
            # Check if the database is already initialized
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='careers'")
            if cursor.fetchone() is not None:
                logger.info("Database already initialized")
                return
            
            # Execute schema.sql to create tables
            with open(os.path.join(os.path.dirname(__file__), "schema.sql"), "r") as f:
                schema_sql = f.read()
                conn.executescript(schema_sql)
            
            # Load sample data from CSV
            self._load_sample_data()
            
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
            
    def _load_sample_data(self) -> None:
        """Load sample career data from CSV file"""
        try:
            # Read the CSV file
            csv_path = os.path.join(os.path.dirname(__file__), "career_data.csv")
            career_data = pd.read_csv(csv_path)
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Insert career fields
            unique_fields = career_data["field"].unique()
            for field in unique_fields:
                cursor.execute(
                    "INSERT INTO career_fields (name, description) VALUES (?, ?)",
                    (field, f"Career field related to {field}")
                )
            
            # Insert careers and related data
            for _, row in career_data.iterrows():
                # Get the field_id
                cursor.execute("SELECT id FROM career_fields WHERE name = ?", (row["field"],))
                field_id = cursor.fetchone()[0]
                
                # Insert career
                cursor.execute(
                    """
                    INSERT INTO careers (title, field_id, description, salary, growth_rate, education_level)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (row["title"], field_id, row["description"], row["salary"], 
                     row["growth_rate"], row["education_level"])
                )
                career_id = cursor.lastrowid
                
                # Insert skills
                skills = row["skills"].split(",")
                for i, skill in enumerate(skills):
                    cursor.execute(
                        "INSERT INTO career_skills (career_id, skill, importance) VALUES (?, ?, ?)",
                        (career_id, skill.strip(), 10 - i)  # Higher importance for earlier skills
                    )
                
                # Insert roadmap steps
                roadmap = json.loads(row["roadmap"])
                for i, step in enumerate(roadmap):
                    cursor.execute(
                        """
                        INSERT INTO roadmap_steps (career_id, step_order, title, description, duration)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (career_id, i+1, step["title"], step["description"], step["duration"])
                    )
                    step_id = cursor.lastrowid
                    
                    # Insert resources for this step
                    if "resources" in step:
                        for resource in step["resources"]:
                            cursor.execute(
                                """
                                INSERT INTO learning_resources 
                                (step_id, title, url, resource_type, is_free)
                                VALUES (?, ?, ?, ?, ?)
                                """,
                                (step_id, resource["title"], resource["url"], 
                                 resource["type"], resource["is_free"])
                            )
            
            conn.commit()
            logger.info("Sample data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading sample data: {str(e)}")
            raise
            
    def get_career_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Get career details by title
        
        Args:
            title: The title of the career
            
        Returns:
            Dictionary with career details or None if not found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get basic career info
            cursor.execute("""
                SELECT c.*, cf.name as field_name
                FROM careers c
                JOIN career_fields cf ON c.field_id = cf.id
                WHERE c.title = ?
            """, (title,))
            
            career_row = cursor.fetchone()
            if not career_row:
                return None
                
            # Convert to dictionary
            career = dict(career_row)
            
            # Get skills
            cursor.execute("""
                SELECT skill FROM career_skills
                WHERE career_id = ?
                ORDER BY importance DESC
            """, (career["id"],))
            
            career["skills"] = [row["skill"] for row in cursor.fetchall()]
            
            # Get roadmap steps
            cursor.execute("""
                SELECT rs.*, 
                       (SELECT json_group_array(json_object(
                           'title', lr.title,
                           'url', lr.url,
                           'type', lr.resource_type,
                           'is_free', lr.is_free
                       ))
                       FROM learning_resources lr
                       WHERE lr.step_id = rs.id) as resources
                FROM roadmap_steps rs
                WHERE rs.career_id = ?
                ORDER BY rs.step_order
            """, (career["id"],))
            
            roadmap_steps = []
            for step in cursor.fetchall():
                step_dict = dict(step)
                if step_dict["resources"]:
                    step_dict["resources"] = json.loads(step_dict["resources"])
                else:
                    step_dict["resources"] = []
                roadmap_steps.append(step_dict)
                
            career["roadmap"] = roadmap_steps
            
            return career
        except Exception as e:
            logger.error(f"Error getting career by title: {str(e)}")
            return None
            
    def search_careers(self, keywords: List[str], limit: int = 3) -> List[Dict[str, Any]]:
        """
        Search for careers based on keywords
        
        Args:
            keywords: List of keywords to search for
            limit: Maximum number of results to return
            
        Returns:
            List of career dictionaries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Build the query with multiple LIKE conditions
            query_conditions = []
            query_params = []
            
            for keyword in keywords:
                keyword_param = f"%{keyword}%"
                query_conditions.append("""
                    (c.title LIKE ? OR 
                     c.description LIKE ? OR 
                     cf.name LIKE ? OR 
                     EXISTS (SELECT 1 FROM career_skills cs WHERE cs.career_id = c.id AND cs.skill LIKE ?))
                """)
                query_params.extend([keyword_param, keyword_param, keyword_param, keyword_param])
            
            query = f"""
                SELECT c.title, c.salary, cf.name as field_name, c.description
                FROM careers c
                JOIN career_fields cf ON c.field_id = cf.id
                WHERE {" OR ".join(query_conditions)}
                GROUP BY c.id
                ORDER BY COUNT(*) DESC
                LIMIT ?
            """
            query_params.append(limit)
            
            cursor.execute(query, query_params)
            
            careers = []
            for row in cursor.fetchall():
                career = dict(row)
                # Get the full career details
                full_career = self.get_career_by_title(career["title"])
                if full_career:
                    careers.append(full_career)
            
            return careers
        except Exception as e:
            logger.error(f"Error searching careers: {str(e)}")
            return []
            
    def add_user(self, name: str, email: str) -> Optional[int]:
        """
        Add a new user to the database
        
        Args:
            name: User's name
            email: User's email
            
        Returns:
            User ID if successful, None otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                (name, email)
            )
            
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error adding user: {str(e)}")
            return None
            
    def add_user_interest(self, user_id: int, interest: str) -> bool:
        """
        Add a user interest
        
        Args:
            user_id: User ID
            interest: Interest to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO user_interests (user_id, interest) VALUES (?, ?)",
                (user_id, interest)
            )
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding user interest: {str(e)}")
            return False
            
    def add_user_sentiment(self, user_id: int, sentiment: str) -> bool:
        """
        Add a user sentiment record
        
        Args:
            user_id: User ID
            sentiment: Sentiment value (positive, neutral, negative)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO user_sentiment (user_id, sentiment) VALUES (?, ?)",
                (user_id, sentiment)
            )
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding user sentiment: {str(e)}")
            return False
            
    def add_chat_message(self, user_id: int, message: str, role: str) -> bool:
        """
        Add a chat message to the history
        
        Args:
            user_id: User ID
            message: Message text
            role: 'user' or 'assistant'
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO chat_history (user_id, message, role) VALUES (?, ?, ?)",
                (user_id, message, role)
            )
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding chat message: {str(e)}")
            return False
            
    def add_career_suggestion(self, user_id: int, career_id: int, relevance_score: float) -> bool:
        """
        Add a career suggestion for a user
        
        Args:
            user_id: User ID
            career_id: Career ID
            relevance_score: Relevance score (0-1)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO user_career_suggestions (user_id, career_id, relevance_score) VALUES (?, ?, ?)",
                (user_id, career_id, relevance_score)
            )
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding career suggestion: {str(e)}")
            return False
            
    def add_learning_goal(self, user_id: int, title: str, description: str, 
                         category: str, deadline: str) -> bool:
        """
        Add a learning goal for a user
        
        Args:
            user_id: User ID
            title: Goal title
            description: Goal description
            category: Goal category
            deadline: Goal deadline (YYYY-MM-DD)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO learning_goals 
                (user_id, title, description, category, deadline) 
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, title, description, category, deadline)
            )
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding learning goal: {str(e)}")
            return False
            
    def add_personality_result(self, user_id: int, technical_score: int, creative_score: int,
                              people_score: int, analytical_score: int, leadership_score: int,
                              detail_oriented_score: int) -> bool:
        """
        Add personality quiz results for a user
        
        Args:
            user_id: User ID
            technical_score: Technical aptitude score
            creative_score: Creative aptitude score
            people_score: People skills score
            analytical_score: Analytical thinking score
            leadership_score: Leadership aptitude score
            detail_oriented_score: Detail orientation score
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO personality_results 
                (user_id, technical_score, creative_score, people_score, 
                analytical_score, leadership_score, detail_oriented_score) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, technical_score, creative_score, people_score, 
                analytical_score, leadership_score, detail_oriented_score)
            )
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding personality results: {str(e)}")
            return False