from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

from app.models import Base, User, Lesson, Quiz, QuizSubmission, Progress, AIChatLog, AIInteraction, AIHint, CodeEvaluation, UserSession
from app.utils import verify_password, generate_token, hash_password
from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal: sessionmaker[AsyncSession] = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def register_user(email: str, password: str, name: str) -> str:
    async with AsyncSessionLocal() as session:
        token = generate_token()
        expire_at = datetime.now(timezone.utc) + timedelta(days=7)
        hashed_password = hash_password(password)
        user = User(email=email, password=hashed_password, name=name, token=token, token_expires_at=expire_at)
        session.add(user)
        try:
            await session.commit()
            await session.refresh(user)
            return token
        except IntegrityError:
            await session.rollback()
            raise ValueError("Email already registered")

async def login_user(email: str, password: str) -> str:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            return "EMAIL_NOT_FOUND"
            
        if not verify_password(password, user.password):
            return "INVALID_PASSWORD"
            
        return user.token

async def get_user(email):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        return user is not None

async def get_user_by_token(token):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.token == token))
        return result.scalar_one_or_none()

async def get_user_by_id(user_id):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

async def update_user_profile(user_id, name=None, email=None):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None
        if name:
            user.name = name
        if email:
            user.email = email
        await session.commit()
        await session.refresh(user)
        return user

async def update_user_password(user_id, new_password):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None
        user.password = hash_password(new_password)
        await session.commit()
        await session.refresh(user)
        return user

async def verify_user(user_id):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None
        user.is_verified = True
        await session.commit()
        await session.refresh(user)
        return user

async def get_all_users():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).order_by(User.created_at.desc()))
        return result.scalars().all()

async def make_user_admin(user_id):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None
        user.is_admin = True
        await session.commit()
        await session.refresh(user)
        return user

async def remove_user_admin(user_id):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None
        user.is_admin = False
        await session.commit()
        await session.refresh(user)
        return user

async def delete_user(user_id):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None
        await session.delete(user)
        await session.commit()
        return True

async def ban_user(user_id):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None
        user.is_verified = False
        await session.commit()
        await session.refresh(user)
        return user

async def get_all_lessons():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Lesson).order_by(Lesson.order_index))
        return result.scalars().all()

async def get_lesson_by_id(lesson_id):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Lesson).where(Lesson.id == lesson_id))
        return result.scalar_one_or_none()

async def create_lesson(title, description, difficulty, content, order_index):
    async with AsyncSessionLocal() as session:
        lesson = Lesson(title=title, description=description, difficulty=difficulty, content=content, order_index=order_index)
        session.add(lesson)
        await session.commit()
        await session.refresh(lesson)
        return lesson

async def update_lesson(lesson_id, title=None, description=None, difficulty=None, content=None, order_index=None):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Lesson).where(Lesson.id == lesson_id))
        lesson = result.scalar_one_or_none()
        if not lesson:
            return None
        if title:
            lesson.title = title
        if description:
            lesson.description = description
        if difficulty:
            lesson.difficulty = difficulty
        if content:
            lesson.content = content
        if order_index is not None:
            lesson.order_index = order_index
        await session.commit()
        await session.refresh(lesson)
        return lesson

async def delete_lesson(lesson_id):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Lesson).where(Lesson.id == lesson_id))
        lesson = result.scalar_one_or_none()
        if not lesson:
            return None
        await session.delete(lesson)
        await session.commit()
        return True

async def get_quiz(lesson_id):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Quiz).where(Quiz.lesson_id == lesson_id))
        return result.scalar_one_or_none()

async def create_quiz(lesson_id, title, questions, total_points=100):
    async with AsyncSessionLocal() as session:
        quiz = Quiz(lesson_id=lesson_id, title=title, questions=questions, total_points=total_points)
        session.add(quiz)
        await session.commit()
        await session.refresh(quiz)
        return quiz

async def update_quiz(quiz_id, title=None, questions=None, total_points=None):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Quiz).where(Quiz.id == quiz_id))
        quiz = result.scalar_one_or_none()
        if not quiz:
            return None
        if title:
            quiz.title = title
        if questions:
            quiz.questions = questions
        if total_points is not None:
            quiz.total_points = total_points
        await session.commit()
        await session.refresh(quiz)
        return quiz

async def submit_quiz(user_id, quiz_id, lesson_id, answers, score, max_score):
    async with AsyncSessionLocal() as session:
        submission = QuizSubmission(user_id=user_id, quiz_id=quiz_id, lesson_id=lesson_id, answers=answers, score=score, max_score=max_score)
        session.add(submission)
        await session.commit()
        await session.refresh(submission)
        return submission

async def get_user_quiz_submissions(user_id):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(QuizSubmission).where(QuizSubmission.user_id == user_id).order_by(QuizSubmission.submitted_at.desc()))
        return result.scalars().all()

async def save_progress(user_id, lesson_id, completed=False, completion_percentage=0.0, time_spent=0):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Progress).where(Progress.user_id == user_id, Progress.lesson_id == lesson_id))
        progress = result.scalar_one_or_none()
        if not progress:
            progress = Progress(user_id=user_id, lesson_id=lesson_id, completed=completed, completion_percentage=completion_percentage, time_spent=time_spent, last_accessed=datetime.utcnow())
            session.add(progress)
        else:
            progress.completed = completed
            progress.completion_percentage = completion_percentage
            progress.time_spent = time_spent
            progress.last_accessed = datetime.utcnow()
        await session.commit()
        await session.refresh(progress)
        return progress

async def get_progress(user_id):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Progress).where(Progress.user_id == user_id))
        return result.scalars().all()

async def get_lesson_progress(user_id, lesson_id):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Progress).where(Progress.user_id == user_id, Progress.lesson_id == lesson_id))
        return result.scalar_one_or_none()

async def save_chat_message(user_id, message, response):
    async with AsyncSessionLocal() as session:
        chat_log = AIChatLog(user_id=user_id, message=message, response=response)
        session.add(chat_log)
        await session.commit()
        await session.refresh(chat_log)
        return chat_log

async def get_user_chat_history(user_id, limit=50):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(AIChatLog).where(AIChatLog.user_id == user_id).order_by(AIChatLog.created_at.desc()).limit(limit))
        return result.scalars().all()

async def log_ai_interaction(user_id, type_, input_code, output, language="python"):
    async with AsyncSessionLocal() as session:
        interaction = AIInteraction(user_id=user_id, type=type_, input_code=input_code, output=output, language=language)
        session.add(interaction)
        await session.commit()
        await session.refresh(interaction)
        return interaction

async def get_user_ai_interactions(user_id):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(AIInteraction).where(AIInteraction.user_id == user_id).order_by(AIInteraction.created_at.desc()))
        return result.scalars().all()

async def get_hint(hint_id):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(AIHint).where(AIHint.id == hint_id))
        return result.scalar_one_or_none()

async def get_hints_by_lesson(lesson_id):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(AIHint).where(AIHint.lesson_id == lesson_id).order_by(AIHint.difficulty_level))
        return result.scalars().all()

async def create_hint(lesson_id, hint_text, difficulty_level=1):
    async with AsyncSessionLocal() as session:
        hint = AIHint(lesson_id=lesson_id, hint_text=hint_text, difficulty_level=difficulty_level)
        session.add(hint)
        await session.commit()
        await session.refresh(hint)
        return hint

async def log_code_evaluation(user_id, code, output, error=None, execution_time=0.0, lesson_id=None, language="python"):
    async with AsyncSessionLocal() as session:
        evaluation = CodeEvaluation(user_id=user_id, lesson_id=lesson_id, code=code, output=output, error=error, execution_time=execution_time, language=language)
        session.add(evaluation)
        await session.commit()
        await session.refresh(evaluation)
        return evaluation

async def get_user_code_evaluations(user_id):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(CodeEvaluation).where(CodeEvaluation.user_id == user_id).order_by(CodeEvaluation.created_at.desc()))
        return result.scalars().all()

async def get_user_stats():
    async with AsyncSessionLocal() as session:
        total_users = await session.scalar(select(func.count(User.id)))
        verified_users = await session.scalar(select(func.count()).where(User.is_verified == True))
        admin_users = await session.scalar(select(func.count()).where(User.is_admin == True))
        return {"total_users": total_users, "verified_users": verified_users, "admin_users": admin_users}

async def get_lesson_stats():
    async with AsyncSessionLocal() as session:
        total_lessons = await session.scalar(select(func.count(Lesson.id)))
        beginner_lessons = await session.scalar(select(func.count()).where(Lesson.difficulty == 'beginner'))
        intermediate_lessons = await session.scalar(select(func.count()).where(Lesson.difficulty == 'intermediate'))
        advanced_lessons = await session.scalar(select(func.count()).where(Lesson.difficulty == 'advanced'))
        return {"total_lessons": total_lessons, "beginner_lessons": beginner_lessons, "intermediate_lessons": intermediate_lessons, "advanced_lessons": advanced_lessons}

async def get_progress_stats():
    async with AsyncSessionLocal() as session:
        total_progress_records = await session.scalar(select(func.count(Progress.id)))
        completed_lessons = await session.scalar(select(func.count()).where(Progress.completed == True))
        avg_completion_percentage = await session.scalar(select(func.avg(Progress.completion_percentage)))
        return {"total_progress_records": total_progress_records, "completed_lessons": completed_lessons, "avg_completion_percentage": avg_completion_percentage}

async def create_session(user_id, session_token, expires_at):
    async with AsyncSessionLocal() as session:
        session_obj = UserSession(user_id=user_id, session_token=session_token, expires_at=expires_at)
        session.add(session_obj)
        await session.commit()
        await session.refresh(session_obj)
        return session_obj

async def get_session(session_token):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(UserSession).where(UserSession.session_token == session_token))
        return result.scalar_one_or_none()

async def delete_session(session_token):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(UserSession).where(UserSession.session_token == session_token))
        session_obj = result.scalar_one_or_none()
        if not session_obj:
            return None
        await session.delete(session_obj)
        await session.commit()
        return True

async def cleanup_expired_sessions():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(UserSession).where(UserSession.expires_at < datetime.utcnow()))
        sessions = result.scalars().all()
        for session_obj in sessions:
            await session.delete(session_obj)
        await session.commit()
        return True