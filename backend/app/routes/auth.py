from datetime import datetime
from flask import Blueprint, request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from ..database import query, execute, row_to_dict
from ..utils import generate_token, login_required, validate_password

bp = Blueprint("auth", __name__)


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def public_user(u):
    return {
        "id": u["id"],
        "student_id": u["student_id"],
        "phone": u["phone"],
        "nickname": u["nickname"],
        "dorm": u["dorm"],
        "campus": u["campus"],
        "avatar": u["avatar"],
    }


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    student_id = (data.get("student_id") or "").strip()
    nickname = (data.get("nickname") or "").strip()
    password = data.get("password") or ""

    if not student_id or not nickname:
        return jsonify(code=400, message="Student ID and nickname are required"), 400
    err = validate_password(password)
    if err:
        return jsonify(code=400, message=err), 400

    exists = query("SELECT id FROM users WHERE student_id = ?", (student_id,), one=True)
    if exists:
        return jsonify(code=409, message="This student ID is already registered"), 409

    rid = execute(
        """INSERT INTO users (student_id, phone, password_hash, nickname, dorm, campus, avatar, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            student_id,
            (data.get("phone") or "").strip(),
            generate_password_hash(password),
            nickname,
            (data.get("dorm") or "").strip(),
            (data.get("campus") or "Main Campus").strip(),
            data.get("avatar") or "",
            now(),
        ),
        lastrowid=True,
    )
    u = row_to_dict(query("SELECT * FROM users WHERE id = ?", (rid,), one=True))
    return jsonify(code=0, message="Registered successfully", data=public_user(u)), 201


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    account = (data.get("account") or data.get("student_id") or "").strip()
    password = data.get("password") or ""
    if not account or not password:
        return jsonify(code=400, message="Please enter your student ID and password"), 400

    u = row_to_dict(query("SELECT * FROM users WHERE student_id = ?", (account,), one=True))
    if not u:
        return jsonify(code=404, message="Account not found"), 404
    if not check_password_hash(u["password_hash"], password):
        return jsonify(code=401, message="Incorrect password"), 401

    token = generate_token()
    execute("UPDATE users SET token = ? WHERE id = ?", (token, u["id"]))
    u["token"] = token
    return jsonify(code=0, message="Login successful", data={"token": token, "user": public_user(u)})


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    execute("UPDATE users SET token = NULL WHERE id = ?", (g.current_user["id"],))
    return jsonify(code=0, message="Logged out")


@bp.route("/me", methods=["GET"])
@login_required
def me():
    return jsonify(code=0, data=public_user(g.current_user))
