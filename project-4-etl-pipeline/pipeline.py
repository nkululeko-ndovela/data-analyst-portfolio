"""
A small, self-contained ETL pipeline: extract a daily CSV batch, run data
quality checks, transform, and load idempotently into a SQLite warehouse
table (standing in for Snowflake/BigQuery/Redshift).

Designed to be run daily by a scheduler (cron, or an Airflow DAG — see
airflow_dag_example.py for how this would be orchestrated in production).

Run:
    python3 pipeline.py
"""
import csv
import sqlite3
import logging
import sys
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler("pipeline.log"), logging.StreamHandler()],
)
log = logging.getLogger("pipeline")

SOURCE_PATH = "source_data/orders_raw.csv"
DB_PATH = "warehouse.db"

# ------------------------------------------------------------------
# QUALITY CHECK THRESHOLDS -- pipeline fails loudly rather than
# silently loading bad data, which is the whole point of a real
# data-quality gate
# ------------------------------------------------------------------
MAX_NULL_RATE = 0.05      # fail if more than 5% of amounts are null
MAX_NEGATIVE_RATE = 0.02  # fail if more than 2% of amounts are negative


def extract(path):
    log.info("EXTRACT: reading %s", path)
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    log.info("EXTRACT: %d rows read", len(rows))
    return rows


def quality_checks(rows):
    log.info("QUALITY CHECKS: validating batch before transform")
    total = len(rows)
    n_null = sum(1 for r in rows if r["amount"] in ("", "None", None))
    n_negative = sum(
        1 for r in rows
        if r["amount"] not in ("", "None", None) and float(r["amount"]) < 0
    )

    null_rate = n_null / total
    negative_rate = n_negative / total
    log.info("QUALITY CHECKS: null_amount_rate=%.3f, negative_amount_rate=%.3f", null_rate, negative_rate)

    failures = []
    if null_rate > MAX_NULL_RATE:
        failures.append(f"null amount rate {null_rate:.1%} exceeds threshold {MAX_NULL_RATE:.1%}")
    if negative_rate > MAX_NEGATIVE_RATE:
        failures.append(f"negative amount rate {negative_rate:.1%} exceeds threshold {MAX_NEGATIVE_RATE:.1%}")

    if failures:
        for f in failures:
            log.error("QUALITY CHECK FAILED: %s", f)
        raise ValueError("Batch failed quality gate: " + "; ".join(failures))

    log.info("QUALITY CHECKS: all checks within threshold, proceeding to transform")
    return n_null, n_negative


def transform(rows):
    log.info("TRANSFORM: dropping invalid rows, casting types")
    clean = []
    dropped = 0
    for r in rows:
        amount = r["amount"]
        if amount in ("", "None", None) or float(amount) < 0:
            dropped += 1
            continue
        clean.append((
            r["order_id"],
            r["order_date"],
            r["customer_email"].lower().strip(),
            round(float(amount), 2),
            r["country"].upper(),
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
        ))
    log.info("TRANSFORM: %d clean rows, %d dropped for failing row-level rules", len(clean), dropped)
    return clean


def load(clean_rows):
    log.info("LOAD: writing to %s (idempotent upsert on order_id)", DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS fact_orders (
        order_id TEXT PRIMARY KEY,
        order_date TEXT,
        customer_email TEXT,
        amount REAL,
        country TEXT,
        loaded_at TEXT
    )
    """)
    # INSERT OR REPLACE makes reruns of the same batch safe (idempotent),
    # which matters because pipelines *will* get rerun after failures
    cur.executemany("""
        INSERT OR REPLACE INTO fact_orders (order_id, order_date, customer_email, amount, country, loaded_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, clean_rows)
    conn.commit()
    total = cur.execute("SELECT COUNT(*) FROM fact_orders").fetchone()[0]
    conn.close()
    log.info("LOAD: complete, warehouse.db now holds %d total rows", total)


def run():
    log.info("=== PIPELINE RUN START ===")
    try:
        rows = extract(SOURCE_PATH)
        quality_checks(rows)
        clean_rows = transform(rows)
        load(clean_rows)
        log.info("=== PIPELINE RUN SUCCESS ===")
    except Exception as e:
        log.error("=== PIPELINE RUN FAILED: %s ===", e)
        sys.exit(1)


if __name__ == "__main__":
    run()
