from sqlalchemy import (
    create_engine, MetaData, Table, Column,
    Integer, String, Text, ForeignKey, Boolean, JSON, DateTime, Float
)
from sqlalchemy.sql import func
import aiosqlite
import secrets
from datetime import datetime, timedelta
from utility import Utility


DATABASE_URL = "sqlite:///./hackathon.db"
metadata = MetaData()

users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, unique=True, nullable=False),
    Column("password", String, nullable=False),
    Column("name", String),
    Column("token", String, unique=True, nullable=True),  
    Column("is_admin", Boolean, default=False),
    Column("is_verified", Boolean, default=False),
    Column("created_at", DateTime, default=func.now())
)

# Lessons table
lessons = Table(
    "lessons", metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
    Column("description", Text),
    Column("difficulty", String),  # beginner, intermediate, advanced
    Column("content", Text),
    Column("order_index", Integer),
    Column("created_at", DateTime, default=func.now())
)

# Quizzes table
quizzes = Table(
    "quizzes", metadata,
    Column("id", Integer, primary_key=True),
    Column("lesson_id", Integer, ForeignKey("lessons.id")),
    Column("title", String),
    Column("questions", JSON),  # Store as JSON array
    Column("total_points", Integer, default=100),
    Column("created_at", DateTime, default=func.now())
)

# Quiz submissions table
quiz_submissions = Table(
    "quiz_submissions", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("quiz_id", Integer, ForeignKey("quizzes.id")),
    Column("lesson_id", Integer, ForeignKey("lessons.id")),
    Column("answers", JSON),  # User's answers
    Column("score", Float),
    Column("max_score", Float),
    Column("completed", Boolean, default=True),
    Column("submitted_at", DateTime, default=func.now())
)

# Progress table
progress = Table(
    "progress", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("lesson_id", Integer, ForeignKey("lessons.id")),
    Column("completed", Boolean, default=False),
    Column("completion_percentage", Float, default=0.0),
    Column("time_spent", Integer, default=0),  # in minutes
    Column("last_accessed", DateTime, default=func.now()),
    Column("created_at", DateTime, default=func.now())
)

# AI chat logs table
ai_chat_logs = Table(
    "ai_chat_logs", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("message", Text),
    Column("response", Text),
    Column("created_at", DateTime, default=func.now())
)

# AI interactions table (explain, optimize, debug)
ai_interactions = Table(
    "ai_interactions", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("type", String),  # explain, optimize, debug
    Column("input_code", Text),
    Column("output", Text),
    Column("language", String, default="python"),
    Column("created_at", DateTime, default=func.now())
)

# AI hints table
ai_hints = Table(
    "ai_hints", metadata,
    Column("id", Integer, primary_key=True),
    Column("lesson_id", Integer, ForeignKey("lessons.id")),
    Column("hint_text", Text),
    Column("difficulty_level", Integer, default=1),  # 1=easy, 2=medium, 3=hard
    Column("created_at", DateTime, default=func.now())
)

# Code evaluation logs table
code_evaluations = Table(
    "code_evaluations", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("lesson_id", Integer, ForeignKey("lessons.id"), nullable=True),
    Column("code", Text),
    Column("output", Text),
    Column("error", Text, nullable=True),
    Column("execution_time", Float),
    Column("language", String, default="python"),
    Column("created_at", DateTime, default=func.now())
)

# User sessions table
user_sessions = Table(
    "user_sessions", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("session_token", String, unique=True),
    Column("expires_at", DateTime),
    Column("created_at", DateTime, default=func.now())
)

# DB Engine (for table creation)
engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

# ---------- Async DB Operations ----------

class DatabaseManager:
    def __init__(self):
        self.db_path = "./hackathon.db"
    
    async def execute_query(self, query, params=None):
        async with aiosqlite.connect(self.db_path) as db:
            if params:
                cursor = await db.execute(query, params)
            else:
                cursor = await db.execute(query)
            await db.commit()
            return cursor.lastrowid
    
    async def fetch_one(self, query, params=None):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if params:
                cursor = await db.execute(query, params)
            else:
                cursor = await db.execute(query)
            return await cursor.fetchone()
    
    async def fetch_all(self, query, params=None):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if params:
                cursor = await db.execute(query, params)
            else:
                cursor = await db.execute(query)
            return await cursor.fetchall()

db_manager = DatabaseManager()

# ---------- USER OPERATIONS ----------

async def register_user(email, password, name="", token=None):
    """Register a new user"""
    query = "INSERT INTO users (email, password, name, token) VALUES (?, ?, ?, ?)"
    return await db_manager.execute_query(query, (email, password, name, token))

async def login_user(email, password):
    """Get user token by email and password for login"""
    query = "SELECT password, token FROM users WHERE email = ?"
    row = await db_manager.fetch_one(query, (email,))
    
    if not row:
        return None
    
    hashed_pwd = row["password"]
    if not hashed_pwd:
        return None
    
    if Utility.pwd_match(password, hashed_password=hashed_pwd):
        return row["token"]
    return None

async def get_user(email):
    """Check if user exists by email"""
    query = "SELECT id FROM users WHERE email = ?"
    row = await db_manager.fetch_one(query, (email,))
    return row is not None

async def get_user_by_token(token):
    """Get user by token"""
    query = "SELECT * FROM users WHERE token = ?"
    return await db_manager.fetch_one(query, (token,))

async def get_user_by_id(user_id):
    """Get user by ID"""
    query = "SELECT * FROM users WHERE id = ?"
    return await db_manager.fetch_one(query, (user_id,))

async def update_user_profile(user_id, name=None, email=None):
    """Update user profile"""
    if name and email:
        query = "UPDATE users SET name = ?, email = ? WHERE id = ?"
        params = (name, email, user_id)
    elif name:
        query = "UPDATE users SET name = ? WHERE id = ?"
        params = (name, user_id)
    elif email:
        query = "UPDATE users SET email = ? WHERE id = ?"
        params = (email, user_id)
    else:
        return None
    return await db_manager.execute_query(query, params)

async def update_user_password(user_id, new_password):
    """Update user password"""
    query = "UPDATE users SET password = ? WHERE id = ?"
    return await db_manager.execute_query(query, (new_password, user_id))

async def verify_user(user_id):
    """Verify user account"""
    query = "UPDATE users SET is_verified = ? WHERE id = ?"
    return await db_manager.execute_query(query, (True, user_id))

# ---------- ADMIN OPERATIONS ----------

async def get_all_users():
    """Get all users (admin only)"""
    query = "SELECT id, email, name, is_admin, is_verified, created_at FROM users ORDER BY created_at DESC"
    return await db_manager.fetch_all(query)

async def make_user_admin(user_id):
    """Make user an admin"""
    query = "UPDATE users SET is_admin = ? WHERE id = ?"
    return await db_manager.execute_query(query, (True, user_id))

async def remove_user_admin(user_id):
    """Remove admin privileges from user"""
    query = "UPDATE users SET is_admin = ? WHERE id = ?"
    return await db_manager.execute_query(query, (False, user_id))

async def delete_user(user_id):
    """Delete user account (admin only)"""
    query = "DELETE FROM users WHERE id = ?"
    return await db_manager.execute_query(query, (user_id,))

async def ban_user(user_id):
    """Ban user by setting is_verified to False"""
    query = "UPDATE users SET is_verified = ? WHERE id = ?"
    return await db_manager.execute_query(query, (False, user_id))

# ---------- LESSON OPERATIONS ----------

async def get_all_lessons():
    """Get all lessons"""
    query = "SELECT * FROM lessons ORDER BY order_index"
    return await db_manager.fetch_all(query)

async def get_lesson_by_id(lesson_id):
    """Get lesson by ID"""
    query = "SELECT * FROM lessons WHERE id = ?"
    return await db_manager.fetch_one(query, (lesson_id,))

async def create_lesson(title, description, difficulty, content, order_index):
    """Create new lesson (admin only)"""
    query = """INSERT INTO lessons (title, description, difficulty, content, order_index) 
               VALUES (?, ?, ?, ?, ?)"""
    return await db_manager.execute_query(query, (title, description, difficulty, content, order_index))

async def update_lesson(lesson_id, title=None, description=None, difficulty=None, content=None, order_index=None):
    """Update lesson (admin only)"""
    updates = []
    params = []
    
    if title:
        updates.append("title = ?")
        params.append(title)
    if description:
        updates.append("description = ?")
        params.append(description)
    if difficulty:
        updates.append("difficulty = ?")
        params.append(difficulty)
    if content:
        updates.append("content = ?")
        params.append(content)
    if order_index is not None:
        updates.append("order_index = ?")
        params.append(order_index)
    
    if not updates:
        return None
        
    params.append(lesson_id)
    query = f"UPDATE lessons SET {', '.join(updates)} WHERE id = ?"
    return await db_manager.execute_query(query, params)

async def delete_lesson(lesson_id):
    """Delete lesson (admin only)"""
    query = "DELETE FROM lessons WHERE id = ?"
    return await db_manager.execute_query(query, (lesson_id,))

# ---------- QUIZ OPERATIONS ----------

async def get_quiz(lesson_id):
    """Get quiz by lesson ID"""
    query = "SELECT * FROM quizzes WHERE lesson_id = ?"
    return await db_manager.fetch_one(query, (lesson_id,))

async def create_quiz(lesson_id, title, questions, total_points=100):
    """Create new quiz (admin only)"""
    query = """INSERT INTO quizzes (lesson_id, title, questions, total_points) 
               VALUES (?, ?, ?, ?)"""
    return await db_manager.execute_query(query, (lesson_id, title, questions, total_points))

async def update_quiz(quiz_id, title=None, questions=None, total_points=None):
    """Update quiz (admin only)"""
    updates = []
    params = []
    
    if title:
        updates.append("title = ?")
        params.append(title)
    if questions:
        updates.append("questions = ?")
        params.append(questions)
    if total_points:
        updates.append("total_points = ?")
        params.append(total_points)
    
    if not updates:
        return None
        
    params.append(quiz_id)
    query = f"UPDATE quizzes SET {', '.join(updates)} WHERE id = ?"
    return await db_manager.execute_query(query, params)

async def submit_quiz(user_id, quiz_id, lesson_id, answers, score, max_score):
    """Submit quiz answers"""
    query = """INSERT INTO quiz_submissions 
               (user_id, quiz_id, lesson_id, answers, score, max_score) 
               VALUES (?, ?, ?, ?, ?, ?)"""
    return await db_manager.execute_query(query, (user_id, quiz_id, lesson_id, answers, score, max_score))

async def get_user_quiz_submissions(user_id):
    """Get all quiz submissions for a user"""
    query = "SELECT * FROM quiz_submissions WHERE user_id = ? ORDER BY submitted_at DESC"
    return await db_manager.fetch_all(query, (user_id,))

# ---------- PROGRESS OPERATIONS ----------

async def save_progress(user_id, lesson_id, completed=False, completion_percentage=0.0, time_spent=0):
    """Save user progress"""
    query = """INSERT OR REPLACE INTO progress 
               (user_id, lesson_id, completed, completion_percentage, time_spent, last_accessed) 
               VALUES (?, ?, ?, ?, ?, datetime('now'))"""
    return await db_manager.execute_query(query, (user_id, lesson_id, completed, completion_percentage, time_spent))

async def get_progress(user_id):
    """Get user progress"""
    query = "SELECT * FROM progress WHERE user_id = ?"
    return await db_manager.fetch_all(query, (user_id,))

async def get_lesson_progress(user_id, lesson_id):
    """Get specific lesson progress"""
    query = "SELECT * FROM progress WHERE user_id = ? AND lesson_id = ?"
    return await db_manager.fetch_one(query, (user_id, lesson_id))

# ---------- AI OPERATIONS ----------

async def save_chat_message(user_id, message, response):
    """Save AI chat message"""
    query = "INSERT INTO ai_chat_logs (user_id, message, response) VALUES (?, ?, ?)"
    return await db_manager.execute_query(query, (user_id, message, response))

async def get_user_chat_history(user_id, limit=50):
    """Get user chat history"""
    query = "SELECT * FROM ai_chat_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT ?"
    return await db_manager.fetch_all(query, (user_id, limit))

async def log_ai_interaction(user_id, type_, input_code, output, language="python"):
    """Log AI interaction"""
    query = """INSERT INTO ai_interactions 
               (user_id, type, input_code, output, language) 
               VALUES (?, ?, ?, ?, ?)"""
    return await db_manager.execute_query(query, (user_id, type_, input_code, output, language))

async def get_user_ai_interactions(user_id):
    """Get user AI interactions"""
    query = "SELECT * FROM ai_interactions WHERE user_id = ? ORDER BY created_at DESC"
    return await db_manager.fetch_all(query, (user_id,))

# ---------- HINTS OPERATIONS ----------

async def get_hint(hint_id):
    """Get hint by ID"""
    query = "SELECT * FROM ai_hints WHERE id = ?"
    return await db_manager.fetch_one(query, (hint_id,))

async def get_hints_by_lesson(lesson_id):
    """Get hints for a lesson"""
    query = "SELECT * FROM ai_hints WHERE lesson_id = ? ORDER BY difficulty_level"
    return await db_manager.fetch_all(query, (lesson_id,))

async def create_hint(lesson_id, hint_text, difficulty_level=1):
    """Create new hint (admin only)"""
    query = "INSERT INTO ai_hints (lesson_id, hint_text, difficulty_level) VALUES (?, ?, ?)"
    return await db_manager.execute_query(query, (lesson_id, hint_text, difficulty_level))

# ---------- CODE EVALUATION ----------

async def log_code_evaluation(user_id, code, output, error=None, execution_time=0.0, lesson_id=None, language="python"):
    """Log code evaluation"""
    query = """INSERT INTO code_evaluations 
               (user_id, lesson_id, code, output, error, execution_time, language) 
               VALUES (?, ?, ?, ?, ?, ?, ?)"""
    return await db_manager.execute_query(query, (user_id, lesson_id, code, output, error, execution_time, language))

async def get_user_code_evaluations(user_id):
    """Get user code evaluations"""
    query = "SELECT * FROM code_evaluations WHERE user_id = ? ORDER BY created_at DESC"
    return await db_manager.fetch_all(query, (user_id,))

# ---------- ANALYTICS (ADMIN) ----------

async def get_user_stats():
    """Get user statistics (admin only)"""
    query = """SELECT 
                COUNT(*) as total_users,
                COUNT(CASE WHEN is_verified = 1 THEN 1 END) as verified_users,
                COUNT(CASE WHEN is_admin = 1 THEN 1 END) as admin_users
               FROM users"""
    return await db_manager.fetch_one(query)

async def get_lesson_stats():
    """Get lesson statistics (admin only)"""
    query = """SELECT 
                COUNT(*) as total_lessons,
                COUNT(CASE WHEN difficulty = 'beginner' THEN 1 END) as beginner_lessons,
                COUNT(CASE WHEN difficulty = 'intermediate' THEN 1 END) as intermediate_lessons,
                COUNT(CASE WHEN difficulty = 'advanced' THEN 1 END) as advanced_lessons
               FROM lessons"""
    return await db_manager.fetch_one(query)

async def get_progress_stats():
    """Get progress statistics (admin only)"""
    query = """SELECT 
                COUNT(*) as total_progress_records,
                COUNT(CASE WHEN completed = 1 THEN 1 END) as completed_lessons,
                AVG(completion_percentage) as avg_completion_percentage
               FROM progress"""
    return await db_manager.fetch_one(query)

# ---------- SESSION MANAGEMENT ----------

async def create_session(user_id, session_token, expires_at):
    """Create user session"""
    query = "INSERT INTO user_sessions (user_id, session_token, expires_at) VALUES (?, ?, ?)"
    return await db_manager.execute_query(query, (user_id, session_token, expires_at))

async def get_session(session_token):
    """Get session by token"""
    query = "SELECT * FROM user_sessions WHERE session_token = ?"
    return await db_manager.fetch_one(query, (session_token,))

async def delete_session(session_token):
    """Delete session"""
    query = "DELETE FROM user_sessions WHERE session_token = ?"
    return await db_manager.execute_query(query, (session_token,))

async def cleanup_expired_sessions():
    """Clean up expired sessions"""
    query = "DELETE FROM user_sessions WHERE expires_at < datetime('now')"
    return await db_manager.execute_query(query)