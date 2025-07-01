import requests
import json
from config import OPENAI_API_KEY, DEFAULT_MODEL

def generate_text(prompt, model=DEFAULT_MODEL, max_tokens=1000):
    """
    Gera texto usando a API da OpenAI via requests.
    
    Args:
        prompt (str): O prompt para gerar o texto
        model (str): O modelo a ser usado
        max_tokens (int): Número máximo de tokens na resposta
        
    Returns:
        str: O texto gerado
    """
    url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Você é um assistente útil."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Erro ao gerar texto: {str(e)}")
        return None

def analyze_sentiment(text, model=DEFAULT_MODEL):
    """
    Analisa o sentimento de um texto usando a API da OpenAI.
    
    Args:
        text (str): O texto para analisar
        model (str): O modelo a ser usado
        
    Returns:
        dict: Dicionário com a análise de sentimento
    """
    prompt = f"Analise o sentimento do seguinte texto e retorne um dicionário com as chaves 'sentiment' (positivo, negativo ou neutro) e 'score' (número entre 0 e 1):\n\n{text}"
    
    response = generate_text(prompt, model)
    return response 