WITH cardholder_data AS (
  SELECT
    *,
    CONCAT("Portador: ", IFNULL(card_holder_name, "N/A"),
    " - Número do cartão: ", card_number,
    " - Total aprovado: ", total_approved_by_ch,
    " - Número de transações aprovadas: ", count_approved_transactions,
    " - Ticket médio: ", CAST(ROUND(total_approved_by_ch / count_approved_transactions, 2) AS STRING),
    " - Porcentagem do TPV: ", CAST(ROUND(percentage, 2) AS STRING), "%.") AS modelo
  FROM `infinitepay-production.metrics_amlft.cardholder_concentration`
  WHERE merchant_id = {id_client}
)
SELECT
  card_holder_name,
  card_token_id,
  capture_method,
  SUM(total_approved_by_ch) AS Total_Aprovado,
  SUM(total_approved_by_ch_atypical_hours) AS Total_Aprovado_Atipico
FROM cardholder_data
GROUP BY 1,2,3