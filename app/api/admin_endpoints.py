from catzilla import JSONResponse
from functools import wraps
from app.database import (
    # Admin operations
    get_all_users, make_user_admin, get_user_stats, get_lesson_stats,
    # Lesson operations
    create_lesson, update_lesson, delete_lesson,
    # Quiz operations
    create_quiz,
    # Hint operations
    create_hint
)
import json

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

class AdminEndpoints:
    def __init__(self):
        pass

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
