-- international_cards_check - Transações internacionais com cartão

SELECT
  t.merchant_id,
  t.id,
  t.created_at,
  t.amount,
  t.card_holder_name,
  t.card_number,
  t.card_token_id,
  t.issuer_id,
  i.legal_name,
  cc.Country_Name, 
  t.capture_method
FROM maindb.transactions t
JOIN maindb.issuers i ON t.issuer_id = i.id
JOIN infinitepay-production.external_sources.country_codes cc ON CAST(i.country_code AS INTEGER) = CAST(cc.code AS INTEGER)
WHERE
  t.status = 'approved'
  AND t.created_at BETWEEN TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)) AND CURRENT_TIMESTAMP()
  AND i.country_code <> '076' 
  AND t.merchant_id = {id_client}
ORDER BY t.created_at DESC 