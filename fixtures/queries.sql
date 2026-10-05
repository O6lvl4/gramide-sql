WITH RECURSIVE numbers(n) AS (
  VALUES (1)
  UNION ALL
  SELECT n + 1 FROM numbers WHERE n < 5
)
SELECT n, CASE WHEN n % 2 = 0 THEN 'even' ELSE 'odd' END AS parity
FROM numbers ORDER BY n DESC LIMIT 3 OFFSET 1;

SELECT u.display_name, count(v.user_id) AS visits,
       sum(v.duration) FILTER (WHERE v.duration > 0) OVER (
         PARTITION BY u.id ORDER BY v.happened_at
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS rolling
FROM users AS u LEFT OUTER JOIN visits AS v ON u.id = v.user_id
WHERE u.active IS NOT NULL AND u.email NOT LIKE '%@invalid' ESCAPE '\'
GROUP BY u.id HAVING count(*) > 0;
