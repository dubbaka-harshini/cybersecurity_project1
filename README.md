# 🛡️ CyberAuth Toolkit

A complete, from-scratch **secure authentication system** built with Flask,
demonstrating industry-standard practices for user registration, login,
session management, and protection against common web authentication
vulnerabilities. Built as a learning project and portfolio piece for
cybersecurity / secure software development.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-black)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📌 Overview

CyberAuth Toolkit is a self-contained Flask web app implementing a full
authentication flow — **register → login → protected dashboard → logout** —
with the kind of security controls a real production app would need. It's
intentionally simple enough to read end-to-end in one sitting, but grounded
in real security principles rather than toy shortcuts.

**Live features:**
- User registration with strict server-side validation
- Real-time password strength meter (client-side JS + matching server rules)
- Secure password storage using salted PBKDF2-SHA256 hashing
- Login with generic error messages (prevents username enumeration)
- Account lockout after repeated failed logins (brute-force mitigation)
- Rate limiting on login/register endpoints
- CSRF-protected forms
- Hardened session cookies (HttpOnly, SameSite, idle timeout)
- Protected routes via a `login_required` decorator
- Parameterized SQL queries (SQL-injection safe)
- Centralized error handling that never leaks stack traces
- Authentication audit log (DB table + log file)
- Clean, responsive, cybersecurity-themed UI

---

## 🧱 Tech Stack

| Layer      | Technology                              |
|------------|------------------------------------------|
| Backend    | Python 3, Flask                          |
| Database   | SQLite3 (raw SQL, no ORM — for transparency) |
| Auth/Security | Werkzeug password hashing, Flask-WTF (CSRF), Flask-Limiter (rate limiting) |
| Frontend   | HTML5, CSS3 (no framework), vanilla JavaScript |

---

## 📂 Project Structure

```
cyber-auth-toolkit/
├── app.py                     # Main Flask application & routes
├── config.py                  # App configuration (secrets, cookie policy, lockout rules)
├── requirements.txt
├── .env.example                # Template for environment variables
├── .gitignore
│
├── database/
│   ├── schema.sql              # SQL table definitions (users, auth_log)
│   ├── init_db.py              # Creates/initializes the SQLite database
│   └── users.db                # Created at runtime (git-ignored)
│
├── models/
│   └── user.py                 # All DB access: create/read users, hashing, lockout logic
│
├── utils/
│   ├── validators.py           # Server-side input validation
│   └── decorators.py           # @login_required route protection
│
├── templates/
│   ├── base.html                # Shared layout, nav, flash messages
│   ├── index.html                # Landing page
│   ├── register.html             # Registration form
│   ├── login.html                 # Login form
│   ├── dashboard.html              # Protected user dashboard
│   └── errors/
│       ├── 404.html
│       ├── 429.html
│       └── 500.html
│
├── static/
│   ├── css/style.css            # Full stylesheet (dark, cybersecurity theme)
│   └── js/
│       ├── password-strength.js  # Real-time strength meter
│       └── main.js               # Show/hide password, flash auto-dismiss
│
└── logs/
    └── security.log             # Runtime auth event log (git-ignored)
```

---

## 🚀 Getting Started

### 1. Clone and enter the project
```bash
git clone https://github.com/<your-username>/cyber-auth-toolkit.git
cd cyber-auth-toolkit
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
# then generate a real secret key:
python -c "import secrets; print(secrets.token_hex(32))"
# paste the output into .env as SECRET_KEY=...
```

### 5. Initialize the database
```bash
python database/init_db.py
```

### 6. Run the app
```bash
python app.py
```

Visit **http://127.0.0.1:5000** in your browser. 🎉

---

## 🔐 Security Implementation Details

This section is written so you can confidently explain each control in an
interview or code review.

### 1. Password Hashing
Passwords are hashed with `werkzeug.security.generate_password_hash` using
**PBKDF2-HMAC-SHA256** with a random 16-byte salt per user. The plaintext
password is never stored or logged. Verification uses constant-time
comparison (`check_password_hash`) to avoid timing attacks.

### 2. Input Validation
Every field (username, email, password) is validated **server-side** in
`utils/validators.py`, independent of the client-side JavaScript — because
JavaScript validation can always be bypassed by an attacker who submits
requests directly (e.g. with `curl` or Burp Suite). Regex whitelisting is
used rather than blacklisting dangerous characters.

### 3. SQL Injection Prevention
All database queries use **parameterized placeholders** (`?`) via Python's
built-in `sqlite3` module — user input is never concatenated into SQL
strings.

### 4. Session Management
- `session.clear()` is called on login to prevent **session fixation**.
- Cookies are `HttpOnly` (unreadable by JavaScript, mitigating XSS-based
  cookie theft) and `SameSite=Lax` (mitigates CSRF).
- Sessions expire automatically after 30 minutes of inactivity
  (`PERMANENT_SESSION_LIFETIME`).
- In production, set `SESSION_COOKIE_SECURE=True` so cookies are only sent
  over HTTPS.

### 5. CSRF Protection
Every POST form includes a CSRF token generated and validated by
`Flask-WTF`'s `CSRFProtect`. Requests without a valid token are rejected.

### 6. Brute-Force & Enumeration Protection
- Failed login attempts are tracked per-account; after **5 consecutive
  failures**, the account is locked for **15 minutes**.
- Login error messages are intentionally generic ("Invalid username or
  password") so an attacker cannot tell whether a username exists.
- `Flask-Limiter` throttles the `/login` and `/register` endpoints
  (10/min and 5/min respectively) to slow down scripted attacks.

### 7. Secure Error Handling
Custom error handlers for 404, 429, and 500 return generic user-facing
pages — no stack traces, file paths, or internal details are ever exposed.
Server-side errors are logged internally instead of shown to the user.

### 8. Authentication Audit Trail
Every register, login success/failure, lockout, and logout event is
recorded in the `auth_log` table and in `logs/security.log`, supporting
traceability and incident investigation.

### 9. Access Control
The `@login_required` decorator (`utils/decorators.py`) guards the
`/dashboard` route. Unauthenticated requests are redirected to `/login`
rather than exposing any information about the protected resource.

---

## 🖥️ Screens

| Page | Description |
|------|-------------|
| **Landing** | Overview of the toolkit's security features |
| **Register** | Real-time password strength meter, live rule checklist |
| **Login** | Generic error handling, account lockout messaging |
| **Dashboard** | Protected page showing account & security status |

---

## 🧪 Manual Testing Checklist

- [ ] Register with a weak password → rejected with specific reason
- [ ] Register with an existing username/email → rejected
- [ ] Login with wrong password 5 times → account locks for 15 minutes
- [ ] Visit `/dashboard` while logged out → redirected to `/login`
- [ ] Submit a form without a CSRF token → request rejected
- [ ] Check `logs/security.log` after using the app → events recorded

---

## 🔮 Possible Extensions

- Multi-factor authentication (TOTP via `pyotp`)
- Email verification on registration
- "Forgot password" flow with time-limited reset tokens
- Move from SQLite to PostgreSQL for multi-user production deployments
- Swap PBKDF2 for `bcrypt` or `argon2` (via `Flask-Bcrypt` / `argon2-cffi`)
- HTTPS enforcement + HSTS headers via `Flask-Talisman`
- Structured JSON logging for SIEM ingestion

---

## ⚠️ Disclaimer

This project is built for **educational purposes** to demonstrate secure
authentication patterns. While it follows solid security practices, it has
not undergone a formal third-party security audit or penetration test.
Do not use it as-is to protect real user data in production without
further review (see "Possible Extensions" above).

---

## 📄 License

MIT License — free to use, modify, and learn from.
