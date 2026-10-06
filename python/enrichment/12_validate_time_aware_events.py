import pandas as pd
import time


# ============================================================
# 1. FILE PATHS
# ============================================================

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

ORIGINAL_EVENTS = BASE_DIR / "data" / "raw" / "events.csv"

ENRICHED_EVENTS = (
    BASE_DIR / "data" / "processed" / "events_time_aware_enriched.csv"
)


# ============================================================
# 2. START
# ============================================================

start_time = time.time()

print("=" * 70)
print("TIME-AWARE ENRICHED EVENTS VALIDATION")
print("=" * 70)


# ============================================================
# 3. LOAD ORIGINAL EVENTS
# ============================================================

print("\n1. Loading original events...")

original = pd.read_csv(
    ORIGINAL_EVENTS,
    usecols=[
        "timestamp",
        "visitorid",
        "event",
        "itemid",
        "transactionid"
    ]
)

print(
    f"Original rows: {len(original):,}"
)


# ============================================================
# 4. LOAD ENRICHED EVENTS
# ============================================================

print("\n2. Loading enriched events...")

enriched = pd.read_csv(
    ENRICHED_EVENTS,
    usecols=[
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
)

print(
    f"Enriched rows: {len(enriched):,}"
)


# ============================================================
# 5. ROW COUNT CHECK
# ============================================================

print("\n" + "=" * 70)
print("CHECK 1 — ROW COUNT")
print("=" * 70)

original_count = len(original)
enriched_count = len(enriched)

print(
    f"\nOriginal:  {original_count:,}"
)

print(
    f"Enriched:  {enriched_count:,}"
)

difference = enriched_count - original_count

print(
    f"Difference: {difference:,}"
)

if difference == 0:
    print("\nPASS: Row counts are identical.")
else:
    print(
        "\nWARNING: Row counts are different."
    )


# ============================================================
# 6. DUPLICATE CHECK — ORIGINAL
# ============================================================

print("\n" + "=" * 70)
print("CHECK 2 — DUPLICATES IN ORIGINAL DATA")
print("=" * 70)

key_columns = [
    "timestamp",
    "visitorid",
    "event",
    "itemid",
    "transactionid"
]

original_duplicates = original.duplicated(
    subset=key_columns,
    keep=False
).sum()

original_duplicate_groups = original[
    key_columns
].duplicated(
    keep=False
).sum()

print(
    f"\nDuplicate event rows in original: "
    f"{original_duplicates:,}"
)

if original_duplicates == 0:
    print("PASS: No duplicate event rows.")
else:
    print(
        "INFO: Original dataset contains "
        "duplicate event records."
    )


# ============================================================
# 7. DUPLICATE CHECK — ENRICHED
# ============================================================

print("\n" + "=" * 70)
print("CHECK 3 — DUPLICATES IN ENRICHED DATA")
print("=" * 70)

enriched_duplicates = enriched.duplicated(
    subset=key_columns,
    keep=False
).sum()

print(
    f"\nDuplicate event rows in enriched: "
    f"{enriched_duplicates:,}"
)

if enriched_duplicates == original_duplicates:
    print(
        "\nPASS: Enrichment did not increase "
        "the number of duplicate event records."
    )
else:
    print(
        "\nWARNING: Duplicate count changed."
    )


# ============================================================
# 8. ORIGINAL EVENTS PRESERVED
# ============================================================

print("\n" + "=" * 70)
print("CHECK 4 — ORIGINAL EVENTS PRESERVED")
print("=" * 70)

# Create event keys
original["_event_key"] = (
    original["timestamp"].astype(str)
    + "_"
    + original["visitorid"].astype(str)
    + "_"
    + original["event"].astype(str)
    + "_"
    + original["itemid"].astype(str)
    + "_"
    + original["transactionid"]
    .fillna(-999999999)
    .astype(str)
)

enriched["_event_key"] = (
    enriched["timestamp"].astype(str)
    + "_"
    + enriched["visitorid"].astype(str)
    + "_"
    + enriched["event"].astype(str)
    + "_"
    + enriched["itemid"].astype(str)
    + "_"
    + enriched["transactionid"]
    .fillna(-999999999)
    .astype(str)
)

original_keys = set(
    original["_event_key"]
)

enriched_keys = set(
    enriched["_event_key"]
)

missing_from_enriched = (
    original_keys - enriched_keys
)

extra_in_enriched = (
    enriched_keys - original_keys
)

print(
    f"\nUnique original event keys: "
    f"{len(original_keys):,}"
)

print(
    f"Unique enriched event keys: "
    f"{len(enriched_keys):,}"
)

print(
    f"Original events missing from enriched: "
    f"{len(missing_from_enriched):,}"
)

print(
    f"Extra event keys in enriched: "
    f"{len(extra_in_enriched):,}"
)

if (
    len(missing_from_enriched) == 0
    and len(extra_in_enriched) == 0
):
    print(
        "\nPASS: All original event keys "
        "are preserved."
    )
else:
    print(
        "\nWARNING: Event keys do not match."
    )


# ============================================================
# 9. TIME VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("CHECK 5 — NO FUTURE PROPERTY MATCHES")
print("=" * 70)

category_future = (
    enriched[
        "category_property_timestamp"
    ].notna()
    &
    (
        enriched[
            "category_property_timestamp"
        ]
        > enriched["timestamp"]
    )
).sum()

availability_future = (
    enriched[
        "availability_property_timestamp"
    ].notna()
    &
    (
        enriched[
            "availability_property_timestamp"
        ]
        > enriched["timestamp"]
    )
).sum()

print(
    f"\nCategory future matches: "
    f"{category_future:,}"
)

print(
    f"Availability future matches: "
    f"{availability_future:,}"
)

if (
    category_future == 0
    and availability_future == 0
):
    print(
        "\nPASS: No future property information "
        "was used."
    )
else:
    print(
        "\nWARNING: Future information detected."
    )


# ============================================================
# 10. PROPERTY TIMESTAMP VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("CHECK 6 — PROPERTY TIMESTAMP VALIDITY")
print("=" * 70)

category_invalid = (
    enriched[
        "category_property_timestamp"
    ].notna()
    &
    (
        enriched[
            "category_property_timestamp"
        ]
        > enriched["timestamp"]
    )
).sum()

availability_invalid = (
    enriched[
        "availability_property_timestamp"
    ].notna()
    &
    (
        enriched[
            "availability_property_timestamp"
        ]
        > enriched["timestamp"]
    )
).sum()

print(
    f"\nInvalid category matches: "
    f"{category_invalid:,}"
)

print(
    f"Invalid availability matches: "
    f"{availability_invalid:,}"
)


# ============================================================
# 11. MATCHING COVERAGE
# ============================================================

print("\n" + "=" * 70)
print("CHECK 7 — PROPERTY COVERAGE")
print("=" * 70)

total = len(enriched)

category_count = (
    enriched["categoryid"]
    .notna()
    .sum()
)

availability_count = (
    enriched["available"]
    .notna()
    .sum()
)

both_count = (
    enriched[
        ["categoryid", "available"]
    ]
    .notna()
    .all(axis=1)
    .sum()
)

neither_count = (
    enriched[
        ["categoryid", "available"]
    ]
    .isna()
    .all(axis=1)
    .sum()
)

category_only = (
    enriched["categoryid"].notna()
    &
    enriched["available"].isna()
).sum()

availability_only = (
    enriched["categoryid"].isna()
    &
    enriched["available"].notna()
).sum()

print(
    f"\nTotal events: {total:,}"
)

print(
    f"Category available: "
    f"{category_count:,} "
    f"({category_count / total * 100:.2f}%)"
)

print(
    f"Availability available: "
    f"{availability_count:,} "
    f"({availability_count / total * 100:.2f}%)"
)

print(
    f"Both available: "
    f"{both_count:,} "
    f"({both_count / total * 100:.2f}%)"
)

print(
    f"Category only: "
    f"{category_only:,}"
)

print(
    f"Availability only: "
    f"{availability_only:,}"
)

print(
    f"Neither available: "
    f"{neither_count:,}"
)


# ============================================================
# 12. EVENT COUNT COMPARISON
# ============================================================

print("\n" + "=" * 70)
print("CHECK 8 — EVENT COUNTS")
print("=" * 70)

original_events = (
    original["event"]
    .value_counts()
    .sort_index()
)

enriched_events = (
    enriched["event"]
    .value_counts()
    .sort_index()
)

comparison = pd.DataFrame({
    "original": original_events,
    "enriched": enriched_events
})

comparison["difference"] = (
    comparison["enriched"]
    - comparison["original"]
)

print("\n")
print(comparison)

if (
    comparison["difference"] == 0
).all():
    print(
        "\nPASS: Event counts are unchanged."
    )
else:
    print(
        "\nWARNING: Event counts changed."
    )


# ============================================================
# 13. VISITOR COUNT COMPARISON
# ============================================================

print("\n" + "=" * 70)
print("CHECK 9 — VISITOR COUNTS")
print("=" * 70)

original_visitors = (
    original["visitorid"]
    .nunique()
)

enriched_visitors = (
    enriched["visitorid"]
    .nunique()
)

print(
    f"\nOriginal unique visitors: "
    f"{original_visitors:,}"
)

print(
    f"Enriched unique visitors: "
    f"{enriched_visitors:,}"
)

if original_visitors == enriched_visitors:
    print(
        "\nPASS: Visitor count unchanged."
    )
else:
    print(
        "\nWARNING: Visitor count changed."
    )


# ============================================================
# 14. ITEM COUNTS
# ============================================================

print("\n" + "=" * 70)
print("CHECK 10 — ITEM COUNTS")
print("=" * 70)

original_items = (
    original["itemid"]
    .nunique()
)

enriched_items = (
    enriched["itemid"]
    .nunique()
)

print(
    f"\nOriginal unique items: "
    f"{original_items:,}"
)

print(
    f"Enriched unique items: "
    f"{enriched_items:,}"
)

if original_items == enriched_items:
    print(
        "\nPASS: Item count unchanged."
    )
else:
    print(
        "\nWARNING: Item count changed."
    )


# ============================================================
# 15. TRANSACTION COUNTS
# ============================================================

print("\n" + "=" * 70)
print("CHECK 11 — TRANSACTION COUNTS")
print("=" * 70)

original_transactions = (
    original["transactionid"]
    .notna()
    .sum()
)

enriched_transactions = (
    enriched["transactionid"]
    .notna()
    .sum()
)

original_unique_transactions = (
    original["transactionid"]
    .nunique()
)

enriched_unique_transactions = (
    enriched["transactionid"]
    .nunique()
)

print(
    f"\nOriginal transaction events: "
    f"{original_transactions:,}"
)

print(
    f"Enriched transaction events: "
    f"{enriched_transactions:,}"
)

print(
    f"\nOriginal unique transaction IDs: "
    f"{original_unique_transactions:,}"
)

print(
    f"Enriched unique transaction IDs: "
    f"{enriched_unique_transactions:,}"
)


# ============================================================
# 16. SAMPLE MATCHED RECORDS
# ============================================================

print("\n" + "=" * 70)
print("CHECK 12 — SAMPLE MATCHED RECORDS")
print("=" * 70)

matched_sample = enriched[
    enriched["categoryid"].notna()
    &
    enriched["available"].notna()
][
    [
        "timestamp",
        "visitorid",
        "event",
        "itemid",
        "categoryid",
        "category_property_timestamp",
        "available",
        "availability_property_timestamp"
    ]
].head(10)

print(
    matched_sample.to_string(
        index=False
    )
)


# ============================================================
# 17. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("FINAL VALIDATION SUMMARY")
print("=" * 70)

checks = {
    "Row count unchanged":
        enriched_count == original_count,

    "No future category matches":
        category_future == 0,

    "No future availability matches":
        availability_future == 0,

    "All original event keys preserved":
        len(missing_from_enriched) == 0
        and len(extra_in_enriched) == 0,

    "Event counts unchanged":
        (comparison["difference"] == 0).all(),

    "Visitor count unchanged":
        original_visitors == enriched_visitors,

    "Item count unchanged":
        original_items == enriched_items
}

for check, result in checks.items():

    status = "PASS" if result else "FAIL"

    print(
        f"{status}: {check}"
    )


# ============================================================
# 18. FINISH
# ============================================================

elapsed = time.time() - start_time

print(
    f"\nValidation completed in "
    f"{elapsed / 60:.2f} minutes"
)

print("\n" + "=" * 70)
print("VALIDATION COMPLETE")
print("=" * 70)
