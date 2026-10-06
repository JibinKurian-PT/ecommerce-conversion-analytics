import sqlite3
import pandas as pd
import os
import time
from pathlib import Path

# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

EVENTS_FILE = (
    BASE_DIR / "data" / "processed" / "final_time_aware_events.csv"
)

CATEGORY_FILE = (
    BASE_DIR / "data" / "raw" / "category_tree.csv"
)

DATABASE_FILE = (
    BASE_DIR / "data" / "processed" / "retail_analytics.db"
)


# ============================================================
# 2. START
# ============================================================

start = time.time()

print("=" * 70)
print("RETAIL ANALYTICS SQL DATABASE")
print("=" * 70)


# ============================================================
# 3. REMOVE OLD FAILED DATABASE
# ============================================================

if os.path.exists(DATABASE_FILE):

    print("\nRemoving previous failed database...")

    os.remove(DATABASE_FILE)


# ============================================================
# 4. CONNECT TO SQLITE
# ============================================================

print("\n1. Creating SQLite database...")

conn = sqlite3.connect(
    DATABASE_FILE
)

cursor = conn.cursor()

cursor.execute(
    "PRAGMA foreign_keys = ON;"
)

print(
    f"Database created:\n{DATABASE_FILE}"
)


# ============================================================
# 5. CREATE CATEGORY TABLE
# ============================================================

print("\n2. Creating dim_category...")

category = pd.read_csv(
    CATEGORY_FILE
)

print(
    f"Category rows: {len(category):,}"
)

print(
    f"Category columns: "
    f"{list(category.columns)}"
)


# Clean column names
category.columns = [
    col.strip().lower()
    for col in category.columns
]


# Remove exact duplicates
category = category.drop_duplicates()


# Convert IDs to nullable integers
category["categoryid"] = (
    category["categoryid"]
    .astype("int64")
)

category["parentid"] = (
    pd.to_numeric(
        category["parentid"],
        errors="coerce"
    )
    .astype("Int64")
)


# ------------------------------------------------------------
# Create table
# ------------------------------------------------------------

cursor.execute("""
DROP TABLE IF EXISTS fact_events;
""")

cursor.execute("""
DROP TABLE IF EXISTS dim_category;
""")


cursor.execute("""
CREATE TABLE dim_category (

    categoryid INTEGER PRIMARY KEY,

    parentid INTEGER,

    FOREIGN KEY (parentid)
        REFERENCES dim_category(categoryid)

        DEFERRABLE INITIALLY DEFERRED
);
""")


# ============================================================
# 6. INSERT CATEGORY DATA
# ============================================================

print(
    "\n3. Loading category hierarchy..."
)

# Start explicit transaction
cursor.execute("BEGIN;")

category.to_sql(
    "dim_category",
    conn,
    if_exists="append",
    index=False
)

# Commit only after ALL category rows exist
conn.commit()

print(
    "dim_category loaded successfully."
)


# ============================================================
# 7. VERIFY CATEGORY FOREIGN KEY
# ============================================================

print(
    "\n4. Checking category hierarchy..."
)

foreign_key_check = cursor.execute(
    "PRAGMA foreign_key_check;"
).fetchall()

if len(foreign_key_check) == 0:

    print(
        "PASS: Category hierarchy has "
        "no foreign-key violations."
    )

else:

    print(
        f"FAIL: "
        f"{len(foreign_key_check):,} "
        f"foreign-key violations found."
    )


# ============================================================
# 8. CREATE FACT EVENTS TABLE
# ============================================================

print(
    "\n5. Creating fact_events..."
)

cursor.execute("""
CREATE TABLE fact_events (

    event_row_id INTEGER PRIMARY KEY,

    timestamp INTEGER NOT NULL,

    visitorid INTEGER NOT NULL,

    event TEXT NOT NULL,

    itemid INTEGER NOT NULL,

    transactionid REAL,

    categoryid INTEGER,

    available INTEGER,

    category_property_timestamp INTEGER,

    availability_property_timestamp INTEGER,

    FOREIGN KEY (categoryid)
        REFERENCES dim_category(categoryid)
);
""")

conn.commit()

print(
    "fact_events table created."
)


# ============================================================
# 9. LOAD EVENTS IN CHUNKS
# ============================================================

print(
    "\n6. Loading final_time_aware_events.csv..."
)

chunk_size = 100_000

total_loaded = 0

columns = [
    "event_row_id",
    "timestamp",
    "visitorid",
    "event",
    "itemid",
    "transactionid",
    "categoryid",
    "available",
    "category_property_timestamp",
    "availability_property_timestamp"
]


for chunk in pd.read_csv(
    EVENTS_FILE,
    usecols=columns,
    chunksize=chunk_size
):

    chunk.to_sql(
        "fact_events",
        conn,
        if_exists="append",
        index=False
    )

    total_loaded += len(chunk)

    print(
        f"Loaded: "
        f"{total_loaded:,} rows"
    )


# ============================================================
# 10. CREATE INDEXES
# ============================================================

print(
    "\n7. Creating indexes..."
)


indexes = [

    """
    CREATE INDEX IF NOT EXISTS
    idx_fact_events_visitor
    ON fact_events(visitorid);
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_fact_events_item
    ON fact_events(itemid);
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_fact_events_event
    ON fact_events(event);
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_fact_events_category
    ON fact_events(categoryid);
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_fact_events_timestamp
    ON fact_events(timestamp);
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_fact_events_transaction
    ON fact_events(transactionid);
    """
]


for sql in indexes:

    cursor.execute(sql)


conn.commit()

print(
    "Indexes created."
)


# ============================================================
# 11. DATABASE TABLE CHECK
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    "DATABASE CHECK"
)

print(
    "=" * 70
)


tables = pd.read_sql_query(
    """
    SELECT
        name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name;
    """,
    conn
)

print("\nTables:")

print(tables)


# ============================================================
# 12. ROW COUNTS
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    "ROW COUNTS"
)

print(
    "=" * 70
)


counts = pd.read_sql_query(
    """
    SELECT

        (
            SELECT COUNT(*)
            FROM fact_events
        ) AS fact_events_rows,

        (
            SELECT COUNT(*)
            FROM dim_category
        ) AS category_rows;
    """,
    conn
)

print(counts)


# ============================================================
# 13. EVENT DISTRIBUTION
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    "EVENT DISTRIBUTION"
)

print(
    "=" * 70
)


event_counts = pd.read_sql_query(
    """
    SELECT

        event,

        COUNT(*) AS event_count

    FROM fact_events

    GROUP BY event

    ORDER BY event_count DESC;
    """,
    conn
)

print(event_counts)


# ============================================================
# 14. FOREIGN KEY CHECK
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    "FOREIGN KEY CHECK"
)

print(
    "=" * 70
)


foreign_key_violations = cursor.execute(
    """
    PRAGMA foreign_key_check;
    """
).fetchall()


if len(foreign_key_violations) == 0:

    print(
        "\nPASS: No foreign-key violations."
    )

else:

    print(
        f"\nWARNING: "
        f"{len(foreign_key_violations):,} "
        f"foreign-key violations found."
    )


# ============================================================
# 15. CATEGORY MATCHING
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    "CATEGORY MATCHING"
)

print(
    "=" * 70
)


category_stats = pd.read_sql_query(
    """
    SELECT

        COUNT(*) AS total_events,

        SUM(
            CASE
                WHEN categoryid IS NOT NULL
                THEN 1
                ELSE 0
            END
        ) AS events_with_category,

        SUM(
            CASE
                WHEN categoryid IS NULL
                THEN 1
                ELSE 0
            END
        ) AS events_without_category

    FROM fact_events;
    """,
    conn
)

print(category_stats)


# ============================================================
# 16. BASIC BUSINESS CHECK
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    "BASIC BUSINESS CHECK"
)

print(
    "=" * 70
)


visitor_summary = pd.read_sql_query(
    """
    SELECT

        COUNT(DISTINCT visitorid)
        AS unique_visitors,

        COUNT(
            CASE
                WHEN event = 'view'
                THEN 1
            END
        ) AS views,

        COUNT(
            CASE
                WHEN event = 'addtocart'
                THEN 1
            END
        ) AS add_to_carts,

        COUNT(
            CASE
                WHEN event = 'transaction'
                THEN 1
            END
        ) AS transactions

    FROM fact_events;
    """,
    conn
)

print(visitor_summary)


# ============================================================
# 17. CLOSE
# ============================================================

conn.close()

elapsed = time.time() - start

print(
    "\n" + "=" * 70
)

print(
    "DATABASE CREATION COMPLETE"
)

print(
    "=" * 70
)

print(
    f"\nDatabase:\n{DATABASE_FILE}"
)

print(
    f"\nExecution time: "
    f"{elapsed / 60:.2f} minutes"
)
