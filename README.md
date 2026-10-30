# Campus Market — Second-Hand Trading Platform (Lab 6)

A full-stack campus second-hand marketplace: **Vue 3 + Vite + Element Plus** frontend, **Flask + SQLite** backend.

## Tech Stack

| Layer | Stack |
|-------|-------|
| Frontend | Vue 3 (`<script setup>` Composition API), Vite, Element Plus, Axios, Vue Router, Pinia |
| Backend | Python 3 + Flask (hand-written CORS middleware, native `sqlite3` wrapper) |
| Database | SQLite (`backend/instance/campus_market.db`) |

> The assignment allows "Flask-SQLAlchemy **or** a native sqlite3 wrapper". This project uses the **native sqlite3 wrapper** (`backend/app/database.py`), so the backend needs **no extra pip installs** beyond Flask.

## Project Structure

```
├── backend/                    # Flask backend
│   ├── app/
│   │   ├── __init__.py         # App factory create_app() + CORS + /uploads static route
│   │   ├── config.py           # Config (paths, English enum constants)
│   │   ├── database.py         # sqlite3 wrapper + schema DDL
│   │   ├── utils.py            # Token generation/validation, login_required decorator
│   │   └── routes/
│   │       ├── auth.py         # Register / Login / Logout / Me
│   │       ├── products.py     # Product CRUD + pagination + keyword search + category/status filter
│   │       ├── orders.py       # Booking + status flow (Available → Reserved → Sold / back to Available)
│   │       ├── comments.py     # Comments / Q&A
│   │       └── upload.py       # Image upload (multipart, ≤5MB, png/jpg/jpeg/gif/webp)
│   ├── static/uploads/         # Uploaded listing photos (served at /uploads/<file>)
│   ├── init_db.py              # Schema + English mock data seeding
│   ├── test_api.py             # API self-test (Flask test_client, no server needed)
│   └── run.py                  # Entry point
├── frontend/                   # Vue 3 frontend
│   ├── src/
│   │   ├── api/                # request.js (axios wrapper) + index.js (business APIs)
│   │   ├── assets/             # Global theme (indigo/slate, rounded cards, shadows)
│   │   ├── components/         # ProductCard.vue
│   │   ├── views/              # Home / Login / Register / Publish / ProductDetail / Profile
│   │   ├── router/             # Routes + auth guard
│   │   ├── stores/             # Pinia user store (token persisted to localStorage)
│   │   └── constants.js        # Categories, conditions, statuses, price formatting
│   ├── vite.config.js          # Dev proxy: /api and /uploads → 127.0.0.1:5000
│   └── package.json
└── README.md
```

## Database Schema (4 tables)

- `users`: id, student_id (unique), phone, password_hash, nickname, dorm, campus, avatar, token, created_at
- `products`: id, seller_id (FK), title, description, category, original_price, price, image_url, condition, contact, status, created_at
- `orders`: id, product_id (FK), buyer_id (FK), status, created_at, updated_at
- `comments`: id, product_id (FK), user_id (FK), content, created_at

**Enums**
- Category: `Books`, `Electronics`, `Daily Essentials`, `Sports & Fitness`, `Fashion & Others`
- Condition: `Brand New`, `Like New`, `Good`, `Fair`
- Product status flow: `Available` → booked → `Reserved` → seller confirms → `Sold` (cancel → back to `Available`)
- Order status: `Reserved` → `Completed` / `Cancelled`

## Getting Started

### 1. Backend (Python 3 + Flask)

```bash
cd backend
python init_db.py     # First run: create tables + seed mock data
python run.py         # Serve API at http://127.0.0.1:5000
```

Optional — run the API self-test (14 checks, no server required):

```bash
cd backend
python test_api.py
```

### 2. Frontend (Node.js)

```bash
cd frontend
npm install           # First run only (if esbuild postinstall fails: npm install --ignore-scripts)
npm run dev           # Serve at http://localhost:5173
```

Open **http://localhost:5173** — Vite proxies `/api` and `/uploads` to `http://127.0.0.1:5000`, so no CORS issues.

### 3. Production build (optional)

```bash
cd frontend
npm run build
```

## Demo Accounts

| Student ID | Password | Nickname |
|-----------|----------|----------|
| 202100101 | alice | Alice |
| 202100102 | bob | Bob |
| 202100203 | cathy | Cathy |
| 202200305 | david | David |

## API Overview

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/register` | Register | No |
| POST | `/api/login` | Login (returns token) | No |
| POST | `/api/logout` | Logout | Yes |
| GET | `/api/me` | Current user | Yes |
| GET | `/api/products` | List (`page/size/keyword/category/status`) | No |
| GET | `/api/products/<id>` | Product detail | No |
| POST | `/api/products` | Publish listing | Yes |
| PUT | `/api/products/<id>` | Update listing | Yes (seller only) |
| DELETE | `/api/products/<id>` | Delete listing | Yes (seller, only when Available) |
| GET | `/api/my/products` | My listings | Yes |
| POST | `/api/orders` | Book an item | Yes |
| GET | `/api/orders?mine=buyer\|seller` | My bookings / Received bookings | Yes |
| PUT | `/api/orders/<id>/status` | Order status flow | Yes (seller confirms Completed) |
| GET | `/api/products/<id>/comments` | Comment list | No |
| POST | `/api/products/<id>/comments` | Post a comment | Yes |
| POST | `/api/upload` | Upload listing image (multipart `file`) | Yes |

Auth: send `Authorization: <token>` header (token generated at login, stored in `users.token`).

## Feature Checklist (per lab requirements)

- **User system**: register (student ID/phone/nickname/dorm/campus), login, logout, auth guard ✅
- **Publishing & browsing**: publish (title/description/category/original price/selling price/image/condition/contact), home grid + pagination + keyword search + category filter + status filter, product detail ✅
- **Trading/booking**: booking flow (Available → Reserved → Sold), comments/Q&A ✅
- **Profile**: My Listings, My Bookings, Received Bookings (seller confirms/declines) ✅

## Production-grade upgrades in this version

- **Images**: realistic Unsplash cover images in seed data; elegant category-based gradient fallback (emoji + label) on load failure or empty URL; local image upload + URL live preview in Publish
- **Localization**: UI, enums, mock data and API messages fully in English
- **Theme**: indigo/slate palette, Inter typography, rounded-2xl cards, hover-lift transitions, badge colors per status
- **UX**: 350 ms debounced search, skeleton loading grid, contextual empty states, ElMessage toasts on publish/book/confirm/comment/delete, client-side form validation (publish/register), ¥ price formatting with strikethrough original price and % OFF badge

## Notes

- Passwords are stored hashed via Werkzeug `generate_password_hash`.
- Uploaded images are stored under `backend/static/uploads/` (≤ 5 MB, image types only) and served at `/uploads/<file>`.
- Delete `backend/instance/campus_market.db` and rerun `python init_db.py` to reset demo data.
