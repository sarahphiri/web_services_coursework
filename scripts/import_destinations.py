import sqlite3
import os
import csv

# -----------------------------------------
# Define project file paths
# -----------------------------------------

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE = os.path.join(PROJECT_ROOT, "travel.db")
CSV_FILE = os.path.join(PROJECT_ROOT, "data", "Tourist_Destinations.csv")

# -----------------------------------------
# Helper functions
# -----------------------------------------

def to_float(value):
    if value is None:
        return None

    value = str(value).strip()

    if value == "":
        return None

    try:
        return float(value)
    except ValueError:
        return None


def to_unesco_flag(value):
    if value is None:
        return 0

    value = str(value).strip().lower()
    return 1 if value in {"yes", "true", "1"} else 0


# -----------------------------------------
# Connect to the SQLite database
# -----------------------------------------

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# -----------------------------------------
# Create the destinations table if needed
# -----------------------------------------

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

# -----------------------------------------
# Clear existing data before importing
# -----------------------------------------

cursor.execute("DELETE FROM destinations")

# -----------------------------------------
# Read CSV file and import rows
# -----------------------------------------

inserted_count = 0
skipped_missing_count = 0
skipped_duplicate_count = 0

seen_destinations = set()

with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)

    print("CSV headers found:", reader.fieldnames)

    for row in reader:
        name = (row.get("Destination Name") or "").strip()
        country = (row.get("Country") or "").strip()
        destination_type = (row.get("Type") or "").strip()

        # Skip rows missing core required fields
        if not name or not country:
            skipped_missing_count += 1
            continue

        # Skip duplicates based on the database uniqueness rule
        unique_key = (name.lower(), country.lower(), destination_type.lower())
        if unique_key in seen_destinations:
            skipped_duplicate_count += 1
            continue

        seen_destinations.add(unique_key)

        cursor.execute("""
        INSERT INTO destinations (
            name,
            country,
            continent,
            type,
            best_season,
            avg_cost_usd,
            rating,
            annual_visitors_m,
            unesco
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            country,
            (row.get("Continent") or "").strip() or None,
            destination_type or None,
            (row.get("Best Season") or "").strip() or None,
            to_float(row.get("Avg Cost (USD/day)")),
            to_float(row.get("Avg Rating")),
            to_float(row.get("Annual Visitors (M)")),
            to_unesco_flag(row.get("UNESCO Site"))
        ))

        inserted_count += 1

# -----------------------------------------
# Save changes and close database
# -----------------------------------------

conn.commit()
conn.close()

# -----------------------------------------
# Output confirmation messages
# -----------------------------------------

print("Destinations successfully imported into:", DATABASE)
print("CSV loaded from:", CSV_FILE)
print("Rows imported:", inserted_count)
print("Rows skipped (missing required fields):", skipped_missing_count)
print("Rows skipped (duplicates):", skipped_duplicate_count)