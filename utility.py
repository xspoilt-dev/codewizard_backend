import hashlib
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
    