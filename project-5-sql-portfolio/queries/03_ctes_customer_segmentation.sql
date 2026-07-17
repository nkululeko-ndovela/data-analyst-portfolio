-- 03_ctes_customer_segmentation.sql
--
-- Business question: Segment customers into Top / Mid / Low spenders based
-- on total lifetime spend, and show how many customers fall into each tier
-- along with their average spend.
--
-- Demonstrates: CTEs (WITH clauses) to break a multi-step calculation into
-- clear, named, testable pieces rather than one deeply nested query.

WITH customer_spend AS (
    SELECT
        o.customer_id,
        SUM(oi.quantity * p.unit_price) AS lifetime_spend
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p     ON oi.product_id = p.product_id
    GROUP BY o.customer_id
),
spend_with_tier AS (
    SELECT
        customer_id,
        lifetime_spend,
        NTILE(3) OVER (ORDER BY lifetime_spend DESC) AS spend_tile
    FROM customer_spend
),
labeled AS (
    SELECT
        customer_id,
        lifetime_spend,
        CASE spend_tile
            WHEN 1 THEN 'Top Spender'
            WHEN 2 THEN 'Mid Spender'
            ELSE 'Low Spender'
        END AS spend_segment
    FROM spend_with_tier
)
SELECT
    spend_segment,
    COUNT(*)                         AS num_customers,
    ROUND(AVG(lifetime_spend), 2)    AS avg_lifetime_spend,
    ROUND(SUM(lifetime_spend), 2)    AS segment_total_spend
FROM labeled
GROUP BY spend_segment
ORDER BY avg_lifetime_spend DESC;
