from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import os
from typing import Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE = os.path.join(PROJECT_ROOT, "travel.db")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
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
        CREATE TABLE IF NOT EXISTS destinations (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
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
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wishlist_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wishlist_id INTEGER NOT NULL,
            destination_id INTEGER NOT NULL,
            notes TEXT,
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


class WishlistCreate(BaseModel):
    name: str


class WishlistItemCreate(BaseModel):
    destination_id: int
    notes: Optional[str] = ""


@app.get("/")
def root():
    return {
        "message": "FastAPI is running",
        "database": DATABASE
    }


@app.get("/recommendations")
def get_recommendations(
    continent: Optional[str] = Query(default=None),
    country: Optional[str] = Query(default=None),
    min_rating: Optional[float] = Query(default=None),
    max_cost: Optional[float] = Query(default=None),
    sort_by: Optional[str] = Query(default=None),
):
    try:
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
                CASE
                    WHEN avg_cost_usd IS NULL THEN 0
                    ELSE ROUND(1000.0 / (avg_cost_usd + 1), 2)
                END AS affordability_score,
                CASE
                    WHEN annual_visitors_m IS NULL THEN 0
                    ELSE ROUND(10.0 / (annual_visitors_m + 1), 2)
                END AS quietness_score,
                COALESCE(rating, 0) AS quality_score,
                CASE
                    WHEN annual_visitors_m IS NULL OR rating IS NULL THEN 0
                    ELSE ROUND((COALESCE(rating, 0) * 2) + (10.0 / (annual_visitors_m + 1)), 2)
                END AS hidden_gem_score,
                CASE
                    WHEN avg_cost_usd IS NULL OR annual_visitors_m IS NULL OR rating IS NULL THEN 0
                    ELSE ROUND(
                        (1000.0 / (avg_cost_usd + 1)) +
                        (10.0 / (annual_visitors_m + 1)) +
                        COALESCE(rating, 0),
                        2
                    )
                END AS barrier_score
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

        allowed_sort_fields = {
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

        query += f" ORDER BY {allowed_sort_fields.get(sort_by, 'barrier_score DESC')}"

        cursor.execute(query, params)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return rows

    except Exception as e:
        print("ERROR IN /recommendations:", repr(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/wishlists")
def get_wishlists():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, created_at
            FROM wishlists
            ORDER BY created_at DESC, id DESC
        """)
        wishlists = [dict(row) for row in cursor.fetchall()]

        for wishlist in wishlists:
            cursor.execute("""
                SELECT
                    wi.id,
                    wi.wishlist_id,
                    wi.destination_id,
                    wi.notes,
                    wi.created_at,
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
            """, (wishlist["id"],))
            wishlist["items"] = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return wishlists

    except Exception as e:
        print("ERROR IN /wishlists:", repr(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/wishlists")
def create_wishlist(payload: WishlistCreate):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO wishlists (name) VALUES (?)",
            (payload.name,)
        )
        conn.commit()
        wishlist_id = cursor.lastrowid

        cursor.execute(
            "SELECT id, name, created_at FROM wishlists WHERE id = ?",
            (wishlist_id,)
        )
        new_wishlist = dict(cursor.fetchone())
        new_wishlist["items"] = []

        conn.close()
        return new_wishlist

    except Exception as e:
        print("ERROR IN POST /wishlists:", repr(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/wishlists/{wishlist_id}")
def delete_wishlist(wishlist_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM wishlist_items WHERE wishlist_id = ?", (wishlist_id,))
        cursor.execute("DELETE FROM wishlists WHERE id = ?", (wishlist_id,))
        conn.commit()
        conn.close()

        return {"message": "Wishlist deleted successfully"}

    except Exception as e:
        print("ERROR IN DELETE /wishlists:", repr(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/wishlists/{wishlist_id}/items")
def add_to_wishlist(wishlist_id: int, payload: WishlistItemCreate):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM wishlists WHERE id = ?", (wishlist_id,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="Wishlist not found")

        cursor.execute("SELECT id FROM destinations WHERE id = ?", (payload.destination_id,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="Destination not found")

        cursor.execute("""
            SELECT id
            FROM wishlist_items
            WHERE wishlist_id = ? AND destination_id = ?
        """, (wishlist_id, payload.destination_id))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="Destination already in wishlist")

        cursor.execute("""
            INSERT INTO wishlist_items (wishlist_id, destination_id, notes)
            VALUES (?, ?, ?)
        """, (wishlist_id, payload.destination_id, payload.notes or ""))
        conn.commit()

        item_id = cursor.lastrowid

        cursor.execute("""
            SELECT
                wi.id,
                wi.wishlist_id,
                wi.destination_id,
                wi.notes,
                wi.created_at,
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
        item = dict(cursor.fetchone())

        conn.close()
        return item

    except HTTPException:
        raise
    except Exception as e:
        print("ERROR IN POST /wishlists/{wishlist_id}/items:", repr(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/wishlists/{wishlist_id}/items/{item_id}")
def delete_wishlist_item(wishlist_id: int, item_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM wishlist_items
            WHERE id = ? AND wishlist_id = ?
        """, (item_id, wishlist_id))
        conn.commit()
        conn.close()

        return {"message": "Wishlist item deleted successfully"}

    except Exception as e:
        print("ERROR IN DELETE /wishlists/{wishlist_id}/items/{item_id}:", repr(e))
        raise HTTPException(status_code=500, detail=str(e))