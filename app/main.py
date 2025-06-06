from catzilla import App, JSONResponse, RouterGroup
import asyncio
import json
from functools import wraps
from app.database import (
    # User operations
    login_user, get_user, register_user, get_user_by_token, get_user_by_id,
    update_user_profile, update_user_password, verify_user,
    # Lesson operations
    get_all_lessons, get_lesson_by_id, create_lesson, update_lesson, delete_lesson,
    # Quiz operations
    get_quiz, create_quiz, submit_quiz, get_user_quiz_submissions,
    # Progress operations
    save_progress, get_progress, get_lesson_progress,
    # AI operations
    save_chat_message, get_user_chat_history, log_ai_interaction,
    get_hints_by_lesson, create_hint,
    # Code evaluation
    log_code_evaluation, get_user_code_evaluations,
    # Admin operations
    get_all_users, make_user_admin, get_user_stats, get_lesson_stats
)
from . import utils


def auth_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    async def decorated_function(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JSONResponse(
                status_code=401,
                data={"error": "Authentication required"}
            )
        
        token = auth_header.split(' ')[1]
        user = await get_user_by_token(token)
        if not user:
            return JSONResponse(
                status_code=401,
                data={"error": "Invalid token"}
            )
        
        request.user = user
        return await f(self, request, *args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    async def decorated_function(self, request, *args, **kwargs):
        if not hasattr(request, 'user') or not request.user.get('is_admin'):
            return JSONResponse(
                status_code=403,
                data={"error": "Admin privileges required"}
            )
        return await f(self, request, *args, **kwargs)
    return decorated_function


class WebBackend:
    def __init__(self):
        self.app = App()
        self.user_app = RouterGroup(prefix="/api/v1", tags=["api"])
        self.admin_app = RouterGroup(prefix="/api/v1/admin", tags=["admin"])
        self._setup_routes()
    
    def _setup_routes(self):
        # Public routes
        self.app.route('/api/v1/', methods=['GET'])(self.index)
        # Public routes
        self.app.route('/api/v1/register', methods=['POST'])(lambda request: asyncio.run(self.register(request)))
        self.app.route('/api/v1/login', methods=['POST'])(lambda request: asyncio.run(self.login(request)))
        
        # Protected user routes
        self.app.route('/api/v1/profile', methods=['GET'])(lambda request: asyncio.run(self.get_profile(request)))
        self.app.route('/api/v1/profile', methods=['PUT'])(lambda request: asyncio.run(self.update_profile(request)))
        self.app.route('/api/v1/lessons', methods=['GET'])(lambda request: asyncio.run(self.get_lessons(request)))
        self.app.route('/api/v1/lessons/<int:lesson_id>', methods=['GET'])(lambda request: asyncio.run(self.get_lesson(request)))
        self.app.route('/api/v1/lessons/<int:lesson_id>/quiz', methods=['GET'])(lambda request: asyncio.run(self.get_lesson_quiz(request)))
        self.app.route('/api/v1/lessons/<int:lesson_id>/quiz/submit', methods=['POST'])(lambda request: asyncio.run(self.submit_lesson_quiz(request)))
        self.app.route('/api/v1/lessons/<int:lesson_id>/progress', methods=['POST'])(lambda request: asyncio.run(self.update_lesson_progress(request)))
        self.app.route('/api/v1/progress', methods=['GET'])(lambda request: asyncio.run(self.get_user_progress(request)))
        self.app.route('/api/v1/quiz-submissions', methods=['GET'])(lambda request: asyncio.run(self.get_quiz_submissions(request)))
        self.app.route('/api/v1/chat', methods=['POST'])(lambda request: asyncio.run(self.ai_chat(request)))
        self.app.route('/api/v1/chat/history', methods=['GET'])(lambda request: asyncio.run(self.get_chat_history(request)))
        self.app.route('/api/v1/code/evaluate', methods=['POST'])(lambda request: asyncio.run(self.evaluate_code(request)))
        self.app.route('/api/v1/code/explain', methods=['POST'])(lambda request: asyncio.run(self.explain_code(request)))
        self.app.route('/api/v1/code/optimize', methods=['POST'])(lambda request: asyncio.run(self.optimize_code(request)))
        self.app.route('/api/v1/code/debug', methods=['POST'])(lambda request: asyncio.run(self.debug_code(request)))
        self.app.route('/api/v1/lessons/<int:lesson_id>/hints', methods=['GET'])(lambda request: asyncio.run(self.get_lesson_hints(request)))
        
        # Admin routes
        self.app.route('/api/v1/admin/', methods=['GET'])(lambda request: asyncio.run(self.admin_dashboard(request)))
        self.app.route('/api/v1/admin/users', methods=['GET'])(lambda request: asyncio.run(self.get_all_users_admin(request)))
        self.app.route('/api/v1/admin/users/<int:user_id>/admin', methods=['POST'])(lambda request: asyncio.run(self.make_admin(request)))
        self.app.route('/api/v1/admin/lessons', methods=['POST'])(lambda request: asyncio.run(self.create_lesson_admin(request)))
        self.app.route('/api/v1/admin/lessons/<int:lesson_id>', methods=['PUT'])(lambda request: asyncio.run(self.update_lesson_admin(request)))
        self.app.route('/api/v1/admin/lessons/<int:lesson_id>', methods=['DELETE'])(lambda request: asyncio.run(self.delete_lesson_admin(request)))
        self.app.route('/api/v1/admin/lessons/<int:lesson_id>/quiz', methods=['POST'])(lambda request: asyncio.run(self.create_quiz_admin(request)))
        self.app.route('/api/v1/admin/lessons/<int:lesson_id>/hints', methods=['POST'])(lambda request: asyncio.run(self.create_hint_admin(request)))
        self.app.route('/api/v1/admin/stats', methods=['GET'])(lambda request: asyncio.run(self.get_stats(request)))
    
    def index(self, request):
        return JSONResponse(
            data={
                "version": "1.0.0",
                "message": "Welcome to the Learning Platform API",
                "endpoints": {
                    "auth": "/api/v1/login, /api/v1/register",
                    "lessons": "/api/v1/lessons",
                    "user": "/api/v1/profile",
                    "admin": "/api/v1/admin"
                }
            }
        )

    # ============ AUTHENTICATION ENDPOINTS ============
    
    async def register(self, request):
        try:
            data = request.json()
            email = data.get('email')
            password = data.get('password')
            name = data.get('name')
            
            # Validate input
            if not email or not password or not name:
                return JSONResponse(
                    status_code=400,
                    data={"error": "Email, password, and name are required"}
                )
            
            if not utils.is_valid_email(email):
                return JSONResponse(
                    status_code=400,
                    data={"error": "Invalid email format"}
                )
            
            if not utils.is_valid_password(password):
                return JSONResponse(
                    status_code=400,
                    data={"error": "Password must be at least 8 characters long"}
                )
            
            # Check if user already exists
            user_exists = await get_user(email)
            if user_exists:
                return JSONResponse(
                    status_code=409,
                    data={"error": "User already exists"}
                )
            
        
            # Register user
            token = await register_user(email, password, name)
            if not token:
                return JSONResponse(
                    status_code=500,
                    data={"error": "Failed to register user"}
                )
            
            return JSONResponse(
                data={
                    "message": "User registered successfully",
                    "email": email,
                    "token": token
                }
            )
            
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )

    async def login(self, request):
        try:
            data = request.json()
            email = data.get('email')
            password = data.get('password')

            # Validate input
            if not email or not password:
                return JSONResponse(
                    status_code=400,
                    data={"error": "Email and password are required"}
                )
            
            if not utils.is_valid_email(email):
                return JSONResponse(
                    status_code=400,
                    data={"error": "Invalid email format"}
                )
            
            # Verify credentials
            token = await login_user(email, password)
            if token == "EMAIL_NOT_FOUND":
                return JSONResponse(
                    status_code=404,
                    data={"error": "User not found"}
                )
            elif token == "INVALID_PASSWORD":
                return JSONResponse(
                    status_code=401,
                    data={"error": "Invalid credentials"}
                )
            
            return JSONResponse(
                data={
                    "message": "Login successful",
                    "token": token
                }
            )
            
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )

    # ============ USER PROFILE ENDPOINTS ============
    
    @auth_required
    async def get_profile(self, request):
        try:
            user = request.user
            return JSONResponse(
                data={
                    "id": user["id"],
                    "email": user["email"],
                    "name": user["name"],
                    "is_admin": user["is_admin"],
                    "is_verified": user["is_verified"],
                    "created_at": user["created_at"]
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )
    
    @auth_required
    async def update_profile(self, request):
        try:
            data = request.json()
            user_id = request.user["id"]
            name = data.get('name')
            email = data.get('email')
            
            if not name and not email:
                return JSONResponse(
                    status_code=400,
                    data={"error": "Name or email is required"}
                )
            
            if email and not utils.is_valid_email(email):
                return JSONResponse(
                    status_code=400,
                    data={"error": "Invalid email format"}
                )
            
            result = await update_user_profile(user_id, name, email)
            if result:
                return JSONResponse(
                    data={"message": "Profile updated successfully"}
                )
            else:
                return JSONResponse(
                    status_code=500,
                    data={"error": "Failed to update profile"}
                )
                
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )

    # ============ LESSON ENDPOINTS ============
    
    @auth_required
    async def get_lessons(self, request):
        try:
            lessons = await get_all_lessons()
            return JSONResponse(
                data={
                    "lessons": [dict(lesson) for lesson in lessons] if lessons else []
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )
    
    @auth_required
    async def get_lesson(self, request):
        try:
            lesson_id = request.path_params.get('lesson_id')
            lesson = await get_lesson_by_id(lesson_id)
            if not lesson:
                return JSONResponse(
                    status_code=404,
                    data={"error": "Lesson not found"}
                )
            
            return JSONResponse(
                data={"lesson": dict(lesson)}
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )

    # ============ QUIZ ENDPOINTS ============
    @auth_required
    async def get_lesson_quiz(self, request):
        try:
            lesson_id = request.path_params.get('lesson_id')
            quiz = await get_quiz(lesson_id)
            if not quiz:
                return JSONResponse(
                    status_code=404,
                    data={"error": "Quiz not found for this lesson"}
                )
            
            return JSONResponse(
                data={"quiz": dict(quiz)}
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )
    @auth_required
    async def submit_lesson_quiz(self, request):
        try:
            lesson_id = request.path_params.get('lesson_id')
            data = request.json()
            user_id = request.user["id"]
            answers = data.get('answers')
            score = data.get('score', 0)
            max_score = data.get('max_score', 100)
            
            if not answers:
                return JSONResponse(
                    status_code=400,
                    data={"error": "Answers are required"}
                )
            
            quiz = await get_quiz(lesson_id)
            if not quiz:
                return JSONResponse(
                    status_code=404,
                    data={"error": "Quiz not found"}
                )
            
            result = await submit_quiz(
                user_id, quiz["id"], lesson_id, 
                json.dumps(answers), score, max_score
            )
            
            if result:
                return JSONResponse(
                    data={
                        "message": "Quiz submitted successfully",
                        "score": score,
                        "max_score": max_score
                    }
                )
            else:
                return JSONResponse(
                    status_code=500,
                    data={"error": "Failed to submit quiz"}
                )
                
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )
    
    @auth_required
    async def get_quiz_submissions(self, request):
        try:
            user_id = request.user["id"]
            submissions = await get_user_quiz_submissions(user_id)
            return JSONResponse(
                data={
                    "submissions": [dict(sub) for sub in submissions] if submissions else []
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )
    @auth_required
    async def update_lesson_progress(self, request):
        try:
            lesson_id = request.path_params.get('lesson_id')
            data = request.json()
            user_id = request.user["id"]
            completed = data.get('completed', False)
            completion_percentage = data.get('completion_percentage', 0.0)
            time_spent = data.get('time_spent', 0)
            
            result = await save_progress(
                user_id, lesson_id, completed, 
                completion_percentage, time_spent
            )
            
            if result:
                return JSONResponse(
                    data={"message": "Progress updated successfully"}
                )
            else:
                return JSONResponse(
                    status_code=500,
                    data={"error": "Failed to update progress"}
                )
                
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )
    
    @auth_required
    async def get_user_progress(self, request):
        try:
            user_id = request.user["id"]
            progress = await get_progress(user_id)
            return JSONResponse(
                data={
                    "progress": [dict(p) for p in progress] if progress else []
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )

    # ============ AI CHAT ENDPOINTS ============
    
    @auth_required
    async def ai_chat(self, request):
        try:
            data = request.json()
            user_id = request.user["id"]
            message = data.get('message')
            
            if not message:
                return JSONResponse(
                    status_code=400,
                    data={"error": "Message is required"}
                )
            
            # Here you would integrate with your AI service
            # For now, returning a placeholder response
            ai_response = f"AI Response to: {message}"
            
            # Save chat message
            await save_chat_message(user_id, message, ai_response)
            
            return JSONResponse(
                data={
                    "message": message,
                    "response": ai_response
                }
            )
            
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )
    
    @auth_required
    async def get_chat_history(self, request):
        try:
            user_id = request.user["id"]
            limit = int(request.args.get('limit', 50))
            history = await get_user_chat_history(user_id, limit)
            return JSONResponse(
                data={
                    "history": [dict(h) for h in history] if history else []
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )

    # ============ CODE EVALUATION ENDPOINTS ============
    
    @auth_required
    async def evaluate_code(self, request):
        try:
            data = request.json()
            user_id = request.user["id"]
            code = data.get('code')
            language = data.get('language', 'python')
            lesson_id = data.get('lesson_id')
            
            if not code:
                return JSONResponse(
                    status_code=400,
                    data={"error": "Code is required"}
                )
            
            # Here you would implement actual code execution
            # For now, returning a placeholder
            output = f"Code executed successfully: {code[:50]}..."
            execution_time = 0.1
            
            # Log code evaluation
            await log_code_evaluation(
                user_id, code, output, None, 
                execution_time, lesson_id, language
            )
            
            return JSONResponse(
                data={
                    "output": output,
                    "execution_time": execution_time,
                    "language": language
                }
            )
            
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )
    
    @auth_required
    async def explain_code(self, request):
        try:
            data = request.json()
            user_id = request.user["id"]
            code = data.get('code')
            language = data.get('language', 'python')
            
            if not code:
                return JSONResponse(
                    status_code=400,
                    data={"error": "Code is required"}
                )
            
            # Placeholder for AI code explanation
            explanation = f"This code appears to be {language} code that does: {code[:100]}..."
            
            # Log AI interaction
            await log_ai_interaction(user_id, 'explain', code, explanation, language)
            
            return JSONResponse(
                data={
                    "explanation": explanation,
                    "language": language
                }
            )
            
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )
    
    @auth_required
    async def optimize_code(self, request):
        try:
            data = request.json()
            user_id = request.user["id"]
            code = data.get('code')
            language = data.get('language', 'python')
            
            if not code:
                return JSONResponse(
                    status_code=400,
                    data={"error": "Code is required"}
                )
            
            # Placeholder for AI code optimization
            optimized_code = f"# Optimized version\n{code}"
            
            # Log AI interaction
            await log_ai_interaction(user_id, 'optimize', code, optimized_code, language)
            
            return JSONResponse(
                data={
                    "optimized_code": optimized_code,
                    "language": language
                }
            )
            
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )
    
    @auth_required
    async def debug_code(self, request):
        try:
            data = request.json()
            user_id = request.user["id"]
            code = data.get('code')
            error_message = data.get('error_message', '')
            language = data.get('language', 'python')
            
            if not code:
                return JSONResponse(
                    status_code=400,
                    data={"error": "Code is required"}
                )
            
            # Placeholder for AI debugging
            debug_info = f"Debug analysis for error: {error_message}\nSuggested fix for code: {code[:50]}..."
            
            # Log AI interaction
            await log_ai_interaction(user_id, 'debug', code, debug_info, language)
            
            return JSONResponse(
                data={
                    "debug_info": debug_info,
                    "language": language
                }
            )
            
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )
    @auth_required
    async def get_lesson_hints(self, request):
        try:
            lesson_id = request.path_params.get('lesson_id')
            hints = await get_hints_by_lesson(lesson_id)
            return JSONResponse(
                data={
                    "hints": [dict(hint) for hint in hints] if hints else []
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )

    # ============ ADMIN ENDPOINTS ============
    
    @auth_required
    @admin_required
    async def admin_dashboard(self, request):
        try:
            user_stats = await get_user_stats()
            lesson_stats = await get_lesson_stats()
            
            return JSONResponse(
                data={
                    "message": "Welcome to admin dashboard",
                    "stats": {
                        "users": dict(user_stats) if user_stats else {},
                        "lessons": dict(lesson_stats) if lesson_stats else {}
                    }
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )
    
    @auth_required
    @admin_required
    async def get_all_users_admin(self, request):
        try:
            users = await get_all_users()
            return JSONResponse(
                data={
                    "users": [dict(user) for user in users] if users else []
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )
    @auth_required
    @admin_required
    async def make_admin(self, request):
        try:
            user_id = request.path_params.get('user_id')
            result = await make_user_admin(user_id)
            if result:
                return JSONResponse(
                    data={"message": "User promoted to admin successfully"}
                )
            else:
                return JSONResponse(
                    status_code=500,
                    data={"error": "Failed to promote user"}
                )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )

    
    @auth_required
    @admin_required
    async def create_lesson_admin(self, request):
        try:
            data = request.json()
            title = data.get('title')
            description = data.get('description', '')
            difficulty = data.get('difficulty', 'beginner')
            content = data.get('content', '')
            order_index = data.get('order_index', 0)
            
            if not title:
                return JSONResponse(
                    status_code=400,
                    data={"error": "Title is required"}
                )
            
            result = await create_lesson(title, description, difficulty, content, order_index)
            if result:
                return JSONResponse(
                    data={
                        "message": "Lesson created successfully",
                        "lesson_id": result
                    }
                )
            else:
                return JSONResponse(
                    status_code=500,
                    data={"error": "Failed to create lesson"}
                )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )
                
    @auth_required
    @admin_required
    async def update_lesson_admin(self, request):
        try:
            lesson_id = request.path_params.get('lesson_id')
            data = request.json()
            title = data.get('title')
            description = data.get('description')
            difficulty = data.get('difficulty')
            content = data.get('content')
            order_index = data.get('order_index')
            
            result = await update_lesson(
                lesson_id, title, description, 
                difficulty, content, order_index
            )
            
            if result:
                return JSONResponse(
                    data={"message": "Lesson updated successfully"}
                )
            else:
                return JSONResponse(
                    status_code=500,
                    data={"error": "Failed to update lesson"}
                )
                
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )
    @auth_required
    @admin_required
    async def delete_lesson_admin(self, request):
        try:
            lesson_id = request.path_params.get('lesson_id')
            result = await delete_lesson(lesson_id)
            if result:
                return JSONResponse(
                    data={"message": "Lesson deleted successfully"}
                )
            else:
                return JSONResponse(
                    status_code=500,
                    data={"error": "Failed to delete lesson"}
                )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )
    @auth_required
    @admin_required
    async def create_quiz_admin(self, request):
        try:
            lesson_id = request.path_params.get('lesson_id')
            data = request.json()
            title = data.get('title')
            questions = data.get('questions')
            total_points = data.get('total_points', 100)
            
            if not title or not questions:
                return JSONResponse(
                    status_code=400,
                    data={"error": "Title and questions are required"}
                )
            
            result = await create_quiz(
                lesson_id, title, json.dumps(questions), total_points
            )
            
            if result:
                return JSONResponse(
                    data={
                        "message": "Quiz created successfully",
                        "quiz_id": result
                    }
                )
            else:
                return JSONResponse(
                    status_code=500,
                    data={"error": "Failed to create quiz"}
                )
                
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )
    @auth_required
    @admin_required
    async def create_hint_admin(self, request):
        try:
            lesson_id = request.path_params.get('lesson_id')
            data = request.json()
            hint_text = data.get('hint_text')
            difficulty_level = data.get('difficulty_level', 1)
            
            if not hint_text:
                return JSONResponse(
                    status_code=400,
                    data={"error": "Hint text is required"}
                )
            
            result = await create_hint(lesson_id, hint_text, difficulty_level)
            if result:
                return JSONResponse(
                    data={
                        "message": "Hint created successfully",
                        "hint_id": result
                    }
                )
            else:
                return JSONResponse(
                    status_code=500,
                    data={"error": "Failed to create hint"}
                )
                
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )
                 

    @auth_required
    @admin_required
    async def get_stats(self, request):
        try:
            user_stats = await get_user_stats()
            lesson_stats = await get_lesson_stats()
            
            return JSONResponse(
                data={
                    "user_stats": dict(user_stats) if user_stats else {},
                    "lesson_stats": dict(lesson_stats) if lesson_stats else {}
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                data={"error": f"Internal server error: {str(e)}"}
            )
    
    def run(self, port=8000):
        # Include routes
        self.app.include_routes(self.user_app)
        self.app.include_routes(self.admin_app)
        
        # Start the application server
        print(f"🚀 Learning Platform API starting on port {port}")
        print(f"📚 API Documentation: http://localhost:{port}/api/v1/")
        print(f"🔧 Admin Panel: http://localhost:{port}/api/v1/admin/")
        return self.app.listen(port)


if __name__ == '__main__':
    backend = WebBackend()
    backend.run()