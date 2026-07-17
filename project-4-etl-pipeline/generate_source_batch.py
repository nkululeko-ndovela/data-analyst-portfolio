"""
Simulates a daily batch file landing from an upstream operational system
(e.g. dropped into an S3/Blob landing zone every night). Includes a few
realistic data quality problems the pipeline's checks are designed to catch.
"""
import csv
import random
from datetime import date, timedelta
from faker import Faker

fake = Faker()
Faker.seed(3)
random.seed(3)

rows = []
today = date.today()
for i in range(1200):
    order_date = today - timedelta(days=random.randint(0, 6))
    amount = round(random.uniform(10, 800), 2)
    # inject a few bad rows the quality checks should catch
    if random.random() < 0.01:
        amount = -5.00  # invalid negative amount
    if random.random() < 0.01:
        amount = None  # missing amount

    rows.append({
        "order_id": f"O{20000 + i}",
        "order_date": order_date.isoformat(),
        "customer_email": fake.email(),
        "amount": amount,
        "country": fake.country_code(),
    })

with open("source_data/orders_raw.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["order_id", "order_date", "customer_email", "amount", "country"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to source_data/orders_raw.csv")
