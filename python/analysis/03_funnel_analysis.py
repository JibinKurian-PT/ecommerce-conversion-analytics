import pandas as pd
from pathlib import Path


# ============================================================
# E-COMMERCE CONVERSION ANALYTICS
# FILE: 03_funnel_analysis.py
#
# PURPOSE:
# Calculate the actual visitor-level e-commerce funnel.
#
# Funnel:
# View → Add to Cart → Transaction
#
# IMPORTANT:
# This script does NOT modify the original events.csv.
# ============================================================


# ------------------------------------------------------------
# 1. File location
# ------------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[2]
FILE_PATH = PROJECT_DIR / "data" / "raw" / "events.csv"

print("=" * 70)
print("E-COMMERCE CONVERSION ANALYTICS")
print("VISITOR FUNNEL ANALYSIS")
print("=" * 70)


# ------------------------------------------------------------
# 2. Check file
# ------------------------------------------------------------

if not FILE_PATH.exists():
    raise FileNotFoundError(
        f"Could not find events.csv at:\n{FILE_PATH}"
    )


# ------------------------------------------------------------
# 3. Load only the columns required for funnel analysis
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
# 4. Basic visitor counts
# ------------------------------------------------------------

total_visitors = events["visitorid"].nunique()

view_visitors = events.loc[
    events["event"] == "view",
    "visitorid"
].nunique()

cart_visitors = events.loc[
    events["event"] == "addtocart",
    "visitorid"
].nunique()

purchase_visitors = events.loc[
    events["event"] == "transaction",
    "visitorid"
].nunique()


# ------------------------------------------------------------
# 5. Visitor-level funnel
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("1. VISITOR FUNNEL")
print("-" * 70)

print(
    f"Total unique visitors:       {total_visitors:,}"
)

print(
    f"Visitors who viewed:         {view_visitors:,}"
)

print(
    f"Visitors who added to cart:  {cart_visitors:,}"
)

print(
    f"Visitors who purchased:      {purchase_visitors:,}"
)


# ------------------------------------------------------------
# 6. Basic conversion rates
# ------------------------------------------------------------

view_to_cart = (
    cart_visitors / view_visitors * 100
    if view_visitors > 0
    else 0
)

cart_to_purchase = (
    purchase_visitors / cart_visitors * 100
    if cart_visitors > 0
    else 0
)

view_to_purchase = (
    purchase_visitors / view_visitors * 100
    if view_visitors > 0
    else 0
)


print("\n" + "-" * 70)
print("2. BASIC CONVERSION RATES")
print("-" * 70)

print(
    f"View → Cart:       {view_to_cart:.2f}%"
)

print(
    f"Cart → Purchase:   {cart_to_purchase:.2f}%"
)

print(
    f"View → Purchase:   {view_to_purchase:.2f}%"
)


# ------------------------------------------------------------
# 7. Find the first/earliest timestamp of each event
#    for every visitor
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("3. ANALYZING EVENT SEQUENCE")
print("-" * 70)

print(
    "Finding the earliest view, cart, and transaction "
    "timestamp for each visitor..."
)


first_events = (
    events
    .groupby(
        ["visitorid", "event"]
    )["timestamp"]
    .min()
    .unstack(fill_value=pd.NA)
)


# Make sure all expected event columns exist
for event_name in [
    "view",
    "addtocart",
    "transaction"
]:

    if event_name not in first_events.columns:
        first_events[event_name] = pd.NA


# ------------------------------------------------------------
# 8. Sequential funnel
#
# A visitor is considered to have completed:
#
# View → Cart
#
# if their earliest cart happened after their earliest view.
#
# View → Cart → Transaction
#
# if:
#
# earliest view < earliest cart < earliest transaction
# ------------------------------------------------------------

view_before_cart = (
    first_events["view"].notna()
    &
    first_events["addtocart"].notna()
    &
    (
        first_events["view"]
        <
        first_events["addtocart"]
    )
)


cart_before_purchase = (
    first_events["addtocart"].notna()
    &
    first_events["transaction"].notna()
    &
    (
        first_events["addtocart"]
        <
        first_events["transaction"]
    )
)


complete_funnel = (
    first_events["view"].notna()
    &
    first_events["addtocart"].notna()
    &
    first_events["transaction"].notna()
    &
    (
        first_events["view"]
        <
        first_events["addtocart"]
    )
    &
    (
        first_events["addtocart"]
        <
        first_events["transaction"]
    )
)


# ------------------------------------------------------------
# 9. Sequential funnel counts
# ------------------------------------------------------------

view_cart_visitors = view_before_cart.sum()

cart_purchase_visitors = cart_before_purchase.sum()

complete_funnel_visitors = complete_funnel.sum()


print("\nSequential funnel:")

print(
    f"View → Cart: "
    f"{view_cart_visitors:,} visitors"
)

print(
    f"Cart → Purchase: "
    f"{cart_purchase_visitors:,} visitors"
)

print(
    f"View → Cart → Purchase: "
    f"{complete_funnel_visitors:,} visitors"
)


# ------------------------------------------------------------
# 10. Sequential conversion rates
# ------------------------------------------------------------

sequential_view_to_cart = (
    view_cart_visitors
    / view_visitors
    * 100
    if view_visitors > 0
    else 0
)


sequential_cart_to_purchase = (
    complete_funnel_visitors
    / view_cart_visitors
    * 100
    if view_cart_visitors > 0
    else 0
)


sequential_view_to_purchase = (
    complete_funnel_visitors
    / view_visitors
    * 100
    if view_visitors > 0
    else 0
)


print("\n" + "-" * 70)
print("4. SEQUENTIAL CONVERSION RATES")
print("-" * 70)

print(
    f"View → Cart: "
    f"{sequential_view_to_cart:.2f}%"
)

print(
    f"Cart → Purchase: "
    f"{sequential_cart_to_purchase:.2f}%"
)

print(
    f"View → Cart → Purchase: "
    f"{sequential_view_to_purchase:.2f}%"
)


# ------------------------------------------------------------
# 11. Drop-off analysis
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("5. FUNNEL DROP-OFF")
print("-" * 70)


view_to_cart_dropoff = (
    view_visitors - view_cart_visitors
)


cart_to_purchase_dropoff = (
    view_cart_visitors - complete_funnel_visitors
)


print(
    f"Viewers who did NOT add to cart: "
    f"{view_to_cart_dropoff:,}"
)


print(
    f"Cart users who did NOT complete purchase: "
    f"{cart_to_purchase_dropoff:,}"
)


# ------------------------------------------------------------
# 12. Visitors with unusual event sequences
# ------------------------------------------------------------

print("\n" + "-" * 70)
print("6. UNUSUAL EVENT SEQUENCES")
print("-" * 70)


# Cart exists but no view before cart
cart_without_prior_view = (
    first_events["addtocart"].notna()
    &
    (
        first_events["view"].isna()
        |
        (
            first_events["addtocart"]
            <
            first_events["view"]
        )
    )
)


# Transaction exists but no cart before transaction
purchase_without_prior_cart = (
    first_events["transaction"].notna()
    &
    (
        first_events["addtocart"].isna()
        |
        (
            first_events["transaction"]
            <
            first_events["addtocart"]
        )
    )
)


print(
    f"Cart without prior recorded view: "
    f"{cart_without_prior_view.sum():,}"
)


print(
    f"Purchase without prior recorded cart: "
    f"{purchase_without_prior_cart.sum():,}"
)


# ------------------------------------------------------------
# 13. Visitors who only viewed
# ------------------------------------------------------------

only_view_visitors = (
    first_events["view"].notna()
    &
    first_events["addtocart"].isna()
    &
    first_events["transaction"].isna()
)


print("\n" + "-" * 70)
print("7. VISITORS WHO ONLY VIEWED")
print("-" * 70)

print(
    f"View-only visitors: "
    f"{only_view_visitors.sum():,}"
)


# ------------------------------------------------------------
# 14. Visitors who added to cart but never purchased
# ------------------------------------------------------------

cart_no_purchase = (
    first_events["addtocart"].notna()
    &
    first_events["transaction"].isna()
)


print("\n" + "-" * 70)
print("8. CART ABANDONMENT CANDIDATES")
print("-" * 70)

print(
    f"Visitors who added to cart "
    f"but never recorded a transaction: "
    f"{cart_no_purchase.sum():,}"
)


# ------------------------------------------------------------
# 15. Visitors who purchased
# ------------------------------------------------------------

purchase_visitors_mask = (
    first_events["transaction"].notna()
)


purchase_with_cart = (
    first_events["transaction"].notna()
    &
    first_events["addtocart"].notna()
    &
    (
        first_events["addtocart"]
        <
        first_events["transaction"]
    )
)


print("\n" + "-" * 70)
print("9. PURCHASE BEHAVIOR")
print("-" * 70)

print(
    f"Visitors with a transaction: "
    f"{purchase_visitors_mask.sum():,}"
)

print(
    f"Purchasers with prior cart event: "
    f"{purchase_with_cart.sum():,}"
)


# ------------------------------------------------------------
# 16. Final summary table
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FINAL FUNNEL SUMMARY")
print("=" * 70)


funnel_summary = pd.DataFrame({
    "Stage": [
        "Unique Visitors",
        "Viewed",
        "Added to Cart",
        "Purchased",
        "View → Cart → Purchase"
    ],
    "Visitors": [
        total_visitors,
        view_visitors,
        view_cart_visitors,
        purchase_visitors,
        complete_funnel_visitors
    ]
})


print(
    funnel_summary.to_string(
        index=False
    )
)


print("\n" + "=" * 70)
print("FUNNEL ANALYSIS COMPLETE")
print("=" * 70)


print("""
IMPORTANT:

These results describe OBSERVED behavior in the dataset.

They do not prove that a specific behavior causes conversion.

Also, "no recorded cart event" does not necessarily mean
the customer never added the product to a cart outside the
recorded event sequence.

We will investigate these relationships further.
""")
