import pandas as pd
from pathlib import Path

# ============================================================
# E-COMMERCE CONVERSION ANALYTICS
# CATEGORY TREE PROFILING
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
FILE = BASE_DIR / "data" / "raw" / "category_tree.csv"

print("=" * 70)
print("E-COMMERCE CONVERSION ANALYTICS")
print("CATEGORY TREE DATA PROFILING")
print("=" * 70)

print("\nLoading category_tree.csv...")
df = pd.read_csv(FILE)

print("\n" + "-" * 70)
print("1. DATASET STRUCTURE")
print("-" * 70)

print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")
print(f"Columns: {list(df.columns)}")

print("\nData types:")
print(df.dtypes)

print("\nFirst 10 rows:")
print(df.head(10).to_string(index=False))

print("\n" + "-" * 70)
print("2. UNIQUE VALUES")
print("-" * 70)

for column in df.columns:
    print(f"{column}: {df[column].nunique(dropna=True):,} unique values")

print("\n" + "-" * 70)
print("3. MISSING VALUES")
print("-" * 70)

missing = df.isnull().sum()

for column in df.columns:
    count = missing[column]
    percentage = (count / len(df)) * 100
    print(f"{column}: {count:,} missing ({percentage:.2f}%)")

print("\n" + "-" * 70)
print("4. DUPLICATES")
print("-" * 70)

duplicate_rows = df.duplicated().sum()

print(f"Exact duplicate rows: {duplicate_rows:,}")

print("\n" + "-" * 70)
print("5. CATEGORY HIERARCHY")
print("-" * 70)

if "parentid" in df.columns:

    root_categories = df["parentid"].isna().sum()

    print(f"Root categories: {root_categories:,}")

    print("\nParent category frequency:")
    print(
        df["parentid"]
        .value_counts(dropna=False)
        .head(20)
        .to_string()
    )

    print("\nCategories with most children:")

    child_counts = (
        df[df["parentid"].notna()]
        .groupby("parentid")
        .size()
        .sort_values(ascending=False)
        .head(20)
    )

    print(child_counts.to_string())

print("\n" + "-" * 70)
print("6. CATEGORY ID VALIDATION")
print("-" * 70)

if "categoryid" in df.columns and "parentid" in df.columns:

    category_ids = set(df["categoryid"].dropna())

    parent_ids = set(df["parentid"].dropna())

    orphan_parents = parent_ids - category_ids

    print(f"Unique category IDs: {len(category_ids):,}")
    print(f"Unique parent IDs: {len(parent_ids):,}")
    print(f"Parent IDs not present as category IDs: {len(orphan_parents):,}")

    if orphan_parents:
        print("\nExample orphan parent IDs:")
        print(list(orphan_parents)[:20])

print("\n" + "-" * 70)
print("7. CATEGORY DEPTH")
print("-" * 70)

# Build parent lookup
if "categoryid" in df.columns and "parentid" in df.columns:

    parent_lookup = dict(
        zip(
            df["categoryid"],
            df["parentid"]
        )
    )

    def get_depth(category_id):
        depth = 0
        current = category_id
        visited = set()

        while pd.notna(current) and current in parent_lookup:

            if current in visited:
                return None

            visited.add(current)

            current = parent_lookup[current]
            depth += 1

        return depth

    df["depth"] = df["categoryid"].apply(get_depth)

    print("Category depth distribution:")
    print(df["depth"].value_counts().sort_index().to_string())

    print(f"\nMaximum category depth: {df['depth'].max()}")

print("\n" + "=" * 70)
print("CATEGORY TREE PROFILING COMPLETE")
print("=" * 70)
