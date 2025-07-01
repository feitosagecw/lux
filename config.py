import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração da API OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("A chave da API OpenAI não foi encontrada. Verifique se o arquivo .env existe e contém OPENAI_API_KEY.")

# Configuração do modelo
DEFAULT_MODEL = "gpt-4-turbo-preview"  # Atualizado para o modelo mais recente 