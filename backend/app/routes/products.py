from datetime import datetime
from flask import Blueprint, request, jsonify, g
from ..database import query, execute, row_to_dict
from ..utils import login_required
from ..config import ALLOWED_CATEGORIES, ALLOWED_CONDITIONS, PRODUCT_STATUS

bp = Blueprint("products", __name__)


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@bp.route("/products", methods=["GET"])
def list_products():
    page = max(int(request.args.get("page", 1)), 1)
    size = min(max(int(request.args.get("size", 12)), 1), 60)
    keyword = (request.args.get("keyword") or "").strip()
    category = (request.args.get("category") or "").strip()
    status = (request.args.get("status", "Available")).strip()

    where = []
    args = []
    if status and status != "all":
        where.append("p.status = ?")
        args.append(status)
    if category:
        where.append("p.category = ?")
        args.append(category)
    if keyword:
        where.append("(p.title LIKE ? OR p.description LIKE ?)")
        kw = f"%{keyword}%"
        args += [kw, kw]

    clause = (" WHERE " + " AND ".join(where)) if where else ""
    total = row_to_dict(query(f"SELECT COUNT(*) AS c FROM products p{clause}", args, one=True))["c"]
    offset = (page - 1) * size
    rows = query(
        f"""SELECT p.*, u.nickname AS seller_name, u.dorm AS seller_dorm
            FROM products p LEFT JOIN users u ON p.seller_id = u.id
            {clause}
            ORDER BY p.created_at DESC LIMIT ? OFFSET ?""",
        args + [size, offset],
    )
    items = []
    for r in rows:
        d = dict(r)
        d["seller"] = {"id": d["seller_id"], "nickname": d.pop("seller_name"), "dorm": d.pop("seller_dorm")}
        items.append(d)
    return jsonify(code=0, data={"list": items, "page": page, "size": size, "total": total,
                                 "pages": (total + size - 1) // size})


@bp.route("/products/<int:pid>", methods=["GET"])
def get_product(pid):
    p = row_to_dict(query(
        """SELECT p.*, u.nickname AS seller_name, u.dorm AS seller_dorm, u.phone AS seller_phone, u.student_id AS seller_sid
           FROM products p LEFT JOIN users u ON p.seller_id = u.id
           WHERE p.id = ?""", (pid,), one=True))
    if not p:
        return jsonify(code=404, message="Product not found"), 404
    d = dict(p)
    d["seller"] = {
        "id": d["seller_id"],
        "nickname": d.pop("seller_name"),
        "dorm": d.pop("seller_dorm"),
        "phone": d.pop("seller_phone"),
        "student_id": d.pop("seller_sid"),
    }
    return jsonify(code=0, data=d)


@bp.route("/products", methods=["POST"])
@login_required
def create_product():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify(code=400, message="Title is required"), 400
    try:
        price = float(data.get("price"))
    except (TypeError, ValueError):
        return jsonify(code=400, message="Invalid price format"), 400
    category = data.get("category") or "Fashion & Others"
    if category not in ALLOWED_CATEGORIES:
        category = "Fashion & Others"
    condition = data.get("condition") or "Like New"
    if condition not in ALLOWED_CONDITIONS:
        condition = "Like New"

    rid = execute(
        """INSERT INTO products (seller_id, title, description, category, original_price, price,
           image_url, condition, contact, status, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Available', ?)""",
        (
            g.current_user["id"],
            title,
            (data.get("description") or "").strip(),
            category,
            float(data.get("original_price") or 0),
            price,
            data.get("image_url") or "",
            condition,
            (data.get("contact") or "").strip(),
            now(),
        ),
        lastrowid=True,
    )
    return jsonify(code=0, message="Listing published", data={"id": rid}), 201


@bp.route("/products/<int:pid>", methods=["PUT"])
@login_required
def update_product(pid):
    p = row_to_dict(query("SELECT * FROM products WHERE id = ?", (pid,), one=True))
    if not p:
        return jsonify(code=404, message="Product not found"), 404
    if p["seller_id"] != g.current_user["id"]:
        return jsonify(code=403, message="You can only edit your own listings"), 403
    data = request.get_json(silent=True) or {}
    fields = ["title", "description", "category", "original_price", "price", "image_url", "condition", "contact"]
    sets, args = [], []
    for f in fields:
        if f in data:
            sets.append(f"{f} = ?")
            args.append(float(data[f]) if f in ("original_price", "price") else data[f])
    if data.get("status") in PRODUCT_STATUS:
        sets.append("status = ?")
        args.append(data["status"])
    if not sets:
        return jsonify(code=0, message="No fields to update")
    args.append(pid)
    execute(f"UPDATE products SET {', '.join(sets)} WHERE id = ?", args)
    return jsonify(code=0, message="Listing updated")


@bp.route("/products/<int:pid>", methods=["DELETE"])
@login_required
def delete_product(pid):
    p = row_to_dict(query("SELECT * FROM products WHERE id = ?", (pid,), one=True))
    if not p:
        return jsonify(code=404, message="Product not found"), 404
    if p["seller_id"] != g.current_user["id"]:
        return jsonify(code=403, message="You can only delete your own listings"), 403
    if p["status"] != "Available":
        return jsonify(code=400, message="Only listings marked 'Available' can be deleted"), 400
    execute("DELETE FROM comments WHERE product_id = ?", (pid,))
    execute("DELETE FROM products WHERE id = ?", (pid,))
    return jsonify(code=0, message="Listing deleted")


@bp.route("/my/products", methods=["GET"])
@login_required
def my_products():
    rows = query("SELECT * FROM products WHERE seller_id = ? ORDER BY created_at DESC",
                 (g.current_user["id"],))
    return jsonify(code=0, data=[dict(r) for r in rows])
