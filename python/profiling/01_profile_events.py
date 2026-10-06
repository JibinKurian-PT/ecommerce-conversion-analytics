import pandas as pd
from pathlib import Path
from collections import Counter


# ============================================================
# PROJECT: E-Commerce Conversion Analytics
# FILE: 01_profile_events.py
# PURPOSE: Understand the structure and quality of events.csv
# IMPORTANT: This script DOES NOT modify the original dataset.
# ============================================================


# ------------------------------------------------------------
# 1. File location
# ------------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[2]
FILE_PATH = PROJECT_DIR / "data" / "raw" / "events.csv"

# ------------------------------------------------------------
# 2. Basic configuration
# ------------------------------------------------------------

CHUNK_SIZE = 100_000


# ------------------------------------------------------------
# 3. Check that the file exists
# ------------------------------------------------------------

if not FILE_PATH.exists():
    raise FileNotFoundError(
        f"Could not find events.csv at:\n{FILE_PATH}"
    )


print("=" * 70)
print("E-COMMERCE CONVERSION ANALYTICS")
print("DATA UNDERSTANDING - EVENTS TABLE")
print("=" * 70)

print(f"\nFile: {FILE_PATH}")
print(f"Chunk size: {CHUNK_SIZE:,}")


# ------------------------------------------------------------
# 4. Read header
# ------------------------------------------------------------

header = pd.read_csv(FILE_PATH, nrows=0)

print("\n" + "-" * 70)
print("1. COLUMNS")
print("-" * 70)

print(list(header.columns))

print(f"\nNumber of columns: {len(header.columns)}")


# ------------------------------------------------------------
# 5. Variables for profiling
# ------------------------------------------------------------

row_count = 0

missing_counts = Counter()

event_counts = Counter()

unique_visitors = set()
unique_items = set()

min_timestamp = None
max_timestamp = None

duplicate_hashes = set()
duplicate_count = 0


# ------------------------------------------------------------
# 6. Process file in chunks
# ------------------------------------------------------------

print("\nProcessing events.csv...")
print("This may take some time because the file is large.\n")


for chunk_number, chunk in enumerate(
    pd.read_csv(
        FILE_PATH,
        chunksize=CHUNK_SIZE
    ),
    start=1
):

    # --------------------------------------------------------
    # Row count
    # --------------------------------------------------------

    row_count += len(chunk)


    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    for column in chunk.columns:
        missing_counts[column] += chunk[column].isna().sum()


    # --------------------------------------------------------
    # Event distribution
    # --------------------------------------------------------

    if "event" in chunk.columns:
        event_counts.update(
            chunk["event"].value_counts().to_dict()
        )


    # --------------------------------------------------------
    # Unique visitors
    # --------------------------------------------------------

    if "visitorid" in chunk.columns:
        unique_visitors.update(
            chunk["visitorid"].dropna().unique()
        )


    # --------------------------------------------------------
    # Unique items
    # --------------------------------------------------------

    if "itemid" in chunk.columns:
        unique_items.update(
            chunk["itemid"].dropna().unique()
        )


    # --------------------------------------------------------
    # Timestamp range
    # --------------------------------------------------------

    if "timestamp" in chunk.columns:

        chunk_min = chunk["timestamp"].min()
        chunk_max = chunk["timestamp"].max()

        if min_timestamp is None or chunk_min < min_timestamp:
            min_timestamp = chunk_min

        if max_timestamp is None or chunk_max > max_timestamp:
            max_timestamp = chunk_max


    # --------------------------------------------------------
    # Exact duplicate rows
    # --------------------------------------------------------

    row_hashes = pd.util.hash_pandas_object(
        chunk,
        index=False
    )

    for row_hash in row_hashes:

        if row_hash in duplicate_hashes:
            duplicate_count += 1
        else:
            duplicate_hashes.add(row_hash)


    # --------------------------------------------------------
    # Progress
    # --------------------------------------------------------

    if chunk_number % 5 == 0:
        print(
            f"Processed approximately "
            f"{row_count:,} rows..."
        )


# ============================================================
# FINAL REPORT
# ============================================================


print("\n")
print("=" * 70)
print("DATA PROFILING REPORT")
print("=" * 70)


# ------------------------------------------------------------
# 7. Dataset size
# ------------------------------------------------------------

print("\n2. DATASET SIZE")
print("-" * 70)

print(f"Total rows:    {row_count:,}")
print(f"Total columns: {len(header.columns)}")


# ------------------------------------------------------------
# 8. Column information
# ------------------------------------------------------------

print("\n3. COLUMN INFORMATION")
print("-" * 70)

print(header)


# ------------------------------------------------------------
# 9. Event distribution
# ------------------------------------------------------------

print("\n4. EVENT DISTRIBUTION")
print("-" * 70)

for event, count in event_counts.most_common():

    percentage = (count / row_count) * 100

    print(
        f"{event:<15} "
        f"{count:>12,} "
        f"({percentage:>6.2f}%)"
    )


# ------------------------------------------------------------
# 10. Unique entities
# ------------------------------------------------------------

print("\n5. UNIQUE ENTITIES")
print("-" * 70)

print(f"Unique visitors: {len(unique_visitors):,}")
print(f"Unique items:    {len(unique_items):,}")


# ------------------------------------------------------------
# 11. Missing values
# ------------------------------------------------------------

print("\n6. MISSING VALUES")
print("-" * 70)

for column in header.columns:

    missing = missing_counts[column]

    percentage = (
        missing / row_count * 100
        if row_count > 0
        else 0
    )

    print(
        f"{column:<15} "
        f"{missing:>12,} "
        f"({percentage:>6.2f}%)"
    )


# ------------------------------------------------------------
# 12. Timestamp range
# ------------------------------------------------------------

print("\n7. TIMESTAMP RANGE")
print("-" * 70)

print(f"Minimum timestamp: {min_timestamp}")
print(f"Maximum timestamp: {max_timestamp}")


# ------------------------------------------------------------
# 13. Duplicate rows
# ------------------------------------------------------------

print("\n8. DUPLICATE ROWS")
print("-" * 70)

print(f"Potential exact duplicate rows: {duplicate_count:,}")


# ------------------------------------------------------------
# 14. Basic event relationship
# ------------------------------------------------------------

print("\n9. BASIC BEHAVIORAL SUMMARY")
print("-" * 70)

if row_count > 0:

    views = event_counts.get("view", 0)
    carts = event_counts.get("addtocart", 0)
    transactions = event_counts.get("transaction", 0)

    print(f"Views:        {views:,}")
    print(f"Add to carts: {carts:,}")
    print(f"Transactions: {transactions:,}")

    print("\nEvent-level proportions:")

    print(
        f"View:        {views / row_count * 100:.2f}%"
    )

    print(
        f"Add to cart: {carts / row_count * 100:.2f}%"
    )

    print(
        f"Transaction: {transactions / row_count * 100:.2f}%"
    )


# ------------------------------------------------------------
# 15. Important warning
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("IMPORTANT")
print("=" * 70)

print("""
These event percentages are NOT visitor conversion rates.

For example:

Transaction events / all events

is NOT the same as:

Visitors who purchased / visitors who viewed.

We will calculate the actual funnel separately.
""")


print("\nProfiling complete.")
print("=" * 70)
