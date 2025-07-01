WITH
  filtered_transactions AS (
    SELECT
      t.merchant_id,
      t.amount,
      t.card_number,
      t.card_holder_name,
      LEFT(t.card_number, 6) AS card_prefix,
      t.Created_at
    FROM maindb.transactions t
    WHERE
      t.Status = 'approved'
      AND t.merchant_id = {id_client}
  ),
  
  summarized_transactions AS (
    SELECT
      merchant_id,
      card_number,
      card_holder_name,
      SUM(CASE WHEN DATE(Created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY) AND card_prefix IN ('409869', '467481', '498409') THEN amount ELSE 0 END) AS sum_30_days,
      SUM(CASE WHEN DATE(Created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 60 DAY) AND card_prefix IN ('409869', '467481', '498409') THEN amount ELSE 0 END) AS sum_60_days,
      SUM(CASE WHEN DATE(Created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY) AND card_prefix IN ('409869', '467481', '498409') THEN amount ELSE 0 END) AS sum_90_days,
      SUM(CASE WHEN card_prefix IN ('409869', '467481', '498409') THEN amount ELSE 0 END) AS total_sum,
      SUM(CASE WHEN card_prefix IN ('409869', '467481', '498409') AND (EXTRACT(HOUR FROM Created_at) >= 19 OR EXTRACT(HOUR FROM Created_at) < 3) THEN amount ELSE 0 END) AS night_sum
    FROM filtered_transactions
    WHERE created_at >= TIMESTAMP_SUB(CAST(CURRENT_DATE() AS TIMESTAMP), INTERVAL 180 DAY)
    GROUP BY merchant_id, card_number, card_holder_name
  )

SELECT
  card_number,
  card_holder_name,
  sum_30_days,
  sum_60_days,
  sum_90_days,
  total_sum,
  night_sum
FROM summarized_transactions
ORDER BY total_sum DESC 