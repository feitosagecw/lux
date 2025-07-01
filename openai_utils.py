import requests
import json
from config import OPENAI_API_KEY, DEFAULT_MODEL
from bdc_utils import analyze_document
from google.cloud import bigquery
from google.auth import default
import unicodedata

# Prompt do sistema para análise jurídica
SYSTEM_PROMPT = (
    "Você é um analista jurídico sênior especializado em avaliação de processos judiciais e sanções administrativas, "
    "com foco na identificação de riscos legais e reputacionais para instituições financeiras. "
    "Seu papel é interpretar dados do BDC (Base de Dados de Clientes) e gerar insights jurídicos estratégicos que auxiliem na tomada de decisão."

    "\n\nSua análise deve considerar, entre outros fatores:"
    "\n1. **Identificação de processos judiciais** ativos e encerrados, com ênfase em ações cíveis, penais, trabalhistas e tributárias relevantes"
    "\n2. **Análise de sanções administrativas e regulatórias**, especialmente aquelas aplicadas por órgãos como BACEN, CVM, Receita Federal, COAF, entre outros"
    "\n3. **Avaliação do risco jurídico**, considerando reincidência, valores envolvidos, natureza da infração e impacto no perfil de risco do cliente"
    "\n4. **Detecção de padrões de litigiosidade**, como frequência de ações, setores envolvidos e relação com a atividade econômica"
    "\n5. **Indicação de possíveis conflitos de interesse** que possam comprometer a integridade da relação comercial"

    "\n\nDiretrizes para sua resposta:"
    "\n- Seja **objetivo, técnico e conciso**, como se estivesse escrevendo para um comitê de compliance ou jurídico"
    "\n- Priorize **informações críticas para avaliação de risco**, evitando redundâncias"
    "\n- Destaque **processos com valores significativos**, natureza grave ou indícios de fraude"
    "\n- Utilize **negrito** para palavras-chave e riscos relevantes"
    "\n- Classifique pontos críticos como [**ALTO RISCO**] quando aplicável"
    "\n- Estruture sua resposta com os seguintes tópicos:"
    "\n   • Perfil jurídico do cliente"
    "\n   • Processos judiciais relevantes"
    "\n   • Sanções administrativas"
    "\n   • Padrões de litigiosidade"
    "\n   • Riscos identificados"
    "\n   • Conflitos de interesse"
    "\n   • Resumo de risco e recomendação final"

    "\n\nCaso não haja processos ou sanções relevantes, informe explicitamente (ex: 'Nenhum processo judicial identificado até a data da análise')."
)

# Prompt do sistema para análise de AML
AML_SYSTEM_PROMPT = (
    "Você é um analista sênior especializado em Prevenção à Lavagem de Dinheiro (AML - Anti-Money Laundering), "
    "com profundo conhecimento em riscos financeiros, regulatórios e comportamentais. Seu papel é atuar como especialista "
    "em análise de risco com base em dados jurídicos, financeiros e transacionais para identificar potenciais esquemas de lavagem de dinheiro. "
    
    "\n\nConsidere os principais pilares da regulação AML, como KYC (Know Your Customer), CDD (Customer Due Diligence), PEP (Pessoas Politicamente Expostas), "
    "relacionamentos com jurisdições de risco, empresas de fachada, transações estruturadas e crimes antecedentes. Use sempre uma abordagem baseada em risco."

    "\n\nSua análise deve contemplar:"
    "\n1. **Avaliação de risco AML** com base em processos judiciais, sanções, histórico e perfil do cliente"
    "\n2. **Identificação de padrões suspeitos**, como transações fracionadas, atípicas, recorrentes ou incompatíveis com o perfil"
    "\n3. **Correlação entre o comportamento transacional e possíveis crimes antecedentes**, como tráfico de drogas, corrupção, evasão de divisas, jogo ilegal, entre outros"
    "\n4. **Recomendações objetivas** para mitigação, como diligência reforçada, bloqueio, reporte ao COAF ou encerramento de relação"
    "\n5. **Parecer final estruturado**, classificando o cliente como 'Adequado', 'Adequado com ressalvas', ou 'Não adequado'"

    "\n\nDiretrizes para a resposta:"
    "\n- Seja **claro, direto e técnico**, como um analista escrevendo para um comitê de risco"
    "\n- Priorize **informações relevantes e críticas** para AML"
    "\n- Use **negrito** para destacar termos-chave e riscos"
    "\n- Classifique pontos críticos com a tag [**ALTO RISCO**]"
    "\n- Estruture sua análise em **tópicos bem definidos**, como:"
    "\n   • Perfil do cliente"
    "\n   • Histórico jurídico e reputacional"
    "\n   • Comportamento transacional"
    "\n   • Riscos identificados"
    "\n   • Recomendações"
    "\n   • Parecer final"

    "\n\nSe houver ausência de dados relevantes, indique explicitamente (ex: 'Não foram identificados processos judiciais', 'Dados de transações indisponíveis')."
)
def extract_lawsuits(result):
    """
    Extrai a lista de processos judiciais do resultado do BDC, independente do formato (pessoa física ou jurídica).
    """
    lawsuits = result.get('Processes', {}).get('Lawsuits', [])
    if not lawsuits:
        lawsuits = result.get('Lawsuits', {}).get('Lawsuits', [])
        if not lawsuits and isinstance(result.get('Lawsuits', []), list):
            lawsuits = result.get('Lawsuits', [])
    return lawsuits

def analyze_bdc_data(document: str, context: str = None) -> dict:
    """
    Analisa os dados do BDC para um documento específico, focando em sanções e processos judiciais.
    
    Args:
        document (str): Número do documento a ser analisado
        context (str, optional): Contexto específico para a análise
        
    Returns:
        dict: Dados processados do BDC ou None em caso de erro
    """
    try:
        # Buscar dados do BDC diretamente da função do bdc_utils
        from bdc_utils import analyze_document as bdc_analyze
        bdc_data = bdc_analyze(document)
        
        if not bdc_data or not bdc_data.get('Result'):
            return None
            
        # Extrair informações do primeiro resultado
        result = bdc_data['Result'][0]
        basic_data = result.get('BasicData', {})
        # Ajuste: para empresas, usar OfficialName ou TradeName
        name = basic_data.get('Name') or basic_data.get('OfficialName') or basic_data.get('TradeName') or ''
        kyc_data = result.get('KycData', {})
        lawsuits = extract_lawsuits(result)
        
        # Preparar dados dos processos
        active_processes = []
        archived_processes = []
        
        # Processar processos
        for process in lawsuits:
            process_info = {
                'number': process.get('Number', ''),
                'type': process.get('Type', ''),
                'value': process.get('Value', 0),
                'status': process.get('Status', ''),
                'location': f"{process.get('CourtDistrict', '')}, {process.get('State', '')}",
                'nature': process.get('MainSubject', ''),
                'parties': [p.get('Name', '') for p in process.get('Parties', [])],
                'last_movement': process.get('LastMovementDate', ''),
                'updates': [u.get('Content', '') for u in process.get('Updates', [])]
            }
            
            if 'arquiv' in process_info['status'].lower() or 'encerr' in process_info['status'].lower() or 'baixado' in process_info['status'].lower():
                archived_processes.append(process_info)
            else:
                active_processes.append(process_info)
        
        # Processar sanções
        sanctions = []
        for sanction in kyc_data.get('SanctionsHistory', []):
            details = sanction.get('Details', {})
            sanction_info = {
                'type': sanction.get('StandardizedSanctionType', sanction.get('Type', '')),
                'description': details.get('WarrantDescription', ''),
                'date': sanction.get('StartDate', ''),
                'status': details.get('Status', ''),
                'agency': details.get('Agency', ''),
                'state': details.get('State', ''),
                'magistrate': details.get('Magistrate', ''),
                'warrant_number': details.get('ArrestWarrantNumber', ''),
                'process_number': details.get('ProcessNumber', ''),
                'expiration_date': details.get('StandardizedExpirationDate', ''),
                'imprisonment_kind': details.get('ImprisonmentKind', '')
            }
            sanctions.append(sanction_info)
        
        # Preparar resultado final
        analysis_result = {
            'name': name,
            'document': document,
            'active_processes': active_processes,
            'archived_processes': archived_processes,
            'sanctions': sanctions,
            'total_active_processes': len(active_processes),
            'total_archived_processes': len(archived_processes),
            'total_sanctions': len(sanctions)
        }
        
        return analysis_result
        
    except Exception as e:
        print(f"Erro ao analisar dados do BDC: {str(e)}")
        return None

def analyze_bdc_data_old(document_number: str) -> dict:
    """
    Analisa os dados do Big Data Corp para um documento específico.
    
    Args:
        document_number (str): Número do documento (CPF/CNPJ)
        
    Returns:
        dict: Dados brutos do BDC ou None em caso de erro
    """
    try:
        # Busca dados no Big Data Corp
        from bdc_utils import analyze_document as bdc_analyze
        bdc_data = bdc_analyze(document_number)
        
        if not bdc_data:
            return None
            
        return bdc_data
        
    except Exception as e:
        print(f"Erro ao analisar dados do BDC: {str(e)}")
        return None

def get_top_pix_transactions(id_cliente: str) -> dict:
    """
    Busca o top 5 party_document_number de Cash In e Cash Out, mas retorna apenas os 2 primeiros document numbers distintos de cada, sem repetição entre cash_in e cash_out.
    
    Args:
        id_cliente (str): ID do cliente obtido do DataFrame df_user['id_cliente']
        
    Returns:
        dict: Dicionário com os documentos do top 2 Cash In e Cash Out (listas, sem repetição entre si)
    """
    try:
        client = bigquery.Client()
        query = f"""
        SELECT 
            party_document_number,
            pix_amount,
            transaction_type
        FROM `infinitepay-production.metrics_amlft.pix_concentration`
        WHERE user_id = {id_cliente}
        """
        df = client.query(query).to_dataframe()
        if df.empty:
            return {"cash_in": [], "cash_out": []}
        
        # Top 5 Cash In
        cash_in = df[df['transaction_type'] == 'Cash In']
        top_in = cash_in.sort_values('pix_amount', ascending=False).head(5)
        # Top 5 Cash Out
        cash_out = df[df['transaction_type'] == 'Cash Out']
        top_out = cash_out.sort_values('pix_amount', ascending=False).head(5)
        
        # Selecionar até 2 document numbers distintos para Cash In
        unique_in = []
        seen = set()
        for doc in top_in['party_document_number']:
            if doc not in seen:
                unique_in.append(doc)
                seen.add(doc)
            if len(unique_in) == 2:
                break
        
        # Selecionar até 2 document numbers distintos para Cash Out, sem repetir os de Cash In
        unique_out = []
        for doc in top_out['party_document_number']:
            if doc not in seen:
                unique_out.append(doc)
                seen.add(doc)
            if len(unique_out) == 2:
                break
        
        return {
            "cash_in": unique_in,
            "cash_out": unique_out
        }
    except Exception as e:
        return {"erro": f"Erro ao buscar transações PIX: {str(e)}"}

def analyze_document(document_number: str, prompt: str = None) -> dict:
    """
    Analisa um documento no BDC usando a API do OpenAI.
    
    Args:
        document_number (str): Número do documento a ser analisado
        prompt (str, optional): Prompt personalizado para a análise
        
    Returns:
        dict: Dados brutos do BDC ou None em caso de erro
    """
    try:
        # Buscar dados do BDC
        bdc_data = analyze_bdc_data(document_number)
        
        if not bdc_data:
            return None
            
        # Se houver prompt personalizado, gerar análise formatada
        if prompt:
            # Configurar a chamada para a API do OpenAI
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            }
            
            data = {
                "model": "gpt-4-turbo-preview",
                "messages": [
                    {"role": "system", "content": "Você é um assistente que fornece resumos simples e diretos."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 500
            }
            
            # Fazer a chamada para a API
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            # Verificar se a chamada foi bem sucedida
            response.raise_for_status()
            
            # Retornar a análise formatada
            return response.json()["choices"][0]["message"]["content"]
        
        # Se não houver prompt, retornar os dados brutos
        return bdc_data
        
    except Exception as e:
        print(f"Erro ao analisar documento: {str(e)}")
        return None

def get_processes_summary(document_number: str) -> dict:
    """
    Retorna um resumo detalhado dos processos judiciais de um documento.
    
    Args:
        document_number (str): Número do documento (CPF/CNPJ)
    
    Returns:
        dict: Resumo detalhado dos processos
    """
    try:
        from bdc_utils import analyze_document as bdc_analyze
        bdc_data = bdc_analyze(document_number)
        
        if not bdc_data or not bdc_data.get('Result'):
            return {"erro": "Não foram encontrados dados do BDC para este documento."}
            
        result = bdc_data['Result'][0]
        
        # Informações pessoais
        personal_info = {
            "nome": result.get('Name', 'Não encontrado'),
            "tipo_pessoa": "Pessoa Física" if len(document_number) == 11 else "Pessoa Jurídica",
            "documento": document_number
        }
        
        lawsuits = extract_lawsuits(result)
        
        if not lawsuits:
            return {
                "info_pessoal": personal_info,
                "total_ativos": 0,
                "total_arquivados": 0,
                "tipos_principais": [],
                "status_predominante": "Nenhum processo encontrado",
                "nivel_risco": "BAIXO",
                "processos_detalhados": []
            }
            
        total_ativos = 0
        total_arquivados = 0
        tipos = {}
        status = {}
        processo_criminal = False
        processos_detalhados = []
        
        for proc in lawsuits:
            st = proc.get('Status', '').lower()
            tipo = proc.get('Type', 'Desconhecido')
            natureza = proc.get('MainSubject', '')
            tribunal = proc.get('Court', 'Não informado')
            numero_processo = proc.get('Number', 'Não informado')
            data_processo = proc.get('Date', 'Não informada')
            
            # Normalizar tipo e natureza para comparação
            def normalize(text):
                return unicodedata.normalize('NFKD', text.lower()).encode('ASCII', 'ignore').decode('ASCII')
            tipo_norm = normalize(tipo)
            natureza_norm = normalize(natureza)
            
            # Contagem de ativos/arquivados
            if 'arquiv' in st or 'encerr' in st or 'baixado' in st:
                total_arquivados += 1
            else:
                total_ativos += 1
                
            # Tipos
            key_tipo = natureza if natureza else tipo
            tipos[key_tipo] = tipos.get(key_tipo, 0) + 1
            
            # Status
            status[st] = status.get(st, 0) + 1
            
            # Verificar se é processo criminal
            termos_criminais = ['criminal', 'crime', 'roubo', 'penal','trafico', 'drogas', 'homicidio', 'sequestro', 'receptacao']
            if any(termo in tipo_norm or termo in natureza_norm for termo in termos_criminais):
                processo_criminal = True
            
            # Detalhes do processo
            processo_detalhado = {
                "numero": numero_processo,
                "tipo": tipo,
                "natureza": natureza,
                "tribunal": tribunal,
                "status": st,
                "data": data_processo
            }
            processos_detalhados.append(processo_detalhado)
                
        # Principais tipos
        tipos_principais = sorted(tipos, key=tipos.get, reverse=True)[:3]
        
        # Status predominante
        status_pred = max(status, key=status.get) if status else "Desconhecido"
        
        # Nível de risco
        nivel_risco = "ALTO" if processo_criminal else ("MÉDIO" if total_ativos > 0 else "BAIXO")
        
        resumo = {
            "info_pessoal": personal_info,
            "total_ativos": total_ativos,
            "total_arquivados": total_arquivados,
            "tipos_principais": tipos_principais,
            "status_predominante": status_pred,
            "nivel_risco": nivel_risco,
            "processos_detalhados": processos_detalhados
        }
        
        if processo_criminal:
            resumo["destaque"] = "[ALTO RISCO] Processo criminal identificado."
            
        return resumo
        
    except Exception as e:
        return {"erro": f"Erro ao resumir processos: {str(e)}"}

def get_basic_summary(document_number: str) -> dict:
    """
    Retorna um resumo das informações básicas (BasicData) do BDC para um documento.
    Args:
        document_number (str): Número do documento (CPF/CNPJ)
    Returns:
        dict: Resumo das informações básicas (apenas nome e documento)
    """
    try:
        from bdc_utils import analyze_document as bdc_analyze
        bdc_data = bdc_analyze(document_number)
        if not bdc_data or not bdc_data.get('Result'):
            return {"erro": "Não foram encontrados dados do BDC para este documento."}
        result = bdc_data['Result'][0]
        basic = result.get('BasicData', {})
        # Ajuste: para empresas, usar OfficialName ou TradeName
        nome = basic.get('Name') or basic.get('OfficialName') or basic.get('TradeName') or 'Não encontrado'
        resumo = {
            "nome": nome,
            "documento": document_number
        }
        return resumo
    except Exception as e:
        return {"erro": f"Erro ao resumir dados básicos: {str(e)}"}

def get_kyc_summary(document_number: str) -> dict:
    """
    Retorna um resumo das informações de KYC e sanções do dataset KYC do BDC para um documento.
    """
    try:
        from bdc_utils import analyze_document as bdc_analyze
        bdc_data = bdc_analyze(document_number)
        if not bdc_data or not bdc_data.get('Result'):
            return {"erro": "Não foram encontrados dados do BDC para este documento."}
        result = bdc_data['Result'][0]
        kyc = result.get('KycData', {})

        # Nome e nascimento
        nome = None
        nascimento = None
        if kyc.get('SanctionsHistory') and len(kyc['SanctionsHistory']) > 0:
            nome = kyc['SanctionsHistory'][0]['Details'].get('NameInSanctionList')
            nascimento = kyc['SanctionsHistory'][0]['Details'].get('BirthDate')
        if not nome:
            nome = kyc.get('Name', 'Não encontrado')
        if not nascimento:
            nascimento = kyc.get('BirthDate', 'Não encontrado')

        # Sanções
        sancoes = []
        for s in kyc.get('SanctionsHistory', []):
            details = s.get('Details', {})
            sancoes.append({
                "tipo": s.get('StandardizedSanctionType', s.get('Type', 'Não informado')),
                "status": details.get('Status', 'Não informado'),
                "estado": details.get('State', 'Não informado'),
                "agencia": details.get('Agency', 'Não informado'),
                "magistrado": details.get('Magistrate', 'Não informado'),
                "numero_mandado": details.get('ArrestWarrantNumber', 'Não informado'),
                "numero_processo": details.get('ProcessNumber', 'Não informado'),
                "data_expiracao": details.get('StandardizedExpirationDate', ''),
                "data_inicio": s.get('StartDate', ''),
                "descricao": details.get('WarrantDescription', ''),
                "imprisonment_kind": details.get('ImprisonmentKind', ''),
            })

        resumo = {
            "nome": nome,
            "documento": document_number,
            "data_nascimento": nascimento,
            "is_pep": kyc.get('IsCurrentlyPEP', False),
            "is_sancionado": kyc.get('IsCurrentlySanctioned', False),
            "sanctions_count": len(sancoes),
            "sanctions": sancoes
        }
        return resumo
    except Exception as e:
        return {"erro": f"Erro ao resumir dados KYC: {str(e)}"}

def get_detailed_analysis(document_number: str) -> dict:
    """
    Retorna uma análise detalhada de sanções e processos para um documento.
    
    Args:
        document_number (str): Número do documento (CPF/CNPJ)
        
    Returns:
        dict: Análise detalhada com informações de sanções e processos
    """
    try:
        # Buscar dados do BDC
        bdc_data = analyze_bdc_data(document_number)
        
        if not bdc_data:
            return {"erro": "Não foram encontrados dados do BDC para este documento."}
            
        # Preparar resultado
        result = {
            "informacoes_basicas": {
                "nome": bdc_data.get('name', 'Não encontrado'),
                "documento": document_number,
                "tipo_pessoa": "Pessoa Física" if len(document_number) == 11 else "Pessoa Jurídica"
            },
            "resumo_processos": {
                "total_ativos": bdc_data.get('total_active_processes', 0),
                "total_arquivados": bdc_data.get('total_archived_processes', 0),
                "processos_ativos": bdc_data.get('active_processes', []),
                "processos_arquivados": bdc_data.get('archived_processes', [])
            },
            "resumo_sancoes": {
                "total_sancoes": bdc_data.get('total_sanctions', 0),
                "sancoes_detalhadas": bdc_data.get('sanctions', []),
                "nivel_risco": "ALTO" if bdc_data.get('total_sanctions', 0) > 0 else "BAIXO"
            }
        }
        
        # Adicionar análise de risco
        if result["resumo_sancoes"]["total_sancoes"] > 0:
            result["resumo_sancoes"]["analise_risco"] = {
                "nivel": "ALTO",
                "justificativa": "Presença de sanções ativas",
                "recomendacao": "Revisão detalhada recomendada"
            }
        elif result["resumo_processos"]["total_ativos"] > 0:
            result["resumo_sancoes"]["analise_risco"] = {
                "nivel": "MÉDIO",
                "justificativa": "Presença de processos ativos",
                "recomendacao": "Monitoramento recomendado"
            }
        else:
            result["resumo_sancoes"]["analise_risco"] = {
                "nivel": "BAIXO",
                "justificativa": "Sem sanções ou processos ativos",
                "recomendacao": "Risco aceitável"
            }
            
        return result
        
    except Exception as e:
        return {"erro": f"Erro ao gerar análise detalhada: {str(e)}"} 