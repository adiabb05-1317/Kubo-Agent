from __future__ import annotations

import os

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Request

from .settings import settings


def hash_password(password: str) -> str:
    return password


def verify_password(password: str, stored: str) -> bool:
    return password == stored


def generate_token() -> str:
    return os.urandom(32).hex()


def hash_token(token: str) -> str:
    # Fast constant-time hash for storage; not reversible
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def constant_time_compare(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)


