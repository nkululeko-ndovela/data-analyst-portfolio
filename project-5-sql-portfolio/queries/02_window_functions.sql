-- 02_window_functions.sql
--
-- Business question: For each customer, what is their running total spend
-- over time, and how does each order rank against their own order history?
--
-- Demonstrates: window functions (SUM() OVER, RANK() OVER) with PARTITION BY,
-- which is the kind of per-customer analysis a simple GROUP BY can't produce.

SELECT
    c.customer_name,
    o.order_id,
    o.order_date,
    ROUND(order_totals.order_value, 2)                                     AS order_value,
    ROUND(SUM(order_totals.order_value) OVER (
        PARTITION BY c.customer_id
        ORDER BY o.order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 2)                                                                  AS running_total_spend,
    RANK() OVER (
        PARTITION BY c.customer_id
        ORDER BY order_totals.order_value DESC
    )                                                                      AS order_rank_for_customer
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN (
    SELECT order_id, SUM(oi.quantity * p.unit_price) AS order_value
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY order_id
) order_totals ON o.order_id = order_totals.order_id
ORDER BY c.customer_id, o.order_date
LIMIT 50;
