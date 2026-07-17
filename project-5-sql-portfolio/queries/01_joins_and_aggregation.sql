-- 01_joins_and_aggregation.sql
--
-- Business question: What is total revenue and order count per product
-- category, and what's the average order value within each category?
--
-- Demonstrates: multi-table joins (4 tables), GROUP BY, aggregate functions.

SELECT
    p.category,
    COUNT(DISTINCT o.order_id)                         AS num_orders,
    SUM(oi.quantity * p.unit_price)                     AS total_revenue,
    ROUND(SUM(oi.quantity * p.unit_price) * 1.0
          / COUNT(DISTINCT o.order_id), 2)              AS avg_order_value
FROM order_items oi
JOIN orders o     ON oi.order_id = o.order_id
JOIN products p   ON oi.product_id = p.product_id
JOIN customers c  ON o.customer_id = c.customer_id
GROUP BY p.category
ORDER BY total_revenue DESC;
