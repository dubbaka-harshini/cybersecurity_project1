"""
config.py
---------
Centralised application configuration.

Security notes:
- SECRET_KEY is read from the environment. A fallback random key is
  generated automatically for local development ONLY so the app never
  crashes on first run, but you should always set a real SECRET_KEY
  via environment variable (or a .env file) before deploying.
- Session cookies are hardened (HttpOnly, SameSite, and Secure-in-prod)
  to reduce the risk of session hijacking / XSS cookie theft.
"""

import os
import secrets
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # --- Core Flask settings -------------------------------------------------
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

    # --- Database --------------------------------------------------------------
    DATABASE_PATH = os.path.join(BASE_DIR, "database", "users.db")

    # --- Session / cookie hardening --------------------------------------------
    SESSION_COOKIE_HTTPONLY = True          # JS cannot read the cookie (mitigates XSS theft)
    SESSION_COOKIE_SAMESITE = "Lax"         # Mitigates CSRF via cross-site requests
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "False").lower() == "true"
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)  # Auto-expire idle sessions

    # --- Account lockout / brute-force protection -------------------------------
    MAX_FAILED_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15

    # --- Password policy ---------------------------------------------------------
    PASSWORD_MIN_LENGTH = 8

    # --- Rate limiting (Flask-Limiter) --------------------------------------------
    RATELIMIT_LOGIN = "10 per minute"
    RATELIMIT_REGISTER = "5 per minute"
