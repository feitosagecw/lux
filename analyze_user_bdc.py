from openai_utils import analyze_bdc_data
import pandas as pd
from google.cloud import bigquery
import os

def get_user_document(user_id: str) -> str:
    """
    Busca o número do documento do usuário no BigQuery.
    
    Args:
        user_id (str): ID do usuário
        
    Returns:
        str: Número do documento
    """
    client = bigquery.Client()
    
    query = f"""
    SELECT 
        COALESCE(b.document_number, b.cpf, e.cpf, "00000000000") as document_number
    FROM `infinitepay-production.maindb.users` a
    LEFT JOIN (
        SELECT DISTINCT me.user_id, me.document_type, me.business_category, 
               me.document_number, me.created_at, re.birthday, re.name, re.cpf
        FROM `infinitepay-production.maindb.merchants` me
        INNER JOIN `infinitepay-production.maindb.legal_representatives` re
        ON me.legal_representative_id = re.id
    ) b ON b.user_id = a.id
    LEFT JOIN (
        SELECT DISTINCT user_id, name, birthday, created_at, cpf
        FROM `infinitepay-production.maindb.cardholders`
    ) e ON e.user_id = a.id
    WHERE CAST(a.id AS STRING) = '{user_id}'
    """
    
    df = client.query(query).to_dataframe()
    
    if df.empty:
        return None
    
    return df['document_number'].iloc[0]

def main():
    # Substitua pelo ID do usuário que você quer analisar
    user_id = input("Digite o ID do usuário: ")
    
    # Busca o documento do usuário
    document = get_user_document(user_id)
    
    if not document:
        print("Usuário não encontrado.")
        return
    
    print(f"\nAnalisando dados do BDC para o documento: {document}")
    
    # Realiza a análise dos dados do BDC
    analysis = analyze_bdc_data(document)
    
    print("\nResultado da análise:")
    print(analysis)

if __name__ == "__main__":
    main() 