import re
import bcrypt
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from config import USER_TOKEN_LENGTH, USER_TOKEN_LIFETIME_HOURS

def get_file_extension(filename: str) -> str:
    """Returns the file extension of the given filename."""
    return Path(filename).suffix[:1]

def is_valid_filename(filename: str) -> bool:
    """Checks if the filename is valid (not empty and does not contain invalid characters)."""
    if not filename or any(char in filename for char in r'\/:*?"<>|'):
        return False
    return True

def hash_password(password: str) -> str:
    """Returns a hashed version of the password."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()

def verify_password(password: str, hashed: str) -> bool:
    """Checks if the provided password matches the hashed password."""
    return bcrypt.checkpw(password.encode(), hashed.encode())

def is_valid_email(email: str) -> bool:
    """Checks if the email is valid."""
    email_regex = (
        r"^(?!.*\.\.)"                 # no consecutive dots anywhere
        r"[a-zA-Z0-9_.+-]+"            # local part
        r"@"
        r"(?!-)[a-zA-Z0-9-]+"          # domain label can't start with '-'
        r"(\.[a-zA-Z0-9-]+)*"          # optional subdomains
        r"\.[a-zA-Z]{2,}$"             # TLD (at least 2 letters)
    )
    return re.match(email_regex, email) is not None

def is_valid_username(username: str) -> bool:
    """Checks if the username is valid (not empty and does not contain invalid characters)."""
    if not username:
        return False
    
    return re.fullmatch(r'[a-zA-Z0-9_]+', username) is not None

def is_valid_password(password: str) -> bool:
    """Checks if the password is valid (not empty and meets length requirements)."""
    return len(password) >= 8  # Example: minimum length of 8 characters

def is_valid_phone(phone: str) -> bool:
    """Checks if the phone number is valid (simple check for digits and length)."""
    return phone.isdigit() and len(phone) >= 10  # Example: minimum length of 10 digits

def is_valid_url(url: str) -> bool:
    """Checks if the URL is valid."""
    import re
    url_regex = r'^(https?|ftp)://[^\s/$.?#].[^\s]*$'
    return re.match(url_regex, url) is not None


def generate_token() -> str:
    """Generate User session token"""
    token = secrets.token_urlsafe(USER_TOKEN_LENGTH)
    return token
