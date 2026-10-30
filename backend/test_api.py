import sys, os, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import create_app

app = create_app()
c = app.test_client()

def show(label, resp):
    body = resp.get_json()
    print(f"[{resp.status_code}] {label} -> code={body.get('code')} msg={body.get('message')}")
    return body

print("===== 1. Root =====")
show("GET /", c.get("/"))

print("\n===== 2. Login alice =====")
b = show("POST /api/login", c.post("/api/login", json={"account": "202100101", "password": "alice"}))
token = b["data"]["token"]
H = {"Authorization": token}
print("   token:", token[:16], "...")

print("\n===== 3. Wrong password =====")
show("POST /api/login(bad)", c.post("/api/login", json={"account": "202100101", "password": "wrong"}))

print("\n===== 4. Product list (pagination + search + filter) =====")
b = show("GET /api/products", c.get("/api/products?page=1&size=5"))
print("   items:", len(b["data"]["list"]), " total:", b["data"]["total"], " pages:", b["data"]["pages"])
b = show("GET /api/products?keyword=iPad&status=all", c.get("/api/products?keyword=iPad&status=all"))
print("   search:", [p["title"] for p in b["data"]["list"]])
b = show("GET /api/products?category=Books", c.get("/api/products?category=Books"))
print("   books:", [p["title"] for p in b["data"]["list"]])

print("\n===== 5. Product detail =====")
b = show("GET /api/products/1", c.get("/api/products/1"))
print("   product:", b["data"]["title"], "| seller:", b["data"]["seller"]["nickname"], "| status:", b["data"]["status"])

print("\n===== 6. Upload image (multipart) =====")
png = bytes.fromhex("89504e470d0a1a0a0000000d4948445200000001000000010806000000000000"[:36]) if False else io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 64)
b = show("POST /api/upload", c.post("/api/upload", data={"file": (png, "test.png")}, content_type="multipart/form-data", headers=H))
img_url = b["data"]["url"]
print("   uploaded url:", img_url)
b = c.get(img_url)
print("   GET", img_url, "->", b.status_code, b.content_type)

print("\n===== 7. Create product (auth) =====")
b = show("POST /api/products", c.post("/api/products", json={
    "title": "Test item — vintage headphones", "description": "Sennheiser MX400, lightly used",
    "category": "Electronics", "original_price": 30, "price": 12,
    "image_url": img_url, "condition": "Like New", "contact": "WeChat: test"
}, headers=H))
new_pid = b["data"]["id"]
print("   new product id:", new_pid)

print("\n===== 8. Create product without token (expect 401) =====")
show("POST /api/products(no token)", c.post("/api/products", json={"title": "x", "price": 1}))

print("\n===== 9. Booking flow (Available -> Reserved -> Completed) =====")
b = show("GET /api/products?status=Available", c.get("/api/products?status=Available"))
avail = [p for p in b["data"]["list"] if p["seller_id"] != 1]
print("   bookable ids:", [p["id"] for p in avail][:6])
target = avail[0]["id"]
b = show("POST /api/orders", c.post("/api/orders", json={"product_id": target}, headers=H))
b = show("GET /api/orders?mine=buyer", c.get("/api/orders?mine=buyer", headers=H))
print("   my bookings:", len(b["data"]))
oid = b["data"][0]["id"]
print("   order id:", oid, "| product:", b["data"][0]["product_title"])

print("\n===== 10. Seller confirms completion =====")
seller_id = avail[0]["seller_id"]
creds = {2: ("202100102", "bob"), 3: ("202100203", "cathy"), 4: ("202200305", "david")}
sid, pwd = creds.get(seller_id, ("202100102", "bob"))
b2 = show(f"POST /api/login(seller {sid})", c.post("/api/login", json={"account": sid, "password": pwd}))
seller_token = b2["data"]["token"]
show("PUT /api/orders/<oid>/status", c.put(f"/api/orders/{oid}/status", json={"status": "Completed"}, headers={"Authorization": seller_token}))
b = show("GET product(after complete)", c.get(f"/api/products/{target}"))
print("   product status now:", b["data"]["status"])

print("\n===== 11. Comments =====")
show("GET /api/products/1/comments", c.get("/api/products/1/comments"))
show("POST /api/products/1/comments", c.post("/api/products/1/comments", json={"content": "Is campus meet-up still possible?"}, headers=H))
b = show("GET /api/products/1/comments(after)", c.get("/api/products/1/comments"))
print("   comments:", len(b["data"]))

print("\n===== 12. My listings =====")
b = show("GET /api/my/products", c.get("/api/my/products", headers=H))
print("   mine:", [p["title"] for p in b["data"]])

print("\n===== 13. Register + duplicate =====")
show("POST /api/register", c.post("/api/register", json={
    "student_id": "202300999", "password": "test123", "nickname": "Test Student",
    "phone": "13900000000", "dorm": "Dorm 5", "campus": "Main Campus"
}))
show("POST /api/register(dup)", c.post("/api/register", json={
    "student_id": "202300999", "password": "test123", "nickname": "Dup"
}))

print("\n===== 14. /api/me =====")
show("GET /api/me", c.get("/api/me", headers=H))

print("\nALL API TESTS PASSED")
