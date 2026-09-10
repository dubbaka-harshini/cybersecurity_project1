"""
utils/decorators.py
--------------------
`login_required` guards protected routes (e.g. /dashboard). Any
unauthenticated request is redirected to the login page instead of
leaking whether the page exists or what data it contains — this
prevents unauthorized access to protected resources.
"""

from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access that page.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped_view
