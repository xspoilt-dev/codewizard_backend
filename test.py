import hashlib

pwd = "password123"
hashed_pwd = hashlib.sha256(pwd.encode()).hexdigest()
print(f"Original Password: {pwd}")
print(f"Hashed Password: {hashed_pwd}")
def verify_password(input_pwd: str, stored_hash: str) -> bool:
    """Verify if the input password matches the stored hashed password."""
    return hashlib.sha256(input_pwd.encode()).hexdigest() == stored_hash
print(f"Password verification: {verify_password('password123', hashed_pwd)}")