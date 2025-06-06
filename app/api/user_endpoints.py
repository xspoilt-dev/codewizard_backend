from catzilla import JSONResponse
from functools import wraps
from app.database import (
    # User operations
    login_user, get_user, register_user, get_user_by_token, get_user_by_id,
    update_user_profile, update_user_password, verify_user,
    # Lesson operations
    get_all_lessons, get_lesson_by_id,
    # Quiz operations
    get_quiz, submit_quiz, get_user_quiz_submissions,
    # Progress operations
    save_progress, get_progress, get_lesson_progress,
    # AI operations
    save_chat_message, get_user_chat_history, log_ai_interaction,
    get_hints_by_lesson,
    # Code evaluation
    log_code_evaluation, get_user_code_evaluations
)
from app import utils
import json

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

class UserEndpoints:
    def __init__(self):
        pass

    async def index(self, request):
        return JSONResponse(
            data={
                "version": "1.0.0",
                "message": "Welcome to the Learning Platform API",
                "endpoints": {
                    "auth": "/api/v1/login, /api/v1/register",
                    "lessons": "/api/v1/lessons",
                    "user": "/api/v1/profile"
                }
            }
        )

    async def register(self, request):
        try:
            data = request.json()
            email = data.get('email')
            password = data.get('password')
            name = data.get('name')
            
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
            
            user_exists = await get_user(email)
            if user_exists:
                return JSONResponse(
                    status_code=409,
                    data={"error": "User already exists"}
                )
            
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
            
            ai_response = f"AI Response to: {message}"
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
            
            output = f"Code executed successfully: {code[:50]}..."
            execution_time = 0.1
            
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
            
            explanation = f"This code appears to be {language} code that does: {code[:100]}..."
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
            
            optimized_code = f"# Optimized version\n{code}"
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
            
            debug_info = f"Debug analysis for error: {error_message}\nSuggested fix for code: {code[:50]}..."
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
