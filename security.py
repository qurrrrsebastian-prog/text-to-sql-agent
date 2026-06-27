"""security.py — Security utilities.
Author: Avatar Putra Sigit | GitHub: qurrrrsebastian-prog
"""
import re
import html
import hashlib
import secrets
import time
from typing import Optional

_rate_limit_store = {}


def sanitize_input(text: str, max_length: int = 5000) -> str:
    """Escape HTML, strip dangerous chars, limit length."""
    if not text:
        return ""
    text = html.escape(text)
    text = re.sub(r'[<>\"\']', '', text)
    return text[:max_length].strip()


def check_rate_limit(key: str, max_requests: int = 30, window_seconds: int = 60) -> bool:
    """Rate limiter. True = allowed, False = blocked."""
    now = time.time()
    if key not in _rate_limit_store:
        _rate_limit_store[key] = []
    _rate_limit_store[key] = [t for t in _rate_limit_store[key] if now - t < window_seconds]
    if len(_rate_limit_store[key]) >= max_requests:
        return False
    _rate_limit_store[key].append(now)
    return True


def hash_password(password: str) -> str:
    """Hash password with a per-password salt."""
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${hashed.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Verify password against a stored salt$hash string."""
    try:
        salt, hash_val = stored.split('$')
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return secrets.compare_digest(hashed.hex(), hash_val)
    except Exception:
        return False


def generate_session_token() -> str:
    """Generate a secure session token."""
    return secrets.token_urlsafe(32)


def validate_email(email: str) -> bool:
    """Return True if the email address looks valid."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def mask_api_key(key: str) -> str:
    """Show only the first 4 and last 4 characters of an API key."""
    if not key or len(key) < 12:
        return "****"
    return f"{key[:4]}...{key[-4:]}"


# --------------------------------------------------------------------------- #
# SQL safety
# --------------------------------------------------------------------------- #
_DANGEROUS = ("drop", "delete", "update", "insert", "alter", "truncate",
              "replace", "create", "attach", "pragma")


def is_safe_sql(sql: str) -> tuple:
    """Return (is_safe, reason). Allows read-only SELECT/WITH statements only."""
    if not sql or not sql.strip():
        return False, "Empty query."
    stripped = sql.strip().rstrip(";")
    # Reject multiple statements.
    if ";" in stripped:
        return False, "Multiple statements are not allowed."
    lowered = stripped.lower()
    first = lowered.split(None, 1)[0] if lowered.split() else ""
    if first not in ("select", "with"):
        return False, f"Only SELECT queries are allowed (got '{first.upper()}')."
    for kw in _DANGEROUS:
        if re.search(rf"\b{kw}\b", lowered):
            return False, f"Blocked potentially destructive keyword: {kw.upper()}."
    return True, ""
