"""
Simulates a legacy on-prem system: a single denormalized table, the kind
you actually inherit from a 15-year-old order management system.
Stands in for a real legacy SQL Server / Oracle system being migrated
to a cloud warehouse.
"""
import sqlite3
import random
from faker import Faker

fake = Faker()
Faker.seed(7)
random.seed(7)

conn = sqlite3.connect("legacy_system.db")
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS legacy_orders")
cur.execute("""
CREATE TABLE legacy_orders (
    order_id INTEGER PRIMARY KEY,
    customer_name TEXT,
    customer_email TEXT,
    customer_city TEXT,
    product_name TEXT,
    product_category TEXT,
    unit_price REAL,
    quantity INTEGER,
    order_date TEXT,
    status TEXT
)
""")

products = [
    ("Wireless Mouse", "Electronics", 19.99),
    ("Standing Desk", "Furniture", 249.00),
    ("Office Chair", "Furniture", 179.50),
    ("USB-C Hub", "Electronics", 34.99),
    ("Notebook Set", "Stationery", 8.25),
    ("Desk Lamp", "Furniture", 42.00),
    ("Mechanical Keyboard", "Electronics", 89.99),
    ("Monitor Stand", "Furniture", 55.00),
]
statuses = ["completed", "completed", "completed", "refunded", "cancelled"]

# generate a fixed pool of customers so the same customer appears across many
# orders in a denormalized, repeated way -- exactly the redundancy normalization fixes
customers = [
    {"name": fake.name(), "email": fake.email(), "city": fake.city()}
    for _ in range(300)
]

rows = []
for order_id in range(1, 4001):
    c = random.choice(customers)
    p = random.choice(products)
    qty = random.randint(1, 5)
    date = fake.date_between(start_date="-2y", end_date="today").isoformat()
    rows.append((
        order_id, c["name"], c["email"], c["city"],
        p[0], p[1], p[2], qty, date, random.choice(statuses)
    ))

cur.executemany("""
INSERT INTO legacy_orders
(order_id, customer_name, customer_email, customer_city, product_name,
 product_category, unit_price, quantity, order_date, status)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", rows)

conn.commit()
count = cur.execute("SELECT COUNT(*) FROM legacy_orders").fetchone()[0]
print(f"legacy_system.db created with {count} rows in legacy_orders (denormalized, flat schema)")
conn.close()
