"""
Password hashing and verification using bcrypt.
Used by init_db.py (seeding) and the admin login endpoint.
"""

import bcrypt

def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash of the given plaintext password."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if the plaintext password matches the bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
