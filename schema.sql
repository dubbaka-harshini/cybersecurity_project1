-- schema.sql
-- SQLite schema for the Cybersecurity Authentication Toolkit
-- Passwords are NEVER stored in plaintext — only salted PBKDF2-SHA256 hashes.

CREATE TABLE IF NOT EXISTS users (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    username              TEXT NOT NULL UNIQUE,
    email                 TEXT NOT NULL UNIQUE,
    password_hash         TEXT NOT NULL,
    created_at            TEXT NOT NULL DEFAULT (datetime('now')),
    last_login            TEXT,
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until          TEXT
);

-- Basic audit log of authentication events (login success/failure, registration, logout).
-- Useful for demonstrating security-monitoring awareness in interviews.
CREATE TABLE IF NOT EXISTS auth_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    username   TEXT,
    event_type TEXT NOT NULL,       -- REGISTER, LOGIN_SUCCESS, LOGIN_FAILURE, LOGOUT, LOCKOUT
    ip_address TEXT,
    timestamp  TEXT NOT NULL DEFAULT (datetime('now')),
    details    TEXT
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_auth_log_username ON auth_log (username);
