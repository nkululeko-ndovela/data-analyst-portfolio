"""
Migration: legacy_system.db (flat, denormalized) -> cloud_warehouse.db
(normalized star schema, standing in for Snowflake/Azure SQL/BigQuery).

This is the E-T-L logic you'd actually run once, carefully, against a
production legacy system -- with logging at every step so the migration
is auditable, not a black box.
"""
import sqlite3
import hashlib
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler("migration.log"), logging.StreamHandler()],
)
log = logging.getLogger("migration")

SRC = "legacy_system.db"
DST = "cloud_warehouse.db"


def extract():
    log.info("EXTRACT: reading legacy_orders from %s", SRC)
    conn = sqlite3.connect(SRC)
    rows = conn.execute("SELECT * FROM legacy_orders").fetchall()
    cols = [d[0] for d in conn.execute("SELECT * FROM legacy_orders LIMIT 1").description]
    conn.close()
    log.info("EXTRACT: %d rows read", len(rows))
    return cols, rows


def transform(cols, rows):
    log.info("TRANSFORM: normalizing into customers / products / orders")
    idx = {c: i for i, c in enumerate(cols)}

    customers = {}   # email -> customer_id
    products = {}    # (name, category) -> product_id
    fact_orders = []

    for r in rows:
        email = r[idx["customer_email"]]
        if email not in customers:
            customers[email] = len(customers) + 1

        pkey = (r[idx["product_name"]], r[idx["product_category"]])
        if pkey not in products:
            products[pkey] = len(products) + 1

        fact_orders.append({
            "order_id": r[idx["order_id"]],
            "customer_id": customers[email],
            "product_id": products[pkey],
            "unit_price": r[idx["unit_price"]],
            "quantity": r[idx["quantity"]],
            "order_date": r[idx["order_date"]],
            "status": r[idx["status"]],
        })

    customer_rows = []
    for email, cid in customers.items():
        r = next(row for row in rows if row[idx["customer_email"]] == email)
        customer_rows.append((cid, r[idx["customer_name"]], email, r[idx["customer_city"]]))

    product_rows = [(pid, name, cat) for (name, cat), pid in products.items()]

    log.info(
        "TRANSFORM: %d orders -> %d unique customers, %d unique products (deduplicated from %d raw rows)",
        len(fact_orders), len(customer_rows), len(product_rows), len(rows),
    )
    return customer_rows, product_rows, fact_orders


def load(customer_rows, product_rows, fact_orders):
    log.info("LOAD: writing normalized schema to %s", DST)
    conn = sqlite3.connect(DST)
    cur = conn.cursor()

    cur.executescript("""
    DROP TABLE IF EXISTS orders;
    DROP TABLE IF EXISTS customers;
    DROP TABLE IF EXISTS products;

    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        customer_name TEXT,
        customer_email TEXT UNIQUE,
        customer_city TEXT
    );

    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT,
        product_category TEXT
    );

    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER REFERENCES customers(customer_id),
        product_id INTEGER REFERENCES products(product_id),
        unit_price REAL,
        quantity INTEGER,
        order_date TEXT,
        status TEXT
    );
    """)

    cur.executemany("INSERT INTO customers VALUES (?, ?, ?, ?)", customer_rows)
    cur.executemany("INSERT INTO products VALUES (?, ?, ?)", product_rows)
    cur.executemany(
        "INSERT INTO orders VALUES (:order_id, :customer_id, :product_id, :unit_price, :quantity, :order_date, :status)",
        fact_orders,
    )
    conn.commit()
    conn.close()
    log.info("LOAD: complete")


def checksum_source(rows):
    """Order-independent checksum over key business fields, used by validate_migration.py"""
    h = hashlib.sha256()
    for r in sorted(rows, key=lambda x: x[0]):
        h.update(str(r).encode())
    return h.hexdigest()


if __name__ == "__main__":
    start = datetime.now()
    log.info("=== MIGRATION START ===")
    cols, rows = extract()

    with open("source_checksum.txt", "w") as f:
        f.write(checksum_source(rows))

    customer_rows, product_rows, fact_orders = transform(cols, rows)
    load(customer_rows, product_rows, fact_orders)

    elapsed = (datetime.now() - start).total_seconds()
    log.info("=== MIGRATION COMPLETE in %.2fs ===", elapsed)
    log.info("Run validate_migration.py next to confirm integrity before cutover.")
