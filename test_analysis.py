import json
from openai_utils import analyze_document, analyze_bdc_data

def main():
    # Documento para teste
    document = "63726238034"
    
    print("Iniciando análise com OpenAI...")
    print("-" * 50)
    
    # Analisa os dados
    analysis = analyze_bdc_data(document)
    
    print(f"Documento utilizado na busca: {document}")
    print("\nAnálise Concluída:")
    print("-" * 50)
    print(analysis)

if __name__ == "__main__":
    main() 