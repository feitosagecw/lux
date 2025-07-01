import streamlit as st
import pandas as pd
import time
from google.cloud import bigquery
from google.auth import default
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from pathlib import Path
import os
from src.sql_manager import SQLManager
from openai_utils import analyze_bdc_data, get_top_pix_transactions, analyze_document, get_processes_summary, get_basic_summary, get_kyc_summary
import gc

# Inicializar o gerenciador de SQL
sql_manager = SQLManager()

# Definir o project_id do BigQuery
project_id = "infinitepay-production"

# Configuração da página
st.set_page_config(
    page_title="Lux on Analysis",
    page_icon="src/images/stars_icon_shapes_v2/solid/10.png",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

# Definir o tema como light
st.markdown("""
    <style>
    /* Definir o tema como light */
    :root {
        --background-color: #ffffff;
        --text-color: #1e293b;
    }
    
    /* Forçar tema light */
    .stApp {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    
    /* Forçar tema light no sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #f8fafc, #ffffff) !important;
        color: #1e293b !important;
    }
    
    /* Estilo para o sidebar com gradiente off-white para branco */
    [data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #f8fafc, #ffffff);
        padding: 2rem 1.5rem;
        border-right: 1px solid rgba(226, 232, 240, 0.5);
        overflow: hidden;
        height: 100vh;
        position: fixed;
        width: 350px !important; /* Aumentado de 300px para 350px */
    }
    
    /* Remover barra de rolagem do sidebar */
    [data-testid="stSidebar"] > div {
        overflow: hidden !important;
    }
    
    /* Remover barra de rolagem do conteúdo do sidebar */
    [data-testid="stSidebar"] > div > div {
        overflow: hidden !important;
    }
    
    /* Estilo para a barra de progresso */
    div[data-testid="stProgress"] > div > div {
        background-color: #1e293b !important;
        border-radius: 4px !important;
    }
    
    /* Ajuste das cores do texto no sidebar para melhor contraste */
    [data-testid="stSidebar"] [data-testid="stMarkdown"] {
        color: #1e293b !important;
    }
    
    /* Estilo para o título no sidebar */
    [data-testid="stSidebar"] h1 {
        color: #1e293b !important;
        text-shadow: none;
    }
    
    /* Estilo para labels no sidebar */
    [data-testid="stSidebar"] label {
        color: #1e293b !important;
    }
    
    /* Estilo para o input de texto no sidebar */
    [data-testid="stTextInput"] input {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        font-size: 0.9em !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stTextInput"] input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
        outline: none !important;
    }
    
    [data-testid="stTextInput"] input::placeholder {
        color: #94a3b8 !important;
        font-size: 0.9em !important;
    }
    
    /* Estilo para o expander no sidebar */
    [data-testid="stExpander"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    /* Estilo para os checkboxes no sidebar */
    [data-testid="stCheckbox"] {
        color: #1e293b !important;
    }
    
    /* Estilo para o botão no sidebar */
    .stButton > button {
        background: linear-gradient(135deg, #1e293b, #334155) !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 0.75rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.8em !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #0f172a, #1e293b) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Estilo para o texto do expander no sidebar */
    [data-testid="stExpander"] [data-testid="stMarkdown"] {
        color: #1e293b !important;
    }
    
    /* Estilo para o texto do checkbox no sidebar */
    [data-testid="stCheckbox"] [data-testid="stMarkdown"] {
        color: #1e293b !important;
    }
    
    /* Estilo para o texto do radio no sidebar */
    [data-testid="stRadio"] [data-testid="stMarkdown"] {
        color: #1e293b !important;
    }
    
    /* Estilo para o texto do selectbox no sidebar */
    [data-testid="stSelectbox"] [data-testid="stMarkdown"] {
        color: #1e293b !important;
    }
    
    /* Estilo para o texto do text input no sidebar */
    [data-testid="stTextInput"] [data-testid="stMarkdown"] {
        color: #1e293b !important;
    }
    
    /* Estilo para o texto do button no sidebar */
    [data-testid="stButton"] [data-testid="stMarkdown"] {
        color: #1e293b !important;
    }
    
    /* Estilo para o texto do divider no sidebar */
    [data-testid="stDivider"] [data-testid="stMarkdown"] {
        color: #1e293b !important;
    }
    
    /* Estilo para o texto do expander header no sidebar */
    .streamlit-expanderHeader {
        color: #1e293b !important;
    }
    
    /* Estilo específico para o título do expander "Filtro de Transações" */
    div[data-testid="stExpander"] > div > div > div > span {
        color: #1e293b !important;
    }
    
    /* Estilo específico para o título do expander "Filtro de Transações" */
    .streamlit-expanderHeader {
        color: #1e293b !important;
    }
    
    /* Estilo específico para o título do expander "Filtro de Transações" */
    .streamlit-expanderHeader p {
        color: #1e293b !important;
    }
    
    /* Estilo específico para o título do expander "Filtro de Transações" */
    .streamlit-expanderHeader div {
        color: #1e293b !important;
    }
    
    /* Estilo para o texto do expander content no sidebar */
    [data-testid="stExpander"] .streamlit-expanderContent {
        background-color: #ffffff !important;
    }
    
    /* Estilo para o texto do checkbox label no sidebar */
    [data-testid="stCheckbox"] .stCheckbox {
        color: #1e293b !important;
    }
    
    /* Estilo para o texto do radio label no sidebar */
    [data-testid="stRadio"] .stRadio {
        color: #1e293b !important;
    }
    
    /* Estilo para o texto do selectbox label no sidebar */
    [data-testid="stSelectbox"] .stSelectbox {
        color: #1e293b !important;
    }
    
    /* Estilo para o texto do text input label no sidebar */
    [data-testid="stTextInput"] .stTextInput {
        color: #1e293b !important;
    }
    
    /* Estilo para o texto do button label no sidebar */
    [data-testid="stButton"] .stButton {
        color: #1e293b !important;
    }
    
    /* Estilo para o texto do divider label no sidebar */
    [data-testid="stDivider"] .stDivider {
        color: #1e293b !important;
    }
    
    /* Estilo para o texto do expander content no sidebar - segunda coluna */
    [data-testid="stExpander"] .streamlit-expanderContent {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    
    /* Estilo para o texto do checkbox label no sidebar - segunda coluna */
    [data-testid="stCheckbox"] .stCheckbox {
        color: #1e293b !important;
    }
    
    /* Estilo para o texto do radio label no sidebar - segunda coluna */
    [data-testid="stRadio"] .stRadio {
        color: #1e293b !important;
    }
    
    /* Estilo para o texto do selectbox label no sidebar - segunda coluna */
    [data-testid="stSelectbox"] .stSelectbox {
        color: #1e293b !important;
    }
    
    /* Estilo para o texto do text input label no sidebar - segunda coluna */
    [data-testid="stTextInput"] .stTextInput {
        color: #1e293b !important;
    }
    
    /* Estilo para o texto do button label no sidebar - segunda coluna */
    [data-testid="stButton"] .stButton {
        color: #1e293b !important;
    }
    
    /* Estilo para o texto do divider label no sidebar - segunda coluna */
    [data-testid="stDivider"] .stDivider {
        color: #1e293b !important;
    }
    
    /* Fundo com gradiente mais suave e moderno */
    body {
        background: linear-gradient(135deg, #f8fafc, #e2e8f0);
        font-family: 'Inter', sans-serif;
        color: #1e293b;
    }
    
    /* Títulos com efeito mais moderno */
    .title {
        font-size: 3.2em;
        font-weight: 800;
        color: #1e293b;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        margin-bottom: 30px;
        letter-spacing: -0.5px;
    }

    .title:hover {
        transform: translateY(-2px);
        text-shadow: 3px 3px 6px rgba(0,0,0,0.15);
    }

    .subheader {
        font-size: 2em;
        font-weight: 600;
        color: #334155;
        margin-bottom: 1em;
        letter-spacing: -0.3px;
    }

    /* Mensagens com ícones e cores mais suaves */
    .st-success { 
        color: #059669; 
        font-weight: 600;
        padding: 12px;
        border-radius: 8px;
        background-color: #ecfdf5;
    }
    
    .st-error { 
        color: #dc2626; 
        font-weight: 600;
        padding: 12px;
        border-radius: 8px;
        background-color: #fef2f2;
    }
    
    .st-warning { 
        color: #d97706; 
        font-weight: 600;
        padding: 12px;
        border-radius: 8px;
        background-color: #fffbeb;
    }

    /* Tabelas mais modernas */
    .css-1oe6wyx, .css-1oe6wyx table {
        border-collapse: separate;
        border-spacing: 0;
        width: 100%;
        font-size: 0.95em;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        overflow: hidden;
    }

    .css-1oe6wyx th, .css-1oe6wyx td {
        border: none;
        padding: 16px;
        text-align: left;
    }

    .css-1oe6wyx th {
        background-color: #3b82f6;
        color: white;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.85em;
        letter-spacing: 0.5px;
    }

    .css-1oe6wyx tr:nth-child(even) {
        background-color: #f8fafc;
    }

    .css-1oe6wyx tr:hover {
        background-color: #f1f5f9;
    }

    /* Cards de dados mais modernos */
    .dataframe {
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        overflow: hidden;
    }

    /* Gráficos mais modernos */
    .js-plotly-plot {
        border-radius: 12px !important;
    }

    /* Estilo para os elementos não selecionados no multiselect */
    .stMultiSelect [data-baseweb="select"] {
        font-size: 0.65em !important;
    }
    
    /* Estilo para as opções do dropdown */
    .stMultiSelect [data-baseweb="option"] {
        font-size: 0.65em !important;
    }
    
    /* Estilo para os elementos selecionados no multiselect */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #1e293b !important;
        color: white !important;
        border-radius: 6px !important;
        padding: 4px 8px !important;
        margin: 2px !important;
        font-size: 1.05em !important;
        font-weight: 500 !important;
    }

    .stMultiSelect [data-baseweb="tag"]:hover {
        background-color: #334155 !important;
    }

    /* Estilo para o botão de remover do tag */
    .stMultiSelect [data-baseweb="tag"] button {
        color: white !important;
    }

    /* Estilo para o conteúdo principal */
    .main .block-container {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        line-height: 1.6;
        color: #1e293b;
    }

    /* Estilo para títulos */
    .main h1, .main h2, .main h3, .main h4 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 1rem;
        letter-spacing: -0.025em;
    }

    .main h1 {
        font-size: 2.5rem;
        font-weight: 700;
    }

    .main h2 {
        font-size: 2rem;
        font-weight: 600;
    }

    .main h3 {
        font-size: 1.5rem;
        font-weight: 600;
    }

    .main h4 {
        font-size: 1.25rem;
        font-weight: 500;
    }

    /* Estilo para parágrafos */
    .main p {
        font-size: 1rem;
        line-height: 1.7;
        color: #334155;
        margin-bottom: 1rem;
    }

    /* Estilo para tabelas */
    .main .dataframe {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    .main .dataframe th {
        font-weight: 600;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .main .dataframe td {
        font-size: 0.95rem;
        color: #334155;
    }

    /* Estilo para métricas */
    .main .stMetric {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    .main .stMetric label {
        font-size: 0.9rem;
        font-weight: 500;
        color: #475569;
    }

    .main .stMetric div {
        font-size: 1.5rem;
        font-weight: 600;
        color: #0f172a;
    }

    /* Estilo para alertas e mensagens */
    .main .stAlert {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* Estilo para gráficos */
    .main .js-plotly-plot {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Estilo para cards e containers */
    .main .stMarkdown > div {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Estilo para listas */
    .main ul, .main ol {
        font-size: 1rem;
        line-height: 1.7;
        color: #334155;
        margin-bottom: 1rem;
    }

    .main li {
        margin-bottom: 0.5rem;
    }

    /* Estilo para links */
    .main a {
        color: #2563eb;
        text-decoration: none;
        font-weight: 500;
    }

    .main a:hover {
        text-decoration: underline;
    }

    /* Estilo para código */
    .main code {
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.9rem;
        background-color: #f1f5f9;
        padding: 0.2em 0.4em;
        border-radius: 4px;
    }

    /* Estilo para blocos de código */
    .main pre {
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.9rem;
        line-height: 1.6;
        background-color: #f8fafc;
        border-radius: 8px;
        padding: 1rem;
    }

    /* Estilo para tooltips */
    .main .tooltip {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 0.9rem;
    }

    /* Estilo para botões */
    .main .stButton > button {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: 500;
        font-size: 0.95rem;
    }

    /* Estilo para inputs */
    .main .stTextInput > div > div > input {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 0.95rem;
    }

    /* Estilo para selects */
    .main .stSelectbox > div > div > select {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 0.95rem;
    }

    /* Estilo para checkboxes */
    .main .stCheckbox > div > label {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 0.95rem;
    }

    /* Estilo para radio buttons */
    .main .stRadio > div > label {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 0.95rem;
    }

    /* Estilo para expanders */
    .main .streamlit-expanderHeader {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: 500;
        font-size: 1rem;
    }

    /* Estilo para dividers */
    .main .stDivider {
        margin: 2rem 0;
    }

    /* Estilo para progress bars */
    .main .stProgress > div > div {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Estilo para multiselect */
    .main .stMultiSelect > div > div > div {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 0.95rem;
    }

    /* Estilo para tooltips de gráficos */
    .main .plotly-graph-div .hovertext {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 0.9rem;
    }

    /* Estilo para legendas de gráficos */
    .main .plotly-graph-div .legend {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 0.9rem;
    }

    /* Estilo para eixos de gráficos */
    .main .plotly-graph-div .xtitle, .main .plotly-graph-div .ytitle {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 0.9rem;
        font-weight: 500;
    }

    /* Estilo para tooltips de gráficos */
    .main .plotly-graph-div .hovertext {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 0.9rem;
    }

    /* Estilo para tooltips de gráficos */
    .main .plotly-graph-div .hovertext {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 0.9rem;
    }

    /* Estilo para tooltips de gráficos */
    .main .plotly-graph-div .hovertext {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Funções de formatação
def format_float(x):
    """Formata um número float para o padrão brasileiro."""
    try:
        return f"{x:,.2f}".replace(",", "temp").replace(".", ",").replace("temp", ".")
    except Exception:
        return x

def format_brl(x):
    """Formata um número para o padrão monetário brasileiro."""
    try:
        return f"R$ {x:,.2f}".replace(",", "temp").replace(".", ",").replace("temp", ".")
    except Exception:
        return x

def format_percent(x):
    """Formata um número para o padrão percentual brasileiro."""
    try:
        return f"{x:,.2f}%".replace(",", "temp").replace(".", ",").replace("temp", ".")
    except Exception:
        return x

def convert_brl_to_float(value):
    """Converte um valor monetário em formato brasileiro para float."""
    try:
        return float(str(value).replace('R$ ', '').replace('.', '').replace(',', '.'))
    except:
        return 0.0

def clean_session_state():
    """Limpa os dados armazenados no session_state após a conclusão da análise."""
    keys_to_clean = [
        'dataset',
        'df_contact_info',
        'df_card_transactions',
        'client_info',
        'df_blocked',
        'blocked_summary',
        'top_cash_in',
        'top_cash_out'
    ]
    for key in keys_to_clean:
        if key in st.session_state:
            del st.session_state[key]
    
    # Limpar variáveis de controle
    if 'should_analyze' in st.session_state:
        st.session_state.should_analyze = False
    if 'analysis_done' in st.session_state:
        st.session_state.analysis_done = False

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

def clean_temp_files():
    """Limpa arquivos temporários e cache."""
    try:
        # Limpar cache do Streamlit
        cache_dir = Path.home() / '.streamlit' / 'cache'
        if cache_dir.exists():
            for file in cache_dir.glob('*'):
                try:
                    file.unlink()
                except Exception as e:
                    print(f"Erro ao deletar {file}: {e}")
        
        # Limpar arquivos temporários do BigQuery
        temp_dir = Path.home() / '.bigquery' / 'temp'
        if temp_dir.exists():
            for file in temp_dir.glob('*'):
                try:
                    file.unlink()
                except Exception as e:
                    print(f"Erro ao deletar {file}: {e}")
        
        # Limpar arquivos temporários do pandas
        temp_dir = Path.home() / '.pandas' / 'temp'
        if temp_dir.exists():
            for file in temp_dir.glob('*'):
                try:
                    file.unlink()
                except Exception as e:
                    print(f"Erro ao deletar {file}: {e}")
        
        return True
    except Exception as e:
        print(f"Erro ao limpar arquivos temporários: {e}")
        return False

# Inicializar variáveis do session_state se não existirem
if 'search_term' not in st.session_state:
    st.session_state.search_term = ""
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'sort_input_sidebar' not in st.session_state:
    st.session_state.sort_input_sidebar = "Valor Pix (num)"
if 'show_pep' not in st.session_state:
    st.session_state.show_pep = False
if 'show_corporate_cards' not in st.session_state:
    st.session_state.show_corporate_cards = False

# Inicializar o session_state para o dataset se não existir
if 'dataset' not in st.session_state:
    st.session_state.dataset = None

# Menu Sidebar
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; margin-bottom: 30px;'>
            <h1 style='color: #1e293b; font-size: 2.2em;'>
                <span style='font-weight: 800;'>LUX</span> 
                <span style='font-weight: 400; text-shadow: 1px 1px 2px rgba(0,0,0,0.1); color: #991b1b;'>ANALYSIS</span>
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Campo de entrada para o ID do Cliente com ícone e placeholder
    st.markdown("""
        <div class="filter-container" style="margin-bottom: -70px;">
            <h3 class="filter-title">ID do Cliente</h3>
            <div class="filter-content">
    """, unsafe_allow_html=True)
    
    id_cliente_str = st.text_input("", placeholder="Digite o ID para análise", key="id_cliente_input", on_change=lambda: st.session_state.update({"should_analyze": True}))
    
    st.markdown("""
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Adicionar espaçamento antes do expander
    st.markdown("<div style='height: -35px;'></div>", unsafe_allow_html=True)
    
    # Filtro de transações
    st.markdown("""
        <div class="filter-container">
            <h3 class="filter-title">Filtro de Transações</h3>
            <div class="filter-content">
    """, unsafe_allow_html=True)
    
    # Opções para o filtro
    options = [
        "PIX",
        "Acquiring",
        "Cartões Corporativos",
        "GAFI",
        "Internacionais",
        "Issuing",
        "PEP",
        "TED"
    ]
    
    # Componente multiselect com estilo personalizado
    selected_options = st.multiselect(
        "Selecione os tipos de transação",
        options=options,
        default=["PIX", "Acquiring"],  # Definindo PIX e Acquiring como padrão
        key="transaction_filter"
    )
    
    # Atualizar o session_state com base nas opções selecionadas
    st.session_state.show_pep = "PEP" in selected_options
    st.session_state.show_corporate_cards = "Cartões Corporativos" in selected_options
    
    st.markdown("""
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Adicionar espaçamento antes do botão
    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
    
    # Botão de análise no sidebar
    if st.button("Analisar", key="analyze_button", use_container_width=True) or st.session_state.get("should_analyze", False):
        if id_cliente_str:
            try:
                st.session_state.id_client = int(id_cliente_str)
                st.session_state.should_analyze = True
            except ValueError:
                st.error("❌ Por favor, insira um ID numérico válido.")
        else:
            st.warning("Por favor, insira um ID do cliente.")
    
    # Se a análise já foi feita, mostrar os filtros
    if 'analysis_done' in st.session_state and st.session_state.analysis_done:
        st.markdown("""
            <div style='color: #1e293b; margin-bottom: 15px;'>
                <h4>🔍 Filtros</h4>
            </div>
        """, unsafe_allow_html=True)

# Título com ícone e subtítulo mais informativo
# Obtém a hora atual
hora_atual = datetime.now().hour

# Define a saudação conforme a hora
if hora_atual < 12:
    saudacao = "Bom dia!"
elif hora_atual < 18:
    saudacao = "Boa tarde!"
else:
    saudacao = "Boa noite!"

# Exibe a saudação usando markdown
st.markdown(f"<div class='subheader'>{saudacao}</div>", unsafe_allow_html=True)

# Adicionar uma descrição mais detalhada
st.markdown("""
    <div style='background-color: #f8fafc; padding: 20px; border-radius: 12px; margin-bottom: 30px;'>
        <h3 style='color: #1e293b; margin-bottom: 10px;'>ℹ︎ Sobre a Análise</h3>
        <p style='color:rgb(40, 48, 60); line-height: 1.6;'>
            Esta ferramenta permite analisar detalhadamente as transações de um cliente, incluindo:
        </p>
        <ul style='color: #475569; line-height: 1.6;'>
            <li>Concentração de transações PIX</li>
            <li>Análise de transações em horários atípicos</li>
            <li>Transações com cartões</li>
            <li>Identificação de padrões suspeitos e outras informações relevantes</li>
        <p style='color:rgb(80, 05, 50); line-height: 2.6;'>
            <b>Para analisar transações específicas como TED, GAFI, PEP e etc, é necessário selecionar o filtro correspondente.
        </p>
    </div>
""", unsafe_allow_html=True)

# Se a análise foi solicitada, executar
if 'should_analyze' in st.session_state and st.session_state.should_analyze:
    id_client = st.session_state.id_client
    st.info(f"Iniciando análise para o cliente: {id_client} 🔎")
    
    # Substituir a barra de progresso pelo spinner
    with st.spinner("Analisando dados...", show_time=True):
        time.sleep(5)
            
    # Conectar ao BigQuery
    creds, _ = default()
    client = bigquery.Client(project="infinitepay-production")
            
    # Consulta informações do cliente
    try:
        query_user = sql_manager.get_user_info_sql(id_client)
        query_job = client.query(query_user)
        df_user = query_job.result().to_dataframe()
        st.success("Consulta de informações do cliente concluída com sucesso! ✅")
    except Exception as e:
        st.error(f"Erro ao executar a consulta de informações do cliente: {e}")
        df_user = None

    if df_user is not None and not df_user.empty:
        try:
            # Extrair informações do cliente
            client_id = df_user.iloc[0]['id_cliente']
            client_name = df_user.iloc[0]['nome']
            client_email = df_user.iloc[0]['email']
            client_age = df_user.iloc[0]['idade']
            client_status = df_user.iloc[0]['status']
            client_role = df_user.iloc[0]['Role_Type']
            client_business = df_user.iloc[0]['categoria_negocio']
            client_document = df_user.iloc[0]['document_number']
            client_created_ch = df_user.iloc[0]['created_at_ch']
            client_created_me = df_user.iloc[0]['created_at_me']
            client_segment = df_user.iloc[0].get('segment', 'N/A')
            client_risk_level = df_user.iloc[0].get('risk_level', 'N/A')
            client_origin = df_user.iloc[0].get('origin', 'N/A')
            
            # Novos campos de endereço
            client_endereco = df_user.iloc[0].get('endereco', 'Não informado')
            client_cidade = df_user.iloc[0].get('cidade', 'Não informado')
            client_estado = df_user.iloc[0].get('estado', 'Não informado')
            
            # Definir a cor do status baseado no valor
            status_color = "color: #dc2626;" if client_status.lower() == "blocked" else "color: #475569;"
            
            # Formatar as datas de criação
            created_ch_str = client_created_ch.strftime('%d/%m/%Y') if pd.notna(client_created_ch) else 'N/A'
            created_me_str = client_created_me.strftime('%d/%m/%Y') if pd.notna(client_created_me) else 'N/A'
            
            # Exibir informações do cliente
            st.markdown(f"""
                <div style='background-color: #f8fafc; padding: 20px; border-radius: 12px; margin-bottom: 20px;'>
                    <h3 style='color: #1e293b; margin-bottom: 15px;'>👤 Informações do Cliente</h3>
                    <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;'>
                        <div>
                            <h4 style='color: #1e293b; margin-bottom: 10px;'>Dados Básicos</h4>
                            <ul style='color: #475569; line-height: 1.6;'>
                                <li><strong>ID do Cliente:</strong> {client_id}</li>
                                <li><strong>Nome:</strong> {client_name}</li>
                                <li><strong>Email:</strong> {client_email} <a href="https://app.intercom.com/a/inbox/cq9sxxvy/inbox/search?query={client_email}" target="_blank" style="color: #2563eb; text-decoration: none; margin-left: 5px;">🔍 Intercom</a></li>
                                <li><strong>Idade:</strong> {client_age} anos</li>
                                <li><strong>Status:</strong> <span style='{status_color}'>{client_status}</span></li>
                                <li><strong>Motivo do Status:</strong> {df_user.iloc[0]['status_reason']}</li>
                            </ul>
                        </div>
                        <div>
                            <h4 style='color: #1e293b; margin-bottom: 10px;'>Informações Adicionais</h4>
                            <ul style='color: #475569; line-height: 1.6;'>
                                <li><strong>Tipo:</strong> {client_role}</li>
                                <li><strong>Categoria do Negócio:</strong> {client_business}</li>
                                <li><strong>Documento:</strong> {client_document}</li>
                                <li><strong>Data de Cadastro Cardholder:</strong> {created_ch_str}</li>
                                <li><strong>Data de Cadastro Merchant:</strong> {created_me_str}</li>
                            </ul>
                        </div>
                    </div>
                    <div style='margin-top: 20px; background: #e0e7ef; border-radius: 8px; padding: 16px;'>
                        <h4 style='color: #1e293b; margin-bottom: 10px;'>📍 Endereço</h4>
                        <ul style='color: #475569; line-height: 1.6;'>
                            <li><strong>Endereço:</strong> {client_endereco}</li>
                            <li><strong>Cidade:</strong> {client_cidade}</li>
                            <li><strong>Estado:</strong> {client_estado}</li>
                        </ul>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Seção de Análise de Ofensas
            st.markdown("### 🚨 Análise de Ofensas")

            # Executar consulta de análise de ofensas
            offense_query = sql_manager.get_offense_analysis_sql(id_client=client_id)
            df_offense = pd.read_gbq(offense_query, project_id=project_id)

            if not df_offense.empty:
                # Converter a data para datetime e ordenar
                df_offense['Data_Offense'] = pd.to_datetime(df_offense['Data_Offense'], dayfirst=True)
                df_offense = df_offense.sort_values('Data_Offense', ascending=False)
                
                # Verificar se existe alguma ofensa normalizada
                ofensas_normais = df_offense[df_offense['conclusion'].str.lower() == 'normal']
                if not ofensas_normais.empty:
                    ultima_normal = ofensas_normais.iloc[0]  # Já está ordenado por data desc
                    data_formatada = pd.to_datetime(ultima_normal['Data_Offense']).strftime('%d/%m/%Y')
                    st.warning(f"⚠️ Este cliente já possui uma ofensa normalizada pelo analista {ultima_normal['analyst']} em {data_formatada}")
                
                # Criar métricas resumidas
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total de Ofensas", len(df_offense))
                
                with col2:
                    st.metric("Última Análise", df_offense['Data_Offense'].iloc[0].strftime('%d/%m/%Y'))
                
                with col3:
                    st.metric("Analista", df_offense['analyst'].iloc[0])
                
                with col4:
                    st.metric("Tipo de Análise", df_offense['name'].iloc[0])
                
                # Exibir tabela com todas as ofensas
                st.markdown("#### Histórico de Ofensas")
                
                # Formatar a data para exibição no dataset
                df_offense['Data_Offense'] = df_offense['Data_Offense'].dt.strftime('%Y-%m-%d')
                
                st.dataframe(
                    df_offense,
                    column_config={
                        "Data_Offense": "Data da Ofensa",
                        "conclusion": "Conclusão",
                        "priority": "Prioridade",
                        "description": "Descrição",
                        "analyst": "Analista",
                        "name": "Tipo de Análise"
                    },
                    hide_index=True
                )
            else:
                st.warning("Nenhuma ofensa encontrada para este cliente.")
            
        except KeyError as e:
            st.error(f"Erro ao processar dados do cliente: Campo {str(e)} não encontrado no resultado da consulta.")
        except Exception as e:
            st.error(f"Erro ao processar dados do cliente: {str(e)}")
    else:
        st.warning("Nenhum dado de cliente foi retornado. Verifique o ID do cliente e tente novamente.")

    # Consulta Pix Concentração
    try:
        query_pix = sql_manager.get_pix_concentration_sql(id_client)
        query_job = client.query(query_pix)
        dataset = query_job.result().to_dataframe()
        st.success("Consulta Pix concluída com sucesso! ✅")
    except Exception as e:
        st.error(f"Erro ao executar a consulta Pix: {e}")
        dataset = None
    
    if dataset is not None and not dataset.empty:
        # Renomear colunas para português
        dataset.rename(columns={
            "user_id": "ID do Usuário",
            "transaction_type": "Tipo de Transação",
            "party": "Parte",
            "pix_amount": "Valor Pix",
            "pix_avg": "Ticket Médio Pix",
            "pix_count": "Quantidade de Pix",
            "percentage": "Percentual",
            "pix_amount_atypical_hours": "Valor Pix em Horário Atípico",
            "pix_count_atypical_hours": "Quantidade de Pix em Horário Atípico",
            "modelo": "Modelo"
        }, inplace=True)
            
        # Formatar as colunas numéricas para o padrão brasileiro
        colunas_formatar = ["Valor Pix", "Ticket Médio Pix", "Valor Pix em Horário Atípico"]
        for coluna in colunas_formatar:
            dataset[coluna] = dataset[coluna].apply(format_float)

        # Criar a coluna numérica para cálculos
        dataset["Valor Pix (num)"] = pd.to_numeric(
            dataset["Valor Pix"].astype(str).apply(lambda x: x.replace(".", "").replace(",", ".")), 
            errors="coerce"
        )
            
        st.markdown("""
            <div style='background-color: #f8fafc; padding: 20px; border-radius: 12px; margin-bottom: 20px;'>
                <h3 style='color: #1e293b; margin-bottom: 15px;'>📊 Dados Analíticos - Consulta Pix</h3>
        """, unsafe_allow_html=True)
            
        # Exibir tabela com estilo personalizado
        st.dataframe(
            dataset,
            use_container_width=True,
            hide_index=True
        )
            
        # Adicionar métricas resumidas para transações PIX
        st.markdown("""
            <div style='background-color: #f8fafc; padding: 20px; border-radius: 12px; margin: 20px 0;'>
                <h3 style='color: #1e293b; margin-bottom: 15px;'>📊 Métricas Resumidas - Transações PIX</h3>
        """, unsafe_allow_html=True)
                
        # Calcular totais para o resumo sintético
        cash_in_total = dataset[dataset['Tipo de Transação'] == 'Cash In']["Valor Pix (num)"].sum()
        cash_out_total = dataset[dataset['Tipo de Transação'] == 'Cash Out']["Valor Pix (num)"].sum()
        total_atipico_pix = dataset["Valor Pix em Horário Atípico"].astype(str).apply(lambda x: x.replace(".", "").replace(",", ".")).astype(float).sum()
        total_transacoes = cash_in_total + cash_out_total
        percentual_atipico_pix = (total_atipico_pix / total_transacoes * 100) if total_transacoes > 0 else 0

        # Criar métricas resumidas para PIX
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Cash In",
                f"R$ {format_float(cash_in_total)}",
                delta=None
            )

        with col2:
            st.metric(
                "Total Cash Out",
                f"R$ {format_float(cash_out_total)}",
                delta=None
            )

        with col3:
            st.metric(
                "Total em Horários Atípicos",
                f"R$ {format_float(total_atipico_pix)}",
                delta=None
            )

        with col4:
            st.metric(
                "% Transações Atípicas",
                f"{format_percent(percentual_atipico_pix)}",
                delta=None
            )
            

            
        balance = cash_in_total - cash_out_total
        
        # Carregar o CSV de apostas ("gateway_bet.csv") e cruzar com a coluna "Parte"
        try:
            csv_path = "src/gateway_bet.csv"
            df_bet = pd.read_csv(csv_path)
            st.success("Dados do gateway BET carregados com sucesso! 🎲")
        except Exception as e:
            st.error(f"Erro ao carregar o CSV 'gateway_bet.csv': {e}")
            df_bet = None
        
        if df_bet is not None and not df_bet.empty and 'gateway' in df_bet.columns:
            dataset['Parte_str'] = dataset['Parte'].astype(str).apply(lambda x: x.strip().lower())
            df_bet['gateway_str'] = df_bet['gateway'].astype(str).apply(lambda x: x.strip().lower())
            bet_mask = dataset['Parte_str'].isin(df_bet['gateway_str'])
            bet_cash_in = dataset[(dataset['Tipo de Transação'] == 'Cash In') & (bet_mask)]["Valor Pix (num)"].sum()
            bet_cash_out = dataset[(dataset['Tipo de Transação'] == 'Cash Out') & (bet_mask)]["Valor Pix (num)"].sum()
        else:
            bet_cash_in = 0
            bet_cash_out = 0
        
        prop_cash_in = (bet_cash_in / cash_in_total * 100) if cash_in_total != 0 else 0
        prop_cash_out = (bet_cash_out / cash_out_total * 100) if cash_out_total != 0 else 0
        
        summary_data = {
            "Tipo de Transação": ["Cash In", "Cash Out", "Saldo", "Bet Cash In", "Bet Cash Out"],
            "Valor Total (R$)": [cash_in_total, cash_out_total, balance, bet_cash_in, bet_cash_out],
            "Proporcional Bet": [prop_cash_in, prop_cash_out, None, None, None]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df["Valor Total (R$)"] = summary_df["Valor Total (R$)"].apply(format_brl)
        summary_df["Proporcional Bet"] = summary_df["Proporcional Bet"].apply(lambda x: format_percent(x) if pd.notnull(x) else "")
        
        st.subheader("💡 Dados Sintéticos - Resumo")
        st.table(summary_df)
        
        # --- NOVO BLOCO: Gráfico de Barras das Maiores Transações ---
        # Selecionar as 5 maiores transações em Cash In e Cash Out com base no valor numérico
        top_cash_in = dataset[dataset['Tipo de Transação'] == 'Cash In'].nlargest(5, 'Valor Pix (num)')
        top_cash_out = dataset[dataset['Tipo de Transação'] == 'Cash Out'].nlargest(5, 'Valor Pix (num)')

        # Truncar o nome da parte para exibir apenas o texto antes do símbolo "|" e converter para maiúsculas
        top_cash_in['Parte'] = top_cash_in['Parte'].str.split('|').str[0].str.upper()
        top_cash_out['Parte'] = top_cash_out['Parte'].str.split('|').str[0].str.upper()

        # Ordenar os dados em ordem decrescente antes de criar os gráficos
        top_cash_in = top_cash_in.sort_values('Valor Pix (num)', ascending=False)
        top_cash_out = top_cash_out.sort_values('Valor Pix (num)', ascending=False)

        # Criar gráfico de barras horizontais para Cash In
        if not top_cash_in.empty:
            fig_cash_in = px.bar(
                top_cash_in,
                y='Parte',
                x='Valor Pix (num)',
                title='Top 5 Transações Cash In',
                labels={'Valor Pix (num)': 'Valor (R$)', 'Parte': ''},
                text='Valor Pix',
                color='Valor Pix (num)',
                color_continuous_scale='Greens',
                orientation='h'
            )
            fig_cash_in.update_traces(
                textposition='outside',
                texttemplate='R$ %{text}',
                hovertemplate='<b>%{y}</b><br>' +
                             'Valor: R$ %{x:,.2f}<br>' +
                             '<extra></extra>'
            )
            fig_cash_in.update_layout(
                template='plotly_white',
                xaxis_title='Valor (R$)',
                yaxis_title=None,
                showlegend=False,
                height=400,
                width=600,
                margin=dict(l=20, r=20, t=40, b=20),
                title=dict(
                    text='Top 5 Transações Cash In',
                    x=0.5,
                    y=0.95,
                    xanchor='center',
                    yanchor='top',
                    font=dict(size=20, color='#1e293b')
                ),
                yaxis=dict(
                    tickfont=dict(size=12),
                    tickangle=0,
                    categoryorder='total descending'
                ),
                xaxis=dict(
                    tickfont=dict(size=12),
                    tickformat='R$ ,.2f'
                )
            )

        # Criar gráfico de barras horizontais para Cash Out
        if not top_cash_out.empty:
            fig_cash_out = px.bar(
                top_cash_out,
                y='Parte',
                x='Valor Pix (num)',
                title='Top 5 Transações Cash Out',
                labels={'Valor Pix (num)': 'Valor (R$)', 'Parte': ''},
                text='Valor Pix',
                color='Valor Pix (num)',
                color_continuous_scale='Reds',
                orientation='h'
            )
            fig_cash_out.update_traces(
                textposition='outside',
                texttemplate='R$ %{text}',
                hovertemplate='<b>%{y}</b><br>' +
                             'Valor: R$ %{x:,.2f}<br>' +
                             '<extra></extra>'
            )
            fig_cash_out.update_layout(
                template='plotly_white',
                xaxis_title='Valor (R$)',
                yaxis_title=None,
                showlegend=False,
                height=400,
                width=600,
                margin=dict(l=20, r=20, t=40, b=20),
                title=dict(
                    text='Top 5 Transações Cash Out',
                    x=0.5,
                    y=0.95,
                    xanchor='center',
                    yanchor='top',
                    font=dict(size=20, color='#1e293b')
                ),
                yaxis=dict(
                    tickfont=dict(size=12),
                    tickangle=0,
                    categoryorder='total descending'
                ),
                xaxis=dict(
                    tickfont=dict(size=12),
                    tickformat='R$ ,.2f'
                )
            )

        # Exibir gráficos lado a lado
        if not top_cash_in.empty or not top_cash_out.empty:
            st.markdown("""
                <div style='background-color: #f8fafc; padding: 20px; border-radius: 12px; margin: 20px 0;'>
                    <h3 style='color: #1e293b; margin-bottom: 15px;'>📈 Top 5 Transações</h3>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)

            if not top_cash_in.empty:
                with col1:
                    st.markdown("""
                        <div style='background-color: #f0fdf4; padding: 15px; border-radius: 8px; margin-bottom: 10px;'>
                            <h4 style='color: #166534; margin: 0;'>💵 Cash In</h4>
                        </div>
                    """, unsafe_allow_html=True)
                    st.plotly_chart(fig_cash_in, use_container_width=True)

            if not top_cash_out.empty:
                with col2:
                    st.markdown("""
                        <div style='background-color: #fef2f2; padding: 15px; border-radius: 8px; margin-bottom: 10px;'>
                            <h4 style='color: #991b1b; margin: 0;'>💸 Cash Out</h4>
                        </div>
                    """, unsafe_allow_html=True)
                    st.plotly_chart(fig_cash_out, use_container_width=True)

            # Gráfico de dispersão entre Quantidade de Pix e Valor Pix (num)
            st.markdown("""
                <div style='background-color: #f8fafc; padding: 20px; border-radius: 12px; margin: 20px 0;'>
                    
                """, unsafe_allow_html=True)
            
            fig_disp = px.scatter(
                dataset,
                x='Quantidade de Pix',
                y='Valor Pix (num)',
                color='Tipo de Transação',
                hover_data=['Parte', 'Valor Pix', 'Ticket Médio Pix'],
                labels={
                    'Quantidade de Pix': 'Quantidade de Pix',
                    'Valor Pix (num)': 'Valor Total Pix (R$)',
                    'Tipo de Transação': 'Tipo'
                },
                title='Dispersão entre Quantidade de Pix e Valor Total',
                template='plotly_white',
                symbol='Tipo de Transação',
                size='Valor Pix (num)',
                size_max=18
            )
            fig_disp.update_traces(marker=dict(opacity=0.7, line=dict(width=1, color='DarkSlateGrey')))
            fig_disp.update_layout(
                xaxis_title='Quantidade de Pix',
                yaxis_title='Valor Total Pix (R$)',
                legend_title='Tipo de Transação',
                height=500,
                margin=dict(l=20, r=20, t=40, b=20),
                title=dict(
                    text='Dispersão entre Quantidade de Pix e Valor Total',
                    x=0.5,
                    y=0.95,
                    xanchor='center',
                    yanchor='top',
                    font=dict(size=20, color='#1e293b')
                )
            )
            st.plotly_chart(fig_disp, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Nenhuma transação encontrada para exibição.")
        # --- Fim do Gráfico de Barras ---

                # Adicionar seção de party document numbers
        st.markdown("### 📄 Party Document Numbers")
        
        # Buscar os document numbers
        result = get_top_pix_transactions(id_client)
        if "erro" not in result:
            # Criar duas colunas para exibir os documentos e suas análises
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 👤↘️ Top 2 Party Cash In Info")
                if result['cash_in']:
                    for doc_in in result['cash_in']:
                        basic_info = get_basic_summary(doc_in)
                        kyc_info = get_kyc_summary(doc_in)
                        summary_cash_in = get_processes_summary(doc_in)
                        has_criminal = bool(summary_cash_in.get("destaque"))
                        expander_label = f"{'🚨 ' if has_criminal else ''}Documento: {doc_in}"
                        with st.expander(expander_label, expanded=has_criminal):
                            if "erro" not in basic_info:
                                st.write(f"**Nome:** {basic_info['nome']}")
                            if "erro" not in kyc_info:
                                nome = kyc_info.get('nome', 'Não encontrado')
                                if nome == 'Não encontrado' and "erro" not in basic_info:
                                    nome = basic_info.get('nome', 'Não encontrado')
                                doc = kyc_info.get('documento', 'Não encontrado')
                                if doc != doc_in:
                                    st.markdown(f"**Documento:** {doc}")
                                st.markdown(f"**Data de Nascimento:** {kyc_info.get('data_nascimento', 'Não encontrado')}")
                                st.markdown(f"**PEP:** {'Sim' if kyc_info.get('is_pep') else 'Não'}")
                                st.markdown(f"**Sancionado:** {'Sim' if kyc_info.get('is_sancionado') else 'Não'}")
                                st.markdown(f"**Total de Sanções:** {kyc_info.get('sanctions_count', 0)}")
                            if "erro" not in summary_cash_in:
                                risk_color = {
                                    "ALTO": "#dc2626",
                                    "MÉDIO": "#d97706",
                                    "BAIXO": "#059669"
                                }.get(summary_cash_in["nivel_risco"], "#475569")
                                st.markdown(f"""
                                    **Nível de Risco:** <span style='color: {risk_color}; font-weight: bold;'>{summary_cash_in["nivel_risco"]}</span>
                                    **Resumo dos Processos:**
                                    - Processos Ativos: {summary_cash_in["total_ativos"]}
                                    - Processos Arquivados: {summary_cash_in["total_arquivados"]}
                                    \n**Principais Tipos de Processos:**
                                    {', '.join(summary_cash_in["tipos_principais"]) if summary_cash_in["tipos_principais"] else "Nenhum processo encontrado"}
                                    **Status Predominante:**
                                    {summary_cash_in["status_predominante"]}
                                """, unsafe_allow_html=True)
                                # NOVO: Exibir detalhes dos processos
                                processos = summary_cash_in.get("processos_detalhados", [])
                                if processos:
                                    st.markdown("**Detalhes dos Processos:**")
                                    for proc in processos:
                                        tribunal = proc.get('tribunal', 'Não informado')
                                        st.markdown(f"""
                                            <div style='background-color:#f1f5f9; border-radius:6px; padding:8px; margin-bottom:6px;'>
                                            <b>Número:</b> {proc.get('numero', 'Não informado')}<br>
                                            <b>Tipo:</b> {proc.get('tipo', 'Não informado')}<br>
                                            <b>Natureza:</b> {proc.get('natureza', 'Não informado')}<br>
                                            <b>Órgão:</b> {tribunal}<br>
                                            <b>Status:</b> {proc.get('status', 'Não informado')}<br>
                                            <b>Data:</b> {proc.get('data', 'Não informada')}
                                            </div>
                                        """, unsafe_allow_html=True)
                                if has_criminal:
                                    st.markdown(f"<div style='background-color:#fee2e2; color:#dc2626; padding:10px; border-radius:8px; font-weight:bold;'>🚨 {summary_cash_in['destaque']}</div>", unsafe_allow_html=True)
                            else:
                                st.warning("Nenhuma análise BDC disponível para Cash In")
                else:
                    st.write("Nenhum documento encontrado")

            with col2:
                st.markdown("#### 👤↗️ Top 2 Party Cash Out Info")
                if result['cash_out']:
                    for doc_out in result['cash_out']:
                        basic_info = get_basic_summary(doc_out)
                        kyc_info = get_kyc_summary(doc_out)
                        summary_cash_out = get_processes_summary(doc_out)
                        has_criminal = bool(summary_cash_out.get("destaque"))
                        expander_label = f"{'🚨 ' if has_criminal else ''}Documento: {doc_out}"
                        with st.expander(expander_label, expanded=has_criminal):
                            if "erro" not in basic_info:
                                st.write(f"**Nome:** {basic_info['nome']}")
                            if "erro" not in kyc_info:
                                nome = kyc_info.get('nome', 'Não encontrado')
                                if nome == 'Não encontrado' and "erro" not in basic_info:
                                    nome = basic_info.get('nome', 'Não encontrado')
                                doc = kyc_info.get('documento', 'Não encontrado')
                                if doc != doc_out:
                                    st.markdown(f"**Documento:** {doc}")
                                st.markdown(f"**Data de Nascimento:** {kyc_info.get('data_nascimento', 'Não encontrado')}")
                                st.markdown(f"**PEP:** {'Sim' if kyc_info.get('is_pep') else 'Não'}")
                                st.markdown(f"**Sancionado:** {'Sim' if kyc_info.get('is_sancionado') else 'Não'}")
                                st.markdown(f"**Total de Sanções:** {kyc_info.get('sanctions_count', 0)}")
                            if "erro" not in summary_cash_out:
                                risk_color = {
                                    "ALTO": "#dc2626",
                                    "MÉDIO": "#d97706",
                                    "BAIXO": "#059669"
                                }.get(summary_cash_out["nivel_risco"], "#475569")
                                st.markdown(f"""
                                    **Nível de Risco:** <span style='color: {risk_color}; font-weight: bold;'>{summary_cash_out["nivel_risco"]}</span>
                                    **Resumo dos Processos:**
                                    - Processos Ativos: {summary_cash_out["total_ativos"]}
                                    - Processos Arquivados: {summary_cash_out["total_arquivados"]}
                                    **Principais Tipos de Processos:**
                                    {', '.join(summary_cash_out["tipos_principais"]) if summary_cash_out["tipos_principais"] else "Nenhum processo encontrado"}
                                    **Status Predominante:**
                                    {summary_cash_out["status_predominante"]}
                                """, unsafe_allow_html=True)
                                # NOVO: Exibir detalhes dos processos
                                processos = summary_cash_out.get("processos_detalhados", [])
                                if processos:
                                    st.markdown("**Detalhes dos Processos:**")
                                    for proc in processos:
                                        tribunal = proc.get('tribunal', 'Não informado')
                                        st.markdown(f"""
                                            <div style='background-color:#f1f5f9; border-radius:6px; padding:8px; margin-bottom:6px;'>
                                            <b>Número:</b> {proc.get('numero', 'Não informado')}<br>
                                            <b>Tipo:</b> {proc.get('tipo', 'Não informado')}<br>
                                            <b>Natureza:</b> {proc.get('natureza', 'Não informado')}<br>
                                            <b>Órgão:</b> {tribunal}<br>
                                            <b>Status:</b> {proc.get('status', 'Não informado')}<br>
                                            <b>Data:</b> {proc.get('data', 'Não informada')}
                                            </div>
                                        """, unsafe_allow_html=True)
                                if has_criminal:
                                    st.markdown(f"<div style='background-color:#fee2e2; color:#dc2626; padding:10px; border-radius:8px; font-weight:bold;'>🚨 {summary_cash_out['destaque']}</div>", unsafe_allow_html=True)
                            else:
                                st.warning("Nenhuma análise BDC disponível para Cash Out")
                else:
                    st.write("Nenhum documento encontrado")
        else:
            st.error(result["erro"])

        # Após a exibição dos gráficos de Cash In e Cash Out, adicionar:
        if not top_cash_in.empty and not top_cash_out.empty:
            st.markdown("---")
            st.markdown("### 🤖 Análise Inteligente de Sanções e Processos")
            
            with st.spinner("Gerando análise judicial inteligente..."):
                # Buscar o documento do usuário para análise do BDC
                document = get_user_document(id_client)
                if document:
                    # Criar um contexto específico para a análise 
                    context = f"""
                    Analise o documento {document} e forneça um resumo objetivo sobre:
                    1. Existência de sanções ou processos judiciais
                    2. Natureza dos processos (se houver)
                    3. Valores envolvidos nos processos
                    4. Status atual dos processos
                    5. Recomendações de ação baseadas nas informações encontradas
                    
                    Formate a resposta em tópicos claros e objetivos.
                    """
                    
                    analysis = analyze_bdc_data(document, context)
                    if analysis:
                        # Container principal com estilo
                        st.markdown("""
                            <div style='background-color: #f8fafc; padding: 20px; border-radius: 12px; margin: 20px 0;'>
                                <h3 style='color: #1e293b; margin-bottom: 15px;'>👨🏻‍⚖️ Análise de Sanções e Processos</h3>
                        """, unsafe_allow_html=True)
                        
                        # Extrair informações relevantes do dicionário
                        if isinstance(analysis, dict):
                            nome = analysis.get('name', 'Não encontrado')
                            doc = analysis.get('document', 'Não encontrado')
                            processos_ativos = len(analysis.get('active_processes', []))
                            processos_arquivados = len(analysis.get('archived_processes', []))
                            total_sancoes = len(analysis.get('sanctions', []))
                            
                            # Métricas principais em colunas
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Processos Ativos", processos_ativos)
                            with col2:
                                st.metric("Processos Arquivados", processos_arquivados)
                            with col3:
                                st.metric("Total de Sanções", total_sancoes)
                            
                            # Informações básicas
                            st.markdown(f"""
                                ### 📋 Informações Básicas
                                - **Nome:** {nome}
                                - **Documento:** {doc}
                            """)
                            
                            # Seção de Processos Ativos
                            if processos_ativos > 0:
                                st.markdown("### ⚖️ Processos Ativos")
                                for proc in analysis.get('active_processes', []):
                                    with st.expander(f"Processo {proc['number']} - {proc.get('type', 'Não informado')}"):
                                        st.markdown(f"""
                                            - **Natureza:** {proc.get('natureza', 'Não informado')}
                                            - **Valor:** R$ {proc.get('value', 0):,.2f}
                                            - **Status:** {proc.get('status', 'Não informado')}
                                            - **Localização:** {proc.get('location', 'Não informado')}
                                            - **Último Movimento:** {proc.get('last_movement', 'Não informado')}
                                            - **Partes Envolvidas:**
                                        """)
                                        for parte in proc.get('parties', []):
                                            st.markdown(f"  - {parte}")
                                        if proc.get('updates'):
                                            st.markdown("**Últimas Atualizações:**")
                                            for update in proc['updates'][-3:]:  # Mostrar apenas as 3 últimas atualizações
                                                st.markdown(f"  - {update}")
                            
                            # Seção de Sanções
                            if total_sancoes > 0:
                                st.markdown("### ⚠️ Sanções")
                                for sancao in analysis.get('sanctions', []):
                                    with st.expander(f"Sanção: {sancao['type']} - {sancao['status']}"):
                                        st.markdown(f"""
                                            - **Descrição:** {sancao['description']}
                                            - **Data:** {sancao['date']}
                                            - **Agência:** {sancao['agency']}
                                            - **Estado:** {sancao['state']}
                                            - **Magistrado:** {sancao['magistrate']}
                                            - **Número do Mandado:** {sancao['warrant_number']}
                                            - **Número do Processo:** {sancao['process_number']}
                                            - **Data de Expiração:** {sancao['expiration_date']}
                                            - **Regime de Prisão:** {sancao['imprisonment_kind']}
                                        """)
                            
                            # Análise de Risco
                            st.markdown("### 🎯 Análise de Risco")
                            nivel_risco = "ALTO" if total_sancoes > 0 or processos_ativos > 0 else "BAIXO"
                            cor_risco = "#dc2626" if nivel_risco == "ALTO" else "#059669"
                            
                            st.markdown(f"""
                                <div style='background-color: {cor_risco}20; padding: 15px; border-radius: 8px; margin: 10px 0;'>
                                    <h4 style='color: {cor_risco}; margin: 0;'>Nível de Risco: {nivel_risco}</h4>
                                    <p style='margin: 10px 0 0 0;'>
                                        {f"⚠️ Atenção: {total_sancoes} sanções ativas e {processos_ativos} processos em andamento." if nivel_risco == "ALTO" else "✅ Situação regular, sem sanções ou processos ativos."}
                                    </p>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Recomendações
                            st.markdown("### 💡 Recomendações")
                            if nivel_risco == "ALTO":
                                st.markdown("""
                                    - Realizar análise detalhada dos processos ativos
                                    - Verificar possíveis impactos nas operações
                                    - Considerar restrições adicionais
                                    - Monitorar atualizações dos processos
                                """)
                            else:
                                st.markdown("""
                                    - Manter monitoramento regular
                                    - Verificar atualizações periódicas
                                    - Documentar análise de risco
                                """)
                        else:
                            st.markdown(analysis)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.error("Não foi possível gerar a análise das transações. Por favor, tente novamente mais tarde.")

    else:
        st.error("Nenhum dado retornado da consulta. ❌")
        
    # Consulta transações de cartões
    if "Acquiring" in selected_options:
        try:
            query_card = sql_manager.get_card_transactions_sql(id_client)
            query_job_card = client.query(query_card)
            df_card_transactions = query_job_card.result().to_dataframe()
            
            if df_card_transactions is not None and not df_card_transactions.empty:
                # Renomear colunas para português
                df_card_transactions.rename(columns={
                    "card_holder_name": "Nome do Portador",
                    "capture_method": "Método de Captura",
                    "Total_Aprovado": "Total Aprovado",
                    "Qtd_Cartoes": "Qtd. Cartões",
                    "Qtd_Transacoes": "Qtd. Transações",
                    "Total_Aprovado_Atipico": "Total em Horário Atípico",
                    "Percentual_TPV": "% do TPV",
                    "card_token_id": "Token do Cartão"
                }, inplace=True)
                
                # Formatar valores monetários
                df_card_transactions["Total Aprovado"] = df_card_transactions["Total Aprovado"].apply(format_brl)
                df_card_transactions["Total em Horário Atípico"] = df_card_transactions["Total em Horário Atípico"].apply(format_brl)
                
                # Formatar percentual do TPV
                if "Percentual_TPV" in df_card_transactions.columns:
                    df_card_transactions["% do TPV"] = df_card_transactions["Percentual_TPV"].apply(
                        lambda x: f"{float(x):.2f}%" if pd.notna(x) and str(x).strip() != '' else "0.00%"
                    )
                
                st.markdown("""
                    <div style='background-color: #f8fafc; padding: 20px; border-radius: 12px; margin: 20px 0;'>
                        <h3 style='color: #1e293b; margin-bottom: 15px;'>💳 Transações de Cartão</h3>
                """, unsafe_allow_html=True)
                
                # Calcular métricas resumidas
                total_aprovado = sum([convert_brl_to_float(v) for v in df_card_transactions["Total Aprovado"]])
                total_atipico = sum([convert_brl_to_float(v) for v in df_card_transactions["Total em Horário Atípico"]])
                qtd_portadores = len(df_card_transactions["Nome do Portador"].unique())
                perc_atipico = (total_atipico / total_aprovado * 100) if total_aprovado > 0 else 0
                
                # Exibir métricas resumidas usando st.metric
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Total Aprovado",
                        format_brl(total_aprovado),
                        delta=None
                    )
                
                with col2:
                    st.metric(
                        "Total em Horário Atípico",
                        format_brl(total_atipico),
                        delta=None
                    )
                
                with col3:
                    st.metric(
                        "Quantidade de Portadores",
                        f"{qtd_portadores}",
                        delta=None
                    )
                
                with col4:
                    st.metric(
                        "% em Horário Atípico",
                        f"{perc_atipico:.2f}%",
                        delta=None
                    )
                
                st.dataframe(
                    df_card_transactions,
                    use_container_width=True,
                    hide_index=True
                )
                
                st.markdown("""
                    <h3 style='color: #1e293b; margin-bottom: 15px;'>📊 Transações por Método de Captura</h3>
                """, unsafe_allow_html=True)
                
                # Criar DataFrame agrupado por método de captura
                df_by_method = df_card_transactions.groupby('Método de Captura').agg({
                    'Total Aprovado': lambda x: sum([convert_brl_to_float(v) for v in x]),
                    'Total em Horário Atípico': lambda x: sum([convert_brl_to_float(v) for v in x])
                }).reset_index()
                
                # Formatar valores do DataFrame agrupado
                df_by_method['Total Aprovado'] = df_by_method['Total Aprovado'].apply(format_brl)
                df_by_method['Total em Horário Atípico'] = df_by_method['Total em Horário Atípico'].apply(format_brl)
                
                # Calcular percentual de transações atípicas
                df_by_method['% Transações Atípicas'] = (
                    df_by_method['Total em Horário Atípico'].apply(convert_brl_to_float) / 
                    df_by_method['Total Aprovado'].apply(convert_brl_to_float) * 100
                ).round(2).astype(str) + '%'
                
                st.dataframe(
                    df_by_method,
                    use_container_width=True,
                    hide_index=True
                )
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("Nenhuma transação de cartão encontrada.")
                
            st.success("Análise de transações de cartões concluída com sucesso! ✅")
        except Exception as e:
            st.error(f"Erro na consulta de transações de cartões: {str(e)}")

    # Executar consulta de informações de contato
    try:
        query_contact_info = sql_manager.get_contact_info_sql(id_client)
        query_job_contact = client.query(query_contact_info)
        df_contact_info = query_job_contact.result().to_dataframe()
        st.success("Consulta de informações de contato concluída com sucesso! ✅")
    except Exception as e:
        st.error(f"Erro ao executar a consulta de informações de contato: {e}")
        df_contact_info = None
    
    if df_contact_info is not None and not df_contact_info.empty:
        # Renomear colunas para português
        df_contact_info.rename(columns={
            "has_phonecast": "Possui Phonecast",
            "user_id": "ID do Usuário",
            "name": "Nome",
            "raw_phone_number": "Número de Telefone",
            "status": "Status",
            "status_reason": "Motivo do Status"
        }, inplace=True)

        # Converter has_phonecast para texto mais amigável
        df_contact_info["Possui Phonecast"] = df_contact_info["Possui Phonecast"].map({True: "Sim", False: "Não"})

        st.markdown("""
            <div style='background-color: #f8fafc; padding: 20px; border-radius: 12px; margin: 20px 0;'>
                <h3 style='color: #1e293b; margin-bottom: 15px;'>📱⭕️ Informações de Contatos Bloqueados</h3>
        """, unsafe_allow_html=True)

        # Exibir tabela com estilo personalizado
        st.dataframe(
            df_contact_info,
            use_container_width=True,
            hide_index=True
        )

        # Criar tabela sintética de bloqueios por motivo
        if 'Status' in df_contact_info.columns and 'Motivo do Status' in df_contact_info.columns:
            # Filtrar apenas registros bloqueados
            df_blocked = df_contact_info[df_contact_info['Status'] != 'active'].copy()
            
            # Agrupar por motivo do status e contar
            blocked_summary = df_blocked.groupby('Motivo do Status').size().reset_index(name='Quantidade')
            
            # Ordenar por quantidade em ordem decrescente
            blocked_summary = blocked_summary.sort_values('Quantidade', ascending=False)
            
            # Calcular o total
            total_blocked = blocked_summary['Quantidade'].sum()
            
            # Adicionar coluna de percentual
            blocked_summary['Percentual'] = (blocked_summary['Quantidade'] / total_blocked * 100).round(2)
            
            # Formatar percentual
            blocked_summary['Percentual'] = blocked_summary['Percentual'].apply(lambda x: f"{x:.2f}%")
            
            st.markdown("""
                <div style='background-color: #f8fafc; padding: 20px; border-radius: 12px; margin: 20px 0;'>
                    <h3 style='color: #1e293b; margin-bottom: 15px;'>🚫 Análise de Bloqueios por Motivo</h3>
            """, unsafe_allow_html=True)
            
            # Exibir métrica do total de bloqueios
            st.metric(
                "Total de Registros Bloqueados",
                f"{total_blocked}",
                delta=None
            )
            
            # Exibir tabela sintética
            st.dataframe(
                blocked_summary,
                use_container_width=True,
                hide_index=True
            )
    else:
        st.warning("Nenhuma informação de contato bloqueado encontrada para este cliente.")
    
    # Consulta PEP
    if "PEP" in selected_options:
        try:
            query_pep = sql_manager.get_pep_sql(id_client)
            query_job_pep = client.query(query_pep)
            df_pep = query_job_pep.result().to_dataframe()
            
            if not df_pep.empty:
                st.markdown("""
                    <div style='background-color: #f8fafc; padding: 20px; border-radius: 12px; margin: 20px 0;'>
                        <h3 style='color: #1e293b; margin-bottom: 15px;'>👥 Transações com PEP</h3>
                """, unsafe_allow_html=True)
                
                # Exibir tabela com estilo personalizado
                st.dataframe(
                    df_pep,
                    use_container_width=True,
                    hide_index=True
                )
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("Nenhuma transação com PEP encontrada para este cliente.")
                
            st.success("Consulta PEP concluída com sucesso! ✅")
        except Exception as e:
            st.error(f"Erro ao executar a consulta de transações PEP: {e}")
            df_pep = None
    
    # Consulta Cartões Corporativos
    if "Cartões Corporativos" in selected_options:
        try:
            query_corporate = sql_manager.get_corporate_cards_sql(id_client)
            query_job_corporate = client.query(query_corporate)
            df_corporate = query_job_corporate.result().to_dataframe()
            
            if not df_corporate.empty:
                st.markdown("""
                    <div style='background-color: #f8fafc; padding: 20px; border-radius: 12px; margin: 20px 0;'>
                        <h3 style='color: #1e293b; margin-bottom: 15px;'>💳 Cartões Corporativos</h3>
                """, unsafe_allow_html=True)
                
                # Exibir tabela com estilo personalizado
                st.dataframe(
                    df_corporate,
                    use_container_width=True,
                    hide_index=True
                )
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("Nenhuma transação com cartões corporativos encontrada para este cliente.")
                
            st.success("Consulta Cartões Corporativos concluída com sucesso! ✅")
        except Exception as e:
            st.error(f"Erro ao executar a consulta de cartões corporativos: {e}")
            df_corporate = None
    
    # Consulta GAFI
    if "GAFI" in selected_options:
        try:
            query_gafi = sql_manager.get_gafi_sql(id_client)
            query_job_gafi = client.query(query_gafi)
            df_gafi = query_job_gafi.result().to_dataframe()
            
            if not df_gafi.empty:
                st.markdown("""
                    <div style='background-color: #f8fafc; padding: 20px; border-radius: 12px; margin: 20px 0;'>
                        <h3 style='color: #1e293b; margin-bottom: 15px;'>🔍 Transações GAFI</h3>
                """, unsafe_allow_html=True)
                
                # Exibir tabela com estilo personalizado
                st.dataframe(
                    df_gafi,
                    use_container_width=True,
                    hide_index=True
                )
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("Nenhuma transação GAFI encontrada para este cliente.")
                
            st.success("Consulta GAFI concluída com sucesso! ✅")
        except Exception as e:
            st.error(f"Erro ao executar a consulta GAFI: {e}")
            df_gafi = None
    
    # Consulta TED
    if "TED" in selected_options:
        try:
            query_ted = sql_manager.get_ted_sql(id_client)
            query_job_ted = client.query(query_ted)
            df_ted = query_job_ted.result().to_dataframe()
            
            if not df_ted.empty:
                st.markdown("""
                    <div style='background-color: #f8fafc; padding: 20px; border-radius: 12px; margin: 20px 0;'>
                        <h3 style='color: #1e293b; margin-bottom: 15px;'>💸 Transações TED</h3>
                """, unsafe_allow_html=True)
                
                # Exibir tabela com estilo personalizado
                st.dataframe(
                    df_ted,
                    use_container_width=True,
                    hide_index=True
                )
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("Nenhuma transação TED encontrada para este cliente.")
                
            st.success("Consulta TED concluída com sucesso! ✅")
        except Exception as e:
            st.error(f"Erro ao executar a consulta TED: {e}")
            df_ted = None
    
    # Consulta Issuing
    if "Issuing" in selected_options:
        try:
            query_issuing = sql_manager.get_issuing_sql(id_client)
            query_job_issuing = client.query(query_issuing)
            df_issuing = query_job_issuing.result().to_dataframe()
            
            if not df_issuing.empty:
                st.markdown("""
                    <div style='background-color: #f8fafc; padding: 20px; border-radius: 12px; margin: 20px 0;'>
                        <h3 style='color: #1e293b; margin-bottom: 15px;'>💳 Transações Issuing</h3>
                """, unsafe_allow_html=True)
                
                # Exibir tabela com estilo personalizado
                st.dataframe(
                    df_issuing,
                    use_container_width=True,
                    hide_index=True
                )
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("Nenhuma transação Issuing encontrada para este cliente.")
                
            st.success("Consulta Issuing concluída com sucesso! ✅")
        except Exception as e:
            st.error(f"Erro ao executar a consulta Issuing: {e}")
            df_issuing = None
    
    # Consulta transações internacionais
    if "Internacionais" in selected_options:
        try:
            query_international = sql_manager.get_international_transactions_sql(id_client)
            query_job_international = client.query(query_international)
            df_international = query_job_international.result().to_dataframe()
            
            if df_international is not None and not df_international.empty:
                # Renomear colunas para português
                df_international.rename(columns={
                    "merchant_id": "ID do Cliente",
                    "id": "ID da Transação",
                    "created_at": "Data da Transação",
                    "amount": "Valor",
                    "card_holder_name": "Nome do Portador",
                    "card_number": "Número do Cartão",
                    "card_token_id": "Token do Cartão",
                    "issuer_id": "ID do Emissor",
                    "legal_name": "Nome do Emissor",
                    "Country_Name": "País",
                    "capture_method": "Método de Captura"
                }, inplace=True)
                
                # Formatar valores monetários
                df_international["Valor"] = df_international["Valor"].apply(format_brl)
                
                # Mascarar número do cartão
                df_international["Número do Cartão"] = df_international["Número do Cartão"].apply(
                    lambda x: f"{str(x)[:6]}******{str(x)[-4:]}" if pd.notna(x) else "N/A"
                )
                
                # Formatar data
                df_international["Data da Transação"] = pd.to_datetime(df_international["Data da Transação"]).dt.strftime('%d/%m/%Y %H:%M:%S')
                
                st.markdown("""
                    <div style='background-color: #f8fafc; padding: 20px; border-radius: 12px; margin: 20px 0;'>
                        <h3 style='color: #1e293b; margin-bottom: 15px;'>🌍 Transações Internacionais</h3>
                """, unsafe_allow_html=True)
                
                st.dataframe(
                    df_international,
                    use_container_width=True,
                    hide_index=True
                )
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("Nenhuma transação internacional encontrada.")
                
            st.success("Análise de transações internacionais concluída com sucesso! ✅")
        except Exception as e:
            st.error(f"Erro na consulta de transações internacionais: {str(e)}")
    
    # Marcar a análise como concluída
    st.session_state.analysis_done = True
    st.session_state.should_analyze = False
    
    st.markdown("""
        <div style='background-color: #ecfdf5; padding: 20px; border-radius: 12px; margin: 20px 0;'>
            <h3 style='color: #059669; margin-bottom: 10px;'>✅ Análise Concluída!</h3>
            <p style='color: #065f46; line-height: 1.6;'>
                A análise foi realizada com sucesso. Você pode visualizar todos os dados e gráficos acima.
                Para realizar uma nova análise, basta inserir um novo ID de cliente.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Limpar dados da sessão após conclusão
    clean_session_state()
    
    # Forçar coleta de lixo
    gc.collect()

def get_pix_transactions(user_id: str):
    """
    Busca as transações PIX de um usuário e armazena no session_state.
    
    Args:
        user_id (str): ID do usuário
    """
    try:
        # Buscar transações PIX
        result = get_top_pix_transactions(user_id)
        
        if isinstance(result, dict):
            st.session_state['top_5_transactions'] = result['top_5_transactions']
            st.session_state['client_name'] = result['client_name']
            return True
        else:
            st.error(result)
            return False
            
    except Exception as e:
        st.error(f"Erro ao buscar transações PIX: {str(e)}")
        return False

#def main():
    # Conteúdo principal
    if 'top_5_transactions' in st.session_state:
        # Exibir nome do cliente
        if 'client_name' in st.session_state:
            st.markdown(f"### Cliente: {st.session_state['client_name']}")
        
        # Exibir top 5 transações
     #  st.markdown("### Top 5 Transações PIX")
        
        for i, transaction in enumerate(st.session_state['top_5_transactions'], 1):
            with st.expander(f"Transação {i}: {transaction['party_name']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Tipo:** {transaction['transaction_type']}")
                    st.markdown(f"**Documento:** {transaction['party_document_number']}")
                    st.markdown(f"**Valor Total:** R$ {format_brl(transaction['pix_amount'])}")
                    st.markdown(f"**Número de Transações:** {transaction['pix_count']}")
                with col2:
                    st.markdown(f"**Valor Médio:** R$ {format_brl(transaction['pix_avg'])}")
                    st.markdown(f"**Percentual:** {format_percent(transaction['percentage'])}")
                    st.markdown(f"**Transações em Horário Atípico:** {transaction['pix_count_atypical_hours']}")
                    st.markdown(f"**Valor em Horário Atípico:** R$ {format_brl(transaction['pix_amount_atypical_hours'])}")

#if __name__ == "__main__":
    main()


