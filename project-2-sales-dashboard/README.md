# Sales Performance Dashboard (Interactive)

A stakeholder-facing BI dashboard built on top of the cleaned dataset from
`project-1-data-cleaning-eda`, demonstrating the second half of the analyst
workflow: turning validated data into something a non-technical audience can
act on.

## Problem

A cleaned dataset is only useful once it's in front of the people making
decisions. This project takes the validated sales data and builds an
interactive dashboard a sales director could actually use in a Monday
morning review — KPIs at a glance, trend over time, and a breakdown by
category, region, and channel.

## Approach

- **Data pipeline**: `prepare_dashboard_data.py` (Python/pandas) aggregates
  the cleaned transaction-level data into a compact JSON data mart — the
  dashboard never touches raw rows, the same separation of concerns you'd
  want in a real Power BI / Looker semantic layer.
- **Front end**: `index.html` (Chart.js) renders KPI cards and four chart
  views, styled deliberately rather than left as default chart-library
  styling, since this is the artifact a hiring manager actually looks at.
- **Data-quality transparency**: a strip at the top of the dashboard
  surfaces exactly what was cleaned upstream (duplicates removed, values
  recomputed, categories normalized) — a detail most dashboards hide, but
  one that builds trust with stakeholders reviewing the numbers.

## Results

- Live KPIs: total revenue, total orders, average order value, top category
- Monthly revenue trend line
- Revenue share by sales channel (doughnut)
- Revenue by category and by region (bar charts)

## What I'd do at scale

- Swap the static JSON for a live connection to a warehouse table
  (Snowflake/BigQuery) refreshed nightly by the pipeline in
  `project-4-etl-pipeline`
- Add drill-down filters (date range, region) and role-based views
- Rebuild the same data mart as an actual Power BI/Tableau workbook for
  environments where that's the standard tool

## Tech stack

Python (pandas) for aggregation, HTML/CSS/JavaScript + Chart.js for the
front end — no build step required.

## Run it yourself

```bash
python3 prepare_dashboard_data.py   # regenerates data/dashboard_data.json
# then open index.html directly in a browser, or serve it:
python3 -m http.server 8000
# visit http://localhost:8000
```
