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

OUTPUT_FILE = (
    BASE_DIR / "data" / "processed" / "final_time_aware_events.csv"
)

# ============================================================
# 2. START
# ============================================================

start_time = time.time()

print("=" * 70)
print("FINAL TIME-AWARE EVENT ENRICHMENT")
print("=" * 70)


# ============================================================
# 3. LOAD ORIGINAL EVENTS
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

print(
    f"Original events loaded: "
    f"{len(events):,}"
)


# ============================================================
# 4. CREATE UNIQUE EVENT ROW ID
# ============================================================

print("\n2. Creating event_row_id...")

events.insert(
    0,
    "event_row_id",
    range(1, len(events) + 1)
)

print(
    f"Created IDs: "
    f"{events['event_row_id'].min():,} "
    f"to "
    f"{events['event_row_id'].max():,}"
)


# ============================================================
# 5. PREPARE EVENT DATA TYPES
# ============================================================

events["timestamp"] = pd.to_numeric(
    events["timestamp"],
    errors="coerce"
)

events["itemid"] = pd.to_numeric(
    events["itemid"],
    errors="coerce"
)

events = events.dropna(
    subset=[
        "timestamp",
        "itemid"
    ]
)

events["timestamp"] = events[
    "timestamp"
].astype("int64")

events["itemid"] = events[
    "itemid"
].astype("int64")


# ============================================================
# 6. LOAD ITEM PROPERTIES
# ============================================================

print("\n3. Loading item property files...")

part1 = pd.read_csv(
    PART1_FILE,
    usecols=[
        "timestamp",
        "itemid",
        "property",
        "value"
    ]
)

print(
    f"Part 1: {len(part1):,} rows"
)

part2 = pd.read_csv(
    PART2_FILE,
    usecols=[
        "timestamp",
        "itemid",
        "property",
        "value"
    ]
)

print(
    f"Part 2: {len(part2):,} rows"
)


# ============================================================
# 7. COMBINE PROPERTIES
# ============================================================

print("\n4. Combining property files...")

properties = pd.concat(
    [part1, part2],
    ignore_index=True
)

del part1
del part2

print(
    f"Combined properties: "
    f"{len(properties):,}"
)


# ============================================================
# 8. KEEP ONLY REQUIRED PROPERTIES
# ============================================================

print("\n5. Filtering categoryid and available...")

properties = properties[
    properties["property"].isin(
        [
            "categoryid",
            "available"
        ]
    )
].copy()

print(
    f"Relevant properties: "
    f"{len(properties):,}"
)

print("\nProperty distribution:")

print(
    properties["property"]
    .value_counts()
)


# ============================================================
# 9. PREPARE PROPERTY DATA
# ============================================================

properties["timestamp"] = pd.to_numeric(
    properties["timestamp"],
    errors="coerce"
)

properties["itemid"] = pd.to_numeric(
    properties["itemid"],
    errors="coerce"
)

properties = properties.dropna(
    subset=[
        "timestamp",
        "itemid",
        "value"
    ]
)

properties["timestamp"] = properties[
    "timestamp"
].astype("int64")

properties["itemid"] = properties[
    "itemid"
].astype("int64")


# ============================================================
# 10. CATEGORY HISTORY
# ============================================================

print("\n6. Preparing category history...")

category_history = properties[
    properties["property"] == "categoryid"
][
    [
        "timestamp",
        "itemid",
        "value"
    ]
].copy()

category_history = category_history.rename(
    columns={
        "timestamp":
            "category_property_timestamp",

        "value":
            "categoryid"
    }
)

print(
    f"Category history rows: "
    f"{len(category_history):,}"
)


# ============================================================
# 11. AVAILABILITY HISTORY
# ============================================================

print("\n7. Preparing availability history...")

availability_history = properties[
    properties["property"] == "available"
][
    [
        "timestamp",
        "itemid",
        "value"
    ]
].copy()

availability_history = availability_history.rename(
    columns={
        "timestamp":
            "availability_property_timestamp",

        "value":
            "available"
    }
)

print(
    f"Availability history rows: "
    f"{len(availability_history):,}"
)

del properties


# ============================================================
# 12. TIME-AWARE MATCHING FUNCTION
# ============================================================

def match_property(
    events_df,
    history_df,
    property_name,
    property_timestamp_name
):

    print("\n" + "-" * 70)
    print(
        f"TIME-AWARE MATCHING: "
        f"{property_name}"
    )
    print("-" * 70)

    results = []

    common_items = set(
        events_df["itemid"].unique()
    ).intersection(
        history_df["itemid"].unique()
    )

    print(
        f"Common items: "
        f"{len(common_items):,}"
    )

    for counter, item_id in enumerate(
        common_items,
        start=1
    ):

        event_part = events_df[
            events_df["itemid"] == item_id
        ][
            [
                "event_row_id",
                "timestamp",
                "itemid"
            ]
        ].copy()

        history_part = history_df[
            history_df["itemid"] == item_id
        ][
            [
                property_timestamp_name,
                "itemid",
                property_name
            ]
        ].copy()

        if event_part.empty:
            continue

        if history_part.empty:
            continue

        # Sort both datasets by time
        event_part = event_part.sort_values(
            "timestamp"
        )

        history_part = history_part.sort_values(
            property_timestamp_name
        )

        # ----------------------------------------------------
        # Time-aware join
        # ----------------------------------------------------

        matched = pd.merge_asof(
            event_part,
            history_part[
                [
                    property_timestamp_name,
                    property_name
                ]
            ],
            left_on="timestamp",
            right_on=property_timestamp_name,
            direction="backward"
        )

        results.append(
            matched[
                [
                    "event_row_id",
                    property_name,
                    property_timestamp_name
                ]
            ]
        )

        if counter % 10000 == 0:

            print(
                f"Processed "
                f"{counter:,} / "
                f"{len(common_items):,} items"
            )

    if not results:

        return pd.DataFrame(
            columns=[
                "event_row_id",
                property_name,
                property_timestamp_name
            ]
        )

    result = pd.concat(
        results,
        ignore_index=True
    )

    return result


# ============================================================
# 13. CATEGORY MATCH
# ============================================================

category_matches = match_property(
    events,
    category_history,
    "categoryid",
    "category_property_timestamp"
)

print(
    f"\nCategory match rows: "
    f"{len(category_matches):,}"
)


# ============================================================
# 14. AVAILABILITY MATCH
# ============================================================

availability_matches = match_property(
    events,
    availability_history,
    "available",
    "availability_property_timestamp"
)

print(
    f"\nAvailability match rows: "
    f"{len(availability_matches):,}"
)


# ============================================================
# 15. REMOVE PROPERTY HISTORY FROM MEMORY
# ============================================================

del category_history
del availability_history


# ============================================================
# 16. LEFT JOIN CATEGORY BACK TO ALL EVENTS
# ============================================================

print("\n8. Attaching category information...")

final_events = events.merge(
    category_matches,
    on="event_row_id",
    how="left",
    validate="one_to_one"
)

del category_matches


# ============================================================
# 17. LEFT JOIN AVAILABILITY BACK TO ALL EVENTS
# ============================================================

print(
    "\n9. Attaching availability information..."
)

final_events = final_events.merge(
    availability_matches,
    on="event_row_id",
    how="left",
    validate="one_to_one"
)

del availability_matches


# ============================================================
# 18. SORT BACK TO ORIGINAL ORDER
# ============================================================

print(
    "\n10. Restoring original event order..."
)

final_events = final_events.sort_values(
    "event_row_id"
).reset_index(
    drop=True
)


# ============================================================
# 19. BASIC FINAL CHECK
# ============================================================

print("\n" + "=" * 70)
print("FINAL DATASET CHECK")
print("=" * 70)

print(
    f"\nOriginal rows: "
    f"{len(events):,}"
)

print(
    f"Final rows: "
    f"{len(final_events):,}"
)

print(
    f"Difference: "
    f"{len(final_events) - len(events):,}"
)


# ============================================================
# 20. PROPERTY COVERAGE
# ============================================================

print("\n" + "=" * 70)
print("PROPERTY COVERAGE")
print("=" * 70)

total_events = len(final_events)

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

both_matched = (
    final_events[
        [
            "categoryid",
            "available"
        ]
    ]
    .notna()
    .all(axis=1)
    .sum()
)

neither_matched = (
    final_events[
        [
            "categoryid",
            "available"
        ]
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
    f"\nBoth matched: "
    f"{both_matched:,}"
)

print(
    f"Neither matched: "
    f"{neither_matched:,}"
)


# ============================================================
# 21. FUTURE MATCH CHECK
# ============================================================

print("\n" + "=" * 70)
print("FUTURE MATCH VALIDATION")
print("=" * 70)

category_future = (
    final_events[
        "category_property_timestamp"
    ].notna()
    &
    (
        final_events[
            "category_property_timestamp"
        ]
        > final_events["timestamp"]
    )
).sum()

availability_future = (
    final_events[
        "availability_property_timestamp"
    ].notna()
    &
    (
        final_events[
            "availability_property_timestamp"
        ]
        > final_events["timestamp"]
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


# ============================================================
# 22. EVENT COUNTS
# ============================================================

print("\n" + "=" * 70)
print("EVENT COUNTS")
print("=" * 70)

print(
    final_events["event"]
    .value_counts()
    .sort_index()
)


# ============================================================
# 23. VISITOR AND ITEM COUNTS
# ============================================================

print("\n" + "=" * 70)
print("VISITOR / ITEM COUNTS")
print("=" * 70)

print(
    f"\nUnique visitors: "
    f"{final_events['visitorid'].nunique():,}"
)

print(
    f"Unique items: "
    f"{final_events['itemid'].nunique():,}"
)


# ============================================================
# 24. TRANSACTION COUNTS
# ============================================================

print("\n" + "=" * 70)
print("TRANSACTION COUNTS")
print("=" * 70)

print(
    f"\nTransaction events: "
    f"{final_events['transactionid'].notna().sum():,}"
)

print(
    f"Unique transaction IDs: "
    f"{final_events['transactionid'].nunique():,}"
)


# ============================================================
# 25. DUPLICATE EVENT ROWS
# ============================================================

print("\n" + "=" * 70)
print("DUPLICATE CHECK")
print("=" * 70)

duplicate_event_rows = final_events.duplicated(
    subset=[
        "timestamp",
        "visitorid",
        "event",
        "itemid",
        "transactionid"
    ],
    keep=False
).sum()

print(
    f"\nDuplicate event rows: "
    f"{duplicate_event_rows:,}"
)

print(
    "\nImportant: duplicate event rows "
    "are preserved because event_row_id "
    "uniquely identifies the original row."
)


# ============================================================
# 26. SAMPLE MATCHED RECORDS
# ============================================================

print("\n" + "=" * 70)
print("SAMPLE MATCHED RECORDS")
print("=" * 70)

sample = final_events[
    final_events["categoryid"].notna()
    &
    final_events["available"].notna()
][
    [
        "event_row_id",
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
    sample.to_string(index=False)
)


# ============================================================
# 27. SAVE FINAL DATASET
# ============================================================

print("\n" + "=" * 70)
print("SAVING FINAL DATASET")
print("=" * 70)

final_events.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"\nSaved to:\n{OUTPUT_FILE}"
)


# ============================================================
# 28. FINAL PASS / FAIL
# ============================================================

print("\n" + "=" * 70)
print("FINAL VALIDATION")
print("=" * 70)

row_count_pass = (
    len(final_events) == len(events)
)

future_pass = (
    category_future == 0
    and availability_future == 0
)

visitor_pass = (
    final_events["visitorid"].nunique()
    == events["visitorid"].nunique()
)

item_pass = (
    final_events["itemid"].nunique()
    == events["itemid"].nunique()
)

event_counts_pass = (
    final_events["event"]
    .value_counts()
    .sort_index()
    .equals(
        events["event"]
        .value_counts()
        .sort_index()
    )
)

checks = {
    "Row count preserved":
        row_count_pass,

    "No future category matches":
        category_future == 0,

    "No future availability matches":
        availability_future == 0,

    "Visitor count preserved":
        visitor_pass,

    "Item count preserved":
        item_pass,

    "Event counts preserved":
        event_counts_pass
}

for check, passed in checks.items():

    if passed:
        print(
            f"PASS: {check}"
        )
    else:
        print(
            f"FAIL: {check}"
        )


# ============================================================
# 29. EXECUTION TIME
# ============================================================

elapsed = time.time() - start_time

print(
    f"\nExecution time: "
    f"{elapsed / 60:.2f} minutes"
)

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
