"""
app.py
------
Cybersecurity Authentication Toolkit — main Flask application.

Routes:
    GET  /            Landing page
    GET  /register     Registration form
    POST /register     Handle registration
    GET  /login         Login form
    POST /login          Handle login
    GET  /logout          Log the user out
    GET  /dashboard        Protected page (login_required)

Run with:  python app.py
"""

import logging
import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import Config
from database.init_db import init_db
from models import user as user_model
from utils.validators import (
    validate_username,
    validate_email,
    validate_password,
    passwords_match,
    sanitize_input,
)
from utils.decorators import login_required

# ---------------------------------------------------------------------------
# App factory / configuration
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.config.from_object(Config)

# CSRF protection: every POST form must carry a valid token, mitigating
# Cross-Site Request Forgery attacks against authenticated sessions.
csrf = CSRFProtect(app)

# Rate limiting: throttles brute-force / credential-stuffing attempts
# against the login and registration endpoints.
limiter = Limiter(get_remote_address, app=app, default_limits=[])

# Basic audit logging to file, in addition to the DB-backed auth_log table.
os.makedirs(os.path.join(os.path.dirname(__file__), "logs"), exist_ok=True)
logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), "logs", "security.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


# Make sure the DB exists even if someone forgets to run init_db.py manually.
with app.app_context():
    init_db()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
@limiter.limit(Config.RATELIMIT_REGISTER)
def register():
    if request.method == "POST":
        username = sanitize_input(request.form.get("username", ""))
        email = sanitize_input(request.form.get("email", "")).lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # --- Server-side validation (never trust the client) -----------------
        checks = [
            validate_username(username),
            validate_email(email),
            validate_password(password, Config.PASSWORD_MIN_LENGTH),
            passwords_match(password, confirm_password),
        ]
        for is_valid, message in checks:
            if not is_valid:
                flash(message, "error")
                return render_template("register.html", username=username, email=email)

        if user_model.username_exists(username):
            flash("That username is already taken.", "error")
            return render_template("register.html", username=username, email=email)

        if user_model.email_exists(email):
            flash("An account with that email already exists.", "error")
            return render_template("register.html", username=username, email=email)

        user_model.create_user(username, email, password)
        user_model.log_auth_event(username, "REGISTER", request.remote_addr)
        logging.info("New user registered: %s", username)

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", username="", email="")


@app.route("/login", methods=["GET", "POST"])
@limiter.limit(Config.RATELIMIT_LOGIN)
def login():
    if request.method == "POST":
        username = sanitize_input(request.form.get("username", ""))
        password = request.form.get("password", "")

        user_row = user_model.get_user_by_username(username)

        # Deliberately generic error message: we never reveal whether the
        # username exists or the password was wrong, which prevents
        # user-enumeration attacks.
        generic_error = "Invalid username or password."

        if user_row is None:
            user_model.log_auth_event(username, "LOGIN_FAILURE", request.remote_addr, "unknown user")
            flash(generic_error, "error")
            return render_template("login.html", username=username)

        if user_model.is_account_locked(user_row):
            flash(
                f"This account is temporarily locked due to repeated failed "
                f"login attempts. Please try again in a few minutes.",
                "error",
            )
            user_model.log_auth_event(username, "LOGIN_BLOCKED", request.remote_addr, "account locked")
            return render_template("login.html", username=username)

        if not user_model.verify_password(user_row["password_hash"], password):
            user_model.register_failed_login(
                username, Config.MAX_FAILED_LOGIN_ATTEMPTS, Config.LOCKOUT_DURATION_MINUTES
            )
            user_model.log_auth_event(username, "LOGIN_FAILURE", request.remote_addr, "bad password")
            flash(generic_error, "error")
            return render_template("login.html", username=username)

        # --- Successful login --------------------------------------------------
        user_model.reset_failed_logins(username)
        user_model.log_auth_event(username, "LOGIN_SUCCESS", request.remote_addr)

        session.clear()  # Prevent session fixation by starting a fresh session
        session.permanent = True
        session["user_id"] = user_row["id"]
        session["username"] = user_row["username"]

        flash(f"Welcome back, {user_row['username']}!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html", username="")


@app.route("/logout")
def logout():
    username = session.get("username")
    session.clear()
    if username:
        user_model.log_auth_event(username, "LOGOUT", request.remote_addr)
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    user_row = user_model.get_user_by_username(session["username"])
    return render_template("dashboard.html", user=user_row)


# ---------------------------------------------------------------------------
# Error handlers — never leak stack traces or internal details to the client
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(e):
    logging.error("Internal server error: %s", e)
    return render_template("errors/500.html"), 500


@app.errorhandler(CSRFError)
def csrf_error(e):
    flash("Your session expired or the form was invalid. Please try again.", "error")
    return redirect(url_for("login"))


@app.errorhandler(429)
def ratelimit_error(e):
    return render_template("errors/429.html"), 429


if __name__ == "__main__":
    # debug=True is fine for local development only. Never run with debug=True
    # in production — it exposes an interactive debugger/RCE risk.
    app.run(debug=Config.DEBUG, host="127.0.0.1", port=5000)
