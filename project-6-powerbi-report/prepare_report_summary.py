"""
Aggregates fact_sales.csv (joined with the dimension tables) into the
same numbers the DAX measures in dax/measures.dax would produce inside
Power BI, so preview.html can render a live static preview of the report
without needing Power BI Desktop installed.
"""
import pandas as pd
import json

fact = pd.read_csv("data/fact_sales.csv", parse_dates=["date_key"])
region = pd.read_csv("data/dim_region.csv")
product = pd.read_csv("data/dim_product.csv")
customer = pd.read_csv("data/dim_customer.csv")

fact["revenue"] = fact["quantity"] * fact["unit_price"]
fact["profit"] = fact["quantity"] * (fact["unit_price"] - fact["unit_cost"])
fact["year"] = fact["date_key"].dt.year
fact["month"] = fact["date_key"].dt.to_period("M").astype(str)

merged = fact.merge(product, on="product_key").merge(region, on="region_key").merge(customer, on="customer_key")

kpis = {
    "total_revenue": round(fact["revenue"].sum(), 2),
    "total_profit": round(fact["profit"].sum(), 2),
    "margin_pct": round(fact["profit"].sum() / fact["revenue"].sum() * 100, 1),
    "distinct_customers": int(fact["customer_key"].nunique()),
    "avg_order_value": round(fact["revenue"].sum() / fact["sale_id"].nunique(), 2),
}

by_region = merged.groupby("region_name")["revenue"].sum().sort_values(ascending=False).round(2)
by_month = fact[fact["date_key"] >= "2025-01-01"].groupby("month")["revenue"].sum().round(2)
by_segment = merged.groupby("customer_segment")["revenue"].sum().round(2)
by_category = merged.groupby("category")["revenue"].sum().sort_values(ascending=False).round(2)

by_year = fact.groupby("year")["revenue"].sum()
yoy = round((by_year.get(2025, 0) - by_year.get(2024, 0)) / by_year.get(2024, 1) * 100, 1) if 2024 in by_year.index else None

output = {
    "kpis": kpis,
    "yoy_growth_pct": yoy,
    "region": {"labels": list(by_region.index), "values": list(by_region.values)},
    "month": {"labels": list(by_month.index), "values": list(by_month.values)},
    "segment": {"labels": list(by_segment.index), "values": list(by_segment.values)},
    "category": {"labels": list(by_category.index), "values": list(by_category.values)},
}

with open("data/report_summary.json", "w") as f:
    json.dump(output, f, indent=2)

print(json.dumps(kpis, indent=2))
print(f"YoY growth 2024 to 2025: {yoy}%")
