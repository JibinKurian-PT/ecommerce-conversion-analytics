import pandas as pd
from pathlib import Path
import os

# ============================================================
# E-COMMERCE CONVERSION ANALYTICS
# ITEM PROPERTIES PROFILING
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
FILE = BASE_DIR / "data" / "raw" / "item_properties_part1.csv"

print("=" * 70)
print("E-COMMERCE CONVERSION ANALYTICS")
print("ITEM PROPERTIES PART 1 - DATA PROFILING")
print("=" * 70)

print("\nLoading item_properties_part1.csv...")
print("This may take some time because the file is large.")

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

exact_duplicates = df.duplicated().sum()

print(f"Exact duplicate rows: {exact_duplicates:,}")

# ------------------------------------------------------------
# 7. PROPERTY INFORMATION
# ------------------------------------------------------------

if "property" in df.columns:

    print("\n" + "-" * 70)
    print("6. PROPERTY ANALYSIS")
    print("-" * 70)

    print(
        f"Total unique properties: "
        f"{df['property'].nunique():,}"
    )

    print("\nMost common properties:")

    print(
        df["property"]
        .value_counts()
        .head(20)
        .to_string()
    )

# ------------------------------------------------------------
# 8. ITEM INFORMATION
# ------------------------------------------------------------

if "itemid" in df.columns:

    print("\n" + "-" * 70)
    print("7. ITEM ANALYSIS")
    print("-" * 70)

    unique_items = df["itemid"].nunique()

    print(f"Unique items: {unique_items:,}")

    properties_per_item = (
        df.groupby("itemid")
        .size()
    )

    print(
        f"\nAverage property records per item: "
        f"{properties_per_item.mean():.2f}"
    )

    print(
        f"Median property records per item: "
        f"{properties_per_item.median():.0f}"
    )

    print(
        f"Maximum property records for one item: "
        f"{properties_per_item.max():,}"
    )

# ------------------------------------------------------------
# 9. TIMESTAMP
# ------------------------------------------------------------

if "timestamp" in df.columns:

    print("\n" + "-" * 70)
    print("8. TIMESTAMP ANALYSIS")
    print("-" * 70)

    print(
        f"Minimum timestamp: "
        f"{df['timestamp'].min()}"
    )

    print(
        f"Maximum timestamp: "
        f"{df['timestamp'].max()}"
    )

# ------------------------------------------------------------
# 10. MEMORY USAGE
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("9. MEMORY USAGE")
print("-" * 70)

memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)

print(f"DataFrame memory usage: {memory_mb:,.2f} MB")

print("\n" + "=" * 70)
print("ITEM PROPERTIES PART 1 PROFILING COMPLETE")
print("=" * 70)
