from openai_utils import generate_text
from bdc_utils import analyze_document
import json

def analyze_processes(document_number: str) -> str:
    """
    Analisa processos relacionados a um documento usando Big Data Corp e OpenAI.
    
    Args:
        document_number (str): Número do documento (CPF/CNPJ)
        
    Returns:
        str: Análise dos processos em formato de texto
    """
    # Busca dados no Big Data Corp
    bdc_data = analyze_document(document_number)
    
    if not bdc_data:
        return "Não foi possível obter dados do Big Data Corp."
    
    # Extrai informações de processos
    processes = bdc_data.get('processes', [])
    
    if not processes:
        return "Nenhum processo encontrado para este documento."
    
    # Prepara o prompt para a OpenAI
    prompt = f"""Analise os seguintes processos judiciais e forneça um resumo em português, destacando:
1. Quantidade total de processos
2. Natureza dos processos (cível, criminal, trabalhista, etc.)
3. Status dos processos
4. Principais pontos de atenção
5. Recomendações para análise de risco

Dados dos processos:
{json.dumps(processes, indent=2, ensure_ascii=False)}

Por favor, forneça uma análise detalhada em português, com foco em aspectos relevantes para análise de risco."""
    
    # Gera a análise usando OpenAI
    analysis = generate_text(prompt)
    
    return analysis

if __name__ == "__main__":
    # Exemplo de uso
    document = "12345678900"  # Substitua pelo número do documento real
    result = analyze_processes(document)
    print(result)