-- 05_month_over_month_growth.sql
--
-- Business question: What is month-over-month revenue growth (%) over the
-- last year?
--
-- Demonstrates: LAG() window function to compare each row to the previous
-- period without a self-join.

WITH monthly_revenue AS (
    SELECT
        strftime('%Y-%m', o.order_date)      AS month,
        SUM(oi.quantity * p.unit_price)       AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p     ON oi.product_id = p.product_id
    GROUP BY month
)
SELECT
    month,
    ROUND(revenue, 2)                                                  AS revenue,
    ROUND(LAG(revenue) OVER (ORDER BY month), 2)                       AS prev_month_revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY month)) * 100.0
        / NULLIF(LAG(revenue) OVER (ORDER BY month), 0), 2
    )                                                                  AS mom_growth_pct
FROM monthly_revenue
ORDER BY month;
