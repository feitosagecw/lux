from openai_utils import get_top_pix_transactions, get_processes_summary, get_basic_summary
import json

def main():
    """Função principal para testar as funções"""
    print("Testando funções de análise de transações PIX...")
    print("-" * 80)
    
    # Teste com ID existente
    id_client = 28133300
    print(f"\nTestando ID: {id_client}")
    result = get_top_pix_transactions(id_client)
    
    if "erro" in result:
        print(f"Erro: {result['erro']}")
    else:
        print("\nResultados encontrados:")
        print(f"Cash In: {result.get('cash_in', 'Não encontrado')}")
        print(f"Cash Out: {result.get('cash_out', 'Não encontrado')}")
        
        # Testar análise BDC para o cash in
        if result.get('cash_in'):
            print("\nAnalisando BDC para Cash In...")
            bdc_result = get_processes_summary(result['cash_in'])
            if "erro" in bdc_result:
                print(f"Erro BDC: {bdc_result['erro']}")
            else:
                print("\nInformações BDC Cash In:")
                print(f"Nome: {bdc_result.get('info_pessoal', {}).get('nome', 'Não encontrado')}")
                print(f"Tipo: {bdc_result.get('info_pessoal', {}).get('tipo_pessoa', 'Não encontrado')}")
                print(f"Documento: {bdc_result.get('info_pessoal', {}).get('documento', 'Não encontrado')}")
                print(f"Nível de Risco: {bdc_result.get('nivel_risco', 'Não encontrado')}")
                print(f"Total Ativos: {bdc_result.get('total_ativos', 0)}")
                print(f"Total Arquivados: {bdc_result.get('total_arquivados', 0)}")
            # Testar resumo básico para o cash in
            print("\nResumo BasicData Cash In:")
            basic_summary = get_basic_summary(result['cash_in'])
            for k, v in basic_summary.items():
                print(f"{k}: {v}")
        
        # Testar análise BDC para o cash out
        if result.get('cash_out'):
            print("\nAnalisando BDC para Cash Out...")
            bdc_result = get_processes_summary(result['cash_out'])
            if "erro" in bdc_result:
                print(f"Erro BDC: {bdc_result['erro']}")
            else:
                print("\nInformações BDC Cash Out:")
                print(f"Nome: {bdc_result.get('info_pessoal', {}).get('nome', 'Não encontrado')}")
                print(f"Tipo: {bdc_result.get('info_pessoal', {}).get('tipo_pessoa', 'Não encontrado')}")
                print(f"Documento: {bdc_result.get('info_pessoal', {}).get('documento', 'Não encontrado')}")
                print(f"Nível de Risco: {bdc_result.get('nivel_risco', 'Não encontrado')}")
                print(f"Total Ativos: {bdc_result.get('total_ativos', 0)}")
                print(f"Total Arquivados: {bdc_result.get('total_arquivados', 0)}")
            # Testar resumo básico para o cash out
            print("\nResumo BasicData Cash Out:")
            basic_summary = get_basic_summary(result['cash_out'])
            for k, v in basic_summary.items():
                print(f"{k}: {v}")
    
    print("\n" + "-" * 80)
    
    # Teste com ID inexistente
    print("\nTestando ID inexistente: 999999")
    result = get_top_pix_transactions(999999)
    print(f"Resultado: {result}")

if __name__ == "__main__":
    main() 