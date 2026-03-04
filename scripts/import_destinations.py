#!/usr/bin/env python3
"""
Import destinations from a CSV into a SQLite database.

- Uses pandas to read CSV
- Creates DB + destinations table if missing
- Cleans basic types (floats, booleans, trimmed strings)
- Avoids duplicates via a UNIQUE constraint + INSERT OR IGNORE
"""

import argparse
import sqlite3
from pathlib import Path
from typing import Optional

import pandas as pd


# ---- SQL schema ----
# We enforce "no duplicates" with a UNIQUE constraint.
# For tourism destinations, (name, country, type) is a reasonable natural key.
# If your data has better identifiers, you can update this.
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS destinations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    continent TEXT,
    type TEXT,
    best_season TEXT,
    avg_cost_usd REAL,
    rating REAL,
    annual_visitors_m REAL,
    unesco INTEGER,
    UNIQUE (name, country, type)
);
"""

INSERT_SQL = """
INSERT OR IGNORE INTO destinations (
    name, country, continent, type, best_season,
    avg_cost_usd, rating, annual_visitors_m, unesco
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
"""


# ---- cleaning helpers ----
def clean_text(x) -> Optional[str]:
    """Strip whitespace; convert empty/NaN to None."""
    if pd.isna(x):
        return None
    s = str(x).strip()
    return s if s else None


def clean_float(x) -> Optional[float]:
    """Convert to float; invalid/NaN -> None."""
    if pd.isna(x):
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        # Try coercing via pandas (handles commas, weird strings better)
        v = pd.to_numeric(pd.Series([x]), errors="coerce").iloc[0]
        return None if pd.isna(v) else float(v)


def clean_bool_to_int(x) -> Optional[int]:
    """
    Convert common truthy/falsey values to 1/0 for SQLite.
    Accepts Yes/No, True/False, 1/0, Y/N.
    """
    if pd.isna(x):
        return None
    s = str(x).strip().lower()
    if s in {"yes", "y", "true", "t", "1"}:
        return 1
    if s in {"no", "n", "false", "f", "0"}:
        return 0
    return None


def detect_and_rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Map common Kaggle-ish CSV headers to your DB schema field names.
    Adjust these mappings if your CSV uses different headers.
    """
    col_map_candidates = {
        "name": ["name", "destination name", "destination", "Destination Name"],
        "country": ["country", "Country"],
        "continent": ["continent", "Continent"],
        "type": ["type", "Type", "destination type"],
        "best_season": ["best_season", "best season", "Best Season"],
        "avg_cost_usd": ["avg_cost_usd", "avg cost usd", "Avg Cost (USD/day)", "Avg Cost (USD/day)"],
        "rating": ["rating", "avg rating", "Avg Rating"],
        "annual_visitors_m": ["annual_visitors_m", "annual visitors (m)", "Annual Visitors (M)"],
        "unesco": ["unesco", "unesco site", "UNESCO Site"],
    }

    # Build a rename dict by matching case-insensitively
    lower_to_original = {c.lower(): c for c in df.columns}
    rename = {}

    for target, candidates in col_map_candidates.items():
        for cand in candidates:
            key = str(cand).lower()
            if key in lower_to_original:
                rename[lower_to_original[key]] = target
                break

    # Apply rename if we found any matches
    if rename:
        df = df.rename(columns=rename)

    return df


def validate_required_columns(df: pd.DataFrame) -> None:
    required = {"name", "country"}
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"CSV is missing required columns: {missing}. "
            f"Columns found: {list(df.columns)}"
        )


def main():
    parser = argparse.ArgumentParser(description="Import destinations CSV into SQLite.")
    parser.add_argument("--csv", required=True, help="Path to source CSV file")
    parser.add_argument("--db", default="travel.db", help="Path to SQLite DB file (default: travel.db)")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="If set, deletes existing destinations before importing (keeps table).",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    db_path = Path(args.db)

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path.resolve()}")

    # Read CSV
    df = pd.read_csv(csv_path)

    # Rename columns to match expected schema keys
    df = detect_and_rename_columns(df)

    # Validate required columns
    validate_required_columns(df)

    # Clean + normalize columns (create missing optional columns as None)
    for col in ["continent", "type", "best_season"]:
        if col not in df.columns:
            df[col] = None

    for col in ["avg_cost_usd", "rating", "annual_visitors_m"]:
        if col not in df.columns:
            df[col] = None

    if "unesco" not in df.columns:
        df["unesco"] = None

    # Apply cleaning
    df["name"] = df["name"].apply(clean_text)
    df["country"] = df["country"].apply(clean_text)
    df["continent"] = df["continent"].apply(clean_text)
    df["type"] = df["type"].apply(clean_text)
    df["best_season"] = df["best_season"].apply(clean_text)

    df["avg_cost_usd"] = df["avg_cost_usd"].apply(clean_float)
    df["rating"] = df["rating"].apply(clean_float)
    df["annual_visitors_m"] = df["annual_visitors_m"].apply(clean_float)
    df["unesco"] = df["unesco"].apply(clean_bool_to_int)

    # Drop rows missing the core required fields
    df = df[df["name"].notna() & df["country"].notna()].copy()

    # Connect + create table
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(CREATE_TABLE_SQL)

        if args.replace:
            cur.execute("DELETE FROM destinations;")

        inserted = 0
        ignored = 0

        # Insert row-by-row (simple + clear for coursework)
        for _, r in df.iterrows():
            before = conn.total_changes

            cur.execute(
                INSERT_SQL,
                (
                    r["name"],
                    r["country"],
                    r["continent"],
                    r["type"],
                    r["best_season"],
                    r["avg_cost_usd"],
                    r["rating"],
                    r["annual_visitors_m"],
                    r["unesco"],
                ),
            )

            after = conn.total_changes
            if after > before:
                inserted += 1
            else:
                ignored += 1

        conn.commit()

        print(f"✅ DB: {db_path.resolve()}")
        print(f"✅ CSV: {csv_path.resolve()}")
        print(f"✅ Inserted: {inserted}")
        print(f"↩️  Skipped as duplicates (ignored): {ignored}")
        print(f"📌 Total rows processed: {inserted + ignored}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()