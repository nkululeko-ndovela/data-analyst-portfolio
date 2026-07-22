# SQL Portfolio: Retail Analytics

A standalone collection of well-commented, non-trivial SQL queries against
a realistic 4-table retail schema (customers, products, orders,
order_items) with 200 customers, 40 products, 1,500 orders, and roughly
3,700 line items, built to be skimmed quickly by anyone assessing SQL depth.

## Why this project exists

Most portfolios show one or two basic `SELECT ... GROUP BY` queries. This
project deliberately covers five different techniques that come up
constantly in real analyst/data work, each framed as an actual business
question rather than a syntax demo.

## Queries

| File | Technique | Business question |
|---|---|---|
| `01_joins_and_aggregation.sql` | 4-table joins, aggregation | Revenue and average order value by category |
| `02_window_functions.sql` | `SUM() OVER`, `RANK() OVER`, `PARTITION BY` | Running spend and order ranking per customer |
| `03_ctes_customer_segmentation.sql` | CTEs, `NTILE()` | Segment customers into spend tiers |
| `04_subquery_repeat_customers.sql` | Correlated subqueries, `EXISTS` | Identify genuine repeat customers |
| `05_month_over_month_growth.sql` | `LAG()`, CTEs | Month-over-month revenue growth % |

## Results (sample)

Category revenue breakdown from `01_joins_and_aggregation.sql`:

| Category | Orders | Revenue | Avg Order Value |
|---|---|---|---|
| Electronics | 817 | R804,976.42 | R985.28 |
| Apparel | 731 | R504,401.83 | R690.02 |
| Beauty | 666 | R444,264.35 | R667.06 |
| Home & Kitchen | 491 | R346,721.61 | R706.15 |
| Sports | 260 | R282,269.99 | R1,085.65 |

Customer spend segmentation from `03_ctes_customer_segmentation.sql` shows
a clear tier split. The top-spending third of customers account for
R1,190,881 of lifetime spend versus R426,637 for the bottom third,
useful for prioritizing retention efforts.

## What I'd do at scale

- Materialize the monthly revenue CTE as a view or dbt model so it's
  reused across multiple downstream queries instead of recomputed
- Add query performance notes (EXPLAIN QUERY PLAN) for the two most
  expensive joins once running against a real multi-million-row table

## Tech stack

SQL (SQLite dialect, window functions, CTEs, correlated subqueries),
Python for the runner script

## Run it yourself

```bash
python3 build_database.py   # builds retail.db
python3 run_queries.py      # runs every query in queries/ and prints results
```
