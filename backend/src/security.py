from __future__ import annotations

import hashlib
import hmac
import os

from passlib.context import CryptContext

from .settings import settings


pwd_context = CryptContext(schemes=[settings.password_scheme], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def generate_token() -> str:
    return os.urandom(32).hex()


def hash_token(token: str) -> str:
    # Fast constant-time hash for storage; not reversible
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def constant_time_compare(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)


