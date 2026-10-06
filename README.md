# E-Commerce Conversion Analytics

A complete end-to-end data analytics project that analyzes how effectively an e-commerce platform converts customer browsing activity into purchases.

The project combines **Python, SQL, MySQL, data cleaning, time-aware data enrichment, statistical analysis, and an interactive dashboard** to identify conversion bottlenecks and opportunities for improvement.

---

## 📌 Business Problem

E-commerce platforms generate large volumes of customer interaction data, but raw event data alone does not explain where customers are being lost.

This project answers:

> **How effectively does the e-commerce platform turn customer browsing activity into purchases, and what factors are associated with conversion?**

The analysis focuses on:

- Customer funnel performance
- View → Cart → Purchase behavior
- Customer engagement
- Product performance
- Category performance
- Product availability
- Conversion drop-offs
- Data quality and tracking limitations

---

## 🎯 Key Questions

The analysis investigates:

1. How many users view products, add products to cart, and complete purchases?
2. Where is the largest conversion drop-off?
3. How many users complete the full View → Cart → Purchase journey?
4. How many users add products to cart without a recorded purchase?
5. How many purchases occur without a preceding recorded cart event?
6. How does customer engagement vary across visitors?
7. Which categories and products perform best?
8. Which products receive high traffic but have relatively low conversion?
9. Is product availability associated with conversion?
10. What data-quality and tracking limitations exist in the dataset?

---

# 📊 Key Results

### Overall Funnel

| Metric | Result |
|---|---:|
| Total events | 2,756,101 |
| Unique visitors | 1,407,580 |
| Unique products | 235,061 |
| Viewers | 1,404,179 |
| Cart users | 37,722 |
| Purchasers | 11,719 |
| View → Cart | 2.69% |
| Cart → Purchase | 31.07% |
| View → Purchase | 0.83% |

### Sequential Funnel

When the stages are required to occur in chronological order:

| Stage | Users |
|---|---:|
| View → Cart | 32,272 |
| Cart → Purchase | 10,447 |
| View → Cart → Purchase | 9,682 |

The complete sequential funnel represents approximately **0.69% of all unique visitors**.

### Customer Engagement

- Average events per visitor: **1.96**
- One-event visitors: **1,001,560**
- Multiple-event visitors: **406,020**
- Approximately **71% of visitors generated only one recorded event**

This indicates that a large proportion of visitors had very limited recorded interaction with the platform.

---

# 🔎 Important Findings

### 1. The largest funnel problem is View → Cart

Only **2.69% of viewers added a product to their cart**.

This suggests that the largest observable drop-off occurs before cart creation.

Potential business areas to investigate include:

- Product relevance
- Product presentation
- Pricing
- Availability
- User intent
- Recommendation quality
- Product detail page experience

These are hypotheses rather than causal conclusions from this dataset.

---

### 2. Cart users convert relatively strongly

Among users who added a product to cart, the observed Cart → Purchase conversion rate was **31.07%**.

This suggests that once users reach the cart stage, the platform is substantially more successful at moving them toward purchase than it is at moving viewers into carts.

---

### 3. The complete sequential funnel is small

Only **9,682 visitors** completed the recorded:

> View → Cart → Purchase

sequence.

That represents approximately **0.69% of all unique visitors**.

This highlights the importance of understanding the large drop between product discovery and cart creation.

---

### 4. Tracking does not perfectly represent customer journeys

The dataset contains:

- **27,275 cart users without a recorded purchase** under the SQL analysis logic.
- **1,272 purchases without a preceding recorded cart event**.

These patterns may represent genuine behavior, missing tracking events, or limitations in how the source data was captured.

Therefore, the analysis does not assume that every missing event represents actual customer behavior.

---

# 🧹 Data Preparation

The raw dataset contains customer interaction events together with separate product-property history files.

The project therefore uses a multi-stage data preparation pipeline.

### Main data preparation steps

1. Profile raw event data
2. Investigate event quality
3. Profile category hierarchy
4. Profile item-property datasets
5. Investigate property overlap
6. Match product properties to events using event time
7. Validate the time-aware enrichment
8. Build the final enriched event dataset
9. Load the analytical data into MySQL
10. Perform SQL analysis
11. Build the dashboard

---

# ⏱️ Time-Aware Product Enrichment

One important challenge in this dataset is that product properties such as:

- `categoryid`
- `available`

change over time.

Therefore, simply joining events to the latest product property would potentially introduce incorrect historical information.

The project uses **time-aware matching** so that an event is matched to the relevant historical product-property record available at that point in time.

The validation produced:

- Original events: **2,756,101**
- Events with matching product-property history: **2,500,516**
- Category matches: **717,018**
- Availability matches: **1,598,062**

This preserves the historical context of the event rather than blindly assigning the latest known product state.

---

# 🗄️ MySQL Data Model

The analytical database uses a simple relational model:

```text
dim_category
     │
     │ categoryid
     ▼
fact_events
