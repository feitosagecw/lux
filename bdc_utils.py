import os
import json
import re
import requests
from typing import Dict, Any

# Configuração das credenciais
BIGDATA_TOKEN_ID = ''
BIGDATA_TOKEN_HASH = ''

def sanitize_document(document: str) -> str:
    """
    Remove caracteres não numéricos do documento.
    
    Args:
        document (str): Número do documento (CPF/CNPJ)
        
    Returns:
        str: Documento sanitizado
    """
    return re.sub(r'\D', '', document)

def fetch_bdc_data(
    document_number: str,
    url: str = "https://plataforma.bigdatacorp.com.br/pessoas",
    dataset: str = """basic_data,
                      processes.filter(partypolarity = PASSIVE, courttype = CRIMINAL),
                      kyc.filter(standardized_type, standardized_sanction_type, type, sanctions_source = Conselho Nacional de Justiça)
                      """,
    token_hash: str = BIGDATA_TOKEN_HASH,
    token_id: str = BIGDATA_TOKEN_ID
) -> Dict[str, Any]:
    """
    Busca dados no Big Data Corp.
    
    Args:
        document_number (str): Número do documento (CPF/CNPJ)
        url (str): URL da API
        dataset (str): Conjunto de dados a ser consultado
        token_hash (str): Hash do token de acesso
        token_id (str): ID do token de acesso
        
    Returns:
        Dict[str, Any]: Dados retornados pela API
    """
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "AccessToken": token_hash,
        "TokenId": token_id
    }
    
    payload = {
        "q": f"doc{{{document_number}}}",
        "Datasets": dataset
    }
    print(f"URL: {url}")
    print(f"Payload: {payload}")
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar dados: {str(e)}")
        return None

def analyze_document(document: str) -> Dict[str, Any]:
    """
    Analisa um documento no Big Data Corp.
    
    Args:
        document (str): Número do documento (CPF/CNPJ)
        
    Returns:
        Dict[str, Any]: Resultado da análise
    """
    sanitized_doc = sanitize_document(document)
    print(f'Documento utilizado na busca: {sanitized_doc}')
    
    # Se for CNPJ (maior que 11 caracteres), usar URL de empresas
    if len(sanitized_doc) > 11:
        url = "https://plataforma.bigdatacorp.com.br/empresas"
    else:
        url = "https://plataforma.bigdatacorp.com.br/pessoas"
    
    # Chamar fetch_bdc_data com o documento sanitizado e url correto
    result = fetch_bdc_data(document_number=sanitized_doc, url=url)
    
    # Verificar se o resultado é válido
    if not result:
        return {"Result": []}
        
    return result 