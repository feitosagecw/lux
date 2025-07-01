-- CH_concentration - métrica construída a partir das transações com clientes (adquirëncia).

SELECT 
  *,
  card_token_id,
  CONCAT("Portador: ", IFNULL(card_holder_name, "N/A"), 
         " - Número do cartão: ", card_number, 
         " - Token do cartão: ", card_token_id,
         " - Total aprovado: R$", total_approved_by_ch, 
         " - Número de transações aprovadas: ", count_approved_transactions, 
         " - Ticket médio: R$", CAST(ROUND(total_approved_by_ch / count_approved_transactions, 2) AS STRING),
         " - Porcentagem do TPV: ", CAST(ROUND(percentage, 2) AS STRING), "%.") AS modelo
FROM `infinitepay-production.metrics_amlft.cardholder_concentration` 
WHERE merchant_id = {id_client} 
ORDER BY percentage DESC; 