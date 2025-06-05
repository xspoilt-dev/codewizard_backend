import hashlib
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

class Utility:
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Returns the file extension of the given filename."""
        return filename.split('.')[-1] if '.' in filename else ''
    
    @staticmethod
    def is_valid_filename(filename: str) -> bool:
        """Checks if the filename is valid (not empty and does not contain invalid characters)."""
        if not filename or any(char in filename for char in r'\/:*?"<>|'):
            return False
        return True
    @staticmethod
    def gethash_pwd(password: str) -> str:
        """Returns a hashed version of the password."""
        return hashlib.sha256(password.encode()).hexdigest()
    @staticmethod
    def pwd_match(password: str, hashed_password: str) -> bool:
        """Checks if the provided password matches the hashed password."""
        return Utility.gethash_pwd(password) == hashed_password


    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Checks if the email is valid."""
        import re
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email) is not None
    @staticmethod
    def is_valid_username(username: str) -> bool:
        """Checks if the username is valid (not empty and does not contain invalid characters)."""
        if not username or any(char in username for char in r'\/:*?"<>|'):
            return False
        return True
    @staticmethod
    def is_valid_password(password: str) -> bool:
        """Checks if the password is valid (not empty and meets length requirements)."""
        return len(password) >= 8  # Example: minimum length of 8 characters
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Checks if the phone number is valid (simple check for digits and length)."""
        return phone.isdigit() and len(phone) >= 10  # Example: minimum length of 10 digits
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Checks if the URL is valid."""
        import re
        url_regex = r'^(https?|ftp)://[^\s/$.?#].[^\s]*$'
        return re.match(url_regex, url) is not None
    @staticmethod
    def _generate_key(password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    @staticmethod
    def gen_token(email: str, password: str) -> str:
        salt = os.urandom(16)
        key = Utility._generate_key(password, salt)
        f = Fernet(key)

        token_data = email.encode()
        token = f.encrypt(token_data)
        combined = base64.urlsafe_b64encode(salt + token).decode()
        return combined

    from typing import Optional

    @staticmethod
    def verify_token(token: str, password: str) -> Optional[str]:
        try:
            combined = base64.urlsafe_b64decode(token)
            salt, encrypted_data = combined[:16], combined[16:]

            key = Utility._generate_key(password, salt)
            f = Fernet(key)
            email = f.decrypt(encrypted_data).decode()
            return email  
        except Exception as e:
            return None  