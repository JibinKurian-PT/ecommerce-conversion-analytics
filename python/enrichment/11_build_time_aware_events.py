import pandas as pd
import time
from pathlib import Path


# ============================================================
# 1. FILE PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

EVENTS_FILE = BASE_DIR / "data" / "raw" / "events.csv"
PART1_FILE = BASE_DIR / "data" / "raw" / "item_properties_part1.csv"
PART2_FILE = BASE_DIR / "data" / "raw" / "item_properties_part2.csv"

OUTPUT_FILE = BASE_DIR / "data" / "processed" / "events_time_aware_enriched.csv"

# ============================================================
# 2. START
# ============================================================

start_time = time.time()

print("=" * 70)
print("TIME-AWARE EVENT ENRICHMENT")
print("=" * 70)


# ============================================================
# 3. LOAD EVENTS
# ============================================================

print("\n1. Loading events.csv...")

events = pd.read_csv(
    EVENTS_FILE,
    usecols=[
        "timestamp",
        "visitorid",
        "event",
        "itemid",
        "transactionid"
    ]
)

print(f"Events loaded: {len(events):,}")


# Convert timestamp to integer
events["timestamp"] = pd.to_numeric(
    events["timestamp"],
    errors="coerce"
)

events = events.dropna(
    subset=["timestamp", "itemid"]
)

events["timestamp"] = events["timestamp"].astype("int64")
events["itemid"] = events["itemid"].astype("int64")


# ============================================================
# 4. LOAD ONLY REQUIRED PROPERTIES
# ============================================================

print("\n2. Loading item property files...")

property_columns = [
    "timestamp",
    "itemid",
    "property",
    "value"
]

part1 = pd.read_csv(
    PART1_FILE,
    usecols=property_columns
)

print(f"Part 1 rows: {len(part1):,}")

part2 = pd.read_csv(
    PART2_FILE,
    usecols=property_columns
)

print(f"Part 2 rows: {len(part2):,}")


# ============================================================
# 5. COMBINE PROPERTY FILES
# ============================================================

print("\n3. Combining property files...")

properties = pd.concat(
    [part1, part2],
    ignore_index=True
)

del part1
del part2

print(
    f"Combined property rows: "
    f"{len(properties):,}"
)


# ============================================================
# 6. KEEP ONLY CATEGORY + AVAILABILITY
# ============================================================

print("\n4. Filtering required properties...")

properties = properties[
    properties["property"].isin(
        ["categoryid", "available"]
    )
].copy()

print(
    f"Relevant property rows: "
    f"{len(properties):,}"
)

print("\nProperty counts:")
print(
    properties["property"]
    .value_counts()
)


# ============================================================
# 7. PREPARE PROPERTY DATA
# ============================================================

properties["timestamp"] = pd.to_numeric(
    properties["timestamp"],
    errors="coerce"
)

properties = properties.dropna(
    subset=["timestamp", "itemid", "value"]
)

properties["timestamp"] = properties[
    "timestamp"
].astype("int64")

properties["itemid"] = properties[
    "itemid"
].astype("int64")


# ============================================================
# 8. CREATE CATEGORY HISTORY
# ============================================================

print("\n5. Preparing category history...")

category_history = properties[
    properties["property"] == "categoryid"
][
    ["timestamp", "itemid", "value"]
].copy()

category_history = category_history.rename(
    columns={
        "value": "categoryid",
        "timestamp": "property_timestamp"
    }
)

print(
    f"Category history rows: "
    f"{len(category_history):,}"
)


# ============================================================
# 9. CREATE AVAILABILITY HISTORY
# ============================================================

print("\n6. Preparing availability history...")

availability_history = properties[
    properties["property"] == "available"
][
    ["timestamp", "itemid", "value"]
].copy()

availability_history = availability_history.rename(
    columns={
        "value": "available",
        "timestamp": "property_timestamp"
    }
)

print(
    f"Availability history rows: "
    f"{len(availability_history):,}"
)

del properties


# ============================================================
# 10. FUNCTION FOR TIME-AWARE MATCHING
# ============================================================

def time_aware_match(
    events_df,
    history_df,
    property_name
):

    print("\n" + "-" * 70)
    print(
        f"TIME-AWARE MATCHING: {property_name}"
    )
    print("-" * 70)

    results = []

    # Only process items that exist in both datasets
    common_items = set(
        events_df["itemid"].unique()
    ).intersection(
        history_df["itemid"].unique()
    )

    print(
        f"Common items: "
        f"{len(common_items):,}"
    )

    # Work item by item
    for counter, item_id in enumerate(
        common_items,
        start=1
    ):

        event_part = events_df[
            events_df["itemid"] == item_id
        ].copy()

        history_part = history_df[
            history_df["itemid"] == item_id
        ].copy()

        if event_part.empty or history_part.empty:
            continue

        # Sort by time
        event_part = event_part.sort_values(
            "timestamp"
        )

        history_part = history_part.sort_values(
            "property_timestamp"
        )

        # Time-aware join
        matched = pd.merge_asof(
            event_part,
            history_part[
                [
                    "property_timestamp",
                    property_name
                ]
            ],
            left_on="timestamp",
            right_on="property_timestamp",
            direction="backward"
        )

        results.append(matched)

        # Progress
        if counter % 10000 == 0:
            print(
                f"Processed {counter:,} / "
                f"{len(common_items):,} items"
            )

    if not results:
        return pd.DataFrame()

    result = pd.concat(
        results,
        ignore_index=True
    )

    return result


# ============================================================
# 11. MATCH CATEGORY
# ============================================================

category_events = time_aware_match(
    events,
    category_history,
    "categoryid"
)

print(
    f"\nCategory matched rows: "
    f"{len(category_events):,}"
)


# ============================================================
# 12. MATCH AVAILABILITY
# ============================================================

availability_events = time_aware_match(
    events,
    availability_history,
    "available"
)

print(
    f"\nAvailability matched rows: "
    f"{len(availability_events):,}"
)


# ============================================================
# 13. PREPARE CATEGORY RESULT
# ============================================================

category_result = category_events[
    [
        "timestamp",
        "visitorid",
        "event",
        "itemid",
        "transactionid",
        "categoryid",
        "property_timestamp"
    ]
].copy()

category_result = category_result.rename(
    columns={
        "property_timestamp":
        "category_property_timestamp"
    }
)


# ============================================================
# 14. PREPARE AVAILABILITY RESULT
# ============================================================

availability_result = availability_events[
    [
        "timestamp",
        "visitorid",
        "event",
        "itemid",
        "transactionid",
        "available",
        "property_timestamp"
    ]
].copy()

availability_result = availability_result.rename(
    columns={
        "property_timestamp":
        "availability_property_timestamp"
    }
)


# ============================================================
# 15. MERGE CATEGORY + AVAILABILITY
# ============================================================

print("\n7. Combining category and availability...")

final_events = pd.merge(
    category_result,
    availability_result[
        [
            "timestamp",
            "visitorid",
            "event",
            "itemid",
            "transactionid",
            "available",
            "availability_property_timestamp"
        ]
    ],
    on=[
        "timestamp",
        "visitorid",
        "event",
        "itemid",
        "transactionid"
    ],
    how="outer"
)


# ============================================================
# 16. CHECK MATCHING
# ============================================================

print("\n" + "=" * 70)
print("MATCHING QUALITY")
print("=" * 70)

total_events = len(events)

category_matched = (
    final_events["categoryid"]
    .notna()
    .sum()
)

availability_matched = (
    final_events["available"]
    .notna()
    .sum()
)

neither_matched = (
    final_events[
        ["categoryid", "available"]
    ]
    .isna()
    .all(axis=1)
    .sum()
)

print(
    f"\nTotal events: "
    f"{total_events:,}"
)

print(
    f"Category matched: "
    f"{category_matched:,}"
)

print(
    f"Category coverage: "
    f"{category_matched / total_events * 100:.2f}%"
)

print(
    f"\nAvailability matched: "
    f"{availability_matched:,}"
)

print(
    f"Availability coverage: "
    f"{availability_matched / total_events * 100:.2f}%"
)

print(
    f"\nNeither property matched: "
    f"{neither_matched:,}"
)


# ============================================================
# 17. VALIDATE FUTURE MATCHES
# ============================================================

print("\n" + "=" * 70)
print("VALIDATION")
print("=" * 70)


# Category future matches
category_future = (
    final_events[
        "category_property_timestamp"
    ]
    > final_events["timestamp"]
).sum()

# Availability future matches
availability_future = (
    final_events[
        "availability_property_timestamp"
    ]
    > final_events["timestamp"]
).sum()


print(
    f"\nCategory matched from future: "
    f"{category_future:,}"
)

print(
    f"Availability matched from future: "
    f"{availability_future:,}"
)


# ============================================================
# 18. AVAILABILITY VALUE DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("AVAILABILITY VALUE DISTRIBUTION")
print("=" * 70)

print(
    final_events["available"]
    .value_counts(dropna=False)
)


# ============================================================
# 19. EVENT TYPE COVERAGE
# ============================================================

print("\n" + "=" * 70)
print("EVENT TYPE COVERAGE")
print("=" * 70)

event_summary = (
    final_events
    .groupby("event")
    .agg(
        total_events=("event", "size"),
        category_matched=(
            "categoryid",
            lambda x: x.notna().sum()
        ),
        availability_matched=(
            "available",
            lambda x: x.notna().sum()
        )
    )
)

event_summary[
    "category_coverage_%"
] = (
    event_summary["category_matched"]
    / event_summary["total_events"]
    * 100
)

event_summary[
    "availability_coverage_%"
] = (
    event_summary["availability_matched"]
    / event_summary["total_events"]
    * 100
)

print(event_summary)


# ============================================================
# 20. SAMPLE RESULTS
# ============================================================

print("\n" + "=" * 70)
print("SAMPLE TIME-AWARE MATCHES")
print("=" * 70)

sample_columns = [
    "timestamp",
    "visitorid",
    "event",
    "itemid",
    "categoryid",
    "category_property_timestamp",
    "available",
    "availability_property_timestamp"
]

print(
    final_events[
        sample_columns
    ].head(20).to_string(index=False)
)


# ============================================================
# 21. SAVE RESULT
# ============================================================

print("\n" + "=" * 70)
print("SAVING RESULT")
print("=" * 70)

final_events.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"\nSaved to:\n{OUTPUT_FILE}"
)


# ============================================================
# 22. FINISH
# ============================================================

elapsed = time.time() - start_time

print(
    f"\nTotal execution time: "
    f"{elapsed / 60:.2f} minutes"
)

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
