import os
import sqlite3
import tempfile

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Destination


@pytest.fixture()
def client():
    """
    Creates a temporary SQLite database for tests,
    overrides get_db dependency so tests don't touch your real travel.db.
    """
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    # seed a couple destinations so /destinations works
    db = TestingSessionLocal()
    db.add_all([
        Destination(
            name="Test Beach",
            country="Spain",
            continent="Europe",
            type="Beach",
            best_season="Summer",
            avg_cost_usd=120.0,
            rating=4.6,
            annual_visitors_m=2.0,
            unesco=False,
        ),
        Destination(
            name="Quiet Mountain",
            country="Japan",
            continent="Asia",
            type="Nature",
            best_season="Spring",
            avg_cost_usd=90.0,
            rating=4.7,
            annual_visitors_m=0.4,
            unesco=True,
        ),
    ])
    db.commit()
    db.close()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    # cleanup
    try:
        os.remove(db_path)
    except FileNotFoundError:
        pass


def test_destinations_list(client):
    r = client.get("/destinations?limit=10&offset=0")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_register_login_and_wishlist_flow(client):
    # Register
    r = client.post("/auth/register", json={"email": "test@example.com", "password": "Password123!"})
    assert r.status_code in (200, 201)

    # Login (OAuth2PasswordRequestForm expects form data)
    r = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "Password123!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token

    headers = {"Authorization": f"Bearer {token}"}

    # Create wishlist
    r = client.post("/wishlists", json={"name": "My Wishlist", "description": "Test"}, headers=headers)
    assert r.status_code in (200, 201)
    wishlist_id = r.json()["id"]

    # List wishlists
    r = client.get("/wishlists", headers=headers)
    assert r.status_code == 200
    assert any(w["id"] == wishlist_id for w in r.json())