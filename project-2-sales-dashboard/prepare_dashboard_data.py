"""
Aggregates the cleaned sales dataset into a compact JSON file consumed by
index.html. Keeping the aggregation in Python (rather than doing it in
JS) mirrors how a real BI dashboard is fed by a pre-aggregated data mart
rather than raw transaction rows.
"""
import pandas as pd
import json

df = pd.read_csv("data/cleaned_sales_data.csv", parse_dates=["order_date"])
df["month"] = df["order_date"].dt.to_period("M").astype(str)

monthly = df.groupby("month")["revenue"].sum().round(2)
category = df.groupby("category")["revenue"].sum().sort_values(ascending=False).round(2)
region = df.groupby("region")["revenue"].sum().sort_values(ascending=False).round(2)
channel = df.groupby("channel")["revenue"].sum().round(2)

kpis = {
    "total_revenue": round(df["revenue"].sum(), 2),
    "total_orders": int(df.shape[0]),
    "avg_order_value": round(df["revenue"].mean(), 2),
    "top_category": category.idxmax(),
    "top_region": region.idxmax(),
}

output = {
    "kpis": kpis,
    "monthly": {"labels": list(monthly.index), "values": list(monthly.values)},
    "category": {"labels": list(category.index), "values": list(category.values)},
    "region": {"labels": list(region.index), "values": list(region.values)},
    "channel": {"labels": list(channel.index), "values": list(channel.values)},
}

with open("data/dashboard_data.json", "w") as f:
    json.dump(output, f, indent=2)

print("Wrote data/dashboard_data.json")
print(json.dumps(kpis, indent=2))
