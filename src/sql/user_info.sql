WITH merchant_info AS (
  SELECT 
    me.user_id, 
    me.document_type, 
    me.business_category, 
    me.document_number, 
    me.created_at AS created_at_me, 
    re.birthday, 
    re.name, 
    re.cpf
  FROM `infinitepay-production.maindb.merchants` me
  INNER JOIN `infinitepay-production.maindb.legal_representatives` re
    ON me.legal_representative_id = re.id
), 

cardholder_info AS (
  SELECT 
    user_id, 
    name, 
    birthday, 
    cpf, 
    created_at
  FROM `infinitepay-production.maindb.cardholders`
), 

address_info AS (
  SELECT 
    user_id,
    CONCAT(street, ', ', CAST(number AS STRING), ', ',city, ', ',state, ', ',cep) AS endereco,
    ARRAY_AGG(city ORDER BY updated_at DESC LIMIT 1)[OFFSET(0)] AS cidade,
    ARRAY_AGG(state ORDER BY updated_at DESC LIMIT 1)[OFFSET(0)] AS estado
  FROM `infinitepay-production.maindb.addresses`
  GROUP BY user_id,endereco
)

SELECT 
a.endereco,
  u.id AS id_cliente,
  COALESCE(c.name, m.name) AS nome,
  u.email,
  SAFE_CAST(
    DATE_DIFF(
      CURRENT_DATE(),
      SAFE.PARSE_DATE('%d/%m/%Y', COALESCE(m.birthday, c.birthday)),
      DAY
    ) / 365.26 AS INT
  ) AS idade,
  u.status,
  u.status_reason,
  CASE 
    WHEN m.document_type = "cnpj" THEN "Merchant Pessoa Jurídica"
    WHEN m.document_type = "cpf" THEN "Merchant Pessoa Física"
    ELSE "Cardholder"
  END AS Role_Type,
  COALESCE(m.business_category, "Não Informado") AS categoria_negocio,
  COALESCE(m.document_number, m.cpf, c.cpf, "00000000000") AS document_number,
  CAST(c.created_at AS DATE) AS created_at_ch,
  CAST(m.created_at_me AS DATE) AS created_at_me,
  a.cidade,
  a.estado
FROM `infinitepay-production.maindb.users` u
LEFT JOIN merchant_info m ON m.user_id = u.id
LEFT JOIN cardholder_info c ON c.user_id = u.id
LEFT JOIN address_info a ON a.user_id = u.id
WHERE u.id = {id_client}