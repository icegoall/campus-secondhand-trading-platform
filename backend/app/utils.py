import secrets
from functools import wraps
from flask import request, jsonify, g
from .config import TOKEN_HEADER
from .database import query, row_to_dict


def generate_token():
    return secrets.token_hex(32)


def get_current_user():
    token = request.headers.get(TOKEN_HEADER, "")
    if not token:
        return None
    row = query("SELECT * FROM users WHERE token = ?", (token,), one=True)
    return row_to_dict(row)


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify(code=401, message="Not logged in or session expired. Please sign in again."), 401
        g.current_user = user
        return fn(*args, **kwargs)
    return wrapper


def validate_password(pwd):
    if not isinstance(pwd, str) or len(pwd) < 6:
        return "Password must be at least 6 characters"
    return None
