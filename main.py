from catzilla import App, JSONResponse, Response, RouterGroup
from database import login_user, get_user
from utility import Utility

class WebBackend:
    def __init__(self):
        self.app = App()
        self.user_app = RouterGroup(prefix="/api/v1", tags=["api"])
        self.admin_app = RouterGroup(prefix="/admin", tags=["admin"])
        self._setup_routes()
    
    def _setup_routes(self):
        self.user_app.route('/')(self.index)
        self.user_app.route('/login', methods=['POST'])(self.login)
    
    def index(self, request):
        return JSONResponse(
                data={
                    "version": "1.0.0"
                }
            )
    def admin_index(self, request):
        return JSONResponse(
                data={
                    "version": "1.0.0",
                    "admin": "Welcome to the admin panel"
                }
            )
    def login(self, request):
        data = request.json()
        username = data.get('email')
        password = data.get('password')

        if not Utility.is_valid_email(username):
            return JSONResponse(
                status_code=400,
                data={"error": "Invalid email format"}
            )
        if not username or not password:
            return JSONResponse(
                status_code=400,
                data={"error": "Username and password are required"}
            )
        user = get_user(username)
        if not user:
            return JSONResponse(
                status_code=404,
                data={"error": "User not found"}
            )
        
        login_chk = login_user(username, password)
        if not login_chk:
            return JSONResponse(
                status_code=401,
                data={"error": "Invalid credentials"}
            )
        return JSONResponse(
                data={
                    "message": "Login successful",
                    "token": login_chk
                }
            )
    
    
    def run(self, port=8000):
        self.app.include_routes(self.user_app)
        self.app.include_routes(self.admin_app)

        """Start the application server"""
        return self.app.listen(port)


if __name__ == '__main__':
    backend = WebBackend()
    backend.run()
