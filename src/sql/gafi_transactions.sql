WITH
    gafi_countries AS (
        SELECT
            country_name,
            code
        FROM `infinitepay-production.external_sources.country_codes`
        WHERE country_name IN ('Algeria', 'Angola', 'Bulgaria', 'Burkina Faso', 'Cameroon', "Cote d'Ivoire", 'Croatia', 'Haiti', 'Monaco', 'Kenya', 'Lebanon', 'Mali', 'Mozambique', 'Myanmar', 'Namibia', 'Nigeria', 'Philippines', 'Senegal', 'South Africa', 'Tanzania', 'Vietnam', 'Congo, Dem. Rep.', 'Syrian Arab Republic', 'Venezuela', 'Yemen, Rep.', 'Yemen Democratic', 'Iran, Islamic Rep.', 'Korea, Dem. Rep.')
    ),

    total_amount_last_24h AS (
        SELECT
            t.merchant_id,
            SUM(t.amount) as total_amount,
            'total_amount_last_24h' AS alert_origin,
            t.card_holder_name,
            t.card_number,
            g.country_name
        FROM `infinitepay-production.maindb.transactions` t
        JOIN `infinitepay-production.maindb.issuers` i ON t.issuer_id = i.id
        JOIN gafi_countries g ON CAST(i.country_code AS STRING) = CAST(g.code AS STRING)
        WHERE
            t.status = 'approved'
            AND t.created_at >= CURRENT_TIMESTAMP() - INTERVAL 24 HOUR
        GROUP BY 1, 4, 5, 6
        HAVING total_amount >= 999
    ),

    high_amount_transactions_last_24h AS (
        SELECT
            t.merchant_id,
            COUNT(DISTINCT t.id) AS high_value_transactions_count,
            'high_amount_transactions_last_24h' AS alert_origin,
            t.card_holder_name,
            t.card_number,
            g.country_name
        FROM `infinitepay-production.maindb.transactions` t
        JOIN `infinitepay-production.maindb.issuers` i ON t.issuer_id = i.id
        JOIN gafi_countries g ON CAST(i.country_code AS STRING) = CAST(g.code AS STRING)
        WHERE
            t.status = 'approved'
            AND t.amount >= 1000
            AND t.created_at >= CURRENT_TIMESTAMP() - INTERVAL 48 HOUR
        GROUP BY 1, 4, 5, 6
    ),

    total_amount_last_30_days AS (
        SELECT
            t.merchant_id,
            SUM(t.amount) as total_amount,
            'total_amount_last_30_days' AS alert_origin,
            t.card_holder_name,
            t.card_number,
            g.country_name
        FROM `infinitepay-production.maindb.transactions` t
        JOIN `infinitepay-production.maindb.issuers` i ON t.issuer_id = i.id
        JOIN gafi_countries g ON CAST(i.country_code AS STRING) = CAST(g.code AS STRING)
        WHERE
            t.status = 'approved'
            AND t.created_at >= CURRENT_TIMESTAMP() - INTERVAL 30 DAY
        GROUP BY 1, 4, 5, 6
        HAVING total_amount >= 10000
    )

SELECT
    DISTINCT m.user_id AS merchant_id,
    ROUND(t24.total_amount, 2) AS total_amount_24h,
    ROUND(t30.total_amount, 2) AS total_amount_30days,
    COALESCE(t24.alert_origin, h24.alert_origin, t30.alert_origin) as alert_origin,
    COALESCE(t24.card_holder_name, h24.card_holder_name, t30.card_holder_name) as card_holder_name,
    COALESCE(t24.card_number, h24.card_number, t30.card_number) as card_number,
    COALESCE(t24.country_name, h24.country_name, t30.country_name) as country_name
FROM `infinitepay-production.maindb.merchants` m
LEFT JOIN total_amount_last_24h t24 ON m.user_id = t24.merchant_id
LEFT JOIN high_amount_transactions_last_24h h24 ON m.user_id = h24.merchant_id
LEFT JOIN total_amount_last_30_days t30 ON m.user_id = t30.merchant_id
WHERE
    (t24.merchant_id IS NOT NULL OR h24.merchant_id IS NOT NULL OR t30.merchant_id IS NOT NULL)
    AND m.user_id = {id_client}
ORDER BY 1 