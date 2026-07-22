"""
Post-migration validation -- the step that actually matters before you're
allowed to say a migration succeeded. Checks:
  1. Row counts reconcile between source and target
  2. Referential integrity holds in the new normalized schema
  3. Aggregate business totals (revenue) match exactly before and after
  4. No orphaned foreign keys
Exits non-zero if anything fails, so this can be wired into a CI/CD gate
before a real cutover.
"""
import sqlite3
import sys

SRC = "legacy_system.db"
DST = "cloud_warehouse.db"

results = []

def check(name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    results.append(passed)
    print(f"[{status}] {name}" + (f" -- {detail}" if detail else ""))

src = sqlite3.connect(SRC)
dst = sqlite3.connect(DST)

# 1. Row count reconciliation
src_count = src.execute("SELECT COUNT(*) FROM legacy_orders").fetchone()[0]
dst_count = dst.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
check("Row count reconciliation (orders)", src_count == dst_count,
      f"source={src_count}, target={dst_count}")

# 2. Revenue totals match exactly pre/post migration
src_revenue = src.execute(
    "SELECT ROUND(SUM(unit_price * quantity), 2) FROM legacy_orders"
).fetchone()[0]
dst_revenue = dst.execute("""
    SELECT ROUND(SUM(unit_price * quantity), 2) FROM orders
""").fetchone()[0]
check("Aggregate revenue matches pre/post migration", src_revenue == dst_revenue,
      f"source=R{src_revenue:,.2f}, target=R{dst_revenue:,.2f}")

# 3. No orphaned foreign keys: every order must reference a valid customer and product
orphan_customers = dst.execute("""
    SELECT COUNT(*) FROM orders o
    LEFT JOIN customers c ON o.customer_id = c.customer_id
    WHERE c.customer_id IS NULL
""").fetchone()[0]
check("No orders with orphaned customer_id", orphan_customers == 0,
      f"orphans={orphan_customers}")

orphan_products = dst.execute("""
    SELECT COUNT(*) FROM orders o
    LEFT JOIN products p ON o.product_id = p.product_id
    WHERE p.product_id IS NULL
""").fetchone()[0]
check("No orders with orphaned product_id", orphan_products == 0,
      f"orphans={orphan_products}")

# 4. Customer deduplication sanity check: unique emails in source == customer rows in target
src_unique_customers = src.execute(
    "SELECT COUNT(DISTINCT customer_email) FROM legacy_orders"
).fetchone()[0]
dst_customers = dst.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
check("Customer deduplication correct", src_unique_customers == dst_customers,
      f"source unique emails={src_unique_customers}, target customers={dst_customers}")

# 5. Every order_id from source exists in target (no dropped records)
src_ids = {r[0] for r in src.execute("SELECT order_id FROM legacy_orders")}
dst_ids = {r[0] for r in dst.execute("SELECT order_id FROM orders")}
missing = src_ids - dst_ids
check("No dropped order records", len(missing) == 0,
      f"missing={len(missing)}")

src.close()
dst.close()

print("\n" + "=" * 50)
if all(results):
    print(f"ALL {len(results)} VALIDATION CHECKS PASSED -- migration cleared for cutover")
    sys.exit(0)
else:
    failed = len(results) - sum(results)
    print(f"{failed} of {len(results)} CHECKS FAILED -- do not cut over, investigate above")
    sys.exit(1)
