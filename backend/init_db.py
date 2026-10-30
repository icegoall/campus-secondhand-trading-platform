import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import init_schema, DB_PATH
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def img(photo_id):
    return f"https://images.unsplash.com/{photo_id}?w=600&q=80&auto=format&fit=crop"


def seed():
    init_schema()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS c FROM users")
    if cur.fetchone()["c"] > 0:
        print("Database already seeded. Delete instance/campus_market.db to reset.")
        conn.close()
        return

    users = [
        ("202100101", "13800000001", "alice", "Alice", "Dorm 1", "Main Campus",
         "https://api.dicebear.com/7.x/avataaars/svg?seed=alice"),
        ("202100102", "13800000002", "bob", "Bob", "Dorm 3", "Main Campus",
         "https://api.dicebear.com/7.x/avataaars/svg?seed=bob"),
        ("202100203", "13800000003", "cathy", "Cathy", "Dorm 7", "South Campus",
         "https://api.dicebear.com/7.x/avataaars/svg?seed=cathy"),
        ("202200305", "13800000004", "david", "David", "Dorm 2", "Main Campus",
         "https://api.dicebear.com/7.x/avataaars/svg?seed=david"),
    ]
    for sid, phone, pwd, nick, dorm, campus, avatar in users:
        cur.execute(
            """INSERT INTO users (student_id, phone, password_hash, nickname, dorm, campus, avatar, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (sid, phone, generate_password_hash(pwd), nick, dorm, campus, avatar, now()),
        )
    conn.commit()
    uid_map = {r["student_id"]: r["id"] for r in cur.execute("SELECT id, student_id FROM users")}

    products = [
        (uid_map["202100101"], "iPad Air 4 — Like New",
         "Used for one year, no scratches or dents. Original charger included. Selling because I upgraded.",
         "Electronics", 670, 390, img("photo-1544244015-0df4b3ffc6b0"), "Like New", "WeChat: alice_ipad"),
        (uid_map["202100101"], "Advanced Mathematics (Tongji 7th Ed.) Vol. 1 & 2",
         "Finals are over. My notes are inside — they might help. Free campus delivery.",
         "Books", 12, 5, img("photo-1509228468518-180dd4864904"), "Good", "QQ: 10001"),
        (uid_map["202100102"], "Logitech G304 Wireless Mouse",
         "Used for six months. Minor scuffs on the battery cover, works perfectly.",
         "Electronics", 30, 15, img("photo-1527864550417-7fd91fc51a46"), "Good", "WeChat: bob_mouse"),
        (uid_map["202100102"], "USB Desk Fan for Dorm",
         "Graduation clearance. Quiet model with adjustable angle. Perfect for summer nights.",
         "Daily Essentials", 15, 5, img("photo-1522708323590-d24dbb6b0267"), "Fair", "Tel: 13800000002"),
        (uid_map["202100203"], "Yonex NR700 Badminton Racket",
         "Bought six months ago. Strung at 26 lbs. Racket bag and a tube of shuttlecocks included.",
         "Sports & Fitness", 185, 95, img("photo-1626224583764-f87db24ac4ea"), "Like New", "WeChat: cathy_racket"),
        (uid_map["202100203"], "Graduate English Exam Prep Papers (2010–2023)",
         "Only the first three years are done; the rest is blank. Great for practice.",
         "Books", 18, 8, img("photo-1497633762265-9d179a990aa6"), "Like New", "QQ: 20003"),
        (uid_map["202200305"], "Nike Kyrie 7 Basketball Shoes (US 8)",
         "Worn only a few times. Clean soles, original box. Great grip on the court.",
         "Fashion & Others", 130, 60, img("photo-1549298916-b41d501d3772"), "Like New", "WeChat: david_shoe"),
        (uid_map["202200305"], "Xiaomi Desk Lamp Pro (Eye-care)",
         "Moving out of the dorm — almost brand new. Adjustable color temperature.",
         "Daily Essentials", 36, 18, img("photo-1507473885765-e6ed057f782c"), "Brand New", "Tel: 13800000004"),
        (uid_map["202100101"], "87-Key Mechanical Keyboard (Red Switches)",
         "Keycaps were swapped once; the original set is included. Satisfying typing feel.",
         "Electronics", 58, 26, img("photo-1587829741301-dc798b83add3"), "Good", "WeChat: alice_kb"),
        (uid_map["202100102"], "University Physics (6th Ed., Cheng Shouzhu)",
         "Light pencil notes that can be erased. All pages intact.",
         "Books", 9, 3, img("photo-1532012197267-da84d127e765"), "Fair", "QQ: 10002"),
        (uid_map["202100203"], "TPE Yoga Mat — Extra Thick 6mm",
         "Used only twice. Purple, non-slip, comes with a carry strap.",
         "Sports & Fitness", 20, 9, img("photo-1544367567-0f2fcb009e0b"), "Like New", "WeChat: cathy_yoga"),
        (uid_map["202200305"], "JBL GO 3 Bluetooth Speaker",
         "Waterproof, punchy sound. Charging cable included. Great for dorm hangouts.",
         "Electronics", 45, 22, img("photo-1545454675-3531b543be5d"), "Like New", "Tel: 13800000004"),
    ]
    for seller_id, title, desc, cat, op, pr, image, cond, contact in products:
        cur.execute(
            """INSERT INTO products (seller_id, title, description, category, original_price, price,
               image_url, condition, contact, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Available', ?)""",
            (seller_id, title, desc, cat, op, pr, image, cond, contact, now()),
        )
    conn.commit()

    pid1 = cur.execute("SELECT id FROM products WHERE title LIKE '%iPad%'").fetchone()["id"]
    pid2 = cur.execute("SELECT id FROM products WHERE title LIKE '%G304%'").fetchone()["id"]
    buyer1 = uid_map["202200305"]
    buyer2 = uid_map["202100203"]
    ts = now()
    cur.execute(
        """INSERT INTO orders (product_id, buyer_id, status, created_at, updated_at)
           VALUES (?, ?, 'Reserved', ?, ?)""", (pid1, buyer1, ts, ts))
    cur.execute("UPDATE products SET status='Reserved' WHERE id=?", (pid1,))
    cur.execute(
        """INSERT INTO orders (product_id, buyer_id, status, created_at, updated_at)
           VALUES (?, ?, 'Reserved', ?, ?)""", (pid2, buyer2, ts, ts))
    cur.execute("UPDATE products SET status='Reserved' WHERE id=?", (pid2,))

    cur.execute(
        "INSERT INTO comments (product_id, user_id, content, created_at) VALUES (?, ?, ?, ?)",
        (pid1, buyer2, "How is the battery health? Any scratches on the screen?", now()))
    cur.execute(
        "INSERT INTO comments (product_id, user_id, content, created_at) VALUES (?, ?, ?, ?)",
        (pid1, uid_map["202100101"], "Screen is flawless — happy to meet on campus so you can check it in person.", now()))
    conn.commit()
    conn.close()
    print("Seed complete: 4 users, 12 products, 2 bookings, 2 comments")
    print("Demo accounts (student ID / password):")
    print("  202100101 / alice   (Alice)")
    print("  202100102 / bob     (Bob)")
    print("  202100203 / cathy   (Cathy)")
    print("  202200305 / david   (David)")


if __name__ == "__main__":
    seed()
