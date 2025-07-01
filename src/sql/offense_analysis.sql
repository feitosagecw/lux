SELECT
  date AS Data_Offense,
  conclusion,
  priority,
  description,
  analyst,
  name
FROM `infinitepay-production.metrics_amlft.lavandowski_offense_analysis_data`
WHERE user_id = {id_client}
AND analysis_type in ("manual", "automatic")
--AND name = "money_laundering"
ORDER BY Data_Offense DESC 