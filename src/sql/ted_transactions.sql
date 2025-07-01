-- ted alert - transações realizadas por TED

WITH
  ted_transactions AS (
      SELECT
      user_id,
      id,
      created_at,
      status,
      amount/100 as amount,
      document_number_debited,
      legal_name_debited,
      document_number_credited,
      legal_name_credited
      FROM `banking_spb.spb_transactions`
      WHERE status = 'CONFIRMED'
      AND message_code = 'STR0008R2'
      AND DATE(created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 60 DAY)
      ORDER BY 2, 5 DESC
  ),

  ted_thresholds AS (
      SELECT
      user_id,
      COUNT(DISTINCT id) as ted_count,
      SUM(amount) as total_amount
      FROM ted_transactions
      GROUP BY 1
  ),

  final_result AS (
      SELECT
        DISTINCT tt.user_id
      FROM ted_transactions tt
      JOIN ted_thresholds th ON tt.user_id = th.user_id
      WHERE (
        (th.total_amount >= 140000)
        OR
        (th.ted_count >= 10 AND th.total_amount >= 50000)
      )
  )

SELECT 
  f.user_id,
  t.amount as ted_amount,
  t.created_at as ted_created_at,
  t.id as ted_id,
  t.document_number_debited,
  t.legal_name_debited,
  t.document_number_credited,
  t.legal_name_credited   
FROM final_result f
JOIN ted_transactions t ON f.user_id = t.user_id
WHERE f.user_id = {id_client} 