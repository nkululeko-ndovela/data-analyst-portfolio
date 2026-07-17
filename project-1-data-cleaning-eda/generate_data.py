"""
Generates a deliberately messy raw e-commerce sales dataset to simulate
what a data analyst would actually receive from an operational system:
missing values, duplicates, inconsistent casing, mixed date formats,
and a few outliers.
"""
import numpy as np
import pandas as pd
from faker import Faker
import random

fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)

N = 5000
categories = ["Electronics", "Home & Kitchen", "Apparel", "Beauty", "Sports", "Toys"]
regions = ["North", "South", "East", "West", "Central"]
channels = ["Web", "Mobile App", "Marketplace", "In-Store"]

rows = []
for i in range(N):
    order_id = f"ORD{100000 + i}"
    customer = fake.name()
    category = random.choice(categories)
    region = random.choice(regions)
    channel = random.choice(channels)

    unit_price = round(np.random.uniform(5, 500), 2)
    quantity = np.random.randint(1, 8)
    revenue = round(unit_price * quantity, 2)

    # inject messiness
    if random.random() < 0.03:
        revenue = None  # missing revenue
    if random.random() < 0.02:
        quantity = -abs(quantity)  # bad data entry
    if random.random() < 0.05:
        category = category.upper()  # inconsistent casing
    if random.random() < 0.05:
        category = category.lower()

    # mixed date formats to simulate multiple source systems
    d = fake.date_between(start_date="-18M", end_date="today")
    if random.random() < 0.5:
        date_str = d.strftime("%Y-%m-%d")
    else:
        date_str = d.strftime("%d/%m/%Y")

    rows.append({
        "order_id": order_id,
        "order_date": date_str,
        "customer_name": customer,
        "category": category,
        "region": region if random.random() > 0.01 else None,
        "channel": channel,
        "unit_price": unit_price,
        "quantity": quantity,
        "revenue": revenue,
    })

df = pd.DataFrame(rows)

# inject ~1.5% exact duplicate rows, as often happens with retry logic in source systems
dupes = df.sample(frac=0.015, random_state=1)
df = pd.concat([df, dupes], ignore_index=True)

df.to_csv("data/raw_sales_data.csv", index=False)
print(f"Generated {len(df)} rows -> data/raw_sales_data.csv")
