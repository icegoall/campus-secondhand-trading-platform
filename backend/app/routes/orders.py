from datetime import datetime
from flask import Blueprint, request, jsonify, g
from ..database import query, execute, row_to_dict
from ..utils import login_required

bp = Blueprint("orders", __name__)


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@bp.route("/orders", methods=["POST"])
@login_required
def create_order():
    data = request.get_json(silent=True) or {}
    pid = data.get("product_id")
    p = row_to_dict(query("SELECT * FROM products WHERE id = ?", (pid,), one=True)) if pid else None
    if not p:
        return jsonify(code=404, message="Product not found"), 404
    if p["seller_id"] == g.current_user["id"]:
        return jsonify(code=400, message="You cannot book your own listing"), 400
    if p["status"] != "Available":
        return jsonify(code=400, message="This item is currently '%s' and cannot be booked" % p["status"]), 400

    rid = execute(
        """INSERT INTO orders (product_id, buyer_id, status, created_at, updated_at)
           VALUES (?, ?, 'Reserved', ?, ?)""",
        (pid, g.current_user["id"], now(), now()),
        lastrowid=True,
    )
    execute("UPDATE products SET status = 'Reserved' WHERE id = ?", (pid,))
    return jsonify(code=0, message="Booked! The item is locked for you until the seller confirms.",
                   data={"id": rid}), 201


@bp.route("/orders", methods=["GET"])
@login_required
def list_orders():
    mine = request.args.get("mine")
    if mine == "buyer":
        rows = query(
            """SELECT o.*, p.title AS product_title, p.image_url AS product_image, p.price AS product_price,
                      p.status AS product_status, u.nickname AS seller_name
               FROM orders o
               JOIN products p ON o.product_id = p.id
               JOIN users u ON p.seller_id = u.id
               WHERE o.buyer_id = ? ORDER BY o.created_at DESC""",
            (g.current_user["id"],),
        )
    else:
        rows = query(
            """SELECT o.*, p.title AS product_title, p.image_url AS product_image, p.price AS product_price,
                      p.status AS product_status, u.nickname AS buyer_name, u.dorm AS buyer_dorm, u.phone AS buyer_phone
               FROM orders o
               JOIN products p ON o.product_id = p.id
               JOIN users u ON o.buyer_id = u.id
               WHERE p.seller_id = ? ORDER BY o.created_at DESC""",
            (g.current_user["id"],),
        )
    return jsonify(code=0, data=[dict(r) for r in rows])


@bp.route("/orders/<int:oid>/status", methods=["PUT"])
@login_required
def update_order_status(oid):
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    if new_status not in ("Completed", "Cancelled"):
        return jsonify(code=400, message="Status must be 'Completed' or 'Cancelled'"), 400

    o = row_to_dict(query(
        """SELECT o.*, p.seller_id AS seller_id, p.status AS product_status
           FROM orders o JOIN products p ON o.product_id = p.id WHERE o.id = ?""",
        (oid,), one=True))
    if not o:
        return jsonify(code=404, message="Order not found"), 404

    is_seller = o["seller_id"] == g.current_user["id"]
    is_buyer = o["buyer_id"] == g.current_user["id"]
    if new_status == "Completed" and not is_seller:
        return jsonify(code=403, message="Only the seller can mark this order as completed"), 403
    if new_status == "Cancelled" and not (is_seller or is_buyer):
        return jsonify(code=403, message="You are not allowed to modify this order"), 403
    if o["status"] != "Reserved":
        return jsonify(code=400, message="Order is already '%s' and cannot be changed" % o["status"]), 400

    execute("UPDATE orders SET status = ?, updated_at = ? WHERE id = ?", (new_status, now(), oid))
    if new_status == "Completed":
        execute("UPDATE products SET status = 'Sold' WHERE id = ?", (o["product_id"],))
    else:
        execute("UPDATE products SET status = 'Available' WHERE id = ?", (o["product_id"],))
    return jsonify(code=0, message="Order updated to '%s'" % new_status)
