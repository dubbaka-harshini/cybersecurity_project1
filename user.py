"""
models/user.py
---------------
All database access for the `users` and `auth_log` tables lives here.

Security notes:
- Every query uses parameterized placeholders ("?") — never string
  formatting/f-strings — which is the primary defense against SQL
  injection in sqlite3.
- Password hashing/verification uses Werkzeug's generate_password_hash /
  check_password_hash, which implements salted PBKDF2-HMAC-SHA256 with
  per-hash random salts, so identical passwords never produce identical
  hashes and offline brute-forcing is computationally expensive.
"""

import sqlite3
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash, check_password_hash

from config import Config


def get_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ---------------------------------------------------------------------------
# User CRUD
# ---------------------------------------------------------------------------

def create_user(username: str, email: str, password: str) -> None:
    """Hash the password and insert a new user record."""
    password_hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash),
        )
        conn.commit()
    finally:
        conn.close()


def get_user_by_username(username: str):
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
    finally:
        conn.close()


def username_exists(username: str) -> bool:
    return get_user_by_username(username) is not None


def email_exists(email: str) -> bool:
    conn = get_connection()
    try:
        row = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        return row is not None
    finally:
        conn.close()


def verify_password(stored_hash: str, provided_password: str) -> bool:
    return check_password_hash(stored_hash, provided_password)


# ---------------------------------------------------------------------------
# Account lockout / brute-force protection
# ---------------------------------------------------------------------------

def is_account_locked(user_row) -> bool:
    if not user_row["locked_until"]:
        return False
    locked_until = datetime.fromisoformat(user_row["locked_until"])
    return datetime.utcnow() < locked_until


def register_failed_login(username: str, max_attempts: int, lockout_minutes: int) -> None:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT failed_login_attempts FROM users WHERE username = ?", (username,)
        ).fetchone()
        if row is None:
            return

        attempts = row["failed_login_attempts"] + 1

        if attempts >= max_attempts:
            locked_until = (datetime.utcnow() + timedelta(minutes=lockout_minutes)).isoformat()
            conn.execute(
                "UPDATE users SET failed_login_attempts = ?, locked_until = ? WHERE username = ?",
                (attempts, locked_until, username),
            )
        else:
            conn.execute(
                "UPDATE users SET failed_login_attempts = ? WHERE username = ?",
                (attempts, username),
            )
        conn.commit()
    finally:
        conn.close()


def reset_failed_logins(username: str) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE users SET failed_login_attempts = 0, locked_until = NULL, "
            "last_login = ? WHERE username = ?",
            (datetime.utcnow().isoformat(), username),
        )
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Auth event logging (audit trail)
# ---------------------------------------------------------------------------

def log_auth_event(username: str, event_type: str, ip_address: str = None, details: str = None) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO auth_log (username, event_type, ip_address, details) VALUES (?, ?, ?, ?)",
            (username, event_type, ip_address, details),
        )
        conn.commit()
    finally:
        conn.close()
