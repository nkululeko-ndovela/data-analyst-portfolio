# Regional Sales Report: Power BI

A regional sales report modeled the way it would actually be built in
Power BI Desktop: a proper star schema, DAX measures for revenue,
profit, margin, and year-over-year growth, and a report layout with
KPI cards, a monthly trend, and breakdowns by region, segment, and
category. Amounts are in South African Rand (ZAR).

## Problem

A retailer with operations across five South African provinces needs a
report that answers: how much revenue and profit are we making, is it
growing year over year, which regions and categories are driving it,
and how does spend differ between new, returning, and loyalty
customers.

## Approach

1. **Data model** (`data_model.md`): a star schema, one `fact_sales`
   table at the transaction grain, surrounded by `dim_date`,
   `dim_customer`, `dim_product`, and `dim_region`. A proper date
   dimension is included specifically so Power BI's time intelligence
   functions (year-over-year, rolling averages) work correctly rather
   than being approximated.
2. **DAX measures** (`dax/measures.dax`): Total Revenue, Total Profit,
   Profit Margin %, Average Order Value, Revenue YoY %, Revenue Rolling
   3M, and a product revenue ranking measure, written and ready to
   paste into Power BI once the model is loaded.
3. **Report layout**: KPI cards across the top, a monthly revenue trend,
   a customer segment breakdown, and revenue by region and category,
   the same layout structure used in the QI Solutions dashboards this
   project is modeled on.

## A note on how this was built

Power BI Desktop is Windows-only software and isn't available in the
Linux environment this portfolio was built in, so there's no `.pbix`
file here. What's included instead is everything needed to build the
real report in Power BI in a few minutes: the CSV data (`data/`), the
data model documentation with exact relationships to draw
(`data_model.md`), and the working DAX (`dax/measures.dax`). A static
preview (`preview.html`) renders the same numbers those DAX measures
would produce, so the results can be reviewed without opening Power BI
at all.

## Results

| Metric | Value |
|---|---|
| Total revenue | R5,995,788.96 |
| Total profit | R4,133,697.90 |
| Profit margin | 68.9% |
| Distinct customers | 250 |
| Average order value | R876.45 |
| Revenue growth, 2024 to 2025 | 4.8% |

Eastern Cape leads all regions in revenue, and Electronics is the
top-performing category by a wide margin over Apparel and Sports,
useful for prioritizing regional stock allocation.

## How to build this in Power BI Desktop

1. Open Power BI Desktop, **Get Data > Text/CSV**, and load all five
   files in `data/`
2. Go to **Model view** and create the five relationships listed in
   `data_model.md`
3. Right-click `dim_date` in the Fields pane, choose **Mark as Date
   Table**, and select `date_key`
4. Go to **Modeling > New Measure** and paste in each measure from
   `dax/measures.dax`
5. Build the report page: card visuals for the KPI measures, a line
   chart for `Total Revenue` by `dim_date[month_name]`, a bar chart for
   `Total Revenue` by `dim_region[region_name]`, and a donut for
   `Total Revenue` by `dim_customer[customer_segment]`

## What I'd do at scale

- Add a Power Query step to handle late-arriving fact rows and slowly
  changing dimensions on `dim_customer`
- Add row-level security so regional managers only see their own
  province's data
- Publish to the Power BI Service and schedule a nightly refresh
  against the source warehouse instead of static CSVs

## Tech stack

Power BI (data model + DAX), Python (data generation and the static
preview's aggregation), Chart.js (preview rendering only)

## Run it yourself

```bash
python3 generate_powerbi_data.py     # builds the star schema CSVs in data/
python3 prepare_report_summary.py    # aggregates data/report_summary.json for the preview
# then open preview.html in a browser, or serve it:
python3 -m http.server 8000
```
