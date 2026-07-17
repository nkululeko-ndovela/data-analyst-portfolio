# Daily Orders ETL Pipeline (with Quality Gate)

A self-contained, runnable ETL pipeline that simulates a daily batch job:
extract a landed CSV file, enforce a data-quality gate before any
transformation happens, transform, and load idempotently into a
warehouse table.

## Problem

Daily batch pipelines fail in two ways: loudly (easy to fix) or silently
(bad data quietly makes it into dashboards and nobody notices until a
stakeholder asks why revenue looks wrong). This pipeline is built to
fail loudly — quality thresholds are checked *before* transformation, so
a genuinely broken batch stops the pipeline instead of getting "cleaned"
into something that looks fine but isn't trustworthy.

## Approach

1. **Extract** — read the daily CSV batch (`source_data/orders_raw.csv`)
2. **Quality gate** — before transforming anything, check the batch
   against thresholds:
   - Null `amount` rate must stay under 5%
   - Negative `amount` rate must stay under 2%
   - If either threshold is breached, the pipeline raises and exits
     non-zero — it does not proceed to load partial or suspect data
3. **Transform** — normalize emails to lowercase, uppercase country
   codes, cast and round amounts, drop row-level invalid records (with
   the count logged, not silently discarded)
4. **Load** — idempotent upsert (`INSERT OR REPLACE`) keyed on
   `order_id` into `warehouse.db`, so re-running the same batch after a
   failure is always safe and never creates duplicates
5. **Orchestration** — `airflow_dag_example.py` shows how this same
   pipeline would be wired into an Airflow DAG for daily 3 AM scheduling
   with retries and failure alerting, since a real production version of
   this wouldn't be triggered by hand

## Results

A sample run against a 1,200-row batch:

```
EXTRACT: 1200 rows read
QUALITY CHECKS: null_amount_rate=0.007, negative_amount_rate=0.011
QUALITY CHECKS: all checks within threshold, proceeding to transform
TRANSFORM: 1178 clean rows, 22 dropped for failing row-level rules
LOAD: complete, warehouse.db now holds 1178 total rows
PIPELINE RUN SUCCESS
```

Re-running the pipeline against the same file a second time correctly
leaves the warehouse at 1,178 rows (proving the load step is idempotent,
not additive).

## What I'd do at scale

- Swap the CSV landing zone for an actual S3/Blob storage trigger
- Replace SQLite with a real warehouse (Snowflake/BigQuery/Redshift) and
  load via bulk COPY rather than row-by-row inserts
- Add schema drift detection (alert if the upstream file gains/loses a
  column) as an additional pre-transform check
- Push pipeline run metrics (rows processed, rows dropped, duration) to
  a monitoring dashboard instead of just a log file

## Tech stack

Python, SQLite, logging, Airflow (orchestration pattern shown, not run
in this environment)

## Run it yourself

```bash
python3 generate_source_batch.py   # creates a sample daily batch file
python3 pipeline.py                # runs extract -> quality gate -> transform -> load
python3 pipeline.py                # run again to see idempotent re-load
```
