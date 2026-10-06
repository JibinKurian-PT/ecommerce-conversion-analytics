import pandas as pd
from pathlib import Path


# ============================================================
# E-COMMERCE CONVERSION ANALYTICS
# EVENTS INVESTIGATION
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[2]
FILE_PATH = PROJECT_DIR / "data" / "raw" / "events.csv"

print("=" * 70)
print("EVENTS.CSV - DEEPER DATA UNDERSTANDING")
print("=" * 70)


# ------------------------------------------------------------
# 1. Load a sample
# ------------------------------------------------------------

sample = pd.read_csv(FILE_PATH, nrows=10)


print("\n1. SAMPLE RECORDS")
print("-" * 70)

print(sample.to_string(index=False))


# ------------------------------------------------------------
# 2. Data types
# ------------------------------------------------------------

print("\n2. DATA TYPES")
print("-" * 70)

print(sample.dtypes)


# ------------------------------------------------------------
# 3. Convert timestamps
# ------------------------------------------------------------

print("\n3. TIMESTAMP CONVERSION")
print("-" * 70)

sample["datetime"] = pd.to_datetime(
    sample["timestamp"],
    unit="ms"
)

print(
    sample[
        ["timestamp", "datetime"]
    ].to_string(index=False)
)


# ------------------------------------------------------------
# 4. Actual date range
# ------------------------------------------------------------

print("\n4. ACTUAL DATE RANGE")
print("-" * 70)

date_range = pd.read_csv(
    FILE_PATH,
    usecols=["timestamp"]
)

date_range["datetime"] = pd.to_datetime(
    date_range["timestamp"],
    unit="ms"
)

print(
    "Start:",
    date_range["datetime"].min()
)

print(
    "End:",
    date_range["datetime"].max()
)


# ------------------------------------------------------------
# 5. Transaction ID missingness by event
# ------------------------------------------------------------

print("\n5. TRANSACTION ID BY EVENT")
print("-" * 70)

events = pd.read_csv(
    FILE_PATH,
    usecols=[
        "event",
        "transactionid"
    ]
)

summary = (
    events
    .groupby("event")
    .agg(
        total_events=("event", "size"),
        missing_transaction_id=(
            "transactionid",
            lambda x: x.isna().sum()
        ),
        non_missing_transaction_id=(
            "transactionid",
            lambda x: x.notna().sum()
        )
    )
)

summary["missing_percentage"] = (
    summary["missing_transaction_id"]
    / summary["total_events"]
    * 100
)

print(summary)


# ------------------------------------------------------------
# 6. Transaction event details
# ------------------------------------------------------------

print("\n6. TRANSACTION EVENTS")
print("-" * 70)

transactions = events[
    events["event"] == "transaction"
]

print(
    f"Transaction events: "
    f"{len(transactions):,}"
)

print(
    f"Missing transaction IDs among "
    f"transaction events: "
    f"{transactions['transactionid'].isna().sum():,}"
)

print(
    f"Unique transaction IDs: "
    f"{transactions['transactionid'].nunique():,}"
)


# ------------------------------------------------------------
# 7. Duplicate investigation
# ------------------------------------------------------------

print("\n7. DUPLICATE INVESTIGATION")
print("-" * 70)

events_full = pd.read_csv(FILE_PATH)

duplicates = events_full[
    events_full.duplicated(
        keep=False
    )
]

print(
    f"Rows involved in duplicate groups: "
    f"{len(duplicates):,}"
)

print(
    f"Number of duplicated row groups: "
    f"{duplicates.duplicated().sum():,}"
)

if len(duplicates) > 0:

    print("\nSample duplicated records:")

    print(
        duplicates
        .sort_values(
            by=[
                "timestamp",
                "visitorid"
            ]
        )
        .head(20)
        .to_string(index=False)
    )


# ------------------------------------------------------------
# 8. Events per visitor
# ------------------------------------------------------------

print("\n8. EVENTS PER VISITOR")
print("-" * 70)

visitor_activity = (
    events_full
    .groupby("visitorid")
    .size()
)

print(
    f"Average events per visitor: "
    f"{visitor_activity.mean():.2f}"
)

print(
    f"Median events per visitor: "
    f"{visitor_activity.median():.0f}"
)

print(
    f"Maximum events by one visitor: "
    f"{visitor_activity.max():,}"
)


# ------------------------------------------------------------
# 9. Final
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("INVESTIGATION COMPLETE")
print("=" * 70)
