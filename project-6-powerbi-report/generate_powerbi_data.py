"""
Builds a proper star schema for Power BI: a fact table plus dimension
tables, including a real date dimension, since date tables are what make
time intelligence DAX (YoY, rolling averages) work correctly in Power BI.
Exports everything to CSV so the model can be loaded straight into
Power BI Desktop via Get Data > Text/CSV.
"""
import csv
import random
from datetime import date, timedelta
from faker import Faker

fake = Faker()
Faker.seed(21)
random.seed(21)

# ------------------------------------------------------------------
# dim_date: a full calendar table, the standard pattern for any Power BI
# model that needs YEAR/QUARTER/MONTH slicing or time intelligence
# ------------------------------------------------------------------
start = date(2024, 1, 1)
end = date(2026, 6, 30)
dim_date = []
d = start
while d <= end:
    dim_date.append({
        "date_key": d.isoformat(),
        "year": d.year,
        "quarter": f"Q{(d.month - 1) // 3 + 1}",
        "month_name": d.strftime("%B"),
        "month_number": d.month,
        "day_name": d.strftime("%A"),
        "is_weekend": d.weekday() >= 5,
    })
    d += timedelta(days=1)

with open("data/dim_date.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=dim_date[0].keys())
    w.writeheader()
    w.writerows(dim_date)

# ------------------------------------------------------------------
# dim_region, dim_product, dim_customer
# ------------------------------------------------------------------
regions = [
    {"region_key": 1, "region_name": "Gauteng", "province_group": "Inland"},
    {"region_key": 2, "region_name": "Western Cape", "province_group": "Coastal"},
    {"region_key": 3, "region_name": "KwaZulu-Natal", "province_group": "Coastal"},
    {"region_key": 4, "region_name": "Eastern Cape", "province_group": "Coastal"},
    {"region_key": 5, "region_name": "Free State", "province_group": "Inland"},
]
with open("data/dim_region.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=regions[0].keys())
    w.writeheader()
    w.writerows(regions)

categories = ["Electronics", "Home & Kitchen", "Apparel", "Beauty", "Sports"]
products = []
for pid in range(1, 31):
    products.append({
        "product_key": pid,
        "product_name": fake.word().title() + " " + random.choice(["Pro", "Max", "Lite", "Plus", "Standard"]),
        "category": random.choice(categories),
        "unit_cost": round(random.uniform(5, 150), 2),
        "unit_price": round(random.uniform(20, 500), 2),
    })
with open("data/dim_product.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=products[0].keys())
    w.writeheader()
    w.writerows(products)

customers = []
for cid in range(1, 251):
    customers.append({
        "customer_key": cid,
        "customer_name": fake.name(),
        "customer_segment": random.choice(["New", "Returning", "Loyalty"]),
        "region_key": random.randint(1, 5),
    })
with open("data/dim_customer.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=customers[0].keys())
    w.writeheader()
    w.writerows(customers)

# ------------------------------------------------------------------
# fact_sales: the transaction grain, referencing every dimension by key
# ------------------------------------------------------------------
fact = []
sale_id = 1
d = start
while d <= end:
    n_sales_today = random.randint(3, 12)
    for _ in range(n_sales_today):
        product = random.choice(products)
        customer = random.choice(customers)
        qty = random.randint(1, 6)
        fact.append({
            "sale_id": sale_id,
            "date_key": d.isoformat(),
            "customer_key": customer["customer_key"],
            "product_key": product["product_key"],
            "region_key": customer["region_key"],
            "quantity": qty,
            "unit_price": product["unit_price"],
            "unit_cost": product["unit_cost"],
        })
        sale_id += 1
    d += timedelta(days=1)

with open("data/fact_sales.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fact[0].keys())
    w.writeheader()
    w.writerows(fact)

print(f"dim_date: {len(dim_date)} rows")
print(f"dim_region: {len(regions)} rows")
print(f"dim_product: {len(products)} rows")
print(f"dim_customer: {len(customers)} rows")
print(f"fact_sales: {len(fact)} rows")
