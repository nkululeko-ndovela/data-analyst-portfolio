"""
Executes every .sql file in queries/ against retail.db and prints the
results, so the SQL in this portfolio is provably correct against real
data rather than just plausible-looking text.
"""
import sqlite3
import glob
import os

conn = sqlite3.connect("retail.db")
conn.row_factory = sqlite3.Row

for path in sorted(glob.glob("queries/*.sql")):
    name = os.path.basename(path)
    print(f"\n{'='*78}\n{name}\n{'='*78}")
    with open(path) as f:
        sql = f.read()
    try:
        cur = conn.execute(sql)
        rows = cur.fetchall()
        if rows:
            headers = rows[0].keys()
            print(" | ".join(headers))
            print("-" * 78)
            for r in rows[:10]:
                print(" | ".join(str(v) for v in r))
            if len(rows) > 10:
                print(f"... ({len(rows)} rows total, showing first 10)")
        else:
            print("(no rows returned)")
    except Exception as e:
        print(f"ERROR running {name}: {e}")

conn.close()
