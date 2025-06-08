from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey,
    Boolean, JSON, Float
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

from sqlalchemy.types import TypeDecorator, DateTime
from datetime import timezone

class _DateTime(TypeDecorator):
    """
    Stores all datetimes in UTC and ensures they're timezone-aware.

    Converts tz-aware datetimes to UTC before storing, and adds UTC tzinfo
    to tz-naive datetimes. Useful for making SQLite behave like it supports timezones.
    """
    impl = DateTime

    def process_bind_param(self, value, dialect):
        if value and value.tzinfo is not None:
            value = value.astimezone(timezone.utc)
        elif value:
            value = value.replace(tzinfo=timezone.utc)

        return value

    def process_result_value(self, value, dialect):
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value


Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String)
    token = Column(String, unique=True, nullable=True)
    token_expires_at = Column(_DateTime(), nullable=True)
    is_admin = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(_DateTime(), default=func.now())

    # Relationships
    sessions = relationship("UserSession", back_populates="user")
    quiz_submissions = relationship("QuizSubmission", back_populates="user")
    progress_entries = relationship("Progress", back_populates="user")
    ai_chat_logs = relationship("AIChatLog", back_populates="user")
    ai_interactions = relationship("AIInteraction", back_populates="user")
    code_evaluations = relationship("CodeEvaluation", back_populates="user")

class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    difficulty = Column(String)  # beginner, intermediate, advanced
    content = Column(Text)
    order_index = Column(Integer)
    created_at = Column(_DateTime(), default=func.now())

    # Relationships
    quizzes = relationship("Quiz", back_populates="lesson")
    quiz_submissions = relationship("QuizSubmission", back_populates="lesson")
    progress_entries = relationship("Progress", back_populates="lesson")
    ai_hints = relationship("AIHint", back_populates="lesson")
    code_evaluations = relationship("CodeEvaluation", back_populates="lesson")

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    title = Column(String)
    questions = Column(JSON)  # JSON array of questions
    total_points = Column(Integer, default=100)
    created_at = Column(_DateTime(), default=func.now())

    lesson = relationship("Lesson", back_populates="quizzes")
    submissions = relationship("QuizSubmission", back_populates="quiz")

class QuizSubmission(Base):
    __tablename__ = "quiz_submissions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    answers = Column(JSON)  # User's answers
    score = Column(Float)
    max_score = Column(Float)
    completed = Column(Boolean, default=True)
    submitted_at = Column(_DateTime(), default=func.now())

    user = relationship("User", back_populates="quiz_submissions")
    quiz = relationship("Quiz", back_populates="submissions")
    lesson = relationship("Lesson", back_populates="quiz_submissions")

class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    completed = Column(Boolean, default=False)
    completion_percentage = Column(Float, default=0.0)
    time_spent = Column(Integer, default=0)  # in minutes
    last_accessed = Column(_DateTime(), default=func.now())
    created_at = Column(_DateTime(), default=func.now())

    user = relationship("User", back_populates="progress_entries")
    lesson = relationship("Lesson", back_populates="progress_entries")

class AIChatLog(Base):
    __tablename__ = "ai_chat_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    response = Column(Text)
    created_at = Column(_DateTime(), default=func.now())

    user = relationship("User", back_populates="ai_chat_logs")

class AIInteraction(Base):
    __tablename__ = "ai_interactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)  # explain, optimize, debug
    input_code = Column(Text)
    output = Column(Text)
    language = Column(String, default="python")
    created_at = Column(_DateTime(), default=func.now())

    user = relationship("User", back_populates="ai_interactions")

class AIHint(Base):
    __tablename__ = "ai_hints"

    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    hint_text = Column(Text)
    difficulty_level = Column(Integer, default=1)  # 1=easy, 2=medium, 3=hard
    created_at = Column(_DateTime(), default=func.now())

    lesson = relationship("Lesson", back_populates="ai_hints")

class CodeEvaluation(Base):
    __tablename__ = "code_evaluations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=True)
    code = Column(Text)
    output = Column(Text)
    error = Column(Text, nullable=True)
    execution_time = Column(Float)
    language = Column(String, default="python")
    created_at = Column(_DateTime(), default=func.now())

    user = relationship("User", back_populates="code_evaluations")
    lesson = relationship("Lesson", back_populates="code_evaluations")

class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_token = Column(String, unique=True)
    expires_at = Column(_DateTime())
    created_at = Column(_DateTime(), default=func.now())

    user = relationship("User", back_populates="sessions")
