import pandas as pd
from pathlib import Path

# ============================================================
# E-COMMERCE CONVERSION ANALYTICS
# PART 1 vs PART 2 OVERLAP CHECK
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

PART1 = BASE_DIR / "data" / "raw" / "item_properties_part1.csv"
PART2 = BASE_DIR / "data" / "raw" / "item_properties_part2.csv"

print("=" * 70)
print("E-COMMERCE CONVERSION ANALYTICS")
print("ITEM PROPERTIES PART 1 vs PART 2")
print("OVERLAP CHECK")
print("=" * 70)

# ------------------------------------------------------------
# 1. LOAD ONLY REQUIRED COLUMNS
# ------------------------------------------------------------

print("\nLoading Part 1...")
p1 = pd.read_csv(
    PART1,
    usecols=["timestamp", "itemid", "property", "value"]
)

print(f"Part 1 rows: {len(p1):,}")

print("\nLoading Part 2...")
p2 = pd.read_csv(
    PART2,
    usecols=["timestamp", "itemid", "property", "value"]
)

print(f"Part 2 rows: {len(p2):,}")

# ------------------------------------------------------------
# 2. TIMESTAMP OVERLAP
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("1. TIMESTAMP OVERLAP")
print("-" * 70)

timestamps_1 = set(p1["timestamp"].unique())
timestamps_2 = set(p2["timestamp"].unique())

common_timestamps = timestamps_1 & timestamps_2

print(f"Part 1 unique timestamps: {len(timestamps_1)}")
print(f"Part 2 unique timestamps: {len(timestamps_2)}")
print(f"Common timestamps: {len(common_timestamps)}")

# ------------------------------------------------------------
# 3. EXACT DUPLICATE RECORDS BETWEEN FILES
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("2. EXACT RECORD OVERLAP")
print("-" * 70)

print("Checking whether identical records exist in both files...")

common_records = p1.merge(
    p2,
    on=["timestamp", "itemid", "property", "value"],
    how="inner"
)

print(
    f"Identical records appearing in BOTH files: "
    f"{len(common_records):,}"
)

# ------------------------------------------------------------
# 4. ITEM + PROPERTY + TIMESTAMP OVERLAP
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("3. ITEM + PROPERTY + TIMESTAMP OVERLAP")
print("-" * 70)

key_columns = ["timestamp", "itemid", "property"]

keys_1 = p1[key_columns].drop_duplicates()
keys_2 = p2[key_columns].drop_duplicates()

common_keys = keys_1.merge(
    keys_2,
    on=key_columns,
    how="inner"
)

print(
    f"Unique Part 1 item-property-timestamp combinations: "
    f"{len(keys_1):,}"
)

print(
    f"Unique Part 2 item-property-timestamp combinations: "
    f"{len(keys_2):,}"
)

print(
    f"Combinations appearing in BOTH files: "
    f"{len(common_keys):,}"
)

# ------------------------------------------------------------
# 5. ITEM OVERLAP
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("4. ITEM OVERLAP")
print("-" * 70)

items_1 = set(p1["itemid"].unique())
items_2 = set(p2["itemid"].unique())

common_items = items_1 & items_2

print(f"Unique items in Part 1: {len(items_1):,}")
print(f"Unique items in Part 2: {len(items_2):,}")
print(f"Items appearing in BOTH files: {len(common_items):,}")

# ------------------------------------------------------------
# 6. PROPERTY OVERLAP
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("5. PROPERTY OVERLAP")
print("-" * 70)

properties_1 = set(p1["property"].unique())
properties_2 = set(p2["property"].unique())

common_properties = properties_1 & properties_2

print(f"Unique properties in Part 1: {len(properties_1):,}")
print(f"Unique properties in Part 2: {len(properties_2):,}")
print(f"Properties appearing in BOTH files: {len(common_properties):,}")

only_part1 = properties_1 - properties_2
only_part2 = properties_2 - properties_1

print(f"Properties only in Part 1: {len(only_part1):,}")
print(f"Properties only in Part 2: {len(only_part2):,}")

if only_part1:
    print("\nProperties only in Part 1:")
    print(sorted(only_part1))

if only_part2:
    print("\nProperties only in Part 2:")
    print(sorted(only_part2))

# ------------------------------------------------------------
# 7. IMPORTANT PROPERTY OVERLAP
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("6. IMPORTANT PROPERTY RECORDS")
print("-" * 70)

for prop in ["categoryid", "available"]:

    p1_prop = p1[p1["property"] == prop]
    p2_prop = p2[p2["property"] == prop]

    print(f"\nProperty: {prop}")

    print(
        f"Part 1 records: {len(p1_prop):,}"
    )

    print(
        f"Part 2 records: {len(p2_prop):,}"
    )

    print(
        f"Part 1 unique items: "
        f"{p1_prop['itemid'].nunique():,}"
    )

    print(
        f"Part 2 unique items: "
        f"{p2_prop['itemid'].nunique():,}"
    )

# ------------------------------------------------------------
# 8. FINAL SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("OVERLAP CHECK COMPLETE")
print("=" * 70)

if len(common_records) == 0:

    print("\nRESULT:")
    print("No exact duplicate records were found between Part 1 and Part 2.")

else:

    print("\nRESULT:")
    print(
        "Exact duplicate records DO exist between Part 1 and Part 2."
    )

print("\nImportant:")
print(
    "Shared timestamps and shared items are NOT automatically a problem."
)
print(
    "We mainly care whether the SAME record exists in both files."
)

print("=" * 70)
