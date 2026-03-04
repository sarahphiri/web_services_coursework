from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.scoring import inverse_minmax, minmax_norm, hidden_gem_score
from app.db import get_db
from app.models import Destination

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError

from app.auth import hash_password, verify_password, create_access_token
from app.schemas import UserCreate, UserOut, TokenOut
from app.models import User

from app.deps import get_current_user
from app.models import Wishlist, User
from app.schemas import WishlistCreate, WishlistUpdate, WishlistOut

from sqlalchemy.exc import IntegrityError

from app.models import WishlistItem, Wishlist, Destination
from app.schemas import WishlistItemCreate, WishlistItemUpdate, WishlistItemOut

from app.errors import install_error_handlers

app = FastAPI(title="Travel Without Barriers API")
install_error_handlers(app)

@app.get("/")
def root():
    return {"message": "Travel Without Barriers API"}


# GET /destinations
@app.get("/destinations")
def get_destinations(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    destinations = db.query(Destination).offset(offset).limit(limit).all()
    return destinations


# GET /destinations/{id}
@app.get("/destinations/{destination_id}")
def get_destination(destination_id: int, db: Session = Depends(get_db)):

    destination = db.query(Destination).filter(
        Destination.id == destination_id
    ).first()

    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")

    return destination

#added for recommendations
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

    # Collect ranges for normalisation
    costs = [d.avg_cost_usd for d in destinations if d.avg_cost_usd is not None]
    visitors = [d.annual_visitors_m for d in destinations if d.annual_visitors_m is not None]
    ratings = [d.rating for d in destinations if d.rating is not None]

    # If a column is missing entirely, choose safe ranges
    cost_min, cost_max = (min(costs), max(costs)) if costs else (0.0, 1.0)
    vis_min, vis_max = (min(visitors), max(visitors)) if visitors else (0.0, 1.0)
    rating_min, rating_max = (min(ratings), max(ratings)) if ratings else (0.0, 5.0)

    results = []

    for d in destinations:
        # Core metrics (0..1)
        affordability = inverse_minmax(d.avg_cost_usd, cost_min, cost_max)  # cheaper -> higher score
        quietness = inverse_minmax(d.annual_visitors_m, vis_min, vis_max)   # fewer visitors -> higher score

        # quality: rating 0..5 -> 0..1 (or min-max)
        quality = (d.rating / 5.0) if d.rating is not None else 0.0
        quality = max(0.0, min(1.0, quality))

        # "Hidden gem": high rating + low visitors (log penalty)
        hidden_gem = hidden_gem_score(d.rating, d.annual_visitors_m)

        # Seasonal pressure/relief (your improved idea)
        # We treat high visitors as "pressure" proxy and invert it to "relief".
        season_pressure = minmax_norm(d.annual_visitors_m, vis_min, vis_max)
        season_relief = 1.0 - season_pressure

        # Budget penalty (optional): if user provides budget, penalise above-budget destinations.
        # This makes affordability more "real" for the user.
        budget_penalty = 0.0
        if budget is not None and d.avg_cost_usd is not None and budget > 0:
            if d.avg_cost_usd > budget:
                # penalty grows with how far above budget it is (capped)
                budget_penalty = min(0.4, (d.avg_cost_usd - budget) / budget * 0.4)

        # Peak-season barrier adjustment (optional)
        # If avoid_peak=True, slightly penalise destinations that are likely "peak pressure" destinations.
        # We approximate this using season_pressure (high visitors => more likely peak stress).
        peak_penalty = 0.15 * season_pressure if avoid_peak else 0.0

        # Final Barrier-Friendly Score (weights you can justify in your report)
        barrier_score = (
            0.35 * affordability +
            0.30 * quietness +
            0.20 * quality +
            0.10 * hidden_gem +
            0.05 * season_relief
        ) - budget_penalty - peak_penalty

        results.append({
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
                "Lower cost improves affordability" if affordability >= 0.6 else "Higher cost may reduce affordability",
                "Lower visitors suggests a calmer destination" if quietness >= 0.6 else "Higher visitors may feel busier",
                "High ratings increase confidence" if quality >= 0.7 else "Moderate ratings",
                "Hidden-gem bonus: well-rated with fewer visitors" if hidden_gem >= 0.4 else "Popular/high-traffic destination"
            ]
        })

    # Sort best-first
    results.sort(key=lambda x: x["barrier_score"], reverse=True)
    return results[:max(1, min(limit, 50))]

@app.post("/auth/register", response_model=UserOut)
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


@app.post("/wishlists", response_model=WishlistOut)
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


@app.post("/wishlists/{wishlist_id}/items", response_model=WishlistItemOut, status_code=201)
def add_wishlist_item(
    wishlist_id: int,
    payload: WishlistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_owned_wishlist(db, wishlist_id, current_user.id)

    # Ensure destination exists
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
    except IntegrityError:
        db.rollback()
        # most likely unique constraint: destination already in wishlist
        raise HTTPException(status_code=409, detail="Destination already in wishlist")

    db.refresh(item)
    return item


@app.get("/wishlists/{wishlist_id}/items", response_model=list[WishlistItemOut])
def list_wishlist_items(
    wishlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_owned_wishlist(db, wishlist_id, current_user.id)

    items = (
        db.query(WishlistItem)
        .filter(WishlistItem.wishlist_id == wishlist_id)
        .order_by(WishlistItem.created_at.desc())
        .all()
    )
    return items


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
        .filter(WishlistItem.id == item_id, WishlistItem.wishlist_id == wishlist_id)
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
        .filter(WishlistItem.id == item_id, WishlistItem.wishlist_id == wishlist_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Wishlist item not found")

    db.delete(item)
    db.commit()
    return {"message": "Wishlist item deleted"}