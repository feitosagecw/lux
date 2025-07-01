-- issuing_alert_check - transações cartão de pagamento da infinite pay ao cliente

WITH
        high_risk_countries AS (
            SELECT
            country_name,
            iso3,
            CASE 
                WHEN iso3 IN ('LBN', 'CIV', 'AGO', 'DZA', 'BGR', 'BFA', 'CMR', 'HRV', 'HTI', 'KEN', 'MLI', 'MOZ', 'MMR', 'NAM', 'NGA', 'PHL', 'SEN', 'ZAF', 'TZA', 'VNM', 'COD', 'SYR', 'YEM', 'YMD', 'IRN', 'PRK', 'MCO', 'VEN')
                THEN 'gafi_country'
                ELSE 'not_gafi_country'
            END AS gafi_or_not   
            FROM external_sources.country_codes
        ),

        
        issuing_analysis AS (
            SELECT
            i.payer_user_id as user_id,
            i.merchant_name,
            mcc_description,
            COUNT(DISTINCT i.issuing_payment_id) AS transactions_count,
            SUM(CASE WHEN i.issuing_payment_message_created_at >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)) THEN i.amount ELSE 0 END) AS total_amount_90d,
            SUM(CASE WHEN i.issuing_payment_message_created_at >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 60 DAY)) THEN i.amount ELSE 0 END) AS total_amount_60d,
            SUM(CASE WHEN i.issuing_payment_message_created_at >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)) THEN i.amount ELSE 0 END) AS total_amount_30d,

            SUM(CASE WHEN i.issuing_payment_message_created_at >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)) AND h.gafi_or_not = 'gafi_country' THEN i.amount ELSE 0 END) AS total_amount_90d_gafi_acquirer,
            SUM(CASE WHEN i.issuing_payment_message_created_at >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 60 DAY)) AND h.gafi_or_not = 'gafi_country' THEN i.amount ELSE 0 END) AS total_amount_60d_gafi_acquirer,
            SUM(CASE WHEN i.issuing_payment_message_created_at >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)) AND h.gafi_or_not = 'gafi_country' THEN i.amount ELSE 0 END) AS total_amount_30d_gafi_acquirer,

            SUM(CASE WHEN i.issuing_payment_message_created_at >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)) AND h.gafi_or_not = 'not_gafi_country' AND i.merchant_region IS NOT NULL AND i.merchant_region <> 'BRA' THEN i.amount ELSE 0 END) AS total_amount_90d_international_acquirer,

            SUM(CASE WHEN i.issuing_payment_message_created_at >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 60 DAY)) AND h.gafi_or_not = 'not_gafi_country' AND i.merchant_region IS NOT NULL AND i.merchant_region <> 'BRA' THEN i.amount ELSE 0 END) AS total_amount_60d_international_acquirer,

            SUM(CASE WHEN i.issuing_payment_message_created_at >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)) AND h.gafi_or_not = 'not_gafi_country' AND i.merchant_region IS NOT NULL AND i.merchant_region <> 'BRA' THEN i.amount ELSE 0 END) AS total_amount_30d_international_acquirer

            FROM metrics_amlft.issuing_transactions_90 i
            LEFT JOIN high_risk_countries h ON i.merchant_region = h.iso3
            WHERE 1=1
            AND i.issuing_payment_actions_status = 'processed' 
            AND i.issuing_payment_actions_type = 'clear'
            AND i.issuing_payment_token = 'brlc'
            GROUP BY 1, 2, 3
        ),

        final_select AS (
            SELECT DISTINCT
            ia.user_id,
            ia.merchant_name,
            mcc_description,
            total_amount_90d,
            total_amount_60d,
            total_amount_30d,
            total_amount_90d_international_acquirer,
            total_amount_60d_international_acquirer,
            total_amount_30d_international_acquirer,
            total_amount_90d_gafi_acquirer,
            total_amount_60d_gafi_acquirer,
            total_amount_30d_gafi_acquirer
            FROM issuing_analysis ia
            WHERE 1=1
        )

      select * from final_select
      where user_id = {id_client}
      ORDER BY 4 DESC 