import pandas as pd
from pathlib import Path

# ============================================================
# E-COMMERCE CONVERSION ANALYTICS
# TIME-AWARE PRODUCT PROPERTY TEST
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

BASE_DIR = Path(__file__).resolve().parents[2]

EVENTS_FILE = BASE_DIR / "data" / "raw" / "events.csv"
PART1_FILE = BASE_DIR / "data" / "raw" / "item_properties_part1.csv"
PART2_FILE = BASE_DIR / "data" / "raw" / "item_properties_part2.csv"	

print("=" * 70)
print("E-COMMERCE CONVERSION ANALYTICS")
print("TIME-AWARE PRODUCT PROPERTY TEST")
print("=" * 70)

# ============================================================
# 1. LOAD EVENTS
# ============================================================

print("\nLoading events.csv...")

events = pd.read_csv(
    EVENTS_FILE,
    usecols=[
        "timestamp",
        "visitorid",
        "event",
        "itemid"
    ]
)

print(f"Events loaded: {len(events):,}")

# ============================================================
# 2. LOAD ONLY RELEVANT PROPERTIES
# ============================================================

print("\nLoading categoryid and available properties...")

property_parts = []

for file in [PART1_FILE, PART2_FILE]:

    print(f"Loading: {file.name}")

    part = pd.read_csv(
        file,
        usecols=[
            "timestamp",
            "itemid",
            "property",
            "value"
        ]
    )

    part = part[
        part["property"].isin(
            ["categoryid", "available"]
        )
    ].copy()

    property_parts.append(part)

properties = pd.concat(
    property_parts,
    ignore_index=True
)

print(
    f"Relevant property records: "
    f"{len(properties):,}"
)

# ============================================================
# 3. CONVERT TIMESTAMPS
# ============================================================

print("\nConverting timestamps...")

events["timestamp"] = pd.to_datetime(
    events["timestamp"],
    unit="ms"
)

properties["timestamp"] = pd.to_datetime(
    properties["timestamp"],
    unit="ms"
)

# ============================================================
# 4. SORT BOTH DATASETS
# ============================================================

print("\nSorting data...")

events = events.sort_values(
    ["itemid", "timestamp"]
).reset_index(drop=True)

properties = properties.sort_values(
    ["itemid", "timestamp"]
).reset_index(drop=True)

# ============================================================
# 5. MATCH ONE ITEM AT A TIME
# ============================================================

print("\nMatching product properties to customer events...")
print("This may take some time.")

matched_parts = []

common_items = set(events["itemid"]) & set(
    properties["itemid"]
)

print(
    f"Items appearing in both datasets: "
    f"{len(common_items):,}"
)

for count, item_id in enumerate(common_items, start=1):

    event_subset = events[
        events["itemid"] == item_id
    ]

    property_subset = properties[
        properties["itemid"] == item_id
    ]

    if event_subset.empty or property_subset.empty:
        continue

    event_subset = event_subset.sort_values(
        "timestamp"
    )

    property_subset = property_subset.sort_values(
        "timestamp"
    )

    matched = pd.merge_asof(
        event_subset,
        property_subset,
        on="timestamp",
        direction="backward",
        allow_exact_matches=True
    )

    matched_parts.append(matched)

    if count % 25000 == 0:

        print(
            f"Processed {count:,} / "
            f"{len(common_items):,} items..."
        )

# ============================================================
# 6. COMBINE MATCHED RESULTS
# ============================================================

print("\nCombining matched results...")

matched = pd.concat(
    matched_parts,
    ignore_index=True
)

print(
    f"Matched rows created: "
    f"{len(matched):,}"
)

# ============================================================
# 7. MATCHING RESULTS
# ============================================================

print("\n" + "-" * 70)
print("1. TIME-AWARE MATCH RESULTS")
print("-" * 70)

print(
    f"Original events: "
    f"{len(events):,}"
)

print(
    f"Events with matching product property history: "
    f"{len(matched):,}"
)

# ============================================================
# 8. PROPERTY COVERAGE
# ============================================================

print("\n" + "-" * 70)
print("2. PROPERTY COVERAGE")
print("-" * 70)

category_matches = (
    matched["property"] == "categoryid"
)

availability_matches = (
    matched["property"] == "available"
)

print(
    f"Rows matched to category information: "
    f"{category_matches.sum():,}"
)

print(
    f"Rows matched to availability information: "
    f"{availability_matches.sum():,}"
)

# ============================================================
# 9. EVENT TYPE COVERAGE
# ============================================================

print("\n" + "-" * 70)
print("3. EVENT TYPE COVERAGE")
print("-" * 70)

for event_type in [
    "view",
    "addtocart",
    "transaction"
]:

    subset = matched[
        matched["event"] == event_type
    ]

    if len(subset) == 0:
        continue

    category_count = (
        subset["property"] == "categoryid"
    ).sum()

    availability_count = (
        subset["property"] == "available"
    ).sum()

    print(f"\nEvent: {event_type}")

    print(
        f"Total matched events: "
        f"{len(subset):,}"
    )

    print(
        f"Category information: "
        f"{category_count:,}"
    )

    print(
        f"Availability information: "
        f"{availability_count:,}"
    )

# ============================================================
# 10. AVAILABILITY VALUES
# ============================================================

print("\n" + "-" * 70)
print("4. AVAILABILITY VALUES AT EVENTS")
print("-" * 70)

availability_events = matched[
    matched["property"] == "available"
]

print(
    availability_events["value"]
    .value_counts(dropna=False)
    .to_string()
)

# ============================================================
# 11. SAMPLE MATCHES
# ============================================================

print("\n" + "-" * 70)
print("5. SAMPLE TIME-AWARE MATCHES")
print("-" * 70)

sample = matched[
    matched["property"].isin(
        ["categoryid", "available"]
    )
].head(20)

print(
    sample[
        [
            "timestamp",
            "visitorid",
            "event",
            "itemid_x",
            "property",
            "value"
        ]
    ].to_string(index=False)
)

# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("TIME-AWARE PROPERTY TEST COMPLETE")
print("=" * 70)
