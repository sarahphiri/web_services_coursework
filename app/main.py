from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.scoring import inverse_minmax, minmax_norm, hidden_gem_score
from app.db import get_db
from app.models import Destination

app = FastAPI(title="Travel Without Barriers API")


@app.get("/")
def root():
    return {"message": "Travel Without Barriers API"}


# GET /destinations
@app.get("/destinations")
def get_destinations(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
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
    limit: int = 10,
    budget: float | None = None,          # optional user budget
    avoid_peak: bool = True,              # treat "best season" as peak pressure (barrier)
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