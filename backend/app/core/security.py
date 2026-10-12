import hashlib
import hmac
from app.core.config import settings

def hash_password(password: str) -> str:
    """Hash a password using salted SHA-256 for secure local storage."""
    salt = settings.SECRET_KEY[:16].encode('utf-8')
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000).hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hmac.compare_digest(hash_password(plain_password), hashed_password)
