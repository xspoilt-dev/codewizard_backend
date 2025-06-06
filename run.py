import os
import sys
import logging
from app.main import WebBackend
from app.config import (
    HOST, PORT, DEBUG, RELOAD,
    DATABASE_FILE, LOG_LEVEL, LOG_FILE
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE)
    ]
)

logger = logging.getLogger(__name__)

def check_database():
    """Check if database file exists and is accessible"""
    if not os.path.exists(DATABASE_FILE):
        logger.warning(f"Database file {DATABASE_FILE} does not exist. It will be created on first run.")
    elif not os.access(DATABASE_FILE, os.R_OK | os.W_OK):
        logger.error(f"Database file {DATABASE_FILE} exists but is not readable/writable")
        sys.exit(1)

def main():
    """Main entry point for the application"""
    try:
        # Check database
        check_database()
        
        # Create and run the backend
        logger.info("Starting CodeWizard Learning Platform API Server...")
        backend = WebBackend()
        
        # Print server information
        logger.info(f"Server running at http://{HOST}:{PORT}")
        logger.info(f"API Documentation: http://{HOST}:{PORT}/api/v1/")
        logger.info(f"Admin Panel: http://{HOST}:{PORT}/api/v1/admin/")
        
        # Run the server
        backend.run(host=HOST, port=PORT, debug=DEBUG, reload=RELOAD)
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
