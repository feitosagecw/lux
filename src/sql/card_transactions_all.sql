SELECT
  card_holder_name,
  card_number,
  total_approved_by_ch,
  count_approved_transactions,
  total_approved_by_ch_atypical_hours,
  capture_method,
  percentage,
  merchant_id,
  card_token_id
FROM `infinitepay-production.metrics_amlft.cardholder_concentration`
ORDER BY total_approved_by_ch DESC 