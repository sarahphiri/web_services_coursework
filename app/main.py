from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
import sqlite3
import os
from typing import Optional
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

security = HTTPBearer()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE = os.path.join(PROJECT_ROOT, "travel.db")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://web-services-coursework.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS destinations (
            id INTEGER PRIMARY KEY,
            name TEXT,
            country TEXT,
            continent TEXT,
            type TEXT,
            best_season TEXT,
            avg_cost_usd REAL,
            rating REAL,
            annual_visitors_m REAL,
            unesco INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wishlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wishlist_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wishlist_id INTEGER NOT NULL,
            destination_id INTEGER NOT NULL,
            notes TEXT,
            priority INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (wishlist_id) REFERENCES wishlists(id),
            FOREIGN KEY (destination_id) REFERENCES destinations(id)
        )
    """)

    conn.commit()
    conn.close()


@app.on_event("startup")
def startup():
    init_db()


class AuthRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Email cannot be blank")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Password cannot be blank")
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return value


class WishlistCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Wishlist name cannot be blank")
        return value


class WishlistUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class WishlistItemCreateRequest(BaseModel):
    destination_id: int
    notes: Optional[str] = None
    priority: Optional[int] = None


class WishlistItemUpdateRequest(BaseModel):
    notes: Optional[str] = None
    priority: Optional[int] = None


def get_user_id_from_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    token = credentials.credentials

    if not token.startswith("demo-token-"):
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        return int(token.replace("demo-token-", ""))
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/")
def root():
    return {"message": "FastAPI is running", "database": DATABASE}


# =========================
# AUTH
# =========================

@app.post("/auth/register")
def register_user(payload: AuthRequest):
    email = payload.email.strip().lower()
    password = payload.password.strip()

    conn = get_connection()
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists."
        )

    cursor.execute(
        "INSERT INTO users (email, password) VALUES (?, ?)",
        (email, password)
    )

    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    return {
        "message": "User registered successfully",
        "user_id": user_id
    }


@app.post("/auth/login")
def login_user(payload: AuthRequest):
    email = payload.email.strip().lower()
    password = payload.password.strip()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, email FROM users WHERE email = ? AND password = ?",
        (email, password)
    )
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "access_token": f"demo-token-{user['id']}",
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"]
        }
    }


# =========================
# DESTINATIONS
# =========================

@app.get("/destinations")
def get_destinations(
    limit: int = Query(default=100, ge=1),
    offset: int = Query(default=0, ge=0)
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id, name, country, continent, type, best_season,
            avg_cost_usd, rating, annual_visitors_m, unesco
        FROM destinations
        ORDER BY id ASC
        LIMIT ? OFFSET ?
    """, (limit, offset))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


@app.get("/destinations/count")
def get_destinations_count():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM destinations")
    count = cursor.fetchone()["count"]
    conn.close()

    return {"count": count}


@app.get("/destinations/{destination_id}")
def get_destination(destination_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id, name, country, continent, type, best_season,
            avg_cost_usd, rating, annual_visitors_m, unesco
        FROM destinations
        WHERE id = ?
    """, (destination_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Destination not found")

    return dict(row)


# =========================
# RECOMMENDATIONS
# =========================

@app.get("/recommendations")
def get_recommendations(
    continent: Optional[str] = Query(default=None),
    country: Optional[str] = Query(default=None),
    min_rating: Optional[float] = Query(default=None),
    max_cost: Optional[float] = Query(default=None),
    sort_by: Optional[str] = Query(default=None),
):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            id,
            name,
            country,
            continent,
            type,
            best_season,
            avg_cost_usd,
            rating,
            annual_visitors_m,
            unesco,
            ROUND(
                CASE
                    WHEN avg_cost_usd IS NULL THEN 0
                    ELSE 1000.0 / (avg_cost_usd + 1)
                END, 2
            ) AS affordability_score,
            ROUND(
                CASE
                    WHEN annual_visitors_m IS NULL THEN 0
                    ELSE 10.0 / (annual_visitors_m + 1)
                END, 2
            ) AS quietness_score,
            ROUND(COALESCE(rating, 0), 2) AS quality_score,
            ROUND(
                COALESCE(rating, 0) + 
                CASE
                    WHEN annual_visitors_m IS NULL THEN 0
                    ELSE 10.0 / (annual_visitors_m + 1)
                END,
                2
            ) AS hidden_gem_score,
            ROUND(
                CASE
                    WHEN avg_cost_usd IS NULL THEN 0
                    ELSE 1000.0 / (avg_cost_usd + 1)
                END +
                CASE
                    WHEN annual_visitors_m IS NULL THEN 0
                    ELSE 10.0 / (annual_visitors_m + 1)
                END +
                COALESCE(rating, 0),
                2
            ) AS barrier_score
        FROM destinations
        WHERE 1=1
    """
    params = []

    if continent:
        query += " AND continent = ?"
        params.append(continent)

    if country:
        query += " AND country LIKE ?"
        params.append(f"%{country}%")

    if min_rating is not None:
        query += " AND rating >= ?"
        params.append(min_rating)

    if max_cost is not None:
        query += " AND avg_cost_usd <= ?"
        params.append(max_cost)

    allowed_sort = {
        "rating": "rating DESC",
        "cost_asc": "avg_cost_usd ASC",
        "cost_desc": "avg_cost_usd DESC",
        "visitors_asc": "annual_visitors_m ASC",
        "visitors_desc": "annual_visitors_m DESC",
        "name": "name ASC",
        "affordability": "affordability_score DESC",
        "quietness": "quietness_score DESC",
        "quality": "quality_score DESC",
        "hidden_gem": "hidden_gem_score DESC",
    }

    query += f" ORDER BY {allowed_sort.get(sort_by, 'barrier_score DESC')}"

    cursor.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return rows


# =========================
# WISHLISTS
# =========================

@app.get("/wishlists")
def get_wishlists(user_id: int = Depends(get_user_id_from_auth)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, user_id, name, description, created_at
        FROM wishlists
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))

    wishlists = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return wishlists


@app.post("/wishlists")
def create_wishlist(
    payload: WishlistCreateRequest,
    user_id: int = Depends(get_user_id_from_auth)
):
    #user_id = get_user_id_from_auth(authorization)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO wishlists (user_id, name, description)
        VALUES (?, ?, ?)
    """, (user_id, payload.name, payload.description))
    conn.commit()

    wishlist_id = cursor.lastrowid

    cursor.execute("""
        SELECT id, user_id, name, description, created_at
        FROM wishlists
        WHERE id = ?
    """, (wishlist_id,))
    row = dict(cursor.fetchone())
    conn.close()

    return row


@app.get("/wishlists/{wishlist_id}")
def get_wishlist(
    wishlist_id: int,
    user_id: int = Depends(get_user_id_from_auth)
):
    #user_id = get_user_id_from_auth(authorization)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, user_id, name, description, created_at
        FROM wishlists
        WHERE id = ? AND user_id = ?
    """, (wishlist_id, user_id))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Wishlist not found")

    return dict(row)


@app.patch("/wishlists/{wishlist_id}")
def update_wishlist(
    wishlist_id: int,
    payload: WishlistUpdateRequest,
    user_id: int = Depends(get_user_id_from_auth)
):
    #user_id = get_user_id_from_auth(authorization)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, description
        FROM wishlists
        WHERE id = ? AND user_id = ?
    """, (wishlist_id, user_id))
    current = cursor.fetchone()

    if not current:
        conn.close()
        raise HTTPException(status_code=404, detail="Wishlist not found")

    new_name = payload.name if payload.name is not None else current["name"]
    new_description = (
        payload.description if payload.description is not None else current["description"]
    )

    cursor.execute("""
        UPDATE wishlists
        SET name = ?, description = ?
        WHERE id = ? AND user_id = ?
    """, (new_name, new_description, wishlist_id, user_id))
    conn.commit()

    cursor.execute("""
        SELECT id, user_id, name, description, created_at
        FROM wishlists
        WHERE id = ? AND user_id = ?
    """, (wishlist_id, user_id))
    updated = dict(cursor.fetchone())
    conn.close()

    return updated


@app.delete("/wishlists/{wishlist_id}")
def delete_wishlist(
    wishlist_id: int,
    user_id: int = Depends(get_user_id_from_auth)
):
    #user_id = get_user_id_from_auth(authorization)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM wishlists
        WHERE id = ? AND user_id = ?
    """, (wishlist_id, user_id))
    exists = cursor.fetchone()

    if not exists:
        conn.close()
        raise HTTPException(status_code=404, detail="Wishlist not found")

    cursor.execute("DELETE FROM wishlist_items WHERE wishlist_id = ?", (wishlist_id,))
    cursor.execute("DELETE FROM wishlists WHERE id = ? AND user_id = ?", (wishlist_id, user_id))
    conn.commit()
    conn.close()

    return {"message": "Wishlist deleted successfully"}


@app.post("/wishlists/{wishlist_id}/items")
def add_wishlist_item(
    wishlist_id: int,
    payload: WishlistItemCreateRequest,
    user_id: int = Depends(get_user_id_from_auth)
):
    #user_id = get_user_id_from_auth(authorization)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM wishlists
        WHERE id = ? AND user_id = ?
    """, (wishlist_id, user_id))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Wishlist not found")

    cursor.execute("SELECT id FROM destinations WHERE id = ?", (payload.destination_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Destination not found")

    cursor.execute("""
        SELECT id FROM wishlist_items
        WHERE wishlist_id = ? AND destination_id = ?
    """, (wishlist_id, payload.destination_id))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Destination already in wishlist")

    cursor.execute("""
        INSERT INTO wishlist_items (wishlist_id, destination_id, notes, priority)
        VALUES (?, ?, ?, ?)
    """, (wishlist_id, payload.destination_id, payload.notes, payload.priority))
    conn.commit()

    item_id = cursor.lastrowid

    cursor.execute("""
        SELECT
            wi.id,
            wi.wishlist_id,
            wi.destination_id,
            wi.notes,
            wi.priority,
            wi.created_at,
            d.id as destination_inner_id,
            d.name,
            d.country,
            d.continent,
            d.type,
            d.best_season,
            d.avg_cost_usd,
            d.rating,
            d.annual_visitors_m,
            d.unesco
        FROM wishlist_items wi
        JOIN destinations d ON wi.destination_id = d.id
        WHERE wi.id = ?
    """, (item_id,))
    row = dict(cursor.fetchone())
    conn.close()

    return row


@app.get("/wishlists/{wishlist_id}/items")
def list_wishlist_items(
    wishlist_id: int,
    user_id: int = Depends(get_user_id_from_auth)
):
    #user_id = get_user_id_from_auth(authorization)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM wishlists
        WHERE id = ? AND user_id = ?
    """, (wishlist_id, user_id))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Wishlist not found")

    cursor.execute("""
        SELECT
            wi.id,
            wi.wishlist_id,
            wi.destination_id,
            wi.notes,
            wi.priority,
            wi.created_at,
            d.id as destination_inner_id,
            d.name,
            d.country,
            d.continent,
            d.type,
            d.best_season,
            d.avg_cost_usd,
            d.rating,
            d.annual_visitors_m,
            d.unesco
        FROM wishlist_items wi
        JOIN destinations d ON wi.destination_id = d.id
        WHERE wi.wishlist_id = ?
        ORDER BY wi.created_at DESC, wi.id DESC
    """, (wishlist_id,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return rows


@app.get("/wishlists/{wishlist_id}/items/{item_id}")
def get_wishlist_item(
    wishlist_id: int,
    item_id: int,
    user_id: int = Depends(get_user_id_from_auth)
):
    #user_id = get_user_id_from_auth(authorization)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM wishlists
        WHERE id = ? AND user_id = ?
    """, (wishlist_id, user_id))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Wishlist not found")

    cursor.execute("""
        SELECT
            wi.id,
            wi.wishlist_id,
            wi.destination_id,
            wi.notes,
            wi.priority,
            wi.created_at,
            d.id as destination_inner_id,
            d.name,
            d.country,
            d.continent,
            d.type,
            d.best_season,
            d.avg_cost_usd,
            d.rating,
            d.annual_visitors_m,
            d.unesco
        FROM wishlist_items wi
        JOIN destinations d ON wi.destination_id = d.id
        WHERE wi.wishlist_id = ? AND wi.id = ?
    """, (wishlist_id, item_id))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Wishlist item not found")

    return dict(row)


@app.patch("/wishlists/{wishlist_id}/items/{item_id}")
def update_wishlist_item(
    wishlist_id: int,
    item_id: int,
    payload: WishlistItemUpdateRequest,
    user_id: int = Depends(get_user_id_from_auth)
):
    #user_id = get_user_id_from_auth(authorization)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM wishlists
        WHERE id = ? AND user_id = ?
    """, (wishlist_id, user_id))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Wishlist not found")

    cursor.execute("""
        SELECT notes, priority
        FROM wishlist_items
        WHERE wishlist_id = ? AND id = ?
    """, (wishlist_id, item_id))
    current = cursor.fetchone()

    if not current:
        conn.close()
        raise HTTPException(status_code=404, detail="Wishlist item not found")

    new_notes = payload.notes if payload.notes is not None else current["notes"]
    new_priority = payload.priority if payload.priority is not None else current["priority"]

    cursor.execute("""
        UPDATE wishlist_items
        SET notes = ?, priority = ?
        WHERE wishlist_id = ? AND id = ?
    """, (new_notes, new_priority, wishlist_id, item_id))
    conn.commit()

    cursor.execute("""
        SELECT
            wi.id,
            wi.wishlist_id,
            wi.destination_id,
            wi.notes,
            wi.priority,
            wi.created_at,
            d.id as destination_inner_id,
            d.name,
            d.country,
            d.continent,
            d.type,
            d.best_season,
            d.avg_cost_usd,
            d.rating,
            d.annual_visitors_m,
            d.unesco
        FROM wishlist_items wi
        JOIN destinations d ON wi.destination_id = d.id
        WHERE wi.wishlist_id = ? AND wi.id = ?
    """, (wishlist_id, item_id))
    updated = dict(cursor.fetchone())
    conn.close()

    return updated


@app.delete("/wishlists/{wishlist_id}/items/{item_id}")
def delete_wishlist_item(
    wishlist_id: int,
    item_id: int,
    user_id: int = Depends(get_user_id_from_auth)
):
    #user_id = get_user_id_from_auth(authorization)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM wishlists
        WHERE id = ? AND user_id = ?
    """, (wishlist_id, user_id))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Wishlist not found")

    cursor.execute("""
        DELETE FROM wishlist_items
        WHERE wishlist_id = ? AND id = ?
    """, (wishlist_id, item_id))
    conn.commit()
    conn.close()

    return {"message": "Wishlist item deleted successfully"}