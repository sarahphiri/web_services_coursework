# Import required libraries
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
# Connect to the SQLite database
# -----------------------------------------

# Create a connection to the SQLite database
# If the database file does not exist yet, SQLite will create it
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

# Remove existing destination rows so re-running the script
# recreates the dataset cleanly without duplicates
cursor.execute("DELETE FROM destinations")

# -----------------------------------------
# Read CSV file and import rows
# -----------------------------------------

with open(CSV_FILE, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)

    inserted_count = 0

    for row in reader:
        # Extract required fields and normalise whitespace
        name = (row.get("name") or row.get("Name") or "").strip()
        country = (row.get("country") or row.get("Country") or "").strip()

        # Skip rows missing required values
        if not name or not country:
            continue

        inserted_count += 1

        cursor.execute("""
        INSERT INTO destinations (
            id,
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
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            inserted_count,
            name,
            country,
            row.get("continent") or row.get("Continent"),
            row.get("type") or row.get("Type"),
            row.get("best_season") or row.get("Best_Season"),
            float(row.get("avg_cost_usd") or row.get("Average_Cost_USD") or 0),
            float(row.get("rating") or row.get("Rating") or 0),
            float(row.get("annual_visitors_m") or row.get("Annual_Visitors_Millions") or 0),
            1 if str(row.get("unesco") or row.get("UNESCO") or "0").lower() in ["1", "true", "yes"] else 0
        ))

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