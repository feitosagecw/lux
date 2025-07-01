#!/bin/bash

# Ativar o ambiente virtual
echo "Ativando ambiente virtual..."
source venv/bin/activate

# Verificar se a autenticação do Google Cloud já está configurada
if ! gcloud auth application-default print-access-token &>/dev/null; then
    echo "Realizando autenticação do Google Cloud..."
    gcloud auth application-default login
else
    echo "Autenticação do Google Cloud já está configurada."
fi

# Iniciar o Streamlit
echo "Iniciando o Streamlit..."
streamlit run app.py 