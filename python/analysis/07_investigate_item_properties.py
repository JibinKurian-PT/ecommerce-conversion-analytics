import pandas as pd
from pathlib import Path

# ============================================================
# E-COMMERCE CONVERSION ANALYTICS
# ITEM PROPERTIES INVESTIGATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
FILE = BASE_DIR / "data" / "raw" / "item_properties_part1.csv"

print("=" * 70)
print("E-COMMERCE CONVERSION ANALYTICS")
print("ITEM PROPERTIES - DEEP INVESTIGATION")
print("=" * 70)

# ============================================================
# LOAD
# ============================================================

print("\nLoading item_properties_part1.csv...")
print("Please wait...")

df = pd.read_csv(FILE)

print(f"Loaded {len(df):,} rows.")

# ============================================================
# 1. CATEGORYID
# ============================================================

print("\n" + "-" * 70)
print("1. CATEGORYID INVESTIGATION")
print("-" * 70)

category = df[df["property"] == "categoryid"].copy()

print(f"Rows containing categoryid: {len(category):,}")
print(f"Unique items with categoryid: {category['itemid'].nunique():,}")
print(f"Unique category values: {category['value'].nunique():,}")

print("\nMost common category IDs:")

print(
    category["value"]
    .value_counts()
    .head(20)
    .to_string()
)

# ============================================================
# 2. AVAILABLE
# ============================================================

print("\n" + "-" * 70)
print("2. AVAILABILITY INVESTIGATION")
print("-" * 70)

available = df[df["property"] == "available"].copy()

print(f"Rows containing available: {len(available):,}")
print(f"Unique items with availability: {available['itemid'].nunique():,}")
print(f"Unique availability values: {available['value'].nunique():,}")

print("\nAvailability values:")

print(
    available["value"]
    .value_counts(dropna=False)
    .to_string()
)

# ============================================================
# 3. PROPERTY TYPES
# ============================================================

print("\n" + "-" * 70)
print("3. PROPERTY FREQUENCY")
print("-" * 70)

property_counts = (
    df["property"]
    .value_counts()
)

print(f"Total unique properties: {len(property_counts):,}")

print("\nTop 30 properties:")

print(
    property_counts
    .head(30)
    .to_string()
)

print("\nProperties appearing only once:")

print(
    (property_counts == 1).sum()
)

# ============================================================
# 4. HOW MANY ITEMS HAVE EACH PROPERTY?
# ============================================================

print("\n" + "-" * 70)
print("4. PROPERTY COVERAGE")
print("-" * 70)

property_item_counts = (
    df.groupby("property")["itemid"]
    .nunique()
    .sort_values(ascending=False)
)

print("\nTop 30 properties by number of unique items:")

print(
    property_item_counts
    .head(30)
    .to_string()
)

# ============================================================
# 5. PROPERTY VALUE EXAMPLES
# ============================================================

print("\n" + "-" * 70)
print("5. PROPERTY VALUE EXAMPLES")
print("-" * 70)

important_properties = [
    "categoryid",
    "available",
    "888",
    "790",
    "6",
    "283",
    "776",
    "678",
    "364",
    "202"
]

for prop in important_properties:

    subset = df[df["property"] == prop]

    if len(subset) == 0:
        continue

    print(f"\nProperty: {prop}")
    print(f"Rows: {len(subset):,}")
    print(f"Unique values: {subset['value'].nunique():,}")

    print("Example values:")

    print(
        subset["value"]
        .drop_duplicates()
        .head(10)
        .tolist()
    )

# ============================================================
# 6. PROPERTY CHANGES OVER TIME
# ============================================================

print("\n" + "-" * 70)
print("6. PROPERTY CHANGE INVESTIGATION")
print("-" * 70)

# For each item + property, count how many different values exist

changes = (
    df.groupby(["itemid", "property"])["value"]
    .nunique()
)

print(
    f"Unique item-property combinations: "
    f"{len(changes):,}"
)

changed = (changes > 1).sum()

print(
    f"Item-property combinations with multiple values: "
    f"{changed:,}"
)

print(
    f"Percentage with multiple values: "
    f"{(changed / len(changes) * 100):.2f}%"
)

# ============================================================
# 7. CATEGORY CHANGES
# ============================================================

print("\n" + "-" * 70)
print("7. CATEGORY CHANGE INVESTIGATION")
print("-" * 70)

category_changes = (
    category.groupby("itemid")["value"]
    .nunique()
)

items_with_category_change = (
    (category_changes > 1).sum()
)

print(
    f"Items with category information: "
    f"{len(category_changes):,}"
)

print(
    f"Items with more than one category value: "
    f"{items_with_category_change:,}"
)

# ============================================================
# 8. AVAILABILITY CHANGES
# ============================================================

print("\n" + "-" * 70)
print("8. AVAILABILITY CHANGE INVESTIGATION")
print("-" * 70)

available_changes = (
    available.groupby("itemid")["value"]
    .nunique()
)

items_with_availability_change = (
    (available_changes > 1).sum()
)

print(
    f"Items with availability information: "
    f"{len(available_changes):,}"
)

print(
    f"Items with more than one availability value: "
    f"{items_with_availability_change:,}"
)

# ============================================================
# 9. TIMESTAMP DISTRIBUTION
# ============================================================

print("\n" + "-" * 70)
print("9. TIMESTAMP INVESTIGATION")
print("-" * 70)

timestamp_counts = (
    df["timestamp"]
    .value_counts()
    .sort_index()
)

print(f"Unique timestamps: {len(timestamp_counts):,}")

print("\nTimestamp records:")

print(timestamp_counts.to_string())

# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("ITEM PROPERTIES INVESTIGATION COMPLETE")
print("=" * 70)
