from catzilla import App, RouterGroup
import asyncio
import logging
from app.api.user_endpoints import UserEndpoints
from app.api.admin_endpoints import AdminEndpoints
from app.database import init_db

logger = logging.getLogger(__name__)

class WebBackend:
    def __init__(self):
        self.app = App()
        self.user_app = RouterGroup(prefix="/api/v1", tags=["api"])
        self.admin_app = RouterGroup(prefix="/api/v1/admin", tags=["admin"])
        self.user_endpoints = UserEndpoints()
        self.admin_endpoints = AdminEndpoints()
        self._setup_routes()
    
    def _setup_routes(self):
        try:
            # Public routes
            self.app.route('/api/v1/', methods=['GET'])(lambda request: asyncio.run(self.user_endpoints.index(request)))
            self.app.route('/api/v1/register', methods=['POST'])(lambda request: asyncio.run(self.user_endpoints.register(request)))
            self.app.route('/api/v1/login', methods=['POST'])(lambda request: asyncio.run(self.user_endpoints.login(request)))
            
            # Protected user routes
            self.app.route('/api/v1/profile', methods=['GET'])(lambda request: asyncio.run(self.user_endpoints.get_profile(request)))
            self.app.route('/api/v1/profile', methods=['PUT'])(lambda request: asyncio.run(self.user_endpoints.update_profile(request)))
            self.app.route('/api/v1/lessons', methods=['GET'])(lambda request: asyncio.run(self.user_endpoints.get_lessons(request)))
            self.app.route('/api/v1/lessons/<int:lesson_id>', methods=['GET'])(lambda request: asyncio.run(self.user_endpoints.get_lesson(request)))
            self.app.route('/api/v1/lessons/<int:lesson_id>/quiz', methods=['GET'])(lambda request: asyncio.run(self.user_endpoints.get_lesson_quiz(request)))
            self.app.route('/api/v1/lessons/<int:lesson_id>/quiz/submit', methods=['POST'])(lambda request: asyncio.run(self.user_endpoints.submit_lesson_quiz(request)))
            self.app.route('/api/v1/lessons/<int:lesson_id>/progress', methods=['POST'])(lambda request: asyncio.run(self.user_endpoints.update_lesson_progress(request)))
            self.app.route('/api/v1/progress', methods=['GET'])(lambda request: asyncio.run(self.user_endpoints.get_user_progress(request)))
            self.app.route('/api/v1/quiz-submissions', methods=['GET'])(lambda request: asyncio.run(self.user_endpoints.get_quiz_submissions(request)))
            self.app.route('/api/v1/chat', methods=['POST'])(lambda request: asyncio.run(self.user_endpoints.ai_chat(request)))
            self.app.route('/api/v1/chat/history', methods=['GET'])(lambda request: asyncio.run(self.user_endpoints.get_chat_history(request)))
            self.app.route('/api/v1/code/evaluate', methods=['POST'])(lambda request: asyncio.run(self.user_endpoints.evaluate_code(request)))
            self.app.route('/api/v1/code/explain', methods=['POST'])(lambda request: asyncio.run(self.user_endpoints.explain_code(request)))
            self.app.route('/api/v1/code/optimize', methods=['POST'])(lambda request: asyncio.run(self.user_endpoints.optimize_code(request)))
            self.app.route('/api/v1/code/debug', methods=['POST'])(lambda request: asyncio.run(self.user_endpoints.debug_code(request)))
            self.app.route('/api/v1/lessons/<int:lesson_id>/hints', methods=['GET'])(lambda request: asyncio.run(self.user_endpoints.get_lesson_hints(request)))
            
            # Admin routes
            self.app.route('/api/v1/admin/', methods=['GET'])(lambda request: asyncio.run(self.admin_endpoints.admin_dashboard(request)))
            self.app.route('/api/v1/admin/users', methods=['GET'])(lambda request: asyncio.run(self.admin_endpoints.get_all_users_admin(request)))
            self.app.route('/api/v1/admin/users/<int:user_id>/admin', methods=['POST'])(lambda request: asyncio.run(self.admin_endpoints.make_admin(request)))
            self.app.route('/api/v1/admin/lessons', methods=['POST'])(lambda request: asyncio.run(self.admin_endpoints.create_lesson_admin(request)))
            self.app.route('/api/v1/admin/lessons/<int:lesson_id>', methods=['PUT'])(lambda request: asyncio.run(self.admin_endpoints.update_lesson_admin(request)))
            self.app.route('/api/v1/admin/lessons/<int:lesson_id>', methods=['DELETE'])(lambda request: asyncio.run(self.admin_endpoints.delete_lesson_admin(request)))
            self.app.route('/api/v1/admin/lessons/<int:lesson_id>/quiz', methods=['POST'])(lambda request: asyncio.run(self.admin_endpoints.create_quiz_admin(request)))
            self.app.route('/api/v1/admin/lessons/<int:lesson_id>/hints', methods=['POST'])(lambda request: asyncio.run(self.admin_endpoints.create_hint_admin(request)))
            self.app.route('/api/v1/admin/stats', methods=['GET'])(lambda request: asyncio.run(self.admin_endpoints.get_stats(request)))
            
            logger.info("Routes setup completed successfully")
        except Exception as e:
            logger.error(f"Error setting up routes: {str(e)}", exc_info=True)
            raise
    
    async def init(self):
        """Initialize the application"""
        try:
            logger.info("Initializing database...")
            await init_db()
            logger.info("Database initialization completed")
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}", exc_info=True)
            raise
    
    def run(self, host='0.0.0.0', port=8000, debug=False, reload=False):
        """Run the application server"""
        try:
            # Initialize the application
            asyncio.run(self.init())
            
            # Include routes
            self.app.include_routes(self.user_app)
            self.app.include_routes(self.admin_app)
            
            # Configure server settings
            self.app.debug = debug
            self.app.reload = reload
            
            # Start the application server
            logger.info(f"Starting server on {host}:{port}")
            logger.info(f"API Documentation: http://{host}:{port}/api/v1/")
            logger.info(f"Admin Panel: http://{host}:{port}/api/v1/admin/")
            return self.app.listen(host=host, port=port)
            
        except Exception as e:
            logger.error(f"Failed to start server: {str(e)}", exc_info=True)
            raise 