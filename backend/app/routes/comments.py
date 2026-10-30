from datetime import datetime
from flask import Blueprint, request, jsonify, g
from ..database import query, execute
from ..utils import login_required

bp = Blueprint("comments", __name__)


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@bp.route("/products/<int:pid>/comments", methods=["GET"])
def list_comments(pid):
    rows = query(
        """SELECT c.*, u.nickname AS user_name, u.avatar AS user_avatar
           FROM comments c JOIN users u ON c.user_id = u.id
           WHERE c.product_id = ? ORDER BY c.created_at DESC""",
        (pid,),
    )
    return jsonify(code=0, data=[dict(r) for r in rows])


@bp.route("/products/<int:pid>/comments", methods=["POST"])
@login_required
def add_comment(pid):
    p = query("SELECT id FROM products WHERE id = ?", (pid,), one=True)
    if not p:
        return jsonify(code=404, message="Product not found"), 404
    data = request.get_json(silent=True) or {}
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify(code=400, message="Comment cannot be empty"), 400
    rid = execute(
        "INSERT INTO comments (product_id, user_id, content, created_at) VALUES (?, ?, ?, ?)",
        (pid, g.current_user["id"], content, now()),
        lastrowid=True,
    )
    return jsonify(code=0, message="Comment posted", data={
        "id": rid, "product_id": pid, "user_id": g.current_user["id"],
        "user_name": g.current_user["nickname"], "user_avatar": g.current_user["avatar"],
        "content": content, "created_at": now(),
    }), 201
