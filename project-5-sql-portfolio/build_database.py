"""
Builds a small but realistic retail database (customers, products, orders,
order_items) for demonstrating non-trivial SQL: window functions, CTEs,
joins across 4 tables, and subqueries.
"""
import sqlite3
import random
from datetime import date, timedelta
from faker import Faker

fake = Faker()
Faker.seed(11)
random.seed(11)

conn = sqlite3.connect("retail.db")
cur = conn.cursor()

cur.executescript("""
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT,
    signup_date TEXT,
    country TEXT
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    unit_price REAL
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    order_date TEXT
);

CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER
);
""")

countries = ["US", "UK", "ZA", "DE", "AU", "CA"]
customers = []
for cid in range(1, 201):
    signup = fake.date_between(start_date="-2y", end_date="-1M")
    customers.append((cid, fake.name(), signup.isoformat(), random.choice(countries)))
cur.executemany("INSERT INTO customers VALUES (?, ?, ?, ?)", customers)

categories = ["Electronics", "Home & Kitchen", "Apparel", "Beauty", "Sports"]
products = []
for pid in range(1, 41):
    products.append((pid, fake.word().title() + " " + random.choice(["Pro", "Max", "Lite", "Plus", ""]).strip(),
                      random.choice(categories), round(random.uniform(5, 400), 2)))
cur.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", products)

orders = []
order_items = []
order_item_id = 1
for oid in range(1, 1501):
    cid = random.randint(1, 200)
    odate = fake.date_between(start_date="-1y", end_date="today").isoformat()
    orders.append((oid, cid, odate))
    for _ in range(random.randint(1, 4)):
        pid = random.randint(1, 40)
        qty = random.randint(1, 5)
        order_items.append((order_item_id, oid, pid, qty))
        order_item_id += 1

cur.executemany("INSERT INTO orders VALUES (?, ?, ?)", orders)
cur.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?)", order_items)

conn.commit()
print(f"retail.db built: {len(customers)} customers, {len(products)} products, "
      f"{len(orders)} orders, {len(order_items)} order_items")
conn.close()
