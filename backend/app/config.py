import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
DB_PATH = os.path.join(INSTANCE_DIR, "campus_market.db")
SECRET_KEY = "campus-market-secret-2026"
TOKEN_HEADER = "Authorization"

ALLOWED_CATEGORIES = ["Books", "Electronics", "Daily Essentials", "Sports & Fitness", "Fashion & Others"]
ALLOWED_CONDITIONS = ["Brand New", "Like New", "Good", "Fair"]
PRODUCT_STATUS = ["Available", "Reserved", "Sold"]
ORDER_STATUS = ["Reserved", "Completed", "Cancelled"]

ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_UPLOAD_SIZE = 5 * 1024 * 1024
