WITH
  pep_pix_data AS (
    SELECT
      pix_id, 
      pix_amount,
      creditor_user_id,
      creditor_document_number,
      debitor_user_id,
      debitor_document_number
    FROM `infinitepay-production.metrics_amlft.pix_transfers_120`
    WHERE pep_involvement <> 'n/a'
    AND status = 'confirmed'
  ),

  final_select AS (
    SELECT DISTINCT
      case
        when p.debitor_document_number = pep.document_number then p.creditor_user_id
        when p.creditor_document_number = pep.document_number then p.debitor_user_id
      end as flagged_user_id,
      case
        when p.debitor_document_number = pep.document_number then 'cash-in'
        when p.creditor_document_number = pep.document_number then 'cash-out'
      end as transfer_type,
      ROUND(SUM(p.pix_amount),2) AS total_amount,
      case
        when p.debitor_document_number = pep.document_number then p.debitor_document_number
        when p.creditor_document_number = pep.document_number then p.creditor_document_number
      end as pep_document_number,
      pep.name,
      pep.agency,
      pep.job,
      pep.job_description,
      pep.started_at,
      pep.final_eligibility_date      
    FROM pep_pix_data p
    JOIN maindb.politically_exposed_people pep ON (p.creditor_document_number = pep.document_number or p.debitor_document_number = pep.document_number)
    GROUP BY flagged_user_id, transfer_type, pep_document_number, pep.name, pep.agency, pep.job, pep.job_description, pep.started_at, pep.final_eligibility_date
  )

SELECT * FROM final_select
WHERE flagged_user_id = {id_client}
ORDER BY transfer_type, total_amount DESC; 