"""
End-to-end cleaning + exploratory analysis of raw e-commerce sales data.

Run:
    python3 clean_and_analyze.py

Outputs:
    data/cleaned_sales_data.csv
    images/*.png  (charts referenced in README.md)
    Console summary of data quality issues found and fixed
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

pd.set_option("display.width", 120)

RAW_PATH = "data/raw_sales_data.csv"
CLEAN_PATH = "data/cleaned_sales_data.csv"

def log(title):
    print(f"\n{'='*70}\n{title}\n{'='*70}")

# ---------------------------------------------------------------
# 1. LOAD
# ---------------------------------------------------------------
log("1. LOADING RAW DATA")
df = pd.read_csv(RAW_PATH)
print(f"Raw shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# ---------------------------------------------------------------
# 2. DATA QUALITY AUDIT (before cleaning)
# ---------------------------------------------------------------
log("2. DATA QUALITY AUDIT")
n_dupes = df.duplicated().sum()
n_missing_revenue = df["revenue"].isna().sum()
n_missing_region = df["region"].isna().sum()
n_negative_qty = (df["quantity"] < 0).sum()
print(f"Exact duplicate rows:      {n_dupes}")
print(f"Missing revenue values:    {n_missing_revenue}")
print(f"Missing region values:     {n_missing_region}")
print(f"Negative quantity entries: {n_negative_qty}")
print(f"Distinct category spellings before cleaning: {df['category'].nunique()} -> {sorted(df['category'].unique())}")

# ---------------------------------------------------------------
# 3. CLEANING
# ---------------------------------------------------------------
log("3. CLEANING")

# 3a. Drop exact duplicates
before = len(df)
df = df.drop_duplicates()
print(f"Dropped {before - len(df)} duplicate rows")

# 3b. Standardize category casing
df["category"] = df["category"].str.strip().str.title()

# 3c. Fix negative quantities (data-entry sign errors) -> take absolute value
df["quantity"] = df["quantity"].abs()

# 3d. Recompute revenue where missing (unit_price * quantity), instead of dropping rows
missing_mask = df["revenue"].isna()
df.loc[missing_mask, "revenue"] = df.loc[missing_mask, "unit_price"] * df.loc[missing_mask, "quantity"]
print(f"Recomputed {missing_mask.sum()} missing revenue values from unit_price * quantity")

# 3e. Fill missing region with 'Unknown' rather than dropping (preserves revenue in aggregates)
n_region_filled = df["region"].isna().sum()
df["region"] = df["region"].fillna("Unknown")
print(f"Filled {n_region_filled} missing region values with 'Unknown'")

# 3f. Normalize mixed date formats (YYYY-MM-DD and DD/MM/YYYY) into a single datetime column
def parse_mixed_date(x):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return pd.to_datetime(x, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT

df["order_date"] = df["order_date"].apply(parse_mixed_date)
n_unparsed = df["order_date"].isna().sum()
print(f"Unparseable dates after normalization: {n_unparsed}")

# 3g. Round money fields
df["unit_price"] = df["unit_price"].round(2)
df["revenue"] = df["revenue"].round(2)

df = df.sort_values("order_date").reset_index(drop=True)
df.to_csv(CLEAN_PATH, index=False)
print(f"\nCleaned data written to {CLEAN_PATH} -> final shape {df.shape}")

# ---------------------------------------------------------------
# 4. EXPLORATORY ANALYSIS + CHARTS
# ---------------------------------------------------------------
log("4. EXPLORATORY ANALYSIS")

df["month"] = df["order_date"].dt.to_period("M").astype(str)
monthly_rev = df.groupby("month")["revenue"].sum().sort_index()

plt.figure(figsize=(10, 5))
monthly_rev.plot(kind="line", marker="o", color="#2E86AB")
plt.title("Monthly Revenue Trend")
plt.ylabel("Revenue (R)")
plt.xlabel("Month")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("images/monthly_revenue_trend.png", dpi=120)
plt.close()

cat_rev = df.groupby("category")["revenue"].sum().sort_values(ascending=False)
plt.figure(figsize=(8, 5))
cat_rev.plot(kind="bar", color="#F26419")
plt.title("Revenue by Category")
plt.ylabel("Revenue (R)")
plt.xlabel("")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("images/revenue_by_category.png", dpi=120)
plt.close()

region_rev = df.groupby("region")["revenue"].sum().sort_values(ascending=False)
plt.figure(figsize=(7, 5))
region_rev.plot(kind="bar", color="#33658A")
plt.title("Revenue by Region")
plt.ylabel("Revenue (R)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("images/revenue_by_region.png", dpi=120)
plt.close()

channel_share = df.groupby("channel")["revenue"].sum()
plt.figure(figsize=(6, 6))
plt.pie(channel_share, labels=channel_share.index, autopct="%1.1f%%",
        colors=["#2E86AB", "#F26419", "#33658A", "#F6AE2D"])
plt.title("Revenue Share by Sales Channel")
plt.tight_layout()
plt.savefig("images/revenue_by_channel.png", dpi=120)
plt.close()

print("Saved 4 charts to images/")

# ---------------------------------------------------------------
# 5. KEY INSIGHTS (printed, also copy into README results section)
# ---------------------------------------------------------------
log("5. KEY INSIGHTS")
top_cat = cat_rev.idxmax()
top_region = region_rev.idxmax()
best_month = monthly_rev.idxmax()
total_rev = df["revenue"].sum()

print(f"Total revenue analyzed:      R{total_rev:,.2f}")
print(f"Top-performing category:     {top_cat} (R{cat_rev.max():,.2f})")
print(f"Top-performing region:       {top_region} (R{region_rev.max():,.2f})")
print(f"Best month:                  {best_month} (R{monthly_rev.max():,.2f})")
print(f"Unknown-region revenue share: {region_rev.get('Unknown', 0) / total_rev * 100:.2f}%  <- data quality issue at source system to flag to stakeholders")
