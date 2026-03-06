from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.auth import hash_password, verify_password, create_access_token
from app.db import get_db, engine
from app.deps import get_current_user
from app.errors import install_error_handlers
from app.models import Base, Destination, User, Wishlist, WishlistItem
from app.schemas import (
    UserCreate,
    UserOut,
    TokenOut,
    WishlistCreate,
    WishlistUpdate,
    WishlistOut,
    WishlistItemCreate,
    WishlistItemUpdate,
    WishlistItemOut,
)
from app.scoring import inverse_minmax, minmax_norm, hidden_gem_score

app = FastAPI(title="Travel Without Barriers API")
install_error_handlers(app)

# Create tables
Base.metadata.create_all(bind=engine)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Travel Without Barriers API"}


# -----------------------------
# Destinations
# -----------------------------
@app.get("/destinations")
def get_destinations(
    limit: int | None = Query(None, ge=1),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(Destination).offset(offset)
    if limit is not None:
        q = q.limit(limit)
    return q.all()


@app.get("/destinations/count")
def destinations_count(db: Session = Depends(get_db)):
    total = db.query(func.count(Destination.id)).scalar()
    return {"total": total}


@app.get("/destinations/{destination_id}")
def get_destination(destination_id: int, db: Session = Depends(get_db)):
    destination = db.query(Destination).filter(Destination.id == destination_id).first()

    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")

    return destination


# -----------------------------
# Recommendations
# -----------------------------
@app.get("/recommendations")
def get_recommendations(
    limit: int = Query(10, ge=1, le=50),
    budget: float | None = Query(None, gt=0),
    avoid_peak: bool = True,
    db: Session = Depends(get_db),
):
    destinations = db.query(Destination).all()

    if not destinations:
        raise HTTPException(status_code=404, detail="No destinations found")

    costs = [d.avg_cost_usd for d in destinations if d.avg_cost_usd is not None]
    visitors = [d.annual_visitors_m for d in destinations if d.annual_visitors_m is not None]
    ratings = [d.rating for d in destinations if d.rating is not None]

    cost_min, cost_max = (min(costs), max(costs)) if costs else (0.0, 1.0)
    vis_min, vis_max = (min(visitors), max(visitors)) if visitors else (0.0, 1.0)
    rating_min, rating_max = (min(ratings), max(ratings)) if ratings else (0.0, 5.0)

    results = []

    for d in destinations:
        affordability = inverse_minmax(d.avg_cost_usd, cost_min, cost_max)
        quietness = inverse_minmax(d.annual_visitors_m, vis_min, vis_max)

        quality = (d.rating / 5.0) if d.rating is not None else 0.0
        quality = max(0.0, min(1.0, quality))

        hidden_gem = hidden_gem_score(d.rating, d.annual_visitors_m)

        season_pressure = minmax_norm(d.annual_visitors_m, vis_min, vis_max)
        season_relief = 1.0 - season_pressure

        budget_penalty = 0.0
        if budget is not None and d.avg_cost_usd is not None and budget > 0:
            if d.avg_cost_usd > budget:
                budget_penalty = min(0.4, (d.avg_cost_usd - budget) / budget * 0.4)

        peak_penalty = 0.15 * season_pressure if avoid_peak else 0.0

        barrier_score = (
            0.35 * affordability
            + 0.30 * quietness
            + 0.20 * quality
            + 0.10 * hidden_gem
            + 0.05 * season_relief
        ) - budget_penalty - peak_penalty

        results.append(
            {
                "id": d.id,
                "name": d.name,
                "country": d.country,
                "continent": d.continent,
                "type": d.type,
                "best_season": d.best_season,
                "avg_cost_usd": d.avg_cost_usd,
                "rating": d.rating,
                "annual_visitors_m": d.annual_visitors_m,
                "unesco": d.unesco,
                "affordability_score": round(affordability, 3),
                "quietness_score": round(quietness, 3),
                "quality_score": round(quality, 3),
                "hidden_gem_score": round(hidden_gem, 3),
                "season_relief_score": round(season_relief, 3),
                "barrier_score": round(barrier_score, 3),
                "explain": [
                    "Lower cost improves affordability"
                    if affordability >= 0.6
                    else "Higher cost may reduce affordability",
                    "Lower visitors suggests a calmer destination"
                    if quietness >= 0.6
                    else "Higher visitors may feel busier",
                    "High ratings increase confidence"
                    if quality >= 0.7
                    else "Moderate ratings",
                    "Hidden-gem bonus: well-rated with fewer visitors"
                    if hidden_gem >= 0.4
                    else "Popular/high-traffic destination",
                ],
            }
        )

    results.sort(key=lambda x: x["barrier_score"], reverse=True)
    return results[: max(1, min(limit, 50))]


# -----------------------------
# Auth
# -----------------------------
@app.post("/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = User(
        email=payload.email.lower().strip(),
        password_hash=hash_password(payload.password),
    )
    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")

    return user


@app.post("/auth/login", response_model=TokenOut)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    email = form_data.username.lower().strip()
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = create_access_token(subject=user.email)
    return {"access_token": token, "token_type": "bearer"}


# -----------------------------
# Wishlists
# -----------------------------
@app.post("/wishlists", response_model=WishlistOut, status_code=status.HTTP_201_CREATED)
def create_wishlist(
    payload: WishlistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    wishlist = Wishlist(
        user_id=current_user.id,
        name=payload.name.strip(),
        description=payload.description.strip() if payload.description else None,
    )
    db.add(wishlist)
    db.commit()
    db.refresh(wishlist)
    return wishlist


@app.get("/wishlists", response_model=list[WishlistOut])
def list_wishlists(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Wishlist)
        .filter(Wishlist.user_id == current_user.id)
        .order_by(Wishlist.created_at.desc())
        .all()
    )


@app.get("/wishlists/{wishlist_id}", response_model=WishlistOut)
def get_wishlist(
    wishlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    wishlist = (
        db.query(Wishlist)
        .filter(Wishlist.id == wishlist_id, Wishlist.user_id == current_user.id)
        .first()
    )

    if not wishlist:
        raise HTTPException(status_code=404, detail="Wishlist not found")

    return wishlist


@app.patch("/wishlists/{wishlist_id}", response_model=WishlistOut)
def update_wishlist(
    wishlist_id: int,
    payload: WishlistUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    wishlist = (
        db.query(Wishlist)
        .filter(Wishlist.id == wishlist_id, Wishlist.user_id == current_user.id)
        .first()
    )

    if not wishlist:
        raise HTTPException(status_code=404, detail="Wishlist not found")

    if payload.name is not None:
        wishlist.name = payload.name.strip()

    if payload.description is not None:
        wishlist.description = payload.description.strip() if payload.description else None

    db.commit()
    db.refresh(wishlist)
    return wishlist


@app.delete("/wishlists/{wishlist_id}")
def delete_wishlist(
    wishlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    wishlist = (
        db.query(Wishlist)
        .filter(Wishlist.id == wishlist_id, Wishlist.user_id == current_user.id)
        .first()
    )

    if not wishlist:
        raise HTTPException(status_code=404, detail="Wishlist not found")

    db.delete(wishlist)
    db.commit()
    return {"message": "Wishlist deleted"}


def _get_owned_wishlist(db: Session, wishlist_id: int, user_id: int) -> Wishlist:
    wishlist = (
        db.query(Wishlist)
        .filter(Wishlist.id == wishlist_id, Wishlist.user_id == user_id)
        .first()
    )

    if not wishlist:
        raise HTTPException(status_code=404, detail="Wishlist not found")

    return wishlist


# -----------------------------
# Wishlist Items
# -----------------------------
@app.post("/wishlists/{wishlist_id}/items", response_model=WishlistItemOut, status_code=status.HTTP_201_CREATED)
def add_wishlist_item(
    wishlist_id: int,
    payload: WishlistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_owned_wishlist(db, wishlist_id, current_user.id)

    destination = db.query(Destination).filter(Destination.id == payload.destination_id).first()
    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")

    item = WishlistItem(
        wishlist_id=wishlist_id,
        destination_id=payload.destination_id,
        notes=payload.notes.strip() if payload.notes else None,
        priority=payload.priority,
    )

    db.add(item)

    try:
        db.commit()
        db.refresh(item)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Destination already exists in wishlist")

    return item


@app.get("/wishlists/{wishlist_id}/items", response_model=list[WishlistItemOut])
def list_wishlist_items(
    wishlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_owned_wishlist(db, wishlist_id, current_user.id)

    return (
        db.query(WishlistItem)
        .filter(WishlistItem.wishlist_id == wishlist_id)
        .order_by(WishlistItem.created_at.desc())
        .all()
    )


@app.get("/wishlists/{wishlist_id}/items/{item_id}", response_model=WishlistItemOut)
def get_wishlist_item(
    wishlist_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_owned_wishlist(db, wishlist_id, current_user.id)

    item = (
        db.query(WishlistItem)
        .filter(
            WishlistItem.id == item_id,
            WishlistItem.wishlist_id == wishlist_id,
        )
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Wishlist item not found")

    return item


@app.patch("/wishlists/{wishlist_id}/items/{item_id}", response_model=WishlistItemOut)
def update_wishlist_item(
    wishlist_id: int,
    item_id: int,
    payload: WishlistItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_owned_wishlist(db, wishlist_id, current_user.id)

    item = (
        db.query(WishlistItem)
        .filter(
            WishlistItem.id == item_id,
            WishlistItem.wishlist_id == wishlist_id,
        )
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Wishlist item not found")

    if payload.notes is not None:
        item.notes = payload.notes.strip() if payload.notes else None

    if payload.priority is not None:
        item.priority = payload.priority

    db.commit()
    db.refresh(item)
    return item


@app.delete("/wishlists/{wishlist_id}/items/{item_id}")
def delete_wishlist_item(
    wishlist_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_owned_wishlist(db, wishlist_id, current_user.id)

    item = (
        db.query(WishlistItem)
        .filter(
            WishlistItem.id == item_id,
            WishlistItem.wishlist_id == wishlist_id,
        )
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Wishlist item not found")

    db.delete(item)
    db.commit()
    return {"message": "Wishlist item deleted"}