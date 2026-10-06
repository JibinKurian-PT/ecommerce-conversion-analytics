import pandas as pd
from pathlib import Path


# ============================================================
# E-COMMERCE CONVERSION ANALYTICS
# FILE: 04_item_funnel_analysis.py
#
# PURPOSE:
# Analyze the funnel at VISITOR + ITEM level.
#
# Funnel:
# View → Add to Cart → Transaction
#
# IMPORTANT:
# The original events.csv is NOT modified.
# ============================================================


# ------------------------------------------------------------
# 1. File location
# ------------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[2]
FILE_PATH = PROJECT_DIR / "data" / "raw" / "events.csv"

print("=" * 70)
print("E-COMMERCE CONVERSION ANALYTICS")
print("VISITOR + ITEM FUNNEL ANALYSIS")
print("=" * 70)


# ------------------------------------------------------------
# 2. Check file
# ------------------------------------------------------------

if not FILE_PATH.exists():
    raise FileNotFoundError(
        f"Could not find events.csv at:\n{FILE_PATH}"
    )


# ------------------------------------------------------------
# 3. Load required columns
# ------------------------------------------------------------

print("\nLoading events.csv...")
print("Please wait...\n")

events = pd.read_csv(
    FILE_PATH,
    usecols=[
        "timestamp",
        "visitorid",
        "event",
        "itemid",
        "transactionid"
    ]
)

print(
    f"Loaded {len(events):,} event records."
)


# ------------------------------------------------------------
# 4. Find first occurrence of each event
#    for each visitor + item combination
# ------------------------------------------------------------

print("\nCreating visitor + item behavioral table...")

grouped = (
    events
    .groupby(
        ["visitorid", "itemid", "event"]
    )["timestamp"]
    .min()
    .unstack()
)


# ------------------------------------------------------------
# 5. Make sure all event columns exist
# ------------------------------------------------------------

for event_name in [
    "view",
    "addtocart",
    "transaction"
]:

    if event_name not in grouped.columns:
        grouped[event_name] = pd.NA


# ------------------------------------------------------------
# 6. Rename columns
# ------------------------------------------------------------

grouped = grouped.rename(
    columns={
        "view": "first_view",
        "addtocart": "first_cart",
        "transaction": "first_transaction"
    }
)


# ------------------------------------------------------------
# 7. Convert index back to columns
#
# IMPORTANT:
# This fixes the error from the previous version.
# ------------------------------------------------------------

grouped = grouped.reset_index()


# ------------------------------------------------------------
# 8. Basic visitor-item counts
# ------------------------------------------------------------

total_pairs = len(grouped)

view_pairs = grouped[
    grouped["first_view"].notna()
]

cart_pairs = grouped[
    grouped["first_cart"].notna()
]

purchase_pairs = grouped[
    grouped["first_transaction"].notna()
]


view_pair_count = len(view_pairs)
cart_pair_count = len(cart_pairs)
purchase_pair_count = len(purchase_pairs)


print("\n" + "-" * 70)
print("1. UNIQUE VISITOR + ITEM INTERACTIONS")
print("-" * 70)

print(
    f"Unique visitor-item combinations: "
    f"{total_pairs:,}"
)

print(
    f"Visitor-item pairs with view: "
    f"{view_pair_count:,}"
)

print(
    f"Visitor-item pairs with add-to-cart: "
    f"{cart_pair_count:,}"
)

print(
    f"Visitor-item pairs with transaction: "
    f"{purchase_pair_count:,}"
)


# ------------------------------------------------------------
# 9. Sequential funnel
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("2. ITEM-LEVEL SEQUENTIAL FUNNEL")
print("-" * 70)


view_before_cart = (
    grouped["first_view"].notna()
    &
    grouped["first_cart"].notna()
    &
    (
        grouped["first_view"]
        <
        grouped["first_cart"]
    )
)


cart_before_purchase = (
    grouped["first_cart"].notna()
    &
    grouped["first_transaction"].notna()
    &
    (
        grouped["first_cart"]
        <
        grouped["first_transaction"]
    )
)


complete_funnel = (
    grouped["first_view"].notna()
    &
    grouped["first_cart"].notna()
    &
    grouped["first_transaction"].notna()
    &
    (
        grouped["first_view"]
        <
        grouped["first_cart"]
    )
    &
    (
        grouped["first_cart"]
        <
        grouped["first_transaction"]
    )
)


view_cart_pairs = view_before_cart.sum()

cart_purchase_pairs = cart_before_purchase.sum()

complete_funnel_pairs = complete_funnel.sum()


print(
    f"View → Cart pairs: "
    f"{view_cart_pairs:,}"
)

print(
    f"Cart → Purchase pairs: "
    f"{cart_purchase_pairs:,}"
)

print(
    f"View → Cart → Purchase pairs: "
    f"{complete_funnel_pairs:,}"
)


# ------------------------------------------------------------
# 10. Conversion rates
# ------------------------------------------------------------

view_to_cart_rate = (
    view_cart_pairs
    / view_pair_count
    * 100
    if view_pair_count > 0
    else 0
)


cart_to_purchase_rate = (
    complete_funnel_pairs
    / view_cart_pairs
    * 100
    if view_cart_pairs > 0
    else 0
)


view_to_purchase_rate = (
    complete_funnel_pairs
    / view_pair_count
    * 100
    if view_pair_count > 0
    else 0
)


print("\n" + "-" * 70)
print("3. ITEM-LEVEL CONVERSION RATES")
print("-" * 70)

print(
    f"View → Cart: "
    f"{view_to_cart_rate:.2f}%"
)

print(
    f"Cart → Purchase: "
    f"{cart_to_purchase_rate:.2f}%"
)

print(
    f"View → Cart → Purchase: "
    f"{view_to_purchase_rate:.2f}%"
)


# ------------------------------------------------------------
# 11. Behavioral flags
# ------------------------------------------------------------

grouped["viewed"] = (
    grouped["first_view"].notna()
)

grouped["added_to_cart"] = (
    grouped["first_cart"].notna()
)

grouped["purchased"] = (
    grouped["first_transaction"].notna()
)

grouped["view_then_cart"] = (
    view_before_cart
)

grouped["cart_then_purchase"] = (
    cart_before_purchase
)

grouped["complete_funnel"] = (
    complete_funnel
)


# ------------------------------------------------------------
# 12. PRODUCT PERFORMANCE
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("4. PRODUCT PERFORMANCE")
print("-" * 70)


product_summary = (
    grouped
    .groupby("itemid")
    .agg(
        unique_visitors=(
            "visitorid",
            "nunique"
        ),

        views=(
            "viewed",
            "sum"
        ),

        cart_adds=(
            "added_to_cart",
            "sum"
        ),

        purchases=(
            "purchased",
            "sum"
        ),

        view_to_cart_pairs=(
            "view_then_cart",
            "sum"
        ),

        cart_to_purchase_pairs=(
            "cart_then_purchase",
            "sum"
        ),

        complete_funnel_pairs=(
            "complete_funnel",
            "sum"
        )
    )
)


# ------------------------------------------------------------
# 13. Product conversion rates
# ------------------------------------------------------------

product_summary["view_to_cart_rate"] = (
    product_summary["view_to_cart_pairs"]
    /
    product_summary["views"]
    * 100
)


product_summary["cart_to_purchase_rate"] = (
    product_summary["cart_to_purchase_pairs"]
    /
    product_summary["view_to_cart_pairs"]
    * 100
)


product_summary["view_to_purchase_rate"] = (
    product_summary["complete_funnel_pairs"]
    /
    product_summary["views"]
    * 100
)


# ------------------------------------------------------------
# 14. Remove invalid infinite values
# ------------------------------------------------------------

product_summary = (
    product_summary
    .replace(
        [float("inf"), -float("inf")],
        pd.NA
    )
)


# ------------------------------------------------------------
# 15. TOP VIEWED PRODUCTS
# ------------------------------------------------------------

print("\nTOP 20 MOST VIEWED PRODUCTS")
print("-" * 70)

top_viewed = (
    product_summary
    .sort_values(
        "views",
        ascending=False
    )
    .head(20)
)


print(
    top_viewed[
        [
            "unique_visitors",
            "views",
            "cart_adds",
            "purchases",
            "view_to_cart_rate",
            "view_to_purchase_rate"
        ]
    ].to_string()
)


# ------------------------------------------------------------
# 16. HIGH-VIEW / LOW-CONVERSION PRODUCTS
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("5. HIGH-VIEW / LOW-CONVERSION PRODUCTS")
print("-" * 70)


high_traffic_products = product_summary[
    product_summary["views"] >= 100
].copy()


low_conversion_products = (
    high_traffic_products
    .sort_values(
        [
            "view_to_purchase_rate",
            "views"
        ],
        ascending=[
            True,
            False
        ]
    )
    .head(20)
)


print(
    low_conversion_products[
        [
            "unique_visitors",
            "views",
            "cart_adds",
            "purchases",
            "view_to_cart_rate",
            "view_to_purchase_rate"
        ]
    ].to_string()
)


# ------------------------------------------------------------
# 17. STRONG OBSERVED CONVERSION
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("6. PRODUCTS WITH STRONG OBSERVED CONVERSION")
print("-" * 70)


strong_products = (
    high_traffic_products
    .sort_values(
        [
            "view_to_purchase_rate",
            "views"
        ],
        ascending=[
            False,
            False
        ]
    )
    .head(20)
)


print(
    strong_products[
        [
            "unique_visitors",
            "views",
            "cart_adds",
            "purchases",
            "view_to_cart_rate",
            "view_to_purchase_rate"
        ]
    ].to_string()
)


# ------------------------------------------------------------
# 18. Unusual sequences
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("7. UNUSUAL ITEM-LEVEL SEQUENCES")
print("-" * 70)


cart_without_view = (
    grouped["first_cart"].notna()
    &
    (
        grouped["first_view"].isna()
        |
        (
            grouped["first_cart"]
            <
            grouped["first_view"]
        )
    )
)


purchase_without_cart = (
    grouped["first_transaction"].notna()
    &
    (
        grouped["first_cart"].isna()
        |
        (
            grouped["first_transaction"]
            <
            grouped["first_cart"]
        )
    )
)


print(
    f"Cart without prior item view: "
    f"{cart_without_view.sum():,}"
)


print(
    f"Purchase without prior item cart: "
    f"{purchase_without_cart.sum():,}"
)


# ------------------------------------------------------------
# 19. Save product-level analysis
# ------------------------------------------------------------

OUTPUT_FILE = (
    PROJECT_DIR
    / "product_funnel_summary.csv"
)


product_summary.reset_index().to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n" + "-" * 70)
print("8. OUTPUT FILE")
print("-" * 70)

print(
    f"Product funnel summary saved to:\n"
    f"{OUTPUT_FILE}"
)


# ------------------------------------------------------------
# 20. Final
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("ITEM-LEVEL FUNNEL ANALYSIS COMPLETE")
print("=" * 70)

print("""
IMPORTANT:

These conversion rates describe OBSERVED event behavior.

They do not establish causation.

A product with a high observed conversion rate is not
automatically a "better" product. We will consider
sample size and other product characteristics later.
""")
