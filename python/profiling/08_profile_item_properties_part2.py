import pandas as pd
from pathlib import Path
import os

# ============================================================
# E-COMMERCE CONVERSION ANALYTICS
# ITEM PROPERTIES PART 2 - PROFILING
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
FILE = BASE_DIR / "data" / "raw" / "item_properties_part2.csv"

print("=" * 70)
print("E-COMMERCE CONVERSION ANALYTICS")
print("ITEM PROPERTIES PART 2 - DATA PROFILING")
print("=" * 70)

print("\nLoading item_properties_part2.csv...")
print("Please wait...")

# ------------------------------------------------------------
# 1. FILE INFORMATION
# ------------------------------------------------------------

file_size_mb = os.path.getsize(FILE) / (1024 * 1024)

print("\n" + "-" * 70)
print("1. FILE INFORMATION")
print("-" * 70)

print(f"File size: {file_size_mb:,.2f} MB")

# ------------------------------------------------------------
# 2. LOAD DATA
# ------------------------------------------------------------

df = pd.read_csv(FILE)

print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")

# ------------------------------------------------------------
# 3. STRUCTURE
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("2. DATASET STRUCTURE")
print("-" * 70)

print(f"Columns: {list(df.columns)}")

print("\nData types:")
print(df.dtypes)

print("\nFirst 10 rows:")
print(df.head(10).to_string(index=False))

# ------------------------------------------------------------
# 4. UNIQUE VALUES
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("3. UNIQUE VALUES")
print("-" * 70)

for column in df.columns:
    print(
        f"{column}: "
        f"{df[column].nunique(dropna=True):,} unique values"
    )

# ------------------------------------------------------------
# 5. MISSING VALUES
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("4. MISSING VALUES")
print("-" * 70)

for column in df.columns:

    missing = df[column].isna().sum()
    percentage = (missing / len(df)) * 100

    print(
        f"{column}: "
        f"{missing:,} missing "
        f"({percentage:.2f}%)"
    )

# ------------------------------------------------------------
# 6. DUPLICATES
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("5. DUPLICATES")
print("-" * 70)

print(
    f"Exact duplicate rows: "
    f"{df.duplicated().sum():,}"
)

# ------------------------------------------------------------
# 7. PROPERTY INFORMATION
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("6. PROPERTY INFORMATION")
print("-" * 70)

print(
    f"Unique properties: "
    f"{df['property'].nunique():,}"
)

print("\nTop 20 properties:")

print(
    df["property"]
    .value_counts()
    .head(20)
    .to_string()
)

# ------------------------------------------------------------
# 8. IMPORTANT PROPERTIES
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("7. IMPORTANT PROPERTY CHECK")
print("-" * 70)

for prop in ["categoryid", "available", "888", "790", "6"]:

    subset = df[df["property"] == prop]

    print(f"\nProperty: {prop}")
    print(f"Rows: {len(subset):,}")
    print(f"Unique items: {subset['itemid'].nunique():,}")
    print(f"Unique values: {subset['value'].nunique():,}")

# ------------------------------------------------------------
# 9. TIMESTAMP
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("8. TIMESTAMP ANALYSIS")
print("-" * 70)

print(
    f"Unique timestamps: "
    f"{df['timestamp'].nunique():,}"
)

print(
    f"Minimum timestamp: "
    f"{df['timestamp'].min()}"
)

print(
    f"Maximum timestamp: "
    f"{df['timestamp'].max()}"
)

print("\nTimestamp distribution:")

print(
    df["timestamp"]
    .value_counts()
    .sort_index()
    .to_string()
)

# ------------------------------------------------------------
# 10. MEMORY
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("9. MEMORY USAGE")
print("-" * 70)

memory_mb = (
    df.memory_usage(deep=True).sum()
    / (1024 * 1024)
)

print(f"DataFrame memory usage: {memory_mb:,.2f} MB")

# ------------------------------------------------------------
# COMPLETE
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("PART 2 PROFILING COMPLETE")
print("=" * 70)
