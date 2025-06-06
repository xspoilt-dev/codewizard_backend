import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Server Configuration
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '8000'))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
RELOAD = os.getenv('RELOAD', 'False').lower() == 'true'

# Database Configuration
DATABASE_FILE = os.getenv('DATABASE_FILE', 'hackathon.db')
DATABASE_URL = os.getenv('DATABASE_URL', f"sqlite+aiosqlite:///./{DATABASE_FILE}")

# Security Configuration
USER_TOKEN_LENGTH = int(os.getenv('USER_TOKEN_LENGTH', '32'))
USER_TOKEN_LIFETIME_HOURS = int(os.getenv('USER_TOKEN_LIFETIME_HOURS', '24'))
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')  # Change this in production!

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'app.log')
