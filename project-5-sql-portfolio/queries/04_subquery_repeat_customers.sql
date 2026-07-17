-- 04_subquery_repeat_customers.sql
--
-- Business question: Which customers placed an order in their first 30
-- days after signup AND placed at least one more order after that? (i.e.
-- genuinely repeat customers, not just one-time signups.)
--
-- Demonstrates: correlated subqueries + EXISTS, an alternative to joins
-- when the question is fundamentally about existence rather than
-- row-level detail.

SELECT
    c.customer_id,
    c.customer_name,
    c.signup_date
FROM customers c
WHERE EXISTS (
    SELECT 1
    FROM orders o
    WHERE o.customer_id = c.customer_id
      AND o.order_date <= date(c.signup_date, '+30 days')
)
AND EXISTS (
    SELECT 1
    FROM orders o2
    WHERE o2.customer_id = c.customer_id
      AND o2.order_date > date(c.signup_date, '+30 days')
)
ORDER BY c.signup_date;
