"""
utils/validators.py
--------------------
Server-side input validation. Never trust client-side (JavaScript)
validation alone — it can always be bypassed by an attacker calling
the endpoint directly (curl, Burp Suite, etc.), so every rule enforced
in the browser is re-checked here.
"""

import re

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_username(username: str):
    if not username:
        return False, "Username is required."
    if not USERNAME_RE.match(username):
        return False, "Username must be 3-20 characters (letters, numbers, underscore only)."
    return True, ""


def validate_email(email: str):
    if not email:
        return False, "Email is required."
    if len(email) > 254 or not EMAIL_RE.match(email):
        return False, "Please enter a valid email address."
    return True, ""


def validate_password(password: str, min_length: int = 8):
    """
    Enforces a baseline password policy:
      - minimum length
      - at least one uppercase, one lowercase, one digit, one special char
    Mirrors the logic used in the client-side strength meter so users
    are never surprised by a server-side rejection.
    """
    if not password:
        return False, "Password is required."
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        return False, "Password must contain at least one special character."
    return True, ""


def passwords_match(password: str, confirm_password: str):
    if password != confirm_password:
        return False, "Passwords do not match."
    return True, ""


def sanitize_input(value: str) -> str:
    """Strip whitespace and cap length to reduce risk of abuse/overflow-style input."""
    if value is None:
        return ""
    return value.strip()[:254]
