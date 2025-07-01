SELECT DISTINCT
p.phone_number IS NOT NULL AS has_phonecast,
u.id AS user_id,
name,
c.raw_phone_number AS raw_phone_number,
u.status AS status,
u.status_reason
FROM
`infinitepay-production.scd_domains.user_contacts` c
LEFT JOIN
infinitepay-production.external_sources.phonecast p ON p.phone_number = `infinitepay-production.udfs.phone_number_norm`(raw_phone_number)
LEFT JOIN
infinitepay-production.maindb.users u ON u.phone_number = `infinitepay-production.udfs.phone_number_norm`(raw_phone_number)
WHERE
user_id = {id_client} and status not in ("active", "null") 
