SELECT
  user_id,
  transaction_type,
  party,
  party_document_number,
  ROUND(pix_amount,2) AS pix_amount,
  ROUND(pix_amount/pix_count,2) AS pix_avg,
  pix_count,
  ROUND(percentage,2) AS percentage,
  ROUND(pix_amount_atypical_hours,2) AS pix_amount_atypical_hours,
  pix_count_atypical_hours,
  CASE
    WHEN transaction_type = 'Cash In' THEN CONCAT('Parte creditora: ', REPLACE(party, '|', ' - Chave pix:'), ' - Valor total: ', pix_amount, ' - Número de transferências: ', pix_count)
    WHEN transaction_type = 'Cash Out' THEN CONCAT('Parte creditada: ', REPLACE(party, '|', ' - Chave pix:'), ' - Valor total: ', pix_amount, ' - Número de transferências: ', pix_count)
  END AS modelo
FROM `infinitepay-production.metrics_amlft.pix_concentration`
WHERE user_id = {id_client}
ORDER BY transaction_type, percentage DESC 