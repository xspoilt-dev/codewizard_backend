import re
import bcrypt
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from app.config import USER_TOKEN_LENGTH, USER_TOKEN_LIFETIME_HOURS

def get_file_extension(filename: str) -> str:
    """Returns the file extension of the given filename without the dot."""
    return Path(filename).suffix[1:]  # Remove the dot and return the full extension

def is_valid_filename(filename: str) -> bool:
    """Checks if the filename is valid (not empty and does not contain invalid characters)."""
    return bool(filename and all(char not in filename for char in r'\/:*?"<>|'))

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


def generate_token() -> tuple[str, datetime]:
    """Generate User session token and expiration time"""
    token = secrets.token_urlsafe(USER_TOKEN_LENGTH)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=USER_TOKEN_LIFETIME_HOURS)
    return token, expires_at
